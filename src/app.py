from flask import Flask
from polygon import RESTClient
from dotenv import load_dotenv
import os
from auth import api
from flasgger import APISpec, Schema, Swagger, fields
from auth import index, login, logout, authorize, auth_callback, signup
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
import oauth

load_dotenv()  # Load environment variables from .env file

SESSION_SECRET = os.getenv("SESSION_SECRET", "dev-change-me")  # set a strong random value

app = Flask(__name__)
app.register_blueprint(api)
app.config.update(
    SECRET_KEY=SESSION_SECRET,
    SESSION_COOKIE_SAMESITE="Lax",      # good default for OAuth code flow
    SESSION_COOKIE_SECURE=False,        # True in HTTPS/prod
)

oauth.init_app(app)

spec = APISpec(
    title='Flasger Petstore',
    version='1.0.10',
    openapi_version='2.0',
    plugins=[
        FlaskPlugin(),
        MarshmallowPlugin(),
    ],
)


client = RESTClient(os.getenv("POLYGON_API"))

@app.get("/")
def home():
    return "Welcome to the Stock Trading API! Visit /apidocs for API documentation."

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
        news_data = client.list_ticker_news(ticker=ticker, limit=10, order="asc", sort="published_utc")
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
    return {"valid": True, "data": f"Trades for {ticker} with limit {limit} not implemented yet."} # TODO: Hard code limit because no access
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

template = spec.to_flasgger(
    app,
    paths=[validate_symbol, symbols, status, news, price, candles, orderbook, trades, portfolio, portfolio_positions, orders, order_details, exec_sim, backtest, risk_beta, ai_summary, alerts, get_alerts, index, login, logout, authorize, auth_callback, signup],
)

swag = Swagger(app, template=template)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)