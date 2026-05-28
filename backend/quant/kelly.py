def kelly_position_size(
    confidence: str,
    direction: str,
    entry_price: float,
    stop_loss: float,
    take_profit: float,
    balance: float,
    leverage: int = 5,
    max_risk_pct: float = 0.10,
) -> dict:
    confidence_to_prob = {"high": 0.60, "medium": 0.50, "low": 0.40}
    win_prob = confidence_to_prob.get(confidence, 0.45)

    # Risk = distance from entry to SL (as fraction of entry)
    if direction == "short":
        risk_pct_per_unit = abs(stop_loss - entry_price) / entry_price
        reward_pct_per_unit = abs(entry_price - take_profit) / entry_price
    else:
        risk_pct_per_unit = abs(entry_price - stop_loss) / entry_price
        reward_pct_per_unit = abs(take_profit - entry_price) / entry_price

    if risk_pct_per_unit == 0:
        return {"quantity": 0, "risk_pct": 0, "kelly_fraction": 0, "leverage": leverage, "error": "zero risk distance"}

    b_ratio = reward_pct_per_unit / risk_pct_per_unit

    kelly_fraction = win_prob - (1 - win_prob) / b_ratio

    # Half-Kelly for safety
    kelly_fraction = kelly_fraction / 2

    # Clamp: min 1%, max based on max_risk_pct
    kelly_fraction = max(0.01, min(max_risk_pct, kelly_fraction))

    # Position value in quote currency (USDT)
    position_value = balance * kelly_fraction * leverage

    # Quantity in base currency (ETH)
    quantity = position_value / entry_price

    # Round quantity to 3 decimal places (Binance step size for ETHUSDT)
    quantity = round(quantity, 3)

    return {
        "quantity": quantity,
        "notional_usdt": round(position_value, 2),
        "risk_pct": round(kelly_fraction * 100, 2),
        "kelly_fraction": round(kelly_fraction, 4),
        "leverage": leverage,
        "sl_distance_pct": round(risk_pct_per_unit * 100, 2),
        "tp_distance_pct": round(reward_pct_per_unit * 100, 2),
    }
