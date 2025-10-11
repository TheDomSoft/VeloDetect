"""Data models for OHLCV (Open, High, Low, Close, Volume) data."""

from dataclasses import dataclass
from datetime import datetime
from typing import List
import pandas as pd


@dataclass
class OHLCVBar:
    """Represents a single OHLCV (Open, High, Low, Close, Volume) bar."""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

    def __post_init__(self):
        """Validate OHLCV data."""
        if self.high < self.low:
            raise ValueError(f"High ({self.high}) cannot be less than Low ({self.low})")
        if self.high < self.open or self.high < self.close:
            raise ValueError(f"High ({self.high}) must be >= Open ({self.open}) and Close ({self.close})")
        if self.low > self.open or self.low > self.close:
            raise ValueError(f"Low ({self.low}) must be <= Open ({self.open}) and Close ({self.close})")
        if self.volume < 0:
            raise ValueError(f"Volume ({self.volume}) cannot be negative")


@dataclass
class OHLCVData:
    """Container for OHLCV data with metadata."""
    symbol: str
    timeframe: str
    exchange: str
    bars: List[OHLCVBar]
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert OHLCV data to a pandas DataFrame."""
        if not self.bars:
            return pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        data = {
            'timestamp': [bar.timestamp for bar in self.bars],
            'open': [bar.open for bar in self.bars],
            'high': [bar.high for bar in self.bars],
            'low': [bar.low for bar in self.bars],
            'close': [bar.close for bar in self.bars],
            'volume': [bar.volume for bar in self.bars],
        }
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        return df
    
    def __len__(self) -> int:
        """Return the number of bars."""
        return len(self.bars)