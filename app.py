"""Streamlit dashboard for the EMA + RSI Combined Trading Strategy Backtester."""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
from plotly.subplots import make_subplots

from backtest import calculate_metrics, run_backtest
from strategy import generate_signals


st.set_page_config(page_title="EMA + RSI Backtester", page_icon="📈", layout="wide")


@st.cache_data(show_spinner=False)
def download_data(ticker: str, start: date, end: date) -> pd.DataFrame:
    """Download daily OHLCV data from Yahoo Finance."""
    data = yf.download(
        ticker,
        start=start,
        end=end + timedelta(days=1),
        auto_adjust=False,
        progress=False,
    )
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    return data.dropna(subset=["Open", "High", "Low", "Close"])


def format_metric(value: float, suffix: str = "%") -> str:
    """Format a metric consistently for the dashboard."""
    return f"{value:,.2f}{suffix}"


st.title("EMA + RSI Combined Trading Strategy Backtester")
st.caption("A beginner-friendly, long-only educational backtester using live Yahoo Finance data.")

with st.sidebar:
    st.header("Backtest settings")
    ticker = st.text_input("Ticker symbol", "RELIANCE.NS").strip().upper()
    default_start = date.today() - timedelta(days=365 * 5)
    start_date = st.date_input("Start date", default_start)
    end_date = st.date_input("End date", date.today())
    fast_ema = st.slider("Fast EMA period", 5, 50, 20)
    slow_ema = st.slider("Slow EMA period", 20, 200, 50)
    rsi_period = st.slider("RSI period", 7, 21, 14)
    rsi_buy = st.slider("RSI buy threshold", 20, 40, 30)
    rsi_sell = st.slider("RSI sell threshold", 60, 80, 70)
    mode = st.selectbox("Strategy mode", ["EMA + RSI", "EMA only", "RSI only"])

if not ticker:
    st.error("Enter a ticker symbol to continue.")
    st.stop()
if end_date <= start_date:
    st.error("End date must be after start date.")
    st.stop()
if slow_ema <= fast_ema:
    st.error("Slow EMA must be greater than fast EMA.")
    st.stop()

try:
    raw_data = download_data(ticker, start_date, end_date)
except Exception as error:
    st.error(f"Could not download data for {ticker}: {error}")
    st.stop()
if raw_data.empty:
    st.error("No market data was returned. Check the ticker and date range.")
    st.stop()

try:
    selected_data = generate_signals(
        raw_data, fast_ema, slow_ema, rsi_period, rsi_buy, rsi_sell, mode
    )
    equity_curve, daily_returns, trade_log = run_backtest(selected_data)
    metrics = calculate_metrics(selected_data, equity_curve, daily_returns, trade_log)
except ValueError as error:
    st.error(str(error))
    st.stop()

st.subheader(f"{ticker} price, indicators, and signals")
figure = make_subplots(
    rows=2,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.08,
    row_heights=[0.7, 0.3],
    subplot_titles=("Price and EMA indicators", "Relative Strength Index (RSI)"),
)
figure.add_trace(
    go.Candlestick(
        x=selected_data.index,
        open=selected_data["Open"],
        high=selected_data["High"],
        low=selected_data["Low"],
        close=selected_data["Close"],
        name="Price",
    ),
    row=1,
    col=1,
)
figure.add_trace(
    go.Scatter(x=selected_data.index, y=selected_data["Fast EMA"], name="Fast EMA"),
    row=1,
    col=1,
)
figure.add_trace(
    go.Scatter(x=selected_data.index, y=selected_data["Slow EMA"], name="Slow EMA"),
    row=1,
    col=1,
)
buy_points = selected_data[selected_data["Buy Signal"]]
sell_points = selected_data[selected_data["Sell Signal"]]
figure.add_trace(
    go.Scatter(
        x=buy_points.index,
        y=buy_points["Low"] * 0.98,
        mode="markers",
        marker={"symbol": "triangle-up", "color": "green", "size": 11},
        name="Buy",
    ),
    row=1,
    col=1,
)
figure.add_trace(
    go.Scatter(
        x=sell_points.index,
        y=sell_points["High"] * 1.02,
        mode="markers",
        marker={"symbol": "triangle-down", "color": "red", "size": 11},
        name="Sell",
    ),
    row=1,
    col=1,
)
figure.add_trace(
    go.Scatter(x=selected_data.index, y=selected_data["RSI"], name="RSI"),
    row=2,
    col=1,
)
figure.add_hline(y=rsi_buy, line_dash="dash", line_color="green", row=2, col=1)
figure.add_hline(y=rsi_sell, line_dash="dash", line_color="red", row=2, col=1)
figure.update_layout(height=750, xaxis_rangeslider_visible=False, hovermode="x unified")
figure.update_yaxes(range=[0, 100], row=2, col=1)
st.plotly_chart(figure, use_container_width=True)

st.subheader("Selected strategy performance")
metric_columns = st.columns(6)
metric_values = [
    ("Strategy return", format_metric(metrics["Strategy Return"])),
    ("Buy-and-hold return", format_metric(metrics["Buy & Hold Return"])),
    ("Win rate", format_metric(metrics["Win Rate"])),
    ("Max drawdown", format_metric(metrics["Max Drawdown"])),
    ("Sharpe ratio", f'{metrics["Sharpe Ratio"]:,.2f}'),
    ("Number of trades", f'{int(metrics["Number of Trades"])}'),
]
for column, (label, value) in zip(metric_columns, metric_values):
    column.metric(label, value)

equity_chart = go.Figure()
equity_chart.add_trace(go.Scatter(x=equity_curve.index, y=equity_curve, name="Strategy"))
buy_hold_equity = 100_000 * selected_data["Close"] / selected_data["Close"].iloc[0]
equity_chart.add_trace(
    go.Scatter(x=buy_hold_equity.index, y=buy_hold_equity, name="Buy and hold")
)
equity_chart.update_layout(title="Equity curve", yaxis_title="Portfolio value")
st.plotly_chart(equity_chart, use_container_width=True)

st.subheader("Comparison of all strategy modes")
comparison_rows = []
for comparison_mode in ["EMA only", "RSI only", "EMA + RSI"]:
    comparison_data = generate_signals(
        raw_data, fast_ema, slow_ema, rsi_period, rsi_buy, rsi_sell, comparison_mode
    )
    comparison_equity, comparison_returns, comparison_trades = run_backtest(comparison_data)
    comparison_metrics = calculate_metrics(
        comparison_data, comparison_equity, comparison_returns, comparison_trades
    )
    comparison_rows.append(
        {
            "Mode": comparison_mode,
            "Strategy Return (%)": comparison_metrics["Strategy Return"],
            "Buy & Hold Return (%)": comparison_metrics["Buy & Hold Return"],
            "CAGR (%)": comparison_metrics["CAGR"],
            "Trades": int(comparison_metrics["Number of Trades"]),
            "Win Rate (%)": comparison_metrics["Win Rate"],
            "Max Drawdown (%)": comparison_metrics["Max Drawdown"],
            "Sharpe Ratio": comparison_metrics["Sharpe Ratio"],
        }
    )
st.dataframe(pd.DataFrame(comparison_rows).set_index("Mode"), use_container_width=True)

st.subheader("Trade log")
if trade_log.empty:
    st.info("No completed or open trades were generated for this configuration.")
else:
    st.dataframe(trade_log, use_container_width=True)
    csv_data = trade_log.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download trade log as CSV",
        data=csv_data,
        file_name=f"{ticker.lower()}_{mode.lower().replace(' ', '_')}_trades.csv",
        mime="text/csv",
    )
