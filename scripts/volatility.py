import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

class volatility():
    """
    Calculates the volatility.
    """
    
    @staticmethod
    def returns(data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate returns and log returns.
        """
        data = data.copy()
        for column in data.columns:
            assert not data[column].isnull().values.any(), f"Column '{column}' contains NaN values."
            data[column+'_returns'] = data[column].pct_change()
            data[column+'_log_returns'] = np.log(data[column]).diff()
            data.drop(column, axis=1, inplace=True)
        
        return data

    @staticmethod
    def standard_deviation(data: pd.DataFrame, annual: bool = False, time: int = 252) -> pd.DataFrame:
        """
        Calculate standard deviation.

        :param data: DataFrame of all stocks
        :param annual: If True, returns annualized standard deviation
        """
        # Apply the returns calculation
        data = volatility.returns(data)

        # Create a list to hold the standard deviation results
        results = []

        # Iterate through columns to calculate standard deviations
        for column in data.columns:
            if '_log_returns' in column:
                stock_name = column.replace('_log_returns', '')
                std_dev = data[column].std()
                # Find if stock already exists in the results
                for item in results:
                    if item['Stock'] == stock_name:
                        item['Log Returns'] = std_dev
                        break
                else:
                    results.append({'Stock': stock_name, 'Returns': np.nan, 'Log Returns': std_dev})
            elif '_returns' in column:
                stock_name = column.replace('_returns', '')
                std_dev = data[column].std()
                results.append({'Stock': stock_name, 'Returns': std_dev, 'Log Returns': np.nan})

        # Convert results list to DataFrame
        std_devs_df = pd.DataFrame(results)

        # If annualization is required, adjust the standard deviation
        if annual:
            std_devs_df['Returns'] *= np.sqrt(time)
            std_devs_df['Log Returns'] *= np.sqrt(time)

        # Set index for better readability
        std_devs_df = std_devs_df.set_index('Stock')

        return std_devs_df


    @staticmethod
    def historical_volatility(data: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        """
        Calculate historical volatility.
        
        :param data: DataFrame of all stocks
        :param window: Number of periods for calculating volatility
        """
        output = pd.DataFrame()
        data = volatility.returns(data)
        
        for column in data.columns:
            if(not column.endswith('_log_returns')):
                data.drop(column, axis=1, inplace=True)
            else:
                output[column] = data[column].rolling(window).std()
        
        return output

    @staticmethod
    def beta(data: pd.DataFrame, market_returns: pd.Series) -> pd.DataFrame:
        """
        Calculate beta for multiple stocks.

        :param data: DataFrame with stocks' log returns
        :param market_returns: Series with market returns
        :return: DataFrame with beta values for each stock
        """
        data = volatility.returns(data)
        
        result = []
        for column in data.columns:
            if '_log_returns' in column:
                stock_returns = data[column]
                beta_value = stock_returns.cov(market_returns) / market_returns.var()
                result.append({'Stock': column.replace('_log_returns', ''), 'Beta': beta_value})
        
        return pd.DataFrame(result).set_index('Stock')
    
    def __black_scholes_price(S, K, T, r, q, sigma, option_type: str = 'call'):
        """
        Calculate Black-Scholes option prices for given parameters.
        """
        d1 = (np.log(S / K) + (r - q + sigma**2 / 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)

        if option_type.lower() == 'call':
            option_price = S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
            vega = S * np.exp(-q * T) * norm.pdf(d1) * np.sqrt(T)
        elif option_type.lower() == 'put':
            option_price = K * np.exp(-r * T) * norm.cdf(-d2) - S * np.exp(-q * T) * norm.cdf(-d1)
            vega = -S * np.exp(-q * T) * norm.pdf(d1) * np.sqrt(T)
        
        return option_price, vega

    @staticmethod
    def implied_volatility(data: pd.DataFrame, iteration: int = 200, init_sigma: float = 0.1, tolerance: float = 0.00001, option_type: str = 'call') -> pd.DataFrame:
        """
        Calculate implied volatility for options data.
        
        The DataFrame `data` should have the following columns:
        - 'S': Current stock price
        - 'K': Strike price
        - 'T': Time to expiration in years
        - 'r': Risk-free interest rate (annualized)
        - 'q': Dividend yield
        - 'market_price': Current market price of the option
        
        :param data: DataFrame with the required columns
        :param iteration: Maximum number of iterations
        :param init_sigma: Initial guess for volatility
        :param tolerance: Tolerance level for convergence
        :param option_type: 'call' or 'put' option type
        """

        def newton_raphson(S, K, T, r, q, price, option_type, tolerance, iteration, init_sigma):
            for _ in range(iteration):
                option_price, vega = volatility.__black_scholes_price(S, K, T, r, q, init_sigma, option_type)
                C = option_price - price
                if vega == 0:
                    raise ValueError("Vega is zero, which can lead to division by zero.")

                new_sigma = init_sigma - C / vega
                
                if abs(init_sigma - new_sigma) < tolerance or abs(option_price - Price) < tolerance:
                    break
                vol = vol_new
    
            return vol

        output = pd.DataFrame()
        
        for index, row in data.iterrows():
            S = row['S']
            K = row['K']
            T = row['T']
            r = row['r']
            q = row['q']
            market_price = row['market_price']

            implied_vol = newton_raphson(S, K, T, r, q, market_price, option_type, tolerance, iteration, init_sigma)
            output.at[index, 'implied_volatility'] = implied_vol

        return output

    @staticmethod
    def average_true_range(data: pd.DataFrame, window: int = 14) -> pd.DataFrame:
        """
        Calculate average true range (ATR) over a specified window.
        
        The DataFrame `data` should have the following columns:
        - 'High': High prices
        - 'Low': Low prices
        - 'Close': Previous close prices
        
        :param data: DataFrame with the required columns
        :param window: Number of periods for calculating ATR
        """
        output = pd.DataFrame()

        data = data.copy()  # Avoid modifying the original DataFrame
        data['prev_close'] = data['Close'].shift(1)
        data['TR'] = np.maximum(data['High'] - data['Low'],
                                np.abs(data['High'] - data['prev_close']),
                                np.abs(data['Low'] - data['prev_close']))
        data['ATR'] = data['TR'].rolling(window=window).mean()
        return data[['ATR']].dropna()

    @staticmethod
    def max_drawdown(data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate maximum drawdown.
        
        The DataFrame `data` should have Close prices.
        
        :param data: DataFrame with the required column
        """
        max_drawdowns = pd.DataFrame(columns=['Max_Drawdown'])

        for stock in data.columns:
            df = pd.DataFrame()
            df['Close'] = data[stock]
        
            df['cum_max'] = df['Close'].cummax()
        
            df['drawdown'] = (df['Close'] - df['cum_max']) / df['cum_max']
        
            max_drawdown = df['drawdown'].min()
            max_drawdowns.loc[stock] = [max_drawdown]
    
        return max_drawdowns