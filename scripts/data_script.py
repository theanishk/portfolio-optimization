import yfinance as yf
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://anishk6374:sylva_123@data.m7zft.mongodb.net/?retryWrites=true&w=majority&appName=Data"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi("1"))

# db.collection.remove()

try:
    db = client.Data
    collection = db.equityHistoricalData
    # x = collection.delete_many({})
    # print(x.deleted_count, " documents deleted.")

except Exception as e:
    print(e)

if __name__ == "__main__":
    start_date = "2016-12-01"
    tickers = [
        "SUNPHARMA.NS",
        "DRREDDY.NS",
        "CIPLA.NS",
        "JBCHEPHARM.NS",
        "POLYMED.NS",
        "ABBOTINDIA.NS",
        "ZYDUSLIFE.NS",
        "NTPC.NS",
        "RELIANCE.NS",
        "ADANIPOWER.NS",
        "BPCL.NS",
        "COALINDIA.NS",
        "GSPL.NS",
        "UNOMINDA.NS",
        "ITC.NS",
        "MARICO.NS",
        "BRITANNIA.NS",
        "COLPAL.NS",
        "VBL.NS",
        "NAVNETEDUL.NS",
        "BALRAMCHIN.NS",
    ]

    # Downloading Historical data
    for ticker in tickers:
        data = yf.download(ticker, start=start_date, interval="1wk")["Adj Close"]

        for date, adj_close in data.items():
            stock_data = {
                "ticker": ticker,
                "date": date.strftime("%Y-%m-%d"),
                "adj_close": adj_close,
            }
            collection.insert_one(stock_data)
