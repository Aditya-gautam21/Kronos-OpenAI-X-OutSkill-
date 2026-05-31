import concurrent.futures
import urllib.request
import feedparser
from datetime import datetime, timedelta
from pathlib import Path

ASSET_KEYWORDS = {
    "ETHUSDT": ["ethereum", "eth", "ether", "vitalik", "merge", "layer 2", "l2", "arbitrum", "optimism"],
    "BTCUSDT": ["bitcoin", "btc", "bitcoin etf", "halving", "satoshi"],
    "SOLUSDT": ["solana", "sol", "phantom"],
}



class NewsCollector:
    def __init__(self, data_dir="./raw_data"):
        self.rss_feeds = {
            "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/?outputType=xml",
            "Cointelegraph": "https://cointelegraph.com/rss",
            "CryptoSlate": "https://cryptoslate.com/feed/",
            "Decrypt": "https://decrypt.co/feed",
            "NewsBTC": "https://www.newsbtc.com/feed/",
            "Bitcoin.com": "https://news.bitcoin.com/feed/",
            "Blockonomi": "https://blockonomi.com/feed/",
            "Coinspeaker": "https://www.coinspeaker.com/feed/",
        }
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _fetch_one(self, source: str, url: str, keywords: list[str], cutoff_time: datetime) -> list[dict]:
        """Fetch and parse a single RSS feed with HTTP timeout."""
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Kronos/1.0"})
            with urllib.request.urlopen(req) as resp:
                raw = resp.read()
            feed = feedparser.parse(raw)
        except Exception:
            return []

        results = []
        for entry in feed.entries:
            try:
                if not hasattr(entry, "published_parsed") or entry.published_parsed is None:
                    continue
                published = datetime(*entry.published_parsed[:6])
                if published <= cutoff_time:
                    continue

                title = entry.get("title", "")
                summary_text = entry.get("summary", "")
                text = (title + " " + summary_text).lower()
                if not any(kw in text for kw in keywords):
                    continue

                results.append({
                    "source": source,
                    "title": title,
                    "published": published.isoformat(),
                    "summary": summary_text[:200],
                })
            except Exception:
                pass

        return results

    def fetch_news(self, hours=12, asset="ETHUSDT"):
        keywords = ASSET_KEYWORDS.get(asset, [])
        cutoff_time = datetime.now() - timedelta(hours=hours)
        all_news = []

        for source, url in self.rss_feeds.items():
            try:
                feed = feedparser.parse(url)

                for entry in feed.entries:
                    try:
                        published = datetime(*entry.published_parsed[:6])

                        if published <= cutoff_time:
                            continue

                        title = entry.title
                        summary = entry.get("summary", "")
                        text = (title + " " + summary).lower()

                        if not any(kw in text for kw in keywords):
                            continue

                        all_news.append({
                            "source": source,
                            "title": title,
                            "published": published.isoformat(),
                            "summary": summary[:200],
                        })

                    except Exception as e:
                        print(f"Published parsed problem: {e}")

            except Exception as e:
                print(f"Error fetching from {source}: {e}")

        return all_news
