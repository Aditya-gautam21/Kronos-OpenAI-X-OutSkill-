class Strategy:
    @staticmethod
    def ma_crossover(df) -> dict:
        """Golden/Death cross: SMA50 vs SMA200"""
        sma_50 = df["SMA_50"].iloc[-1]
        sma_200 = df["SMA_200"].iloc[-1]
        signal = "SHORT" if sma_200 > sma_50 else "LONG"
        return {"strategy": "MA_crossover", "signal": signal}

    @staticmethod
    def rsi_mean_revert(df, oversold=30, overbought=70) -> dict:
        """RSI overbought/oversold"""
        rsi = df["RSI_14"].iloc[-1]
        if rsi < oversold:
            signal = "LONG"
        elif rsi > overbought:
            signal = "SHORT"
        else:
            signal = "HOLD"
        return {"strategy": "RSI_mean_revert", "signal": signal, "rsi": round(rsi, 2)}

    @staticmethod
    def macd_momentum(df) -> dict:
        """MACD line crosses signal line"""
        macd = df["MACD"].iloc[-1]
        sig = df["MACDs"].iloc[-1]
        signal = "LONG" if macd > sig else "SHORT"
        return {"strategy": "MACD_momentum", "signal": signal}

    @staticmethod
    def all_strategies(df) -> list[dict]:
        return [
            Strategy.ma_crossover(df),
            Strategy.rsi_mean_revert(df),
            Strategy.macd_momentum(df),
        ]

    @staticmethod
    def majority_signal(df) -> str:
        results = Strategy.all_strategies(df)
        longs = sum(1 for r in results if r["signal"] == "LONG")
        shorts = sum(1 for r in results if r["signal"] == "SHORT")
        if longs > shorts:
            return "LONG"
        elif shorts > longs:
            return "SHORT"
        return "HOLD"
