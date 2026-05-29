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
            timeInForce="GTC",
            quoteOrderQty=quantity
        )

    def place_sl(self, symbol: str, direction: str, stop_price: float, quantity: float) -> dict:
        side = "BUY" if direction == "short" else "SELL"
        return self.client.futures_create_order(
            symbol=symbol,
            side=side,
            type="STOP_LOSS",
            stopPrice=round(stop_price, 2),
            quoteOrderQty=quantity,
            reduceOnly="true",
            workingType="MARK_PRICE",
            priceProtect="TRUE",
        )

    def place_tp(self, symbol: str, direction: str, tp_price: float, quantity: float) -> dict:
        side = "BUY" if direction == "short" else "SELL"
        return self.client.futures_create_order(
            symbol=symbol,
            side=side,
            type="TAKE_PROFIT",
            stopPrice=round(tp_price, 2),
            quantity=quantity,
            reduceOnly="true",
            workingType="MARK_PRICE",
            priceProtect="TRUE",
        )

    def _ok(self, order: dict) -> bool:
        return "orderId" in order

    def execute(self) -> dict:
        print("--- Research Agent ---")
        trade = QuantAgent().generate_trade()

        if not trade or not trade.get("edge_found"):
            reason = (trade or {}).get("hypothesis", "No edge found")
            print(f"SKIP: {reason}")
            return {"status": "skipped", "reason": reason}

        symbol = trade["symbol"]
        print(f"Direction: {trade['direction'].upper()} | Confidence: {trade['confidence']}")
        print(f"Entry: ${trade['entry_price']} | SL: ${trade['stop_loss']} | TP: ${trade['take_profit']}")
        print(f"Hypothesis: {trade['hypothesis']}")

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

        qty = sizing["quantity"]
        print(f"Qty: {qty} | Notional: ${sizing['notional_usdt']} ({LEVERAGE}x) | Risk: {sizing['risk_pct']}%")

        print("--- Placing Orders ---")
        #self.cancel_all_orders(symbol)
        self.set_leverage(symbol)

        result = {"status": "executed", "trade": trade, "sizing": sizing, "orders": {}}

        try:
            entry = self.place_entry(symbol, trade["direction"], qty)
            if self._ok(entry):
                result["orders"]["entry"] = entry
                print(f"ENTRY: {entry['side']} {qty} @ ${entry.get('price')} (ID: {entry['orderId']})")
            else:
                result["orders"]["entry"] = {"error": entry}
                print(f"ENTRY FAILED: {entry}")
                return result
        except BinanceAPIException as e:
            result["orders"]["entry"] = {"error": str(e)}
            print(f"ENTRY FAILED: {e}")
            return result

        try:
            sl = self.place_sl(symbol, trade["direction"], trade["stop_loss"], qty)
            if self._ok(sl):
                result["orders"]["stop_loss"] = sl
                print(f"STOP LOSS: @ ${trade['stop_loss']} (ID: {sl['orderId']})")
            else:
                result["orders"]["stop_loss"] = {"error": sl}
                print(f"SL FAILED: {sl}")
        except BinanceAPIException as e:
            result["orders"]["stop_loss"] = {"error": str(e)}
            print(f"SL FAILED: {e}")

        try:
            tp = self.place_tp(symbol, trade["direction"], trade["take_profit"], qty)
            if self._ok(tp):
                result["orders"]["take_profit"] = tp
                print(f"TAKE PROFIT: @ ${trade['take_profit']} (ID: {tp['orderId']})")
            else:
                result["orders"]["take_profit"] = {"error": tp}
                print(f"TP FAILED: {tp}")
        except BinanceAPIException as e:
            result["orders"]["take_profit"] = {"error": str(e)}
            print(f"TP FAILED: {e}")

        print("DONE — check testnet.binancefuture.com")
        return result


if __name__ == "__main__":
    agent = TradeExecutionAgent()
    result = agent.execute()
    print("\n" + json.dumps(result, indent=2))
