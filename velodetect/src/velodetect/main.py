from velodetect.data.fetch_ohlcv_dataframe import OHLCVFetcher
from velodetect.indicator.technical_indicators import TechnicalIndicators


def main():
    # Fetch OHLCV data
    fetcher = OHLCVFetcher("bybit")
    df = fetcher.fetch_ohlcv_dataframe(
        symbol="BTC/USDT",
        timeframe="1h",
        since="2024-01-01",
        until="2024-02-01",
    )

    print(f"Fetched {len(df)} candles")
    print("OHLCV Data Sample:")
    print(df.head())
    print("\n" + "="*50 + "\n")

    # Initialize technical indicators
    indicators = TechnicalIndicators(df)

    # Demonstrate key velocity indicators
    print("VELOCITY INDICATORS DEMONSTRATION")
    print("="*50)

    # Price velocity (momentum)
    price_velocity = indicators.price_velocity()
    print(f"Price Velocity (1-period % change): {price_velocity.tail(3).values}")

    # Rate of Change (ROC) - key momentum indicator
    roc = indicators.roc(period=14)
    print(f"ROC (14-period): Last 3 values: {roc.tail(3).values}")

    # RSI - momentum oscillator
    rsi = indicators.rsi()
    print(f"RSI (14): Last 3 values: {rsi.tail(3).values}")

    # MACD - trend-following momentum
    macd_line, signal_line, histogram = indicators.macd()
    print(f"MACD Line: {macd_line.tail(1).values[0]:.4f}")
    print(f"Signal Line: {signal_line.tail(1).values[0]:.4f}")
    print(f"Histogram: {histogram.tail(1).values[0]:.4f}")

    # Volume velocity
    vol_velocity = indicators.volume_velocity()
    print(f"Volume Velocity (ratio to MA): {vol_velocity.tail(3).values}")

    print("\n" + "="*50)
    print("VELOCITY SIGNALS DETECTION")
    print("="*50)

    # Detect velocity signals
    signals = indicators.detect_velocity_signals()
    recent_signals = signals.tail(5)
    print("Recent signals (last 5 periods):")
    print(recent_signals)

    # Summary of active signals
    latest_signals = signals.iloc[-1]
    active_signals = latest_signals[latest_signals == True]
    if len(active_signals) > 0:
        print(f"\nActive signals in latest period: {list(active_signals.index)}")
    else:
        print("\nNo active signals in latest period")

    print("\nTechnical Indicators ready for VeloDetect velocity analysis!")


if __name__ == "__main__":
    main()
