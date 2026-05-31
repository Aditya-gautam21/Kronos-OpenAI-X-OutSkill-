import os
import json
from dotenv import load_dotenv
from binance.client import Client
from binance.exceptions import BinanceAPIException

from backend.quant.agent import QuantAgent
from backend.quant.kelly import kelly_position_size

load_dotenv()

LEVERAGE = 5
MAX_RISK_PCT = 0.10


class TradeExecutionAgent:
    def __init__(self):
        self.client = Client(
            api_key=os.getenv("BINANCE_TESTNET_API"),
            api_secret=os.getenv("BINANCE_TESTNET_SECRET"),
            testnet=True,
        )

    def get_balance(self) -> float:
        balances = self.client.futures_account_balance()
        usdt = next((item for item in balances if item["asset"] == "USDT"), None)
        if not usdt:
            raise Exception("No USDT balance found on testnet")
        return float(usdt["balance"])

    def cancel_all_orders(self, symbol: str):
        try:
            orders = self.client.futures_get_open_orders(symbol=symbol)
            for o in orders:
                self.client.futures_cancel_order(symbol=symbol, orderId=o["orderId"])
            if orders:
                print(f"  Cancelled {len(orders)} existing open order(s)")
        except BinanceAPIException as e:
            print(f"  [WARN] Cancel orders failed: {e}")

    def set_leverage(self, symbol: str):
        try:
            self.client.futures_change_leverage(symbol=symbol, leverage=LEVERAGE)
        except BinanceAPIException as e:
            print(f"  [WARN] Leverage: {e}")

    def place_entry(self, symbol: str, direction: str, quantity: float) -> dict:
        side = "SELL" if direction == "short" else "BUY"
        return self.client.futures_create_order(
            symbol=symbol,
            side=side,
            type="MARKET",
            quantity=quantity
        )

    def place_sl(self, symbol: str, direction: str, stop_price: float, quantity: float) -> dict:
        side = "BUY" if direction == "short" else "SELL"
        return self.client.futures_create_order(
            symbol=symbol,
            side=side,
            type="STOP_MARKET",
            stopPrice=round(stop_price, 2),
            quantity=quantity,
            reduceOnly=True,
            workingType="MARK_PRICE",
            priceProtect="TRUE",
        )

    def place_tp(self, symbol: str, direction: str, tp_price: float, quantity: float) -> dict:
        side = "BUY" if direction == "short" else "SELL"
        return self.client.futures_create_order(
            symbol=symbol,
            side=side,
            type="TAKE_PROFIT_MARKET",
            stopPrice=round(tp_price, 2),
            quantity=quantity,
            reduceOnly=True,
            workingType="MARK_PRICE",
            priceProtect="TRUE",
        )

    def execute(self) -> dict:
        print("--- Research Agent ---")
        trade = QuantAgent().generate_trade()

        if not trade or not trade.get("edge_found"):
            reason = (trade or {}).get("hypothesis", "No edge found")
            print(f"SKIP: {reason}")
            return {"status": "skipped", "reason": reason}

        symbol = trade.get("symbol")

        balance = self.get_balance()
        print(f"Balance: ${balance:.2f}")

        sizing = kelly_position_size(
            confidence=trade["confidence"],
            direction=trade["direction"],
            entry_price=trade["entry_price"],
            stop_loss=trade["stop_loss"],
            take_profit=trade["take_profit"],
            balance=balance,
            leverage=LEVERAGE,
            max_risk_pct=MAX_RISK_PCT,
        )

        if sizing.get("error") or sizing["quantity"] <= 0:
            print(f"SKIP: zero quantity — {sizing.get('error', '')}")
            return {"status": "skipped", "reason": sizing.get("error", "zero quantity")}

        qty = sizing.get("quantity")
        print(f"Qty: {qty} | Notional: ${sizing['notional_usdt']} ({LEVERAGE}x) | Risk: {sizing['risk_pct']}%")

        print("--- Placing Orders ---")
        self.set_leverage(symbol)

        result = {"status": "executed", "trade": trade, "sizing": sizing, "orders": {}}

        try:
            entry = self.place_entry(symbol=symbol, direction=trade.get("direction"), quantity=qty)
            result["orders"]["entry"] = entry
            print(f"ENTRY placed: {entry.get('orderId', 'OK')}")
        except BinanceAPIException as e:
            result["orders"]["entry"] = {"error": str(e)}
            print(f"ENTRY FAILED: {e}")
            return result

        try:
            sl = self.place_sl(symbol, trade["direction"], trade["stop_loss"], qty)
            result["orders"]["stop_loss"] = sl
            print(f"SL placed: {sl.get('orderId', 'OK')}")
        except BinanceAPIException as e:
            result["orders"]["stop_loss"] = {"error": str(e)}
            print(f"SL FAILED: {e}")

        try:
            tp = self.place_tp(symbol, trade["direction"], trade["take_profit"], qty)
            result["orders"]["take_profit"] = tp
            print(f"TP placed: {tp.get('orderId', 'OK')}")
        except BinanceAPIException as e:
            result["orders"]["take_profit"] = {"error": str(e)}
            print(f"TP FAILED: {e}")

        print("DONE — check testnet.binancefuture.com")
        return result
