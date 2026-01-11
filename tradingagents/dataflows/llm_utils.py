from litellm import completion
from .config import get_config

def get_search_tool_for_model(model_name):
    """
    Returns the appropriate search tool definition based on the model/provider.
    """
    if "gemini" in model_name.lower():
        # Google Gemini Search Grounding configuration
        # LiteLLM passes this through to the Google API
        return [
            {
                "google_search_retrieval": {
                    "dynamic_retrieval_config": {
                        "mode": "dynamic",
                        "dynamic_threshold": 0.7,
                    }
                }
            }
        ]
    else:
        # Default/OpenAI-like "web_search_preview" tool (as requested by user)
        return [
            {
                "type": "web_search_preview",
                "user_location": {"type": "approximate"},
                "search_context_size": "low",
            }
        ]

def get_stock_news_llm(query, start_date, end_date):
    config = get_config()
    model = config["quick_think_llm"]
    
    messages = [
        {
            "role": "user",
            "content": f"Can you search Social Media for {query} from {start_date} to {end_date}? Make sure you only get the data posted during that period."
        }
    ]

    tools = get_search_tool_for_model(model)

    response = completion(
        model=model,
        messages=messages,
        base_url=config.get("backend_url"),
        temperature=1,
        max_tokens=4096,
        top_p=1,
        tools=tools # Pass the provider-specific tool
    )

    # Handle response format differences if necessary, but usually content is in message.content
    return response.choices[0].message.content


def get_global_news_llm(curr_date, look_back_days=7, limit=5):
    config = get_config()
    model = config["quick_think_llm"]
    
    messages = [
        {
            "role": "user",
            "content": f"Can you search global or macroeconomics news from {look_back_days} days before {curr_date} to {curr_date} that would be informative for trading purposes? Make sure you only get the data posted during that period. Limit the results to {limit} articles."
        }
    ]

    tools = get_search_tool_for_model(model)

    response = completion(
        model=model,
        messages=messages,
        base_url=config.get("backend_url"),
        temperature=1,
        max_tokens=4096,
        top_p=1,
        tools=tools
    )

    return response.choices[0].message.content


def get_fundamentals_llm(ticker, curr_date):
    config = get_config()
    model = config["quick_think_llm"]
    
    messages = [
        {
            "role": "user",
            "content": f"Can you search Fundamental for discussions on {ticker} during of the month before {curr_date} to {curr_date}. Make sure you only get the data posted during that period. List as a table, with PE/PS/Cash flow/ etc"
        }
    ]

    tools = get_search_tool_for_model(model)

    response = completion(
        model=model,
        messages=messages,
        base_url=config.get("backend_url"),
        temperature=1,
        max_tokens=4096,
        top_p=1,
        tools=tools
    )

    return response.choices[0].message.content
