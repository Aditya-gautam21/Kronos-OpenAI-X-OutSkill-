# StratOS — Autonomous AI Quant Hedge Fund for Crypto Futures

> A multi-agent AI system that replicates the full workflow of a quant hedge fund for solo crypto futures traders. You act as the CIO. The agents do everything else.

---

## The Problem

Retail crypto futures traders have ideas but no infrastructure. Hedge funds have entire teams — quant researchers, risk managers, portfolio managers, execution desks — all working in parallel. That organizational structure has never existed for a single person.

Existing tools are either:
- **Too simple** — TradingView alerts, basic screeners
- **Too expensive** — institutional Bloomberg terminals, proprietary quant platforms
- **Too manual** — writing your own backtests in Python from scratch every time

The agentic middle layer — a system that *reasons* over market structure, writes and validates strategies autonomously, manages risk, and executes paper trades in real time — does not exist for retail traders.

**StratOS is that layer.**

---

## What It Does

You type a hypothesis in plain English:

> *"Test if BTC tends to recover within 3 days after a 15%+ weekly drop when funding rate is negative and open interest drops simultaneously"*

StratOS autonomously:

1. Fetches and cleans all relevant market data
2. Forms a structured, testable hypothesis
3. Writes and backtests a strategy via Codex
4. Critiques its own results for overfitting and risk
5. Stress tests against historical crashes
6. Allocates it a capital slice using Kelly Criterion
7. Executes paper trades in real time
8. Surfaces everything to you on a CIO dashboard for approval

You are not a trader. You are running a fund.

---

## The Five Agents

### 1. Researcher Agent
**Role:** Hypothesis generation and data acquisition

- Accepts natural language hypotheses or auto-generates them from market anomalies
- Fetches OHLCV price data, volume, funding rates, open interest, long/short ratios, liquidation data
- Pulls news sentiment via Tavily or NewsAPI
- Outputs a structured hypothesis object:
  ```json
  {
    "asset": "BTC/USDT",
    "signal": "funding_rate < -0.01 AND weekly_return < -0.15 AND oi_change < -0.10",
    "direction": "long",
    "timeframe": "3D",
    "entry": "market open next candle",
    "exit": "3 days or +8% take profit or -4% stop loss",
    "hypothesis": "BTC mean-reverts after overleveraged short liquidations"
  }
  ```

### 2. Quant Agent
**Role:** Strategy coding and backtesting via Codex

- Takes the structured hypothesis from the Researcher Agent
- Uses Codex to write a complete Python backtest using vectorbt
- Executes the backtest in a sandboxed environment (E2B)
- Returns structured results:
  - Sharpe Ratio
  - Max Drawdown
  - Win Rate
  - CAGR
  - Total trades
  - Equity curve data
- Iterates up to 3 times if results are below threshold before passing to Risk Agent

### 3. Risk Agent
**Role:** Stress testing, overfitting detection, correlation analysis

- Stress tests the strategy against historical crash events:
  - March 2020 COVID crash
  - May 2021 BTC -50% drawdown
  - LUNA collapse (May 2022)
  - FTX collapse (November 2022)
  - 2024 ETF-driven volatility periods
- Detects overfitting: flags strategies with Sharpe > 3.0 on short backtests as suspicious
- Checks correlation with existing live strategies in the portfolio — rejects strategies that are >0.7 correlated with an existing one
- Outputs a risk score (0–100) and a PASS / FAIL / REVIEW verdict
- Strategies scoring below 40 are killed automatically

### 4. Portfolio Agent
**Role:** Capital allocation and rebalancing

- Takes all Risk Agent approved strategies
- Allocates capital using **Kelly Criterion** — sizes each strategy proportional to its edge and variance
- Applies a half-Kelly cap to prevent overbetting
- Rebalances dynamically when:
  - A new strategy is approved
  - An existing strategy degrades below performance threshold
  - Correlation between strategies exceeds threshold
- Outputs a capital allocation table across all active strategies

### 5. Execution Agent
**Role:** Paper trading and live performance tracking

- Executes approved strategies as paper trades via Binance Futures Testnet API
- Tracks in real time:
  - Entry/exit prices
  - Actual vs expected slippage
  - Live PnL per strategy
  - Portfolio-level drawdown
- Sends alerts when a strategy's live performance deviates significantly from backtest
- Surfaces degraded strategies back to the CIO dashboard for review

---

## CIO Dashboard

The user sits at the top of the system as Chief Investment Officer. The dashboard shows:

- **Strategy Pipeline** — all strategies in each stage: Researching → Backtesting → Risk Review → Active → Degraded
- **Approval Queue** — strategies that passed Risk Agent, waiting for CIO sign-off before going live
- **Portfolio Overview** — current capital allocation, live PnL, drawdown, Sharpe (live)
- **Active Paper Trades** — open positions with real-time price and PnL
- **Agent Logs** — full transparency into what each agent decided and why
- **Override Controls** — kill any strategy, adjust allocation, force-rerun any agent

Every agent decision surfaces to the CIO. You override, adjust, or let it run.

---

## Tech Stack

### Backend
| Tool | Purpose |
|------|---------|
| **FastAPI** | Agent orchestration API, WebSocket streaming |
| **OpenAI Agents SDK** | Multi-agent loop orchestration |
| **GPT-4o / Codex** | Powers all five agents |
| **E2B (e2b.dev)** | Sandboxed Python execution for backtests |
| **Redis** | Async job queue for agent tasks |
| **Supabase** | Hosted Postgres — strategies, backtest results, paper trades |

### Data
| Tool | Purpose |
|------|---------|
| **Binance Futures REST API** | OHLCV, funding rates, open interest, long/short ratios |
| **Binance Futures Testnet** | Paper trading execution |
| **Tavily API** | News and sentiment search |
| **pandas + numpy** | Data manipulation inside backtests |
| **vectorbt** | Fast backtesting engine (pure pandas, Codex-friendly) |

### Frontend
| Tool | Purpose |
|------|---------|
| **Next.js 15** | CIO Dashboard |
| **Lightweight Charts** | Equity curves, price charts |
| **Recharts** | Portfolio allocation, performance metrics |
| **Tailwind CSS** | Styling |

### Infrastructure
| Tool | Purpose |
|------|---------|
| **Docker** | Containerize backend + frontend |
| **AWS EC2 / Railway** | Deployment |

---

## Data Sources (All Free)

### Binance Futures Public API (No Auth Required)
```
GET /fapi/v1/klines         → OHLCV candles (any timeframe, up to 1000 bars)
GET /fapi/v1/fundingRate     → Historical funding rates
GET /futures/data/openInterestHist → Open interest history
GET /futures/data/globalLongShortAccountRatio → Long/short ratio
GET /futures/data/takerlongshortRatio → Taker buy/sell volume ratio
```

### Binance Futures Testnet (Paper Trading)
- Full API parity with live Binance Futures
- Free test USDT allocated on account creation
- Endpoint: `https://testnet.binancefuture.com`

### News / Sentiment
- **Tavily API** — free tier: 1000 searches/month
- **NewsAPI** — free tier: 100 requests/day

---

## Agent Communication Flow

```
User Input (Natural Language Hypothesis)
        │
        ▼
┌─────────────────┐
│ Researcher Agent │  ← Fetches market data, structures hypothesis
└────────┬────────┘
         │ Structured Hypothesis JSON
         ▼
┌─────────────────┐
│   Quant Agent   │  ← Codex writes backtest → E2B executes it
└────────┬────────┘
         │ Backtest Results (Sharpe, Drawdown, Win Rate, Equity Curve)
         ▼
┌─────────────────┐
│   Risk Agent    │  ← Stress test, overfitting check, correlation check
└────────┬────────┘
         │ Risk Score + PASS/FAIL/REVIEW
         ▼
┌──────────────────────────┐
│   CIO Dashboard (You)    │  ← Approve or Reject
└────────┬─────────────────┘
         │ Approved
         ▼
┌──────────────────┐
│ Portfolio Agent  │  ← Kelly allocation, rebalancing
└────────┬─────────┘
         │ Capital Allocation
         ▼
┌──────────────────┐
│ Execution Agent  │  ← Paper trades on Binance Testnet, live tracking
└──────────────────┘
```

---

## 7-Day Build Plan

| Day | Deliverable |
|-----|------------|
| **Day 1** | Project setup (FastAPI + Next.js + Docker + Supabase). Binance data pipeline working. Researcher Agent producing structured hypothesis JSON. |
| **Day 2** | Quant Agent — Codex writes vectorbt backtest, E2B executes it, results stored in Supabase. |
| **Day 3** | Risk Agent — stress testing against historical crashes, overfitting detection, correlation check. |
| **Day 4** | Portfolio Agent — Kelly Criterion allocation, rebalancing logic. |
| **Day 5** | Execution Agent — Binance Testnet paper trading, real-time PnL tracking via WebSocket. |
| **Day 6** | CIO Dashboard — Next.js frontend, approval queue, portfolio overview, live trades, agent logs. |
| **Day 7** | Polish, full Docker compose, deploy to Railway/EC2, record demo video. |

---

## Project Structure

```
stratos/
├── backend/
│   ├── main.py                  # FastAPI entry point
│   ├── agents/
│   │   ├── researcher.py        # Researcher Agent
│   │   ├── quant.py             # Quant Agent (Codex + E2B)
│   │   ├── risk.py              # Risk Agent
│   │   ├── portfolio.py         # Portfolio Agent
│   │   └── execution.py         # Execution Agent
│   ├── data/
│   │   ├── binance.py           # Binance Futures API client
│   │   └── news.py              # Tavily/NewsAPI client
│   ├── db/
│   │   └── supabase.py          # Supabase client + schema
│   ├── queue/
│   │   └── redis_worker.py      # Async job queue
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── page.tsx             # CIO Dashboard
│   │   ├── strategies/          # Strategy pipeline view
│   │   ├── portfolio/           # Portfolio overview
│   │   └── trades/              # Live paper trades
│   ├── components/
│   │   ├── ApprovalQueue.tsx
│   │   ├── EquityCurve.tsx
│   │   ├── AgentLog.tsx
│   │   └── PortfolioAllocation.tsx
│   └── package.json
├── docker-compose.yml
└── README.md
```

---

## Supabase Schema

```sql
-- Strategies
CREATE TABLE strategies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hypothesis TEXT,
  structured_hypothesis JSONB,
  status TEXT,  -- researching | backtesting | risk_review | approved | active | degraded | killed
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Backtest Results
CREATE TABLE backtest_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  strategy_id UUID REFERENCES strategies(id),
  sharpe FLOAT,
  max_drawdown FLOAT,
  win_rate FLOAT,
  cagr FLOAT,
  total_trades INT,
  equity_curve JSONB,
  code TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Risk Assessments
CREATE TABLE risk_assessments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  strategy_id UUID REFERENCES strategies(id),
  risk_score INT,
  verdict TEXT,  -- PASS | FAIL | REVIEW
  stress_test_results JSONB,
  overfitting_flag BOOLEAN,
  correlation_flag BOOLEAN,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Portfolio Allocations
CREATE TABLE allocations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  strategy_id UUID REFERENCES strategies(id),
  kelly_fraction FLOAT,
  allocated_usdt FLOAT,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Paper Trades
CREATE TABLE paper_trades (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  strategy_id UUID REFERENCES strategies(id),
  symbol TEXT,
  side TEXT,
  entry_price FLOAT,
  exit_price FLOAT,
  pnl FLOAT,
  status TEXT,  -- open | closed
  opened_at TIMESTAMPTZ,
  closed_at TIMESTAMPTZ
);
```

---

## Scalability as a Business

### Freemium Tier
- 3 active strategies
- Paper trading only
- 30-day backtest window
- Community strategy templates

### Pro Tier ($49/month)
- Unlimited strategies
- 5-year backtest window
- Live execution via Binance API key
- Priority agent runs
- Strategy export

### Institutional Tier ($299/month)
- White-label for small prop desks and family offices
- Custom data source integrations
- Multi-user CIO access
- Dedicated agent compute

### Future Moats
- **Strategy marketplace** — users publish and monetize their approved strategies
- **Agent fine-tuning** — StratOS learns from your approval/rejection history and personalizes agent behavior
- **Cross-asset expansion** — equities (Alpaca), forex, options
- **Social layer** — follow top-performing CIOs, copy their portfolio allocations

---

## Why This Hasn't Been Built Before

1. **Codex-class models** couldn't reliably write and execute backtesting code in a loop until recently
2. **Multi-agent orchestration** at this complexity was too fragile 6 months ago
3. **E2B-style sandboxed execution** is a new primitive that makes the Quant Agent safe to run in production
4. Nobody has connected the full fund workflow — research → backtest → risk → allocation → execution — end-to-end for a single person

StratOS is the first system to do all five in one agentic loop.

---

*Built at OpenAI x Outskill AI Builders Hackathon — May 2026*
