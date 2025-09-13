import yfinance as yf
import pandas as pd
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import RFE
from sklearn.metrics import mean_absolute_error
import optuna

uri = "mongodb+srv://anishk6374:sylva_123@data.m7zft.mongodb.net/?retryWrites=true&w=majority&appName=Data"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi("1"))

try:
    db = client.Data
    collection = db.equityHistoricalData

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

    data = yf.download(tickers, start=start_date, interval="1mo")["Adj Close"]

    # data = pd.DataFrame(data_list)
    data.index = pd.to_datetime(data.index)
    # data.drop("_id", axis=1, inplace=True)
    # data = data.pivot(index="date", columns="ticker", values="adj_close")
    data.sort_index(inplace=True)
    data.columns = [i.replace(".NS", "") for i in data.columns]

    # Returns of the stock
    returns = data.pct_change().dropna()

    # Generate next 4 weekly dates
    next_dates = pd.date_range(start=returns.index[-1], periods=2, freq="MS")[1]

    # Dataframe to store the estimated returns
    forecasted_returns = pd.DataFrame()
    forecasted_returns["date"] = next_dates

    # Predicting the returns of the stock using Random Forest Regressor
    for ticker in returns.columns:
        lags = pd.DataFrame({"returns": returns[ticker]})
        for i in range(18, 0, -1):  # 1 to 18 months lag
            lags[i] = returns[ticker].shift(i)

        lags.dropna(inplace=True)

        X = lags.iloc[:, 1:]
        y = lags.iloc[:, 0]

        # train-test split
        X_train, X_test = X[:-3], X[-3:]
        y_train, y_test = y[:-3], y[-3:]

        # Feature selection using Recursive Feature Elimination and using Optuna to select the best number of features
        def objective(trial):
            n_estimators = trial.suggest_int("n_estimators", 10, 75)
            max_depth = trial.suggest_int("max_depth", 1, 20)
            n_features = trial.suggest_int("n_features", 1, 10)
            rfe = RFE(
                RandomForestRegressor(
                    n_estimators=n_estimators, max_depth=max_depth, random_state=1
                ),
                n_features_to_select=n_features,
            )
            fit = rfe.fit(X, y)

            return mean_absolute_error(y, fit.predict(X))

        study = optuna.create_study(direction="minimize")
        study.optimize(objective, n_trials=10)
        best_params = study.best_params

        # Getting the best features
        rfe = RFE(
            RandomForestRegressor(
                n_estimators=best_params["n_estimators"],
                max_depth=best_params["max_depth"],
                random_state=1,
            ),
            n_features_to_select=best_params["n_features"],
        )
        fit = rfe.fit(X, y)
        names = lags.columns[1:]
        columns = []
        for i in range(len(fit.support_)):
            if fit.support_[i]:
                columns.append(names[i])
        print("Columns with predictive power:", columns)  # best predictors

        # New dataframe for actual model
        df = pd.DataFrame()
        df["returns"] = returns[ticker]

        df = pd.concat(
            [
                df,
                pd.DataFrame(
                    {
                        "returns": [
                            0,
                        ]
                    },
                    index=[next_dates],
                ),
            ]
        )  # Adding null value for the next 1 month

        for i in columns:
            df["t_" + str(i)] = df["returns"].shift(i)

        df = df.dropna()

        X = df.iloc[:, 1:]
        y = df["returns"]

        # Random Forest Model
        mdl = RandomForestRegressor(n_estimators=100, random_state=1)
        mdl.fit(X[:-1], y[:-1])

        # Predicting the returns for the next 4 weeks
        mdl.predict(X[-1:])
        forecasted_returns[ticker] = mdl.predict(X[-1:])

    # forecasted_returns.set_index("date", inplace=True)
