import os
import pandas as pd
from dotenv import load_dotenv
from binance.client import Client

load_dotenv()

class BINANCE:
    def __init__(self):
        self.public_client = Client()

        self.testnet_client = Client(
            api_key=os.getenv("BINANCE_TESTNET_API"),
            api_secret=os.getenv("BINANCE_TESTNET_SECRET"),
            testnet=True,
        )

    def load_data(self):
        all_data = []

        klines = self.public_client.futures_klines(symbol='ETHUSDT', interval='1h', limit=1000)
        for k in klines:
            all_data.append(k)

        data = pd.DataFrame(all_data, columns=["timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_volume", "trades",
        "taker_buy_base", "taker_buy_quote","ignore"])
        
        
        data["timestamp"] = pd.to_datetime(data["timestamp"], unit="ms")
        data.set_index("timestamp", inplace=True)
        data = data[["open", "high", "low", "close", "volume"]].astype(float)

        return data