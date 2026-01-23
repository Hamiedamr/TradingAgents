import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from tradingagents.dataflows.interface import route_to_vendor
from tradingagents.dataflows.config import set_config
from tradingagents.default_config import DEFAULT_CONFIG

# Set config to ensure Alpha Vantage is selected for news_data
set_config(DEFAULT_CONFIG)

def test_global_news():
    print("Testing get_global_news with Alpha Vantage default...")
    try:
        current_date = datetime.now().strftime("%Y-%m-%d")
        # Call the routing function directly
        result = route_to_vendor("get_global_news", current_date, look_back_days=3, limit=2)
        
        print("\n--- Result Preview ---")
        if isinstance(result, str):
            print(result[:500] + "..." if len(result) > 500 else result)
        else:
            print(result)
            
        if "Error" in str(result) and "failed" in str(result):
             print("\nFAILED: Still got an error message in the result string.")
             sys.exit(1)
        
        print("\nSUCCESS: route_to_vendor returned data.")
        
    except Exception as e:
        print(f"\nCRITICAL FAILURE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_global_news()
