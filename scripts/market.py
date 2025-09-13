import yfinance as yf
import json
from datetime import datetime


# Function to download indices
def save_stock_data_to_json(
    name, symbol, start_date, end_date=None, json_filename="stock_data.json"
):
    # If end_date is not provided, use today's date
    if end_date is None:
        end_date = datetime.today().strftime("%Y-%m-%d")

    # Download the stock data for the specified date range
    stock_data = (
        yf.download(symbol, start=start_date, end=end_date)["Adj Close"]
        .reset_index()
        .rename(columns={symbol: "Adj Close"})
    )

    # Create the structure for data
    historical_data = []
    for _, row in stock_data.iterrows():
        historical_data.append(
            {"date": row["Date"].strftime("%Y-%m-%d"), "close": row["Adj Close"]}
        )

    # Prepare the final JSON structure
    result = {"name": name, "symbol": symbol, "historicalData": historical_data}

    # Convert the result to a JSON string
    stock_json_string = json.dumps(result)

    # Print the JSON string (optional)
    print(stock_json_string)

    # Save the JSON string to a file
    with open(json_filename, "w") as f:
        f.write(stock_json_string)

    print(f"Data saved to {json_filename}")


#! NIFTY 50
save_stock_data_to_json(
    name="Nifty 50",
    symbol="^NSEI",
    start_date="2020-01-01",
    json_filename="nifty50.json",
)

#! NIFTY FMCG
save_stock_data_to_json(
    name="Nifty FMCG",
    symbol="^CNXFMCG",
    start_date="2020-01-01",
    json_filename="niftyFMCG.json",
)

#! NIFTY PHARMA
save_stock_data_to_json(
    name="Nifty Pharma",
    symbol="^CNXPHARMA",
    start_date="2020-01-01",
    json_filename="niftyPharma.json",
)

#! NIFTY ENERGY
save_stock_data_to_json(
    name="Nifty Energy",
    symbol="^CNXENERGY",
    start_date="2020-01-01",
    json_filename="niftyEnergy.json",
)
