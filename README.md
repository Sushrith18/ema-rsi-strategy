# EMA + RSI Combined Trading Strategy Backtester

A beginner-friendly Streamlit dashboard for exploring long-only trading
strategies built from exponential moving averages (EMA) and the relative
strength index (RSI). Market data is fetched live from Yahoo Finance through
`yfinance`; no database is required.

## Features

- Interactive candlestick chart with fast/slow EMA overlays.
- EMA-only, RSI-only, and EMA + RSI strategy modes.
- RSI subplot with buy and sell thresholds.
- Next-day signal execution to avoid lookahead bias.
- Strategy and buy-and-hold equity curves.
- Return, CAGR, win rate, drawdown, and annualized Sharpe ratio metrics.
- Trade log with CSV download.
- Side-by-side comparison of all three modes.

## Tech stack

Python 3.10+, pandas, NumPy, yfinance, Plotly, and Streamlit.

## Install and run

1. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Start the dashboard:

   ```bash
   streamlit run app.py
   ```

## Strategy explanation

- **EMA only:** Buy while the fast EMA is above the slow EMA. Exit when the
  fast EMA falls below the slow EMA.
- **RSI only:** Buy when RSI is below the oversold buy threshold and hold until
  RSI reaches the overbought sell threshold.
- **EMA + RSI:** Buy only when the fast EMA confirms an uptrend and RSI crosses
  upward out of the oversold/pullback zone. Exit when the trend turns down or
  RSI reaches the sell threshold.

Signals are shifted by one trading day, so a signal calculated from one
completed candle is executed on the following day's close in the simulation.

## Screenshot

_Placeholder: add a screenshot of the running Streamlit dashboard here._

## Example results

| Mode | Strategy Return | CAGR | Win Rate | Max Drawdown | Sharpe Ratio |
| --- | ---: | ---: | ---: | ---: | ---: |
| EMA only | _Run the app_ | _Run the app_ | _Run the app_ | _Run the app_ | _Run the app_ |
| RSI only | _Run the app_ | _Run the app_ | _Run the app_ | _Run the app_ | _Run the app_ |
| EMA + RSI | _Run the app_ | _Run the app_ | _Run the app_ | _Run the app_ | _Run the app_ |

## Limitations

- There are no transaction costs, brokerage fees, slippage, or taxes.
- Yahoo Finance data availability and quality can change.
- Past performance does not guarantee future results.
- This is an educational mini project, not financial advice.

## Future improvements

- Add transaction costs and slippage assumptions.
- Support stop-loss, take-profit, and position sizing.
- Add more indicators and parameter optimization.
- Add walk-forward testing and out-of-sample evaluation.
- Add downloadable performance reports.
