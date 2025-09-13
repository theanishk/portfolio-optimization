import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Data for forecasted returns
forecast_data = {
    "forecast_date": [
        "03/07/23",
        "10/07/23",
        "17/07/23",
        "24/07/23",
        "10/07/23",
        "17/07/23",
        "24/07/23",
        "31/07/23",
        "17/07/23",
        "24/07/23",
        "31/07/23",
        "07/08/23",
        "24/07/23",
        "31/07/23",
        "07/08/23",
        "14/08/23",
        "31/07/23",
        "07/08/23",
        "14/08/23",
        "21/08/23",
        "07/08/23",
        "14/08/23",
        "21/08/23",
        "28/08/23",
        "14/08/23",
        "21/08/23",
        "28/08/23",
        "04/09/23",
        "21/08/23",
        "28/08/23",
        "04/09/23",
        "11/09/23",
        "28/08/23",
        "04/09/23",
        "11/09/23",
        "18/09/23",
        "04/09/23",
        "11/09/23",
        "18/09/23",
        "25/09/23",
        "11/09/23",
        "18/09/23",
        "25/09/23",
        "02/10/23",
        "18/09/23",
        "25/09/23",
        "02/10/23",
        "09/10/23",
        "25/09/23",
        "02/10/23",
        "09/10/23",
        "16/10/23",
        "02/10/23",
        "09/10/23",
        "16/10/23",
        "23/10/23",
        "09/10/23",
        "16/10/23",
        "23/10/23",
        "30/10/23",
        "16/10/23",
        "23/10/23",
        "30/10/23",
        "06/11/23",
    ],
    "forecasted_return": [
        0.000520382,
        -0.010664386,
        0.006367976,
        -0.010120362,
        -0.004728346,
        0.000365971,
        -0.004756068,
        -0.004268708,
        0.012973972,
        -0.01277862,
        -0.006617191,
        -0.000964498,
        -0.014608392,
        -0.005832697,
        -0.003221909,
        0.001105414,
        -0.00179148,
        0.000955688,
        -5.90e-05,
        0.017972678,
        -0.003438663,
        -0.001039039,
        -0.010540142,
        -0.006637615,
        0.002539099,
        0.000410818,
        -0.008477157,
        0.002850226,
        0.002210589,
        -0.004864472,
        0.012427707,
        0.014443239,
        -0.006103662,
        0.005630043,
        -0.001358278,
        -0.00835584,
        0.001653221,
        -0.01080091,
        -0.00472777,
        0.011866902,
        -0.006121802,
        -0.009617677,
        0.008885219,
        0.011097339,
        -0.002286834,
        0.00980681,
        0.010335655,
        0.006824806,
        0.001152506,
        0.00855808,
        0.006256186,
        0.010701695,
        0.001209341,
        0.005675631,
        -0.003100684,
        -0.001438254,
        0.00688495,
        0.000209735,
        0.003584439,
        0.005859266,
        0.009585805,
        -0.000901889,
        0.010078213,
        0.002759083,
    ],
}

# Convert to DataFrame and set 'forecast_date' as datetime
forecast_data = pd.DataFrame(forecast_data)
forecast_data["forecast_date"] = pd.to_datetime(
    forecast_data["forecast_date"], format="%d/%m/%y"
)
forecast_data = forecast_data.set_index("forecast_date")


# Download actual ITC data from Yahoo Finance
ticker = "ITC.NS"
start_date = "2023-07-03"
end_date = "2023-11-06"
data = yf.download(ticker, start=start_date, end=end_date)

# Calculate actual daily returns
data["actual_return"] = data["Adj Close"].pct_change()

# Resample actual returns to match forecast dates (weekly returns)
actual_returns_resampled = data["actual_return"].resample("7D").sum()

# Match the forecasted dates with actual returns
# If a forecasted date doesn't match an actual date exactly, use the nearest date available
comparison_df = pd.DataFrame(
    {
        "forecast_date": forecast_data.index,
        "forecasted_return": forecast_data["forecasted_return"],
        "actual_return": actual_returns_resampled.loc[
            actual_returns_resampled.index.isin(forecast_data.index)
        ].values,
    }
)

plt.plot(
    forecast_data["forecast_date"],
    forecast_data["forecasted_return"],
    label="Forecasted Return",
    color="blue",
    marker="o",
)
# Plot actual vs forecasted returns
plt.figure(figsize=(14, 7))
plt.plot(
    comparison_df["forecast_date"],
    comparison_df["forecasted_return"],
    label="Forecasted Return",
    color="blue",
    marker="o",
)
plt.plot(
    comparison_df["forecast_date"],
    comparison_df["actual_return"],
    label="Actual Return",
    color="red",
    marker="x",
)
plt.title(f"Actual vs Forecasted Returns for {ticker}")
plt.xlabel("Date")
plt.ylabel("Return")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
