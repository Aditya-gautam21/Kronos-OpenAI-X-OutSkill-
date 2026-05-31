# Kronos

Autonomous multi-agent AI quant hedge fund for crypto futures. Built at the **OpenAI x OutSkill AI Builders Hackathon (May 2026)**.

A system of five AI agents that replicate the full workflow of a quant fund — research, backtesting, risk management, portfolio allocation, and trade execution. You act as CIO. The agents do everything else.

## How It Works

You type a hypothesis in plain English:

> *"Test if BTC tends to recover within 3 days after a 15%+ weekly drop when funding rate is negative and OI drops simultaneously"*

1. **Researcher Agent** — Fetches OHLCV, funding rates, open interest, news sentiment. Structures a testable hypothesis.
2. **Quant Agent** — Uses an LLM to write and execute a vectorbt backtest. Returns Sharpe, drawdown, win rate, equity curve.
3. **Risk Agent** — Stress tests against historical crashes (COVID, LUNA, FTX). Flags overfitting and strategy correlation.
4. **Portfolio Agent** — Allocates capital via Kelly Criterion across approved strategies.
5. **Execution Agent** — Paper trades on Binance Futures Testnet. Tracks live PnL.

All decisions surface to a CIO dashboard for approval, override, or audit.

## Project Structure

```text
backend/
├── researcher/
│   ├── binance.py           # Binance Futures public + testnet client
│   ├── crypto_news.py       # RSS news fetcher (CoinDesk, CryptoSlate, Decrypt)
│   ├── indicators.py        # SMA, RSI, MACD, Bollinger Bands via pandas-ta
│   ├── sentiment.py         # Financial sentiment via HuggingFace transformers
│   ├── research_agent.py    # LLM-powered hypothesis generation
│   └── summary.py           # Research output summarization
├── quant/
│   ├── agent.py             # Quant agent — LLM-driven strategy generation
│   ├── backtest.py          # Backtest runner
│   ├── kelly.py             # Kelly Criterion position sizing
│   ├── vecbt.py             # vectorbt backtest engine integration
│   └── vecbt_inputs.py      # Input preparation for vectorbt
├── utils/
│   ├── extract_json.py      # JSON extraction from LLM output
│   ├── prompts.py           # Prompt templates
│   └── stratigies.py        # Strategy definitions
├── routes/
│   └── trader.py            # FastAPI endpoints for CIO dashboard and bot execution
├── main.py                  # FastAPI application entry point
├── state.py                 # Backend state and logging manager
├── local_llm.py             # Local LLM wrapper (llama-cpp-python)
├── deepseek_llm.py          # DeepSeek API integration
└── trade_execution_agent.py # Binance Testnet paper trading

frontend/
├── src/                     # Next.js frontend application (React, Tailwind CSS, Recharts)
├── public/                  # Static assets
└── package.json             # Frontend dependencies
```

## Tech Stack

| Layer | Tools |
|-------|-------|
| **Backend** | FastAPI, OpenAI Agents SDK, GPT-4o / Codex, llama-cpp-python |
| **Data** | Binance Futures API, Binance Testnet, Tavily, pandas, numpy, pandas-ta, vectorbt |
| **Sandbox** | E2B (e2b.dev) for safe backtest execution |
| **DB / Queue** | Supabase (hosted Postgres), Redis |
| **Frontend** | Next.js 15, Lightweight Charts, Recharts, Tailwind CSS |
| **Infra** | Docker, AWS EC2 / Railway |

## Setup

### Prerequisites
- Python 3.11+
- conda (environment manager)
- Binance Testnet account (free)

### Environment Variables

```
BINANCE_TESTNET_API=your_testnet_api_key
BINANCE_TESTNET_SECRET=your_testnet_secret
LOCAL_MODEL_PATH=/path/to/gguf/model
```

### Install

**Backend (Python):**
```bash
conda create -n kronos python=3.12
conda activate kronos
pip install python-binance pandas numpy pandas-ta feedparser llama-cpp-python transformers torch python-dotenv fastapi uvicorn
```

**Frontend (Node.js):**
```bash
cd frontend
npm install
```

### Run

Start the backend API server:
```bash
python -m uvicorn backend.main:app --reload --port 8000
```

Start the Next.js CIO Dashboard (in a new terminal):
```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:3000`. You can start the autonomous bot directly from the dashboard UI.

## Build Status (Hackathon Day 1–3)

- [x] Researcher Agent — Binance data pipeline, news fetching, sentiment analysis, hypothesis generation
- [x] Quant Agent — LLM-driven backtest generation with vectorbt, Kelly Criterion allocation
- [x] Trade Execution Agent — Binance Testnet paper trading
- [ ] Risk Agent — stress testing, overfitting detection, correlation checks
- [ ] Portfolio Agent — dynamic rebalancing across active strategies
- [x] CIO Dashboard — Next.js frontend built with React, Tailwind CSS, Recharts
- [x] FastAPI orchestration — seamless integration between Next.js frontend and trading pipeline

## License

MIT
