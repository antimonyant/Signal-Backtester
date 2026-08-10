import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

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


def get_moving_average_signal(data, ticker, short_window, long_window):
    """
    Computes short-term and long-term moving averages for a given ticker.

    Parameters:
    data (DataFrame): A pandas DataFrame containing historical stock data.
    ticker (str): The ticker symbol for which to compute moving averages.
    short_window (int): The window size for the short-term moving average.
    long_window (int): The window size for the long-term moving average.

    Returns:
    DataFrame with MA_short, MA_long, and signal (1 = long, 0 = flat) columns.
    """
    close = data['Close'][ticker]
    ma_short = close.rolling(short_window).mean()
    ma_long = close.rolling(long_window).mean()
    signal = (ma_short > ma_long).astype(int)

    return pd.DataFrame({
        'Close': close,
        'Short': ma_short,
        'Long': ma_long,
        'Signal': signal})


def get_mean_reversion_signal(data, ticker, window, entry_threshold, exit_threshold):
    """
    Computes a mean reversion signal for a given ticker.

    Parameters:
    data (DataFrame): A pandas DataFrame containing historical stock data.
    ticker (str): The ticker symbol for which to compute the mean reversion signal.
    window (int): The window size for the moving average.
    entry_threshold (float): The z-score threshold for entering a position.
    exit_threshold (float): The z-score threshold for exiting a position.

    Returns:
    DataFrame with Close, Z-score, and Signal columns.
    """
    close = data['Close'][ticker]
    rolling_mean = close.rolling(window).mean()
    rolling_std = close.rolling(window).std()
    z_score = (close - rolling_mean) / rolling_std

    signal = pd.Series(0, index=close.index)
    in_position = False
    for i in range(len(z_score)):
        if not in_position and z_score.iloc[i] < entry_threshold:
            in_position = True
        elif in_position and z_score.iloc[i] > exit_threshold:
            in_position = False
        signal.iloc[i] = 1 if in_position else 0

    return pd.DataFrame({
        'Close': close,
        'Z-Score': z_score,
        'Signal': signal})


def plot_signal(signal_df, title="Signal vs Price"):
    """
    Plots price with the long/flat signal shaded, for visual sanity-checking.

    Parameters:
    signal_df (DataFrame): must contain 'Close' and 'Signal' columns
                            (the output of get_ma_crossover_signal or get_mean_reversion_signal).
    title (str): plot title.

    Returns:
    No returns, shows the plot.
    """
    fig, ax = plt.subplots(figsize=(14, 6))

    ax.plot(signal_df.index, signal_df['Close'], label='Close Price', color='black', linewidth=1)

    # Shade the periods where signal == 1 (long)
    in_long = signal_df['Signal'] == 1
    ax.fill_between(signal_df.index, signal_df['Close'].min(), signal_df['Close'].max(),
                     where=in_long, color='green', alpha=0.15, label='Long')

    # Overlay MAs if given (MA crossover signal)
    if 'Short' in signal_df.columns:
        ax.plot(signal_df.index, signal_df['Short'], label='MA Short', color='blue', linewidth=1)
        ax.plot(signal_df.index, signal_df['Long'], label='MA Long', color='orange', linewidth=1)

    ax.set_title(title)
    ax.set_ylabel("Price ($)")
    ax.legend()
    plt.tight_layout()
    plt.show()


def plot_strategy_comparison(strategy_cumulative_dict, buyhold_cumulative, title="Strategy vs Buy & Hold"):
    """
    Plots one or more strategy cumulative return series against buy-and-hold.

    Parameters:
    strategy_cumulative_dict (dict): {label: cumulative_return_series}, e.g.
                                      {'MA Crossover': ma_cumulative, 'Mean Reversion': mr_cumulative}
    buyhold_cumulative (Series): buy-and-hold cumulative return series.
    title (str): plot title.

    Returns:
    No returns, shows the plot.
    """
    fig, ax = plt.subplots(figsize=(14, 6))

    for label, series in strategy_cumulative_dict.items():
        ax.plot(series.index, series, label=label, linewidth=1.5)

    ax.plot(buyhold_cumulative.index, buyhold_cumulative, label='Buy & Hold',
            color='black', linewidth=1.5, linestyle='--')

    ax.set_title(title)
    ax.set_ylabel("Cumulative Return (start = 1.0)")
    ax.set_xlabel("Date")
    ax.legend()
    plt.tight_layout()
    plt.show()


def backtest_signal(signal, returns):
    '''
    Backtests a trading signal against the returns of a stock.

    Parameters:
    signal (Series): A pandas Series containing the trading signal (1 = long, 0 = flat).
    returns (Series): A pandas Series containing the daily returns of the stock.

    Returns:
    Series: A pandas Series containing the strategy returns.
    '''
    signal_shifted = signal.shift(1).fillna(0)
    strategy_returns = signal_shifted * returns

    return strategy_returns

def sharpe_ratio(strategy_returns):
    """
    Computes the Sharpe ratio for a given strategy returns series.

    Parameters:
    strategy_returns (Series): A pandas Series containing the strategy returns.

    Returns:
    float: The Sharpe ratio of the strategy.
    """
    mean_return = strategy_returns.mean()
    std_return = strategy_returns.std()

    # Puts ratio into an annual perspective
    sharpe_ratio = mean_return / std_return * (252 ** 0.5)
    return sharpe_ratio


def max_drawdown(cumulative_returns):
    """
    Computes the maximum drawdown for a given cumulative returns series.

    Parameters:
    cumulative_returns (Series): A pandas Series containing the cumulative returns.

    Returns:
    float: The maximum drawdown of the strategy.
    """
    rolling_max = cumulative_returns.cummax()
    drawdown = (cumulative_returns - rolling_max) / rolling_max
    # Most negative is worst drawdown
    max_drawdown = drawdown.min()
    return max_drawdown


def evaluate_strategy(strategy_returns):
    """
    Evaluates a trading strategy by computing its Sharpe ratio and maximum drawdown.

    Parameters:
    strategy_returns (Series): A pandas Series containing the strategy returns.

    Returns:
    dict: A dictionary containing the Sharpe ratio and maximum drawdown.
    """
    cumulative_returns = get_cumulative_returns(strategy_returns)
    sharpe = sharpe_ratio(strategy_returns)
    max_dd = max_drawdown(cumulative_returns)

    return {
        'Sharpe Ratio': sharpe,
        'Max Drawdown': max_dd
    }


def run_backtest(data, ticker, signal_type, signal_params, plot=True):
    """
    Runs a full backtest pipeline for a single ticker and signal type.

    Parameters:
    data (DataFrame): historical stock data from get_data.
    ticker (str): ticker symbol to backtest.
    signal_type (str): 'ma' for moving average crossover, 'mr' for mean reversion.
    signal_params (dict): parameters for the chosen signal.
                           'ma' expects {'short': int, 'long': int}
                           'mr' expects {'window': int, 'entry': float, 'exit': float}
    plot (bool): whether to show signal and comparison plots.

    Returns:
    dict: performance metrics for the strategy vs buy-and-hold.
    """
    stock_returns = get_returns(data)[ticker]

    if signal_type == 'ma':
        signal_df = get_moving_average_signal(
            data, ticker, signal_params['short'], signal_params['long']
        )
    elif signal_type == 'mr':
        signal_df = get_mean_reversion_signal(
            data, ticker, signal_params['window'], signal_params['entry'], signal_params['exit']
        )
    else:
        raise ValueError(f"Unknown signal_type: {signal_type}")

    strategy_returns = backtest_signal(signal_df['Signal'], stock_returns)
    strategy_cumulative = get_cumulative_returns(strategy_returns)
    buyhold_cumulative = get_cumulative_returns(stock_returns)

    metrics = {
        'ticker': ticker,
        'strategy': signal_type,
        'strategy_sharpe': sharpe_ratio(strategy_returns),
        'buyhold_sharpe': sharpe_ratio(stock_returns),
        'strategy_max_dd': max_drawdown(strategy_cumulative),
        'buyhold_max_dd': max_drawdown(buyhold_cumulative),
        'strategy_total_return': strategy_cumulative.iloc[-1] - 1,
        'buyhold_total_return': buyhold_cumulative.iloc[-1] - 1
    }

    if plot:
        plot_signal(signal_df, title=f"{ticker} - {signal_type.upper()} Signal")
        plot_strategy_comparison(
            {signal_type.upper(): strategy_cumulative},
            buyhold_cumulative,
            title=f"{ticker}: Strategy vs Buy & Hold"
        )

    return metrics


def run_all(data, tickers, signal_type, signal_params, plot=False):
    """
    Runs run_backtest across a list of tickers and returns a results table.

    Parameters:
    data (DataFrame): historical stock data from get_data.
    tickers (list): list of ticker symbols.
    signal_type (str): 'ma' or 'mr'.
    signal_params (dict): parameters for the chosen signal (see run_backtest).
    plot (bool): whether to show plots for each ticker (off by default — noisy in bulk mode).

    Returns:
    DataFrame: one row per ticker with performance metrics.
    """
    results = []
    for ticker in tickers:
        result = run_backtest(data, ticker, signal_type, signal_params, plot=plot)
        results.append(result)
    return pd.DataFrame(results)