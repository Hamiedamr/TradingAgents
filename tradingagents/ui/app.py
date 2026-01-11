
import streamlit as st
import datetime
import sys
import os
from pathlib import Path

# Add project root to path to ensure imports work
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.ui.styles import apply_styles
from tradingagents.cli.models import AnalystType

# Page Config
st.set_page_config(
    page_title="TradingAgents AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Styles
apply_styles()

def main():
    # --- Sidebar Configuration ---
    st.sidebar.title("Configuration")
    
    # Analyst Team Selection (The "Tasks")
    st.sidebar.markdown("### Analyst Team")
    all_analysts = [a.value for a in AnalystType]
    selected_analysts = st.sidebar.multiselect(
        "Select Active Agents",
        options=all_analysts,
        default=all_analysts,
        help="Choose which AI agents will participate in the analysis."
    )

    # Advanced Settings Expander (kept for structural settings)
    with st.sidebar.expander("System Settings"):
        research_depth = st.slider("Research Depth", 1, 5, DEFAULT_CONFIG.get("max_debate_rounds", 1))
        st.caption(f"Provider: `{DEFAULT_CONFIG.get('llm_provider')}`")

    # --- Main Chat Interface ---
    st.title("TradingAgents AI 🚀")
    st.markdown("_Conversational Financial Analysis_")

    # Initialize State
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I am your AI Trading Assistant.\n\nPlease select the **Analyst Team** in the sidebar, then tell me **which stock ticker** you would like to analyze today."}
        ]
    if "workflow_state" not in st.session_state:
        st.session_state.workflow_state = {"step": "ask_ticker", "ticker": None, "date": None}

    # Display Chat Messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # --- Chat Logic ---
    if prompt := st.chat_input("Type your response here..."):
        # 1. User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Assistant Response Logic
        with st.chat_message("assistant"):
            current_step = st.session_state.workflow_state["step"]
            
            # --- PARSING & STATE TRANSITIONS ---
            
            # Shortcut: Detect "Analyze TARGET" at any time to reset and start
            import re
            shortcut_ticker = re.findall(r'\b[A-Z]{1,5}\b', prompt.upper())
            if "ANALYZE" in prompt.upper() and shortcut_ticker:
                 st.session_state.workflow_state["ticker"] = shortcut_ticker[0]
                 st.session_state.workflow_state["date"] = datetime.datetime.now().date()
                 st.session_state.workflow_state["step"] = "run_analysis"
                 current_step = "run_analysis" # Force jump

            # Linear Flow Logic
            if current_step == "ask_ticker":
                # Assume input is ticker if not shortcut
                potential_ticker = prompt.upper().strip()
                # Basic validation (1-5 chars)
                if 1 <= len(potential_ticker) <= 5 and potential_ticker.isalpha():
                    st.session_state.workflow_state["ticker"] = potential_ticker
                    st.session_state.workflow_state["step"] = "ask_date"
                    
                    response = f"Great, **{potential_ticker}**. What date should I analyze? (YYYY-MM-DD or say 'Today')"
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                else:
                    response = "I didn't catch a valid ticker. Please enter a stock symbol (e.g. NVDA, AAPL)."
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})

            elif current_step == "ask_date":
                # Parse Date
                target_date = None
                if "TODAY" in prompt.upper():
                    target_date = datetime.datetime.now().date()
                else:
                    try:
                        target_date = datetime.datetime.strptime(prompt.strip(), "%Y-%m-%d").date()
                    except ValueError:
                        pass
                
                if target_date:
                    st.session_state.workflow_state["date"] = target_date
                    st.session_state.workflow_state["step"] = "run_analysis"
                    current_step = "run_analysis" # Proceed immediately
                else:
                    response = "Please enter a valid date in **YYYY-MM-DD** format, or just say 'Today'."
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})

            # --- EXECUTION ---
            
            if current_step == "run_analysis":
                ticker = st.session_state.workflow_state["ticker"]
                date_val = st.session_state.workflow_state["date"]
                
                status_msg = f"Starting analysis for **{ticker}** on **{date_val}**..."
                st.markdown(status_msg)
                
                status_container = st.status("Initializing Agents...", expanded=True)
                
                try:
                    # 1. Setup Config
                    config = DEFAULT_CONFIG.copy()
                    config["max_debate_rounds"] = research_depth
                    
                    # 2. Initialize Graph
                    status_container.write("🧠 Instantiating Trading Graph...")
                    ta = TradingAgentsGraph(
                        selected_analysts=selected_analysts,
                        config=config,
                        debug=False
                    )

                    # 3. Running Analysis
                    status_container.write(f"🔍 Gathering data for {ticker}...")
                    
                    with st.spinner(f"Agents are analyzing {ticker}..."):
                        final_state, decision = ta.propagate(ticker, str(date_val))

                    status_container.update(label="Analysis Complete!", state="complete", expanded=False)

                    # 4. Display Results
                    report_md = f"# Analysis Report: {ticker}\n\n"
                    decision_emoji = "🟢" if "buy" in decision.lower() else ("🔴" if "sell" in decision.lower() else "⚪")
                    report_md += f"## {decision_emoji} Final Decision: **{decision.upper()}**\n\n"
                    
                    if final_state.get("final_trade_decision"):
                         report_md += f"### 🏦 Portfolio Manager Decision\n{final_state['final_trade_decision']}\n\n---\n\n"
                    if final_state.get("trader_investment_plan"):
                        report_md += f"### ⚖️ Trader Plan\n{final_state['trader_investment_plan']}\n\n---\n\n"
                    
                    with st.expander("See Analyst Reports"):
                        if final_state.get("market_report"): st.markdown(f"#### Market\n{final_state['market_report']}")
                        if final_state.get("sentiment_report"): st.markdown(f"#### Sentiment\n{final_state['sentiment_report']}")
                        if final_state.get("fundamentals_report"): st.markdown(f"#### Fundamentals\n{final_state['fundamentals_report']}")
                        if final_state.get("news_report"): st.markdown(f"#### News\n{final_state['news_report']}")

                    st.markdown(report_md)
                    st.session_state.messages.append({"role": "assistant", "content": report_md})
                    
                    # Reset state for next round
                    st.session_state.workflow_state = {"step": "ask_ticker", "ticker": None, "date": None}
                    reset_msg = "Analysis done. Which stock should I check next?"
                    st.markdown(reset_msg)
                    st.session_state.messages.append({"role": "assistant", "content": reset_msg})

                except Exception as e:
                    status_container.update(label="Analysis Failed", state="error")
                    st.error(f"Error: {e}")
                    # Allow retry
                    st.session_state.workflow_state["step"] = "ask_ticker"

if __name__ == "__main__":
    main()
