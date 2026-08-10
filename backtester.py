import helpers

# Inspect Data
tickers = "AAPL MSFT GOOG NVDA SPY VOO"
start_date = "2015-01-01"
end_date = "2026-01-01"
allow_plots = True

data = helpers.get_data(tickers, start_date, end_date)
print(data.head())
print(data.columns)
print(data['Close']['2020-01-01':'2020-12-31']['GOOG'])

# Compute daily returns on each ticker
returns = helpers.get_returns(data)
print(returns.head())
print(returns.describe())

# Compute Moving Average Signal
ma_signal = helpers.get_moving_average_signal(data, "AAPL", 20, 100)
#plot_signal = helpers.plot_signal(ma_signal, title="AAPL - MA Crossover Signal")

# Compute Mean Reversion Signal
mr_signal = helpers.get_mean_reversion_signal(data, "AAPL", 20, -1.0, 0.0)
#plot_signal = helpers.plot_signal(mr_signal, title="AAPL - Mean Reversion Signal")

# Backtest the signals
ma_strategy_returns = helpers.backtest_signal(ma_signal['Signal'], returns['AAPL'])
mr_strategy_returns = helpers.backtest_signal(mr_signal['Signal'], returns['AAPL'])

ma_cumulative_returns = helpers.get_cumulative_returns(ma_strategy_returns)
mr_cumulative_returns = helpers.get_cumulative_returns(mr_strategy_returns)
buyhold_cumulative_returns = helpers.get_cumulative_returns(returns['AAPL'])

helpers.plot_strategy_comparison({'Moving Average': ma_cumulative_returns, 'Mean Reversion': mr_cumulative_returns}, 
                                 buyhold_cumulative_returns, title="AAPL: Strategy Comparison")

# Run metrics to rank strategies
print("Moving Average Strategy:")
print(f"Sharpe Ratio: {helpers.sharpe_ratio(ma_strategy_returns)}")
print(f"Max Drawdown: {helpers.max_drawdown(ma_cumulative_returns)}")

print("\nMean Reversion Strategy:")
print(f"Sharpe Ratio: {helpers.sharpe_ratio(mr_strategy_returns)}")
print(f"Max Drawdown: {helpers.max_drawdown(mr_cumulative_returns)}")

print("\nBuy & Hold Strategy:")
print(f"Sharpe Ratio: {helpers.sharpe_ratio(returns['AAPL'])}")
print(f"Max Drawdown: {helpers.max_drawdown(buyhold_cumulative_returns)}")