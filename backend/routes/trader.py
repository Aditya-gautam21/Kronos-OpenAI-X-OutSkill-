import asyncio
import os
import uuid
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import APIRouter
from binance.client import Client
from binance.exceptions import BinanceAPIException

from backend.trade_execution_agent import TradeExecutionAgent, LEVERAGE
from backend.state import load_state, save_state, add_log

load_dotenv()
router = APIRouter()


def _get_binance_client():
    return Client(
        api_key=os.getenv("BINANCE_TESTNET_API"),
        api_secret=os.getenv("BINANCE_TESTNET_SECRET"),
        testnet=True,
    )


@router.get("/bot-status")
async def bot_status():
    state = load_state()
    return {
        "is_running": state["is_running"],
        "last_execution": state["last_execution"],
        "last_result": state["last_result"],
        "total_executions": state["bot_runs"],
    }


@router.get("/positions")
async def positions():
    try:
        client = _get_binance_client()
        raw = client.futures_position_information()
        active = [p for p in raw if float(p.get("positionAmt", 0)) != 0]

        result = []
        for p in active:
            symbol = p.get("symbol", "UNKNOWN")
            amt = float(p.get("positionAmt", 0))
            entry_price = float(p.get("entryPrice", 0))
            mark_price = float(p.get("markPrice", 0))
            unrealized_pnl = float(p.get("unRealizedProfit", 0))

            side = "LONG" if amt > 0 else "SHORT"
            size = abs(amt)

            if entry_price > 0:
                pnl_pct = ((mark_price - entry_price) / entry_price * 100)
                if side == "SHORT":
                    pnl_pct = -pnl_pct
                pnl_pct_str = f"{pnl_pct:+.2f}%"
            else:
                pnl_pct_str = "0.00%"

            result.append({
                "symbol": symbol,
                "side": side,
                "size": size,
                "entry_price": entry_price,
                "mark_price": mark_price,
                "pnl": round(unrealized_pnl, 2),
                "pnl_pct": pnl_pct_str,
                "leverage": int(float(p.get("leverage", 1))),
                "liquidation_price": float(p.get("liquidationPrice", 0)),
            })

        return result
    except Exception:
        return []


@router.get("/trade-history")
async def trade_history():
    state = load_state()
    return state["trade_history"]


@router.get("/metrics")
async def metrics():
    state = load_state()
    trades = state["trade_history"]

    total_pnl = sum(t.get("pnl", 0) or 0 for t in trades)
    winners = [t for t in trades if (t.get("pnl") or 0) > 0]
    losers = [t for t in trades if (t.get("pnl") or 0) < 0]
    win_rate = (len(winners) / len(trades) * 100) if trades else 0

    active_count = 0
    try:
        client = _get_binance_client()
        raw = client.futures_position_information()
        active_count = len([p for p in raw if float(p.get("positionAmt", 0)) != 0])
    except Exception:
        pass

    return {
        "total_pnl": round(total_pnl, 2),
        "active_strategies": active_count,
        "max_strategies": 12,
        "strategies_in_risk_review": 0,
        "drawdown": 0.0,
        "max_drawdown_limit": -5.0,
        "win_rate": round(win_rate, 1),
        "win_rate_period": "30D",
    }


@router.get("/pipeline")
async def pipeline():
    state = load_state()
    return state.get("pipeline", {"research": [], "backtest": [], "risk_review": []})


@router.get("/allocation")
async def allocation():
    try:
        client = _get_binance_client()
        account = client.futures_account()
        total_balance = float(account.get("totalWalletBalance", 0))
        raw_positions = client.futures_position_information()

        total_position_value = sum(
            abs(float(p.get("positionAmt", 0))) * float(p.get("markPrice", 0))
            for p in raw_positions
        )

        cash_pct = max(0, (total_balance - total_position_value) / total_balance * 100) if total_balance > 0 else 100
        exposed_pct = (total_position_value / total_balance * 100) if total_balance > 0 else 0

        allocations = []
        for p in raw_positions:
            amt = float(p.get("positionAmt", 0))
            if amt == 0:
                continue
            value = abs(amt * float(p.get("markPrice", 0)))
            pct = round(value / total_balance * 100, 1) if total_balance > 0 else 0
            allocations.append({
                "name": p.get("symbol", "UNKNOWN"),
                "value": pct,
                "color": "#00f0ff" if amt > 0 else "#ff00ff",
            })

        if cash_pct > 0.5:
            allocations.append({"name": "Cash (Reserve)", "value": round(cash_pct, 1), "color": "#333333"})

        return {
            "exposure_pct": round(exposed_pct, 1),
            "total_balance": round(total_balance, 2),
            "allocations": allocations,
        }
    except Exception:
        return {
            "exposure_pct": 0,
            "total_balance": 0,
            "allocations": [{"name": "Cash (Reserve)", "value": 100, "color": "#333333"}],
        }


@router.get("/logs")
async def logs():
    state = load_state()
    return state["logs"]


@router.post("/start-autonomous-bot")
async def start_bot():
    try:
        agent = TradeExecutionAgent()
        result = agent.execute()
        return result
    except Exception as e:
        return {"status": "error", "reason": str(e)}
