# Kronos

Autonomous multi-agent AI quant hedge fund for crypto futures. Built at the **OpenAI x OutSkill AI Builders Hackathon (May 2026)**.

A system of AI agents that replicate the workflow of a quant fund — research, trade generation, and execution. You act as CIO via the dashboard. The agents do the rest.

## How It Works

Click **"START AUTONOMOUS BOT"** from the CIO dashboard. The pipeline runs:

1. **Researcher Agent** — Fetches live OHLCV, computes technical indicators (RSI, MACD, SMA, Bollinger Bands), pulls crypto news from RSS feeds, runs sentiment analysis via HuggingFace, and compiles a market summary.
2. **Quant Agent** — Feeds the research output to DeepSeek with a structured prompt that includes pre-computed strategy signals (trend, momentum, mean-reversion). The LLM returns a JSON trade plan with entry, stop-loss, take-profit, and a confidence level.
3. **Execution Agent** — Sizes the position via Kelly Criterion, sets 5x leverage, and places a market entry + stop-loss + take-profit on Binance Futures Testnet. Results are logged to the dashboard.

**Risk Agent** and **Portfolio Agent** are planned but not yet implemented. There is no backtesting engine (no vectorbt, no E2B sandbox) — the bot trades directly on testnet using LLM-generated signals.

## Project Structure

```text
backend/
├── researcher/
│   ├── binance.py              # Binance Futures public + testnet client
│   ├── ccxt.py                 # CCXT exchange wrapper (fallback)
│   ├── crypto_news.py          # RSS news fetcher (CoinDesk, CryptoSlate, Decrypt, etc.)
│   ├── indicators.py           # SMA, RSI, MACD, Bollinger Bands via pandas-ta
│   ├── sentiment.py            # Financial sentiment via HuggingFace transformers
│   ├── research_agent.py       # Orchestrates indicators + sentiment + news → LLM prompt
│   └── summary.py              # Compiles market data for LLM input
├── quant/
│   ├── agent.py                # Quant agent — invokes research, extracts trade plan from LLM
│   └── kelly.py                # Kelly Criterion position sizing
├── utils/
│   ├── extract_json.py         # JSON extraction from LLM output
│   ├── prompts.py              # Structured prompt templates for the research pipeline
│   └── stratigies.py           # Pre-computed strategy signals (trend, momentum, mean-reversion)
├── routes/
│   └── trader.py               # FastAPI endpoints for the CIO dashboard
├── main.py                     # FastAPI application entry point
├── state.py                    # In-memory state persisted to state.json (no database)
├── local_llm.py                # Local LLM wrapper (llama-cpp-python, fallback)
├── deepseek_llm.py             # DeepSeek API integration (primary LLM)
└── trade_execution_agent.py    # Paper trading on Binance Futures Testnet

frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx          # Root layout (fonts, metadata, dark theme)
│   │   ├── page.tsx            # Main CIO dashboard
│   │   └── globals.css         # Tailwind CSS v4 + custom neon theme
│   ├── components/
│   │   ├── Sidebar.tsx         # Navigation sidebar
│   │   ├── MetricsRibbon.tsx   # KPI ribbon (PnL, win rate, drawdown, exposure)
│   │   ├── StrategyPipeline.tsx
│   │   ├── ApprovalQueue.tsx
│   │   ├── LiveTrades.tsx
│   │   ├── PortfolioAllocation.tsx
│   │   └── AgentLog.tsx
│   └── lib/
│       └── api.ts              # API client (fetch wrappers for backend endpoints)
└── package.json
```

## Tech Stack

| Layer | Tools |
|-------|-------|
| **LLM** | DeepSeek (langchain-deepseek, model `deepseek-chat`) — primary. llama-cpp-python (local GGUF) — fallback |
| **Backend** | FastAPI, Python 3.12, python-binance |
| **Data** | Binance Futures API, Binance Testnet, pandas, numpy, pandas-ta |
| **NLP** | HuggingFace transformers (FinBERT/Twitter-roBERTa for sentiment) |
| **News** | RSS feeds from CoinDesk, CryptoSlate, Decrypt, Cointelegraph, Bitcoin Magazine, Reddit crypto subs |
| **Frontend** | Next.js 16, React 19, Recharts, Tailwind CSS v4, Framer Motion, Lucide React |

## Setup

### Prerequisites
- Python 3.11+ (3.12 recommended)
- conda (environment manager)
- Node.js 18+
- Binance Testnet account (free)

### Environment Variables

Create `backend/.env`:

```
BINANCE_TESTNET_API=your_testnet_api_key
BINANCE_TESTNET_SECRET=your_testnet_secret
DEEPSEEK_API_KEY=your_deepseek_api_key
LOCAL_MODEL_PATH=/path/to/gguf/model    # optional fallback
```

### Install

**Backend (Python):**
```bash
conda create -n kronos python=3.12
conda activate kronos
pip install python-binance pandas numpy pandas-ta feedparser llama-cpp-python \
    transformers torch python-dotenv fastapi uvicorn langchain-deepseek
```

**Frontend (Node.js):**
```bash
cd frontend
npm install
```

### Run

Start the backend API server:
```bash
conda activate kronos
python -m backend.main
```

Start the Next.js CIO Dashboard (in a new terminal):
```bash
cd frontend
npm run dev
```

Backend runs on `http://localhost:8000`, frontend on `http://localhost:3000`. Click **"START AUTONOMOUS BOT"** in the dashboard to run the full pipeline.

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/bot-status` | GET | Current bot state, last execution, run count |
| `/metrics` | GET | Aggregate PnL, win rate, active strategies, drawdown |
| `/positions` | GET | Live open positions from Binance Testnet |
| `/trade-history` | GET | Closed trade log |
| `/pipeline` | GET | Strategy pipeline state (research/backtest/risk review queues) |
| `/allocation` | GET | Portfolio allocation from live account balance |
| `/logs` | GET | Agent activity log (last 200 entries) |
| `/start-autonomous-bot` | POST | Trigger the full research → quant → execution pipeline |

## Implementation Status

- [x] Researcher Agent — OHLCV, indicators (RSI/MACD/SMA/BB), news aggregation, sentiment analysis
- [x] Quant Agent — LLM-generated trade plans with Kelly sizing
- [x] Execution Agent — Binance Testnet paper trading (market entry + SL + TP)
- [x] CIO Dashboard — Next.js dashboard with live metrics, trades, positions, agent logs
- [x] FastAPI backend — REST API connecting dashboard to trading pipeline
- [x] Strategy signals — Pre-computed trend, momentum, and mean-reversion signals
- [ ] Risk Agent — Stress testing, overfitting detection, strategy correlation
- [ ] Portfolio Agent — Dynamic rebalancing across active strategies
- [ ] Backtesting engine — Historical backtesting with vectorbt (planned, not implemented)

## License

MIT
