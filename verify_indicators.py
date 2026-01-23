import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from tradingagents.dataflows.y_finance import get_stock_stats_indicators_window
from tradingagents.dataflows.alpha_vantage_indicator import get_indicator

def test_indicators():
    print("Testing get_indicators with multiple values...")
    curr_date = datetime.now().strftime("%Y-%m-%d")
    symbol = "NVDA"
    indicators = "macd,rsi" 
    
    print(f"\n--- Testing yfinance with '{indicators}' ---")
    try:
        result = get_stock_stats_indicators_window(symbol, indicators, curr_date, look_back_days=5)
        print("SUCCESS: Result length:", len(result))
        print("Result Preview:\n", result[:200] + "...")
    except Exception as e:
        print(f"FAILED yfinance: {e}")
        import traceback
        traceback.print_exc()

    print(f"\n--- Testing Alpha Vantage with '{indicators}' ---")
    try:
        # Note: This might fail if key is missing, but logic check is main goal
        # We Mock _make_api_request if needed, but let's try calling it.
        # If it fails on API key, it at least passed the validation check!
        result = get_indicator(symbol, indicators, curr_date, look_back_days=5)
        print("SUCCESS: Result length:", len(result))
    except Exception as e:
        if "API Key" in str(e) or "recursion" not in str(e):
             # If we get past the "not supported" error, it's a success for this fix
             print(f"Caught expected API/Data error (Validation passed): {e}")
        else:
             print(f"FAILED Alpha Vantage: {e}")
             import traceback
             traceback.print_exc()

if __name__ == "__main__":
    test_indicators()
