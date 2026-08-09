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