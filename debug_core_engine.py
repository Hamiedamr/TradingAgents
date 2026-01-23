import sys
import os
import datetime

# Add project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

def debug_core():
    print("\n--- 🧠 DEBUGGING CORE ENGINE ---")
    
    # Force minimal config
    config = DEFAULT_CONFIG.copy()
    config["max_debate_rounds"] = 1
    
    try:
        # 1. Initialize Graph
        print("1. Intitalizing Graph...", end=" ")
        graph = TradingAgentsGraph(
            selected_analysts=["market"], # Minimal team
            config=config,
            debug=True
        )
        print("✅ OK")
        
        # 2. Run Propagate
        ticker = "AAPL"
        date = datetime.datetime.now().date().strftime("%Y-%m-%d")
        print(f"2. Running propagation for {ticker}...", end="\n")
        
        final_state, decision = graph.propagate(ticker, date)
        
        # 3. Validation
        print(f"\n3. Decision Reached: {decision}")
        if final_state.get("market_report"):
             print("✅ Market Report generated.")
        else:
             print("❌ Market Report MISSING.")
             
        print("\n✅ CORE ENGINE IS FUNCTIONAL")

    except Exception as e:
        print(f"\n❌ CORE ENGINE CRASHED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore") # Clear noise
    debug_core()
