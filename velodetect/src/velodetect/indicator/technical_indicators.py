import pandas as pd
import numpy as np
from typing import Optional, Tuple


class TechnicalIndicators:
    """Calculate various technical indicators from OHLCV data for velocity detection."""

    def __init__(self, ohlcv_df: pd.DataFrame):
        """
        Initialize with OHLCV DataFrame.

        Args:
            ohlcv_df: DataFrame with columns ['open', 'high', 'low', 'close', 'volume']
                     and timestamp index
        """
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in ohlcv_df.columns for col in required_cols):
            raise ValueError(f"DataFrame must contain columns: {required_cols}")

        self.df = ohlcv_df.copy()
        self._validate_data()

    def _validate_data(self) -> None:
        """Validate the input data."""
        if self.df.empty:
            raise ValueError("DataFrame cannot be empty")

        # Check for NaN values
        if self.df.isnull().any().any():
            print("Warning: DataFrame contains NaN values. They will be forward-filled.")
            self.df = self.df.ffill()

    # ============================================================================
    # MOVING AVERAGES
    # ============================================================================

    def sma(self, period: int, column: str = 'close') -> pd.Series:
        """
        Simple Moving Average.

        Args:
            period: Period for the moving average
            column: Column to calculate SMA on ('open', 'high', 'low', 'close', 'volume')

        Returns:
            Series with SMA values
        """
        if column not in self.df.columns:
            raise ValueError(f"Column '{column}' not found in data")

        return self.df[column].rolling(window=period).mean()

    def ema(self, period: int, column: str = 'close') -> pd.Series:
        """
        Exponential Moving Average.

        Args:
            period: Period for the moving average
            column: Column to calculate EMA on

        Returns:
            Series with EMA values
        """
        if column not in self.df.columns:
            raise ValueError(f"Column '{column}' not found in data")

        return self.df[column].ewm(span=period, adjust=False).mean()

    # ============================================================================
    # MOMENTUM INDICATORS (VELOCITY)
    # ============================================================================

    def roc(self, period: int = 14, column: str = 'close') -> pd.Series:
        """
        Rate of Change (ROC) - measures velocity of price changes.

        Args:
            period: Period for ROC calculation
            column: Column to calculate ROC on

        Returns:
            Series with ROC values as percentages
        """
        if column not in self.df.columns:
            raise ValueError(f"Column '{column}' not found in data")

        return ((self.df[column] - self.df[column].shift(period)) / self.df[column].shift(period)) * 100

    def momentum(self, period: int = 14, column: str = 'close') -> pd.Series:
        """
        Momentum indicator - difference between current and past values.

        Args:
            period: Period for momentum calculation
            column: Column to calculate momentum on

        Returns:
            Series with momentum values
        """
        if column not in self.df.columns:
            raise ValueError(f"Column '{column}' not found in data")

        return self.df[column] - self.df[column].shift(period)

    def rsi(self, period: int = 14) -> pd.Series:
        """
        Relative Strength Index (RSI) - momentum oscillator.

        Args:
            period: Period for RSI calculation (typically 14)

        Returns:
            Series with RSI values (0-100)
        """
        delta = self.df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def williams_r(self, period: int = 14) -> pd.Series:
        """
        Williams %R - momentum indicator showing overbought/oversold levels.

        Args:
            period: Period for Williams %R calculation

        Returns:
            Series with Williams %R values (-100 to 0)
        """
        highest_high = self.df['high'].rolling(window=period).max()
        lowest_low = self.df['low'].rolling(window=period).min()
        return ((highest_high - self.df['close']) / (highest_high - lowest_low)) * -100

    def stochastic_oscillator(self, k_period: int = 14, d_period: int = 3) -> Tuple[pd.Series, pd.Series]:
        """
        Stochastic Oscillator - momentum indicator.

        Args:
            k_period: Period for %K calculation
            d_period: Period for %D (signal line) calculation

        Returns:
            Tuple of (%K, %D) series
        """
        lowest_low = self.df['low'].rolling(window=k_period).min()
        highest_high = self.df['high'].rolling(window=k_period).max()
        k_percent = ((self.df['close'] - lowest_low) / (highest_high - lowest_low)) * 100
        d_percent = k_percent.rolling(window=d_period).mean()

        return k_percent, d_percent

    def macd(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Moving Average Convergence Divergence (MACD) - trend-following momentum indicator.

        Args:
            fast_period: Fast EMA period
            slow_period: Slow EMA period
            signal_period: Signal line EMA period

        Returns:
            Tuple of (MACD line, Signal line, Histogram)
        """
        fast_ema = self.ema(fast_period)
        slow_ema = self.ema(slow_period)
        macd_line = fast_ema - slow_ema
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        histogram = macd_line - signal_line

        return macd_line, signal_line, histogram

    # ============================================================================
    # VOLATILITY INDICATORS
    # ============================================================================

    def bollinger_bands(self, period: int = 20, std_dev: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Bollinger Bands - volatility bands around price.

        Args:
            period: Period for moving average
            std_dev: Standard deviation multiplier

        Returns:
            Tuple of (Upper Band, Middle Band, Lower Band)
        """
        middle_band = self.sma(period)
        std = self.df['close'].rolling(window=period).std()
        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)

        return upper_band, middle_band, lower_band

    def atr(self, period: int = 14) -> pd.Series:
        """
        Average True Range (ATR) - volatility indicator.

        Args:
            period: Period for ATR calculation

        Returns:
            Series with ATR values
        """
        high_low = self.df['high'] - self.df['low']
        high_close = np.abs(self.df['high'] - self.df['close'].shift())
        low_close = np.abs(self.df['low'] - self.df['close'].shift())

        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return true_range.rolling(window=period).mean()

    # ============================================================================
    # VOLUME INDICATORS
    # ============================================================================

    def volume_sma(self, period: int = 20) -> pd.Series:
        """
        Volume Simple Moving Average.

        Args:
            period: Period for volume SMA

        Returns:
            Series with volume SMA values
        """
        return self.sma(period, 'volume')

    def obv(self) -> pd.Series:
        """
        On-Balance Volume (OBV) - cumulative volume indicator.

        Returns:
            Series with OBV values
        """
        obv = pd.Series(index=self.df.index, dtype=float)
        obv.iloc[0] = self.df['volume'].iloc[0]

        for i in range(1, len(self.df)):
            if self.df['close'].iloc[i] > self.df['close'].iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] + self.df['volume'].iloc[i]
            elif self.df['close'].iloc[i] < self.df['close'].iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] - self.df['volume'].iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]

        return obv

    # ============================================================================
    # VELOCITY-SPECIFIC METHODS
    # ============================================================================

    def price_velocity(self, period: int = 1) -> pd.Series:
        """
        Price velocity as rate of change over periods.

        Args:
            period: Number of periods for velocity calculation

        Returns:
            Series with price velocity values
        """
        return self.df['close'].pct_change(periods=period)

    def volume_velocity(self, period: int = 20) -> pd.Series:
        """
        Volume velocity as ratio of current volume to its moving average.

        Args:
            period: Period for volume moving average

        Returns:
            Series with volume velocity values
        """
        volume_ma = self.volume_sma(period)
        return self.df['volume'] / volume_ma

    def detect_velocity_signals(self, roc_threshold: float = 2.0, volume_multiplier: float = 1.5) -> pd.DataFrame:
        """
        Detect velocity-based trading signals.

        Args:
            roc_threshold: ROC threshold for strong momentum (%)
            volume_multiplier: Volume multiplier for high volume detection

        Returns:
            DataFrame with various velocity signals
        """
        signals = pd.DataFrame(index=self.df.index)

        # Price momentum signals
        roc_14 = self.roc(14)
        signals['strong_upward_momentum'] = roc_14 > roc_threshold
        signals['strong_downward_momentum'] = roc_14 < -roc_threshold

        # RSI signals
        rsi = self.rsi()
        signals['overbought'] = rsi > 70
        signals['oversold'] = rsi < 30

        # Volume signals
        volume_velocity = self.volume_velocity()
        signals['high_volume'] = volume_velocity > volume_multiplier

        # MACD signals
        macd_line, signal_line, histogram = self.macd()
        signals['macd_bullish'] = (macd_line > signal_line) & (histogram > 0)
        signals['macd_bearish'] = (macd_line < signal_line) & (histogram < 0)

        # Bollinger Band signals
        upper_bb, middle_bb, lower_bb = self.bollinger_bands()
        signals['price_above_upper_bb'] = self.df['close'] > upper_bb
        signals['price_below_lower_bb'] = self.df['close'] < lower_bb

        return signals
    