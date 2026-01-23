import sys
import os
import datetime
from typing import List

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.dataflows.config import set_config

# Constants
TEST_TICKER = "AAPL"
TEST_DATE = datetime.datetime.now().date().strftime("%Y-%m-%d")

# Force defaults
set_config(DEFAULT_CONFIG)

def run_test(name: str, analysts: List[str]):
    print(f"\n{'='*60}")
    print(f"TESTING: {name.upper()} FLOW")
    print(f"Analysts: {analysts}")
    print(f"{'='*60}")
    
    try:
        # Initialize graph with specific analysts
        print(f"Initializing graph for {name} using DEFAULT_CONFIG...") 
        graph = TradingAgentsGraph(
            selected_analysts=analysts,
            debug=True, # Enable debug output
            config=DEFAULT_CONFIG
        )
        
        print(f"Running propagation for {TEST_TICKER} on {TEST_DATE}...")
        final_state, decision = graph.propagate(TEST_TICKER, TEST_DATE)
        
        print(f"\n{'-'*20} RESULTS: {name} {'-'*20}")
        print(f"Decision: {decision}")
        
        # Check specific outputs based on analyst type
        if "market" in analysts:
            has_report = bool(final_state.get("market_report"))
            print(f"Market Report Generated: {'✅' if has_report else '❌'}")
            
        if "news" in analysts:
            has_report = bool(final_state.get("news_report"))
            print(f"News Report Generated: {'✅' if has_report else '❌'}")
            
        if "fundamentals" in analysts:
             has_report = bool(final_state.get("fundamentals_report"))
             print(f"Fundamentals Report Generated: {'✅' if has_report else '❌'}")
        
        if "social" in analysts:
             has_report = bool(final_state.get("sentiment_report"))
             print(f"Social/Sentiment Report Generated: {'✅' if has_report else '❌'}")
             
        if name == "FULL_TEAM":
             has_plan = bool(final_state.get("trader_investment_plan"))
             print(f"Trader Plan Generated: {'✅' if has_plan else '❌'}")

        print(f"\n✅ SUCCESS: {name} Flow Passed")
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: {name} Flow Crashed")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("Starting Comprehensive Analyst Flow Tests...")
    print(f"Target: {TEST_TICKER} @ {TEST_DATE}")
    
    results = {}
    
    # 1. Market Analyst
    results["Market"] = run_test("Market_Analyst", ["market"])
    
    # 2. News Analyst
    results["News"] = run_test("News_Analyst", ["news"])
    
    # 3. Fundamentals Analyst
    results["Fundamentals"] = run_test("Fundamentals_Analyst", ["fundamentals"])
    
    # 4. Social Media Analyst
    results["Social"] = run_test("Social_Media_Analyst", ["social"])
    
    # 5. Full Team (Integration)
    # Only run if individual components look somewhat healthy, or just run it anyway
    # to see interaction failures.
    results["Full_Team"] = run_test("FULL_TEAM", ["market", "news", "fundamentals", "social"])
    
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    all_passed = True
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name:<20} : {status}")
        if not passed: all_passed = False
        
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
