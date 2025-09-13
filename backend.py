import fastapi
from polygon import RESTClient
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

app = fastapi.FastAPI()
client = RESTClient(os.getenv("POLYGON_API"))

@app.get("/v1/validate/{symbol}")
def validate_symbol(symbol: str):
    try:
        symbol_data = client.list_tickers(search=symbol, limit="1")
        return {"valid": True, "data": symbol_data}
    except Exception:
        return {"valid": False}


@app.get("/v1/symbols/{market}")
def symbols(market: str = "stocks"):
    try:
        symbols_data = client.list_tickers(market=market)
        return {"valid": True, "data": symbols_data}
    except Exception:
        return {"valid": False}


@app.get("/v1/status")
def status():
    try:
        status_data = client.list_tickers(ticker="AAPL")
        return {"valid": True, "data": status_data}
    except Exception:
        return {"valid": False}

@app.get("/v1/news/{ticker}")
def news(ticker: str):
    try:
        news_data = client.list_ticker_news(ticker=ticker, limit=10, sort="asc", sort="published_utc")
        return {"valid": True, "data": news_data}
    except Exception:
        return {"valid": False}


@app.get("/v1/price/{ticker}")
def price(ticker: str):
    try:
        price_data = client.get_last_trade(ticker)
        return {"valid": True, "data": price_data}
    except Exception:
        return {"valid": False}

@app.post("/v1/candles")
def candles(ticker: str, timeframe: str = "1Day", start: str = "2023-01-01", end: str = "2023-12-31"):
    try:
        candles_data = client.list_aggs(ticker, 1, timeframe, start, end)
        return {"valid": True, "data": candles_data}
    except Exception:
        return {"valid": False}

@app.post("/v1/orderbook")
def orderbook(ticker: str):
    try:
        orderbook_data = client.get_last_quote(ticker)
        return {"valid": True, "data": orderbook_data}
    except Exception:
        return {"valid": False}

@app.post("/v1/trades")
def trades(ticker: str, limit: int = 10):
    try:
        trades_data = client.list_trades(ticker, limit=limit, sort="desc")
        return {"valid": True, "data": trades_data}
    except Exception:
        return {"valid": False}

@app.post("/v1/portfolio")
def portfolio():
    return {"valid": True, "data": "Portfolio endpoint not implemented yet."}

@app.post("/v1/portfolio/positions")
def portfolio_positions():
    return {"valid": True, "data": "Portfolio positions endpoint not implemented yet."}

@app.post("/v1/orders")
def orders():
    return {"valid": True, "data": "Orders endpoint not implemented yet."}

@app.post("/v1/orders/{order_id}")
def order_details(order_id: str):
    return {"valid": True, "data": f"Order details for {order_id} not implemented yet."}

@app.post("/v1/exec/sim")
def exec_sim():
    return {"valid": True, "data": "Execution simulation endpoint not implemented yet."}

@app.post("/v1/backtest")
def backtest():
    return {"valid": True, "data": "Backtest endpoint not implemented yet."}

@app.post("/v1/risk/beta")
def risk_beta():
    return {"valid": True, "data": "Risk beta endpoint not implemented yet."}

@app.post("/v1/ai/summary")
def ai_summary(ticker: str):
    return {"valid": True, "data": f"AI summary for {ticker} not implemented yet."}

@app.post("/v1/alerts")
def alerts():
    return {"valid": True, "data": "Alerts endpoint not implemented yet."}

@app.get("/v1/alerts")
def get_alerts():
    return {"valid": True, "data": "Get alerts endpoint not implemented yet."}
