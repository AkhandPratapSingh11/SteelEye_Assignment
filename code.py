from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

app = FastAPI()

# Mocked database
trades_db = []

# Pydantic models
class TradeDetails(BaseModel):
    buySellIndicator: str = Field(description="A value of BUY for buys, SELL for sells.")
    price: float = Field(description="The price of the Trade.")
    quantity: int = Field(description="The amount of units traded.")

class Trade(BaseModel):
    asset_class: Optional[str] = Field(alias="assetClass", default=None, description="The asset class of the instrument traded.")
    counterparty: Optional[str] = Field(default=None, description="The counterparty the trade was executed with.")
    instrument_id: str = Field(alias="instrumentId", description="The ISIN/ID of the instrument traded.")
    instrument_name: str = Field(alias="instrumentName", description="The name of the instrument traded.")
    trade_date_time: datetime = Field(alias="tradeDateTime", description="The date-time the Trade was executed")
    trade_details: TradeDetails = Field(alias="tradeDetails", description="The details of the trade, i.e. price, quantity")
    trade_id: Optional[str] = Field(alias="tradeId", default=None, description="The unique ID of the trade")
    trader: str = Field(description="The name of the Trader")

# Endpoint to fetch a list of trades
@app.get("/trades")
def get_trades(skip: int = 0, limit: int = 10):
    return trades_db[skip : skip + limit]

# Endpoint to fetch a single trade by ID
@app.get("/trades/{trade_id}")
def get_trade_by_id(trade_id: str):
    for trade in trades_db:
        if trade.trade_id == trade_id:
            return trade
    raise HTTPException(status_code=404, detail="Trade not found")

# Endpoint to search trades based on various fields
@app.get("/trades/search")
def search_trades(
    search: Optional[str] = None,
    counterparty: Optional[str] = None,
    instrumentId: Optional[str] = None,
    instrumentName: Optional[str] = None,
    trader: Optional[str] = None
):
    search_results = []
    for trade in trades_db:
        if (
            (search is None or search.lower() in trade.dict().values()) and
            (counterparty is None or trade.counterparty == counterparty) and
            (instrumentId is None or trade.instrument_id == instrumentId) and
            (instrumentName is None or trade.instrument_name == instrumentName) and
            (trader is None or trade.trader == trader)
        ):
            search_results.append(trade)
    return search_results

# Endpoint to filter trades based on optional query parameters
@app.get("/trades/filter")
def filter_trades(
    assetClass: Optional[str] = Query(None, description="Asset class of the trade."),
    end: Optional[datetime] = Query(None, description="The maximum date for the tradeDateTime field."),
    maxPrice: Optional[float] = Query(None, description="The maximum value for the tradeDetails.price field."),
    minPrice: Optional[float] = Query(None, description="The minimum value for the tradeDetails.price field."),
    start: Optional[datetime] = Query(None, description="The minimum date for the tradeDateTime field."),
    tradeType: Optional[str] = Query(None, description="The tradeDetails.buySellIndicator is a BUY or SELL.")
):
    filtered_trades = []
    for trade in trades_db:
        if (
            (assetClass is None or trade.asset_class == assetClass) and
            (end is None or trade.trade_date_time <= end) and
            (maxPrice is None or trade.trade_details.price <= maxPrice) and
            (minPrice is None or trade.trade_details.price >= minPrice) and
            (start is None or trade.trade_date_time >= start) and
            (tradeType is None or trade.trade_details.buySellIndicator == tradeType)
        ):
            filtered_trades.append(trade)
    return filtered_trades

# Mock data generation (you can replace this with your own data retrieval logic)
def generate_mock_data():
    trade1 = Trade(
        asset_class="Equity",
        counterparty="Counterparty 1",
        instrument_id="AAPL",
        instrument_name="Apple Inc",
        trade_date_time=datetime.now(),
        trade_details=TradeDetails(buySellIndicator="BUY", price=150.5, quantity=100),
        trade_id="1",
        trader="John"
    )
    trade2 = Trade(
        asset_class="Bond",
        counterparty="Counterparty 2",
        instrument_id="TSLA",
        instrument_name="Tesla Inc",
        trade_date_time=datetime.now(),
        trade_details=TradeDetails(buySellIndicator="SELL", price=800.25, quantity=50),
        trade_id="2",
        trader="Jane"
    )
    trades_db.append(trade1)
    trades_db.append(trade2)

# Generate mock data
generate_mock_data()
