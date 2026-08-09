import yfinance as yf
import matplotlib.pyplot as plt

def get_data(tickers, start_date, end_date):
    """
    Fetches historical stock data for the given tickers and date range.

    Parameters:
    tickers (str): A string of ticker symbols separated by spaces.
    start_date (str): The start date in 'YYYY-MM-DD' format.
    end_date (str): The end date in 'YYYY-MM-DD' format.

    Returns:
    DataFrame: A pandas DataFrame containing the historical stock data.
    """
    data = yf.download(tickers, start=start_date, end=end_date)
    return data


def get_returns(data):
    """
    Computes daily returns for the given stock data.

    Parameters:
    data (DataFrame): A pandas DataFrame containing historical stock data.

    Returns:
    DataFrame: A pandas DataFrame containing daily returns.
    """
    returns = data['Close'].pct_change()
    return returns


def get_cumulative_returns(returns):
    """
    Computes cumulative returns from daily returns.

    Parameters:
    returns (DataFrame): A pandas DataFrame containing daily returns.

    Returns:
    DataFrame: A pandas DataFrame containing cumulative returns.
    """
    cumulative_returns = (1 + returns).cumprod()
    return cumulative_returns


def visualizations(data, tickers):
    """
    Shows plots for given data

    Parameters:
    data (DataFrame): A pandas DataFrame containing historical stock data.
    tickers (list): A list of ticker symbols.

    Returns:
    No returns, but shows plots for the given data.
    """
        
    # All plots
    data['Close'].plot(figsize=(12, 6), title="Daily Close Prices")
    plt.ylabel("Price ($)")
    plt.xlabel("Date")
    plt.show()

    # Individual plots
    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    # zip pairs the lists together
    for ax, ticker in zip(axes.flatten(), tickers):
        ax.plot(data['Close'][ticker])
        ax.set_title(ticker)
    plt.tight_layout()
    plt.show()

    # Normalized log plot
    normalized = data['Close'] / data['Close'].iloc[0] * 100
    normalized.plot(figsize=(12, 6), title="Normalized Price (start = 100)")
    plt.yscale('log')
    plt.show()

    # Daily returns histogram plots
    returns = data['Close'].pct_change()
    fig, axes = plt.subplots(2, 3, figsize=(12, 8), sharex=True)
    for ax, ticker in zip(axes.flatten(), tickers):
        returns[ticker].hist(bins=100, ax=ax, range=(-0.2, 0.3))
        ax.set_title(ticker)
    plt.tight_layout()
    plt.show()