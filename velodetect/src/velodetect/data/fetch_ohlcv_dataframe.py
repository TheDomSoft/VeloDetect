from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import pandas as pd
import ccxt

from velodetect.model.ohlcv import OHLCVBar, OHLCVData

class OHLCVFetcher:
    """Fetches OHLCV data from cryptocurrency exchanges using CCXT."""
    
    def __init__(self, exchange_id: str, api_key: Optional[str] = None, secret: Optional[str] = None):
        """
        Initialize the OHLCV fetcher.
        
        Args:
            exchange_id: Exchange name (e.g., 'bybit', 'binance', 'coinbase')
            api_key: Optional API key for authenticated requests
            secret: Optional API secret for authenticated requests
        """
        self.exchange_id = exchange_id
        
        # Initialize the exchange
        exchange_class = getattr(ccxt, exchange_id)
        config = {}
        if api_key and secret:
            config['apiKey'] = api_key
            config['secret'] = secret
        
        self.exchange = exchange_class(config)
        
        # Load markets
        try:
            self.exchange.load_markets()
        except Exception as e:
            print(f"Warning: Could not load markets: {e}")

    def fetch_ohlcv_dataframe(
        self, 
        symbol: str, 
        timeframe: str, 
        since: str, 
        until: str
    ) -> pd.DataFrame:
        """
        Fetch OHLCV data and return as a pandas DataFrame.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT', 'ETH/USDT')
            timeframe: Candle timeframe (e.g., '1m', '5m', '1h', '1d')
            since: Start date (ISO format: 'YYYY-MM-DD')
            until: End date (ISO format: 'YYYY-MM-DD')
            
        Returns:
            DataFrame with OHLCV data indexed by timestamp
        """
        ohlcv_data = self.fetch_ohlcv(symbol, timeframe, since, until)
        return ohlcv_data.to_dataframe()
    
    def fetch_ohlcv(
        self, 
        symbol: str, 
        timeframe: str, 
        since: str, 
        until: str
    ) -> OHLCVData:
        """
        Fetch OHLCV data and return as OHLCVData object.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT', 'ETH/USDT')
            timeframe: Candle timeframe (e.g., '1m', '5m', '1h', '1d')
            since: Start date (ISO format: 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS')
            until: End date (ISO format: 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS')
            
        Returns:
            OHLCVData object containing the fetched data
        """
        # Convert date strings to timestamps (milliseconds)
        since_timestamp = self._parse_date_to_timestamp(since)
        until_timestamp = self._parse_date_to_timestamp(until)
        
        # Fetch all data in chunks (exchanges have limits on how much data can be fetched at once)
        all_bars = []
        current_timestamp = since_timestamp
        
        while current_timestamp < until_timestamp:
            try:
                # Fetch OHLCV data from exchange
                ohlcv = self.exchange.fetch_ohlcv(
                    symbol=symbol,
                    timeframe=timeframe,
                    since=current_timestamp,
                    limit=1000  # Max limit for most exchanges
                )
                
                if not ohlcv:
                    break
                
                # Convert to OHLCVBar objects
                for candle in ohlcv:
                    timestamp_ms, open_price, high_price, low_price, close_price, volume = candle
                    
                    # Skip candles beyond the until date
                    if timestamp_ms >= until_timestamp:
                        break
                    
                    bar = OHLCVBar(
                        timestamp=datetime.fromtimestamp(timestamp_ms / 1000),
                        open=float(open_price),
                        high=float(high_price),
                        low=float(low_price),
                        close=float(close_price),
                        volume=float(volume)
                    )
                    all_bars.append(bar)
                
                # Update current timestamp to the last fetched candle
                current_timestamp = ohlcv[-1][0] + 1
                
                # If we got less than the limit, we've reached the end
                if len(ohlcv) < 1000:
                    break
                    
            except Exception as e:
                print(f"Error fetching OHLCV data: {e}")
                raise
        
        return OHLCVData(
            symbol=symbol,
            timeframe=timeframe,
            exchange=self.exchange_id,
            bars=all_bars
        )
    
    def _parse_date_to_timestamp(self, date_str: str) -> int:
        """
        Parse date string to Unix timestamp in milliseconds.
        
        Args:
            date_str: Date string in ISO format
            
        Returns:
            Unix timestamp in milliseconds
        """
        try:
            # Try parsing with time
            dt = datetime.fromisoformat(date_str)
        except ValueError:
            # If no time specified, parse as date only
            dt = datetime.strptime(date_str, '%Y-%m-%d')
        
        return int(dt.timestamp() * 1000)