"""Technical indicators and trading signal generation for the backtester."""

from __future__ import annotations

import numpy as np
import pandas as pd


def calculate_ema(series: pd.Series, period: int) -> pd.Series:
    """Return an exponential moving average using pandas' EWM implementation."""
    if period <= 0:
        raise ValueError("EMA period must be positive.")
    return series.ewm(span=period, adjust=False, min_periods=period).mean()


def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Calculate RSI with Wilder's smoothing.

    Wilder's smoothing is equivalent to an exponential moving average with
    ``alpha=1 / period`` and ``adjust=False``.
    """
    if period <= 0:
        raise ValueError("RSI period must be positive.")

    delta = series.diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)
    average_gain = gains.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    average_loss = losses.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()

    relative_strength = average_gain.div(average_loss.replace(0, np.nan))
    rsi = 100 - (100 / (1 + relative_strength))
    # A continuously rising series has no losses, so its RSI is 100.
    rsi = rsi.mask((average_loss == 0) & (average_gain > 0), 100)
    # A flat series has neither gains nor losses, so its RSI is neutral.
    return rsi.mask((average_gain == 0) & (average_loss == 0), 50)


def _hold_between_entry_and_exit(
    entry_condition: pd.Series, exit_condition: pd.Series
) -> pd.Series:
    """Build a 0/1 position series from entry and exit conditions."""
    position = []
    in_position = False
    for enter, exit_ in zip(entry_condition.fillna(False), exit_condition.fillna(False)):
        if not in_position and enter:
            in_position = True
        elif in_position and exit_:
            in_position = False
        position.append(int(in_position))
    return pd.Series(position, index=entry_condition.index, dtype=int)


def generate_signals(
    df: pd.DataFrame,
    fast_ema: int,
    slow_ema: int,
    rsi_period: int,
    rsi_buy: float,
    rsi_sell: float,
    mode: str,
) -> pd.DataFrame:
    """Add indicators and a next-day-executed long-only ``position`` column.

    Signals are first calculated from today's completed candle and then shifted
    by one trading day. This prevents a strategy from buying at today's close
    using information that would only be known after that close.
    """
    valid_modes = {"EMA only", "RSI only", "EMA + RSI"}
    if mode not in valid_modes:
        raise ValueError(f"mode must be one of {sorted(valid_modes)}.")
    if slow_ema <= fast_ema:
        raise ValueError("slow_ema must be greater than fast_ema.")
    if rsi_buy >= rsi_sell:
        raise ValueError("rsi_buy must be lower than rsi_sell.")
    if "Close" not in df.columns:
        raise ValueError("DataFrame must contain a 'Close' column.")

    result = df.copy()
    result["Fast EMA"] = calculate_ema(result["Close"], fast_ema)
    result["Slow EMA"] = calculate_ema(result["Close"], slow_ema)
    result["RSI"] = calculate_rsi(result["Close"], rsi_period)

    uptrend = result["Fast EMA"] > result["Slow EMA"]
    downtrend = result["Fast EMA"] < result["Slow EMA"]
    rsi_rising_from_zone = (result["RSI"].shift(1) <= rsi_buy) & (
        result["RSI"] > rsi_buy
    )

    if mode == "EMA only":
        desired_position = uptrend.astype(int)
    elif mode == "RSI only":
        desired_position = _hold_between_entry_and_exit(
            result["RSI"] < rsi_buy, result["RSI"] > rsi_sell
        )
    else:
        desired_position = _hold_between_entry_and_exit(
            uptrend & rsi_rising_from_zone,
            downtrend | (result["RSI"] > rsi_sell),
        )

    # Execute a signal on the next trading day's close.
    result["position"] = desired_position.shift(1).fillna(0).astype(int)
    result["Buy Signal"] = result["position"].diff().eq(1)
    result["Sell Signal"] = result["position"].diff().eq(-1)
    return result
