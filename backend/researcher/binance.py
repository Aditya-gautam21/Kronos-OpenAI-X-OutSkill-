import os
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
        klines = self.public_client.futures_klines(symbol='ETHUSDT', interval='1h', limit=200)
        



if __name__ == "__main__":
    klines = self.public_client.futures_klines(symbol="BTCUSDT", interval="1d", limit=5)
    print("Public API works — latest 5 daily candles:")
    for k in klines:
        print(f"  Open time: {k[0]}, Close: {k[4]}")

    try:
        account = self.testnet_client.futures_account()
        balances = [b for b in account["assets"] if float(b["walletBalance"]) > 0]
        print(f"\nTestnet auth works — {len(balances)} assets with balance")
        for b in balances[:5]:
            print(f"  {b['asset']}: {b['walletBalance']}")
    except Exception as e:
        print(f"\nTestnet auth failed — check your API key/secret: {e}")