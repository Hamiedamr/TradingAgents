import os
from tradingagents.default_config import DEFAULT_CONFIG
from langchain_litellm import ChatLiteLLM
from langchain_core.messages import HumanMessage

def test_llm():
    print("--- 🔍 Diagnosing LLM Connection ---")
    
    # 1. Inspect Config
    model_name = DEFAULT_CONFIG.get("deep_think_llm")
    print(f"Configured Model: {model_name}")
    
    # 2. Check API Key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ CRITICAL: GEMINI_API_KEY is not set in environment variables.")
        return
    else:
        print(f"API Key found: {api_key[:5]}...{api_key[-4:]}")

    # 3. Attempt Generation
    try:
        print(f"Attempting to invoke {model_name}...")
        llm = ChatLiteLLM(model=model_name, api_key=api_key)
        response = llm.invoke([HumanMessage(content="Hello, are you operational? Reply with 'Yes, I am working'.")])
        print("\n✅ LLM Success!")
        print(f"Response: {response.content}")
        return True
    except Exception as e:
        print("\n❌ LLM Failed!")
        print(f"Error: {e}")
        print("\nPossible fixes:")
        print("1. Check if model name is correct (try 'gemini/gemini-1.5-flash').")
        print("2. Verify API key validity.")
        return False

if __name__ == "__main__":
    test_llm()
