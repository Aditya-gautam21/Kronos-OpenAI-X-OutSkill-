import ccxt.pro as ccxtpro
import pandas as pd
from datetime import datetime, timedelta

class CryptoCollector:
    def __init__(self):
        self.exchange = ccxtpro.binance({
            'enableRateLimit': True,
            'options': {
                'adjustForTimeDifference': True
            }
        })

    async def fetch_ohlcv_data(self, symbol, timeframe, since=None):
        if since is None:
            since = datetime.now() - timedelta(days=1 * 365)

        since_ms = self.exchange.parse8601(
            since.strftime("%Y-%m-%dT%H:%M:%SZ")
        )

        all_data = []

        while True:
            ohlcv = await self.exchange.fetch_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                since=since_ms,
                limit=1000
            )

            if not ohlcv:
                break

            all_data.extend(ohlcv)
            since_ms = ohlcv[-1][0] + 1

        if not all_data:
            print("No data fetched.")
            return None

        df = pd.DataFrame(
            all_data,
            columns=["Timestamp", "Open", "High", "Low", "Close", "Volume"]
        )

        df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="ms")
        df.set_index("Timestamp", inplace=True)

        df = df[~df.index.duplicated()]
        df = df.sort_index()

        return df

    async def ohlcv_continuous(self, symbol, timeframe):
        since = datetime.now() - timedelta(days=365)
        historical = await self.fetch_ohlcv_data(symbol, timeframe, since=since)

        try:
            while True:
                ohlcv = await self.exchange.watch_ohlcv(
                    symbol=symbol, timeframe=timeframe
                )

                if ohlcv:
                    new = pd.DataFrame(
                        ohlcv,
                        columns=["Timestamp", "Open", "High", "Low", "Close", "Volume"]
                    )
                    new["Timestamp"] = pd.to_datetime(new["Timestamp"], unit="ms")
                    new.set_index("Timestamp", inplace=True)

                    if historical is not None:
                        historical = historical[~historical.index.isin(new.index)]

                    # yield the combined view each update
                    if historical is not None:
                        combined = pd.concat([historical, new])
                    else:
                        combined = new

                    combined = combined[~combined.index.duplicated()]
                    combined = combined.sort_index()
                    yield combined
                else:
                    break

        except Exception as e:
            print(f"WebSocket error: {e}")
            # reconnect could go here
            raise

    
