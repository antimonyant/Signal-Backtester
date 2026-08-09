import helpers

# Inspect Data
tickers = "AAPL MSFT GOOG NVDA SPY VOO"
start_date = "2015-01-01"
end_date = "2026-01-01"

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
plot_signal = helpers.plot_signal(ma_signal, title="AAPL - MA Crossover Signal")

# Compute Mean Reversion Signal
mr_signal = helpers.get_mean_reversion_signal(data, "AAPL", 20, -1.0, 0.0)
plot_signal = helpers.plot_signal(mr_signal, title="AAPL - Mean Reversion Signal")