# MyStock Manager

A personal investment portfolio dashboard with **agentic AI**, built with Python and Streamlit.

Track stocks, mutual funds, and precious metals across **India**, **Singapore**, and **USA** — with live market data, currency conversion, AI-powered chat, and automated price monitoring.

## Features

- **Multi-market portfolio tracking** — Indian stocks (NSE/BSE), Singapore stocks (SGX), US stocks (NYSE/NASDAQ), Indian mutual funds, Singapore mutual funds, and precious metals (Gold/Silver)
- **Live market data** — Real-time prices via yfinance, Indian MF NAVs via mfapi.in, forex rates via Frankfurter API
- **Unified dashboard** — Holdings grouped by symbol, P&L calculation, currency conversion to SGD base currency
- **AI Chat Agent** — Ask questions about your portfolio; the agent uses tools to query real data before answering
- **AI Insights Agent** — Automated portfolio analysis covering diversification, performance, risk, and opportunities
- **Price Monitor Agent** — Background daemon checks prices every 5 minutes, alerts on significant moves (no AI cost)
- **Provider-agnostic AI** — Swap between OpenAI, Anthropic (Claude), Google Gemini, or Ollama (local) with zero code changes
- **Authentication** — Username/password auth with bcrypt hashing and cookie-based sessions
- **Import/Export** — Download holdings as CSV, upload to sync between environments
- **Dark theme** — Pre-configured dark UI theme

## Screenshots

*(Add screenshots of your dashboard, AI chat, and holdings pages here)*

## Project Structure

```
mystock-mgmt/
├── app.py                          # Streamlit entrypoint + navigation + auth
├── requirements.txt                # Python dependencies
├── .env                            # AI & app configuration (gitignored)
├── auth_config.yaml                # Auth credentials (gitignored)
│
├── .streamlit/
│   └── config.toml                 # Streamlit theme & server config
│
├── pages/
│   ├── 1_Dashboard.py              # Portfolio dashboard with summary + tables
│   ├── 2_Indian_Stocks.py          # NSE/BSE holdings CRUD
│   ├── 3_Singapore_Stocks.py       # SGX holdings CRUD
│   ├── 4_US_Stocks.py              # NYSE/NASDAQ holdings CRUD
│   ├── 5_Indian_Mutual_Funds.py    # Zerodha MF holdings CRUD
│   ├── 6_SG_Mutual_Funds.py        # Tiger Trade MF holdings CRUD
│   ├── 7_Precious_Metals.py        # Gold/Silver OCBC holdings CRUD
│   ├── 8_AI_Chat.py                # AI chatbot page
│   └── 9_Import_Export.py          # CSV download/upload for data sync
│
├── db/
│   ├── database.py                 # SQLite connection, CRUD, caching
│   └── models.py                   # Dataclasses (Holding, PriceData, EnrichedHolding)
│
├── services/
│   ├── market_data.py              # yfinance wrapper (stocks + ATH/ATL + trend)
│   ├── mf_data.py                  # mfapi.in wrapper (Indian MF NAVs)
│   ├── metals_data.py              # Gold/Silver prices (USD/oz to SGD/gram)
│   └── forex_data.py               # Frankfurter API + yfinance fallback
│
├── components/
│   ├── summary_cards.py            # Portfolio summary metric cards
│   ├── holdings_table.py           # Grouped holdings table with P&L
│   ├── holding_form.py             # Reusable add/edit/delete form
│   ├── trend_indicator.py          # Trend arrows (UP/DOWN/SIDEWAYS)
│   ├── ai_insights_panel.py        # AI insights display
│   └── alert_sidebar.py            # Sidebar alert notifications
│
├── ai/
│   ├── config.py                   # AIConfig (provider, tier, API key, budget)
│   ├── llm_provider.py             # Provider-agnostic LLM interface (LiteLLM)
│   ├── tools/
│   │   ├── registry.py             # Tool registry + schema generation
│   │   ├── portfolio_tools.py      # 6 DB query tools for the AI agent
│   │   └── market_tools.py         # 4 live market data tools for the AI agent
│   ├── agents/
│   │   ├── chat_agent.py           # Conversational agent with tool-use loop
│   │   ├── insights_agent.py       # Portfolio insights (single LLM call)
│   │   └── monitor_agent.py        # Background price monitor (no LLM)
│   └── prompts/
│       ├── system_prompts.py       # Chat agent system prompt
│       └── insight_templates.py    # Insights JSON prompt template
│
└── utils/
    ├── constants.py                # Enums, currency codes, exchange suffixes
    ├── formatters.py               # Currency/percentage formatting
    └── validators.py               # Input validation
```

## Data Sources

| Asset Type | Source | Ticker Format | Cost |
|---|---|---|---|
| Indian Stocks | yfinance | `RELIANCE.NS` / `RELIANCE.BO` | Free |
| Singapore Stocks | yfinance | `D05.SI` | Free |
| US Stocks | yfinance | `AAPL` | Free |
| Indian Mutual Funds | mfapi.in | AMFI scheme code (e.g., `119551`) | Free |
| Singapore Mutual Funds | Manual NAV entry | N/A | Free |
| Precious Metals | yfinance | `GC=F` (Gold), `SI=F` (Silver) | Free |
| Forex Rates | Frankfurter API | `INR` to `SGD`, `USD` to `SGD` | Free |

---

## Local Setup

### Prerequisites

- Python 3.10+
- pip

### 1. Clone the repository

```bash
git clone https://github.com/palanibsm/mystock-mgmt.git
cd mystock-mgmt
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure authentication

Create `auth_config.yaml` in the project root:

```yaml
credentials:
  usernames:
    admin:
      name: Admin
      password: <bcrypt-hashed-password>

cookie:
  name: mystock_auth
  key: <random-secret-key>
  expiry_days: 30
```

To generate a bcrypt password hash:

```python
python -c "import streamlit_authenticator as stauth; print(stauth.Hasher().hash('your_password'))"
```

### 5. Configure AI (optional)

Create `.env` in the project root:

```env
# Provider: "openai" | "anthropic" | "gemini" | "ollama"
AI_PROVIDER=openai

# Tier: "economy" (cheap/fast) | "quality" (expensive/smart)
AI_TIER=economy

# API key for the selected provider
AI_API_KEY=sk-your-api-key-here

# Ollama settings (only needed if AI_PROVIDER=ollama)
OLLAMA_BASE_URL=http://localhost:11434

# Monthly budget cap in USD
AI_MONTHLY_BUDGET=5.00

# Generate insights automatically on dashboard load (true/false)
AI_INSIGHTS_ON_LOAD=true

# Background price check interval in seconds (300 = 5 minutes)
AI_MONITOR_INTERVAL=300

# Alert threshold: alert if a holding moves more than this % in a day
AI_PRICE_ALERT_PCT=5.0
```

> **Note:** AI features are optional. The app works fully without any AI configuration — you just won't have the chat, insights, and will see warnings on the AI Chat page.

### 6. Run the app

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`. Log in with the credentials you configured in step 4.

---

## Streamlit Cloud Deployment

### 1. Push code to GitHub

Make sure your repo is on GitHub. Sensitive files (`.env`, `auth_config.yaml`, `portfolio.db`) are already in `.gitignore` and won't be pushed.

### 2. Connect to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **New app**
3. Select your GitHub repo, branch (`master`), and main file (`app.py`)
4. Click **Deploy**

### 3. Configure secrets

In your Streamlit Cloud app, go to **Settings > Secrets** and paste the following TOML configuration:

```toml
# ── Authentication ──
[auth]

[auth.credentials.usernames.admin]
name = "Admin"
password = "$2b$12$your_bcrypt_hash_here"

[auth.cookie]
name = "mystock_auth"
key = "your-random-secret-key-here"
expiry_days = 30

# ── AI Configuration ──
AI_PROVIDER = "openai"
AI_TIER = "economy"
AI_API_KEY = "sk-your-api-key-here"
AI_MONTHLY_BUDGET = "5.00"
AI_INSIGHTS_ON_LOAD = "true"
AI_MONITOR_INTERVAL = "300"
AI_PRICE_ALERT_PCT = "5.0"
```

### 4. Import your portfolio data

Since Streamlit Cloud uses an ephemeral filesystem, your local SQLite database won't be available. Use the **Import/Export** page to transfer data:

1. **On your local machine:** Go to Import/Export > **Download CSV**
2. **On Streamlit Cloud:** Go to Import/Export > **Upload CSV** > confirm replacement

> **Important:** Streamlit Cloud may reset the database on redeployment. Always keep a local CSV backup of your holdings.

---

## AI Providers

The app supports four LLM providers. Switch by changing `AI_PROVIDER` and `AI_TIER`:

| Provider | Economy Model | Quality Model | API Key Required |
|---|---|---|---|
| `openai` | gpt-4o-mini | gpt-4o | Yes |
| `anthropic` | claude-haiku-4-5 | claude-sonnet-4-5 | Yes |
| `gemini` | gemini-2.0-flash | gemini-2.5-pro | Yes |
| `ollama` | llama3.1:8b | llama3.1:70b | No (local) |

### Estimated monthly AI cost

| Usage Level | GPT-4o-mini | Gemini Flash | Claude Haiku | Ollama |
|---|---|---|---|---|
| Light (5 chats/day) | ~$0.10 | ~$0.06 | ~$0.55 | $0.00 |
| Moderate (15 chats/day) | ~$0.30 | ~$0.18 | ~$1.65 | $0.00 |
| Heavy (30 chats/day) | ~$0.55 | ~$0.35 | ~$3.00 | $0.00 |

### Using Ollama (fully local, free)

1. Install Ollama: [ollama.com](https://ollama.com)
2. Pull a model: `ollama pull llama3.1:8b`
3. Set in `.env`:
   ```env
   AI_PROVIDER=ollama
   AI_TIER=economy
   OLLAMA_BASE_URL=http://localhost:11434
   ```

No API key needed. No internet required for AI features. Zero cost.

---

## Configuration Reference

### `.env` variables

| Variable | Default | Description |
|---|---|---|
| `AI_PROVIDER` | `openai` | LLM provider: `openai`, `anthropic`, `gemini`, `ollama` |
| `AI_TIER` | `economy` | Model tier: `economy` (cheap/fast), `quality` (smart/expensive) |
| `AI_API_KEY` | *(empty)* | API key for the selected provider (not needed for Ollama) |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `AI_MONTHLY_BUDGET` | `5.00` | Monthly AI spending cap in USD |
| `AI_INSIGHTS_ON_LOAD` | `true` | Auto-generate insights on dashboard load |
| `AI_MONITOR_INTERVAL` | `300` | Price check interval in seconds (300 = 5 min) |
| `AI_PRICE_ALERT_PCT` | `5.0` | Alert threshold for daily price moves (%) |

### `auth_config.yaml` structure

```yaml
credentials:
  usernames:
    <username>:
      name: <Display Name>
      password: <bcrypt hash>

cookie:
  name: <cookie name>
  key: <cookie secret key>
  expiry_days: <number>
```

### Streamlit theme (`.streamlit/config.toml`)

The app ships with a dark theme. Modify `.streamlit/config.toml` to customize:

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#0e1117"
secondaryBackgroundColor = "#262730"
textColor = "#fafafa"
font = "sans serif"
```

---

## How It Works

### Dashboard

The dashboard fetches all holdings from SQLite, enriches each with live price data from the appropriate service (yfinance, mfapi.in, or manual cache), calculates P&L, converts values to SGD, and renders grouped tables per asset category.

### AI Chat Agent

The chat agent implements a tool-use loop:

1. User sends a question
2. LLM selects relevant tools (e.g., `get_portfolio_summary`, `get_current_price`)
3. Tools execute against the database and live APIs
4. Results are fed back to the LLM
5. LLM generates a grounded response

Up to 5 tool-call rounds per question. 10 tools available (6 portfolio, 4 market).

### AI Insights Agent

Pre-fetches all portfolio data, sends it to the LLM in a single call, and receives structured JSON insights categorized as: diversification, performance, risk, opportunity, or alert.

### Price Monitor Agent

A background daemon thread (no LLM) that checks stock prices at a configurable interval. Alerts appear in the sidebar when any holding moves more than the configured threshold percentage in a day.

---

## Troubleshooting

### `TypeError: Secrets does not support item assignment` (Streamlit Cloud)

This happens because `st.secrets` returns immutable objects. The app handles this with `_secrets_to_dict()` in `app.py` — make sure you're running the latest version.

### `streamlit-authenticator` version errors

This app requires `streamlit-authenticator>=0.4.0`. The v0.4.x API changed how password hashing works:

```python
# v0.4.x (correct)
stauth.Hasher().hash('password')

# v0.3.x (old, won't work)
stauth.Hasher(['password']).generate()
```

### yfinance returns no data

- Check your internet connection
- Verify the symbol format (e.g., `RELIANCE.NS` not `RELIANCE`)
- Some symbols may not be available on weekends/holidays
- yfinance has rate limits; the app's cache layer mitigates this

### AI features not working

- Verify `AI_API_KEY` is set correctly in `.env` or Streamlit secrets
- Check that `AI_PROVIDER` matches your API key provider
- For Ollama, ensure the server is running (`ollama serve`) and a model is pulled

### Database reset on Streamlit Cloud

Streamlit Cloud uses an ephemeral filesystem. Your SQLite database will reset on redeployment. Use **Import/Export** to backup and restore your data.

---

## License

This project is for personal use. Feel free to fork and adapt for your own portfolio tracking needs.

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on [GitHub](https://github.com/palanibsm/mystock-mgmt).
