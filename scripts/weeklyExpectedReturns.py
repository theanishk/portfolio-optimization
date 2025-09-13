import pandas as pd
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import RFE
from sklearn.metrics import mean_absolute_error
import optuna
from datetime import timedelta
import ssl

# MongoDB connection URI
uri = "mongodb+srv://anishk6374:sylva_123@data.m7zft.mongodb.net/?retryWrites=true&w=majority&appName=Data"

# Create MongoDB client with ssl_cert_reqs=CERT_NONE to bypass certificate verification
client = MongoClient(uri, server_api=ServerApi("1"), tls=True, tlsAllowInvalidCertificates=True)
db = client.get_database("Data")
collection = db.get_collection("equityHistoricalData")


def fetch_data(collection, start_date):
    """Fetches data from MongoDB starting from a given date and returns a DataFrame with required transformations."""
    # Query MongoDB for records with `date` greater than or equal to the start_date
    data_cursor = collection.find({"date": {"$gte": pd.to_datetime(start_date).strftime('%Y-%m-%d')}})
    data_list = list(data_cursor)
    
    # Convert to DataFrame and prepare data
    data = pd.DataFrame(data_list)
    data["date"] = pd.to_datetime(data["date"])  # Ensure date is in datetime format
    data.drop("_id", axis=1, inplace=True)  # Drop MongoDB's ObjectId
    
    # Pivot data to have tickers as columns and dates as index
    data = data.pivot(index="date", columns="ticker", values="adj_close")
    data.sort_index(inplace=True)  # Sort data by date
    data.columns = [col.replace(".NS", "") for col in data.columns]  # Clean up ticker names
    
    return data



def generate_forecasted_returns(returns, tickers, forecast_horizon=4):
    """Predicts returns for the specified horizon using Recursive Feature Elimination and Random Forest."""
    forecasted_returns = pd.DataFrame(
        index=pd.date_range(
            start=returns.index[-1], periods=forecast_horizon + 1, freq="W-MON"
        )[1:]
    )

    for ticker in tickers:
        lags = pd.DataFrame({"returns": returns[ticker]})
        for lag in range(70, 4, -1):
            lags[f"lag_{lag}"] = returns[ticker].shift(lag)
        lags.dropna(inplace=True)

        X = lags.iloc[:, 1:]
        y = lags.iloc[:, 0]

        # Define Optuna objective for RFE with Random Forest
        def objective(trial):
            n_estimators = trial.suggest_int("n_estimators", 10, 100)
            max_depth = trial.suggest_int("max_depth", 1, 32)
            n_features = trial.suggest_int("n_features", 1, X.shape[1])
            model = RandomForestRegressor(
                n_estimators=n_estimators, max_depth=max_depth, random_state=1
            )
            selector = RFE(estimator=model, n_features_to_select=n_features)
            selector.fit(X, y)
            return mean_absolute_error(y, selector.predict(X))

        study = optuna.create_study(direction="minimize")
        study.optimize(objective, n_trials=10)
        best_params = study.best_params

        # Retrain with best parameters
        model = RandomForestRegressor(
            n_estimators=best_params["n_estimators"],
            max_depth=best_params["max_depth"],
            random_state=1,
        )
        selector = RFE(estimator=model, n_features_to_select=best_params["n_features"])
        selector.fit(X, y)
        selected_features = X.columns[selector.support_]

        # Create final dataset for prediction
        forecast_df = pd.DataFrame({"returns": returns[ticker]})
        forecast_df = pd.concat(
            [forecast_df, pd.DataFrame(index=forecasted_returns.index)], axis=0
        )
        for feature in selected_features:
            forecast_df[feature] = forecast_df["returns"].shift(
                int(feature.split("_")[1])
            )
        forecast_df.dropna(inplace=True)

        # Train model and predict
        X_final = forecast_df[selected_features]
        y_final = forecast_df["returns"]
        model.fit(X_final[:-forecast_horizon], y_final[:-forecast_horizon])
        forecasted_returns[ticker] = model.predict(X_final[-forecast_horizon:])

    return forecasted_returns


# Code start here
# Backtest period
backtest_start_date = "2023-07-01"
backtest_end_date = "2024-07-01"
forecast_horizon = 4  # weeks
output_path = "returns/weekly_forecasted_returns_backtest.csv"

# Initialize CSV file with headers if it doesn't exist
with open(output_path, "w") as f:
    f.write("forecast_date,ticker,forecasted_return\n")

current_date = pd.to_datetime(backtest_start_date)

while current_date <= pd.to_datetime(backtest_end_date):
    # Fetch data up to the current date
    data = fetch_data(collection, start_date="2018-01-01")
    data = data[data.index <= current_date]
    
    # Calculate returns and tickers
    returns = data.pct_change().dropna()
    tickers = returns.columns

    # Generate forecast for the next 4 weeks
    forecasted_returns = generate_forecasted_returns(returns, tickers, forecast_horizon=forecast_horizon)
    
    # Append forecasted results to CSV file
    forecasted_returns.reset_index().melt(id_vars="index", var_name="ticker", value_name="forecasted_return")\
        .assign(forecast_date=current_date)\
        .to_csv(output_path, mode="a", index=False, header=False)
    
    # Update to the next weekly date
    current_date += timedelta(weeks=1)
