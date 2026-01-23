from .alpha_vantage_common import _make_api_request, format_datetime_for_api

def get_news(ticker, start_date, end_date) -> dict[str, str] | str:
    """Returns live and historical market news & sentiment data from premier news outlets worldwide.

    Covers stocks, cryptocurrencies, forex, and topics like fiscal policy, mergers & acquisitions, IPOs.

    Args:
        ticker: Stock symbol for news articles.
        start_date: Start date for news search.
        end_date: End date for news search.

    Returns:
        Dictionary containing news sentiment data or JSON string.
    """

    params = {
        "tickers": ticker,
        "time_from": format_datetime_for_api(start_date),
        "time_to": format_datetime_for_api(end_date),
        "sort": "LATEST",
        "limit": "50",
    }
    
    return _make_api_request("NEWS_SENTIMENT", params)

def get_global_news(curr_date, look_back_days=7, limit=5) -> dict[str, str] | str:
    """Returns global market news via Alpha Vantage.
    
    Uses 'EARNINGS,IPO,MERGERS_AND_ACQUISITIONS,TECHNOLOGY,FINANCIAL_MARKETS' topics 
    to approximate global market news since no specific global endpoint exists.
    """
    from datetime import datetime, timedelta
    
    # Calculate start date based on lookback
    if isinstance(curr_date, str):
        end_dt = datetime.strptime(curr_date, "%Y-%m-%d")
    else:
        end_dt = curr_date
        
    start_dt = end_dt - timedelta(days=look_back_days)
    
    params = {
        "topics": "financial_markets,economy_macro,earnings,ipo,mergers_and_acquisitions,technology",
        "time_from": format_datetime_for_api(start_dt.strftime("%Y-%m-%d")),
        "time_to": format_datetime_for_api(end_dt.strftime("%Y-%m-%d")),
        "sort": "LATEST",
        "limit": str(limit),
    }
    
    return _make_api_request("NEWS_SENTIMENT", params)

def get_insider_transactions(symbol: str) -> dict[str, str] | str:
    """Returns latest and historical insider transactions by key stakeholders.

    Covers transactions by founders, executives, board members, etc.

    Args:
        symbol: Ticker symbol. Example: "IBM".

    Returns:
        Dictionary containing insider transaction data or JSON string.
    """

    params = {
        "symbol": symbol,
    }

    return _make_api_request("INSIDER_TRANSACTIONS", params)