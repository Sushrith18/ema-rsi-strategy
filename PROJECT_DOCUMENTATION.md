# EMA + RSI Combined Trading Strategy Backtester

## 1. Project overview

This project is an educational Streamlit dashboard for testing long-only trading
strategies based on exponential moving averages (EMA) and the relative strength
index (RSI). It downloads daily market data from Yahoo Finance, calculates
technical indicators, generates trading signals, simulates a portfolio, and
displays the results interactively.

The application does not place real trades. Its results are historical
backtest results and should not be treated as financial advice.

## 2. Technology stack

- **Python**: Application and strategy implementation language.
- **Streamlit**: Web dashboard framework and interactive controls.
- **pandas**: Tabular market data, time-series calculations, and tables.
- **NumPy**: Numerical calculations, including the Sharpe ratio.
- **yfinance**: Yahoo Finance market-data download client.
- **Plotly**: Interactive price, indicator, signal, and equity charts.

## 3. Project files

### `app.py`

The main Streamlit application. It:

1. Configures the page title, icon, and wide layout.
2. Defines the Yahoo Finance download function.
3. Creates the sidebar controls.
4. Validates user input.
5. Downloads and prepares market data.
6. Generates signals and runs the backtest.
7. Displays charts, metrics, comparisons, and the trade log.

### `strategy.py`

Contains indicator and signal-generation logic:

- EMA calculation.
- Wilder-smoothed RSI calculation.
- Position holding between entry and exit conditions.
- EMA-only, RSI-only, and EMA + RSI signal modes.
- One-day signal shifting to avoid lookahead bias.

### `backtest.py`

Contains portfolio simulation and performance metrics:

- Close-to-close portfolio returns.
- Equity-curve construction.
- Trade-log generation.
- Strategy return.
- Buy-and-hold return.
- CAGR.
- Number of trades.
- Win rate.
- Maximum drawdown.
- Annualized Sharpe ratio.

### `requirements.txt`

Lists the Python packages required to run the dashboard.

### `README.md`

Provides quick-start installation and usage instructions.

## 4. Website layout and visible components

### Page title

At the top of the website, the dashboard displays:

> EMA + RSI Combined Trading Strategy Backtester

This identifies the application and its purpose.

### Introductory caption

The caption explains that the application is a beginner-friendly, long-only
educational backtester using live Yahoo Finance data.

### Sidebar: Backtest settings

The left sidebar contains all user-configurable inputs.

#### Ticker symbol

Text input containing the default ticker `RELIANCE.NS`. The value is stripped of
leading/trailing whitespace and converted to uppercase before it is sent to
Yahoo Finance.

Examples:

- `RELIANCE.NS` for Reliance Industries on the National Stock Exchange of India.
- `AAPL` for Apple.
- `MSFT` for Microsoft.

#### Start date

Date picker for the first date included in the backtest. The default is
approximately five years before the current date.

#### End date

Date picker for the last date included in the backtest. The default is the
current date.

The end date must be later than the start date.

#### Fast EMA period

Slider from 5 to 50 days, defaulting to 20 days. This controls the faster EMA
used to identify recent price movement.

#### Slow EMA period

Slider from 20 to 200 days, defaulting to 50 days. This controls the slower EMA
used to identify the broader trend.

The slow EMA period must be greater than the fast EMA period.

#### RSI period

Slider from 7 to 21 days, defaulting to 14 days. This controls how many periods
are used to calculate RSI.

#### RSI buy threshold

Slider from 20 to 40, defaulting to 30. Lower RSI values indicate that the
market may be in an oversold or pullback area.

#### RSI sell threshold

Slider from 60 to 80, defaulting to 70. Higher RSI values indicate that the
market may be in an overbought area.

The buy threshold must be lower than the sell threshold.

#### Strategy mode

Dropdown with three choices:

- **EMA + RSI**
- **EMA only**
- **RSI only**

The selected mode controls the primary metrics, charts, signals, and trade log.

## 5. Input validation and error messages

The dashboard stops and displays an error when:

- The ticker field is empty.
- The end date is not after the start date.
- The slow EMA period is not greater than the fast EMA period.
- Yahoo Finance returns an exception.
- Yahoo Finance returns no usable market data.
- The strategy parameters are invalid.

These checks prevent the backtest from running with invalid or incomplete inputs.

## 6. Market-data processing

The application requests daily OHLCV data from Yahoo Finance using:

- The selected ticker.
- The selected start date.
- The selected end date, inclusive.
- `auto_adjust=False`, preserving the downloaded OHLC values.

The application supports Yahoo Finance responses with multi-level columns by
flattening the column index. Rows missing `Open`, `High`, `Low`, or `Close`
values are removed.

Downloaded data is cached by Streamlit so that reruns with the same ticker and
date range do not repeatedly download identical data.

## 7. Indicator calculations

### Fast EMA and slow EMA

An EMA gives more weight to recent prices than a simple moving average.

- The **Fast EMA** reacts more quickly to price changes.
- The **Slow EMA** reacts more slowly and represents the broader trend.

The application uses:

```text
Fast EMA = exponential moving average using the fast period
Slow EMA = exponential moving average using the slow period
```

### RSI

RSI measures recent upward and downward price momentum on a scale from 0 to 100.

- RSI below the buy threshold represents the configured oversold/pullback zone.
- RSI above the sell threshold represents the configured overbought zone.

The implementation uses Wilder-style smoothing. A continuously rising series is
assigned an RSI of 100, while a flat series is assigned an RSI of 50.

## 8. Trading strategy modes

### EMA only

The strategy is in a long position while:

```text
Fast EMA > Slow EMA
```

It exits when the fast EMA is no longer above the slow EMA.

### RSI only

The strategy enters when:

```text
RSI < RSI buy threshold
```

It remains in the position until:

```text
RSI > RSI sell threshold
```

The position is held between those entry and exit conditions.

### EMA + RSI

The combined strategy enters when both conditions are satisfied:

```text
Fast EMA > Slow EMA
RSI crosses upward out of the buy zone
```

The RSI crossing condition means the previous RSI was at or below the buy
threshold and the current RSI is above it.

The strategy exits when either condition occurs:

```text
Fast EMA < Slow EMA
RSI > RSI sell threshold
```

## 9. Lookahead-bias protection

Signals are calculated using a completed candle and then shifted by one trading
day before they become positions. This means information from today's close is
not used to pretend that a trade was executed earlier on that same close.

The backtest therefore uses the next available trading day's close for the
simulated position.

## 10. Price and indicator chart

The section title is shown as:

> `<TICKER> price, indicators, and signals`

The interactive Plotly chart has two vertically stacked panels.

### Upper panel: Price and EMA indicators

The upper panel displays:

- **Candlestick price chart** using Open, High, Low, and Close.
- **Fast EMA** line.
- **Slow EMA** line.
- **Buy markers**, shown as green upward triangles below the candle.
- **Sell markers**, shown as red downward triangles above the candle.

The chart includes a hover mode that aligns information across traces. The
default Plotly range slider is hidden to keep the chart compact.

### Lower panel: Relative Strength Index

The lower panel displays:

- The RSI line.
- A dashed green horizontal line at the RSI buy threshold.
- A dashed red horizontal line at the RSI sell threshold.

The RSI y-axis is fixed from 0 to 100.

## 11. Selected strategy performance section

The section title is:

> Selected strategy performance

Six metric cards are displayed.

### Strategy return

The percentage gain or loss produced by the selected strategy over the tested
period.

### Buy-and-hold return

The percentage gain or loss from buying at the first available close and
holding until the final available close.

### Win rate

The percentage of logged trades whose return is positive:

```text
Winning trades / total trades × 100
```

If there are no trades, the win rate is displayed as 0%.

### Maximum drawdown

The largest decline from a previous equity-curve peak. It is normally displayed
as a negative percentage.

### Sharpe ratio

The annualized risk-adjusted return estimate:

```text
sqrt(252) × average daily strategy return / daily return standard deviation
```

If the daily return standard deviation is zero, the dashboard displays 0.

### Number of trades

The number of trades in the trade log, including a final open trade closed at
the last available price.

## 12. Equity curve chart

The equity chart is titled:

> Equity curve

It displays two lines:

- **Strategy**: simulated portfolio value beginning with an initial capital of
  100,000.
- **Buy and hold**: the value of holding the underlying asset from the first
  available close, also normalized to 100,000.

The y-axis represents portfolio value.

## 13. Comparison of all strategy modes

The comparison section displays results for all three modes, regardless of which
mode is selected in the sidebar:

- EMA only
- RSI only
- EMA + RSI

The table contains:

- **Strategy Return (%)**
- **Buy & Hold Return (%)**
- **CAGR (%)**
- **Trades**
- **Win Rate (%)**
- **Max Drawdown (%)**
- **Sharpe Ratio**

This allows the user to compare the selected parameters across the three
strategy approaches.

## 14. Trade log

The trade-log section lists every simulated trade.

Each row contains:

- **Entry Date**
- **Exit Date**
- **Entry Price**
- **Exit Price**
- **Return %**

If no trades are generated, the website displays:

> No completed or open trades were generated for this configuration.

When trades exist, the table includes a CSV download button. The filename is
based on the ticker and selected strategy mode.

## 15. Why values can show as zero

Zero values are not automatically an application error. They can occur when the
selected configuration generates no trades or when there is insufficient usable
data.

For example:

- No entry condition was met, so the strategy return remains 0%.
- No trades exist, so the win rate is 0%.
- No trades exist, so the trade count is 0.
- A very short date range may not provide enough rows for the EMA and RSI
  warm-up periods.

On narrow screens, Streamlit may visually shorten long metric labels or values
with an ellipsis. This is a layout effect, not a calculation failure.

## 16. Important limitations

The backtester currently does not model:

- Brokerage fees.
- Transaction costs.
- Slippage.
- Taxes.
- Stop-loss orders.
- Take-profit orders.
- Position sizing.
- Partial fills.
- Intraday prices.
- Dividends or corporate-action assumptions beyond the downloaded data.

Yahoo Finance availability and data quality can change. Historical performance
does not guarantee future results.

## 17. Running the project

From the project directory:

```powershell
.\venv\Scripts\streamlit.exe run app.py
```

The local dashboard is normally available at:

```text
http://localhost:8501
```

## 18. End-to-end data flow

```text
Sidebar inputs
    ↓
Validate ticker, dates, and indicator parameters
    ↓
Download daily OHLCV data from Yahoo Finance
    ↓
Calculate EMA and RSI indicators
    ↓
Generate mode-specific signals
    ↓
Shift signals by one trading day
    ↓
Simulate portfolio and trades
    ↓
Calculate performance metrics
    ↓
Render charts, metric cards, comparison table, and trade log
```
