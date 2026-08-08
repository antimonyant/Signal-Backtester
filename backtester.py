import yfinance as yf
import matplotlib.pyplot as plt

# Inspect Data
data = yf.download("AAPL MSFT GOOG NVDA SPY VOO", start="2015-01-01", end="2026-01-01")
print(data.head())
print(data.columns)
print(data['Close']['2020-01-01':'2020-12-31']['GOOG'])

# Plot to visualize
data['Close'].plot(figsize=(12, 6), title="Daily Close Prices")
plt.ylabel("Price ($)")
plt.xlabel("Date")
plt.show()

fig, axes = plt.subplots(2, 3, figsize=(12, 8))
tickers = ['AAPL', 'MSFT', 'GOOG', 'NVDA', 'SPY', 'VOO']
# zip pairs the lists together
for ax, ticker in zip(axes.flatten(), tickers):
    ax.plot(data['Close'][ticker])
    ax.set_title(ticker)
plt.tight_layout()
plt.show()

normalized = data['Close'] / data['Close'].iloc[0] * 100
normalized.plot(figsize=(12, 6), title="Normalized Price (start = 100)")
plt.yscale('log')
plt.show()

# Compute daily returns on each ticker
returns = data['Close'].pct_change()
print(returns.head())
print(returns.describe())

fig, axes = plt.subplots(2, 3, figsize=(12, 8), sharex=True)
for ax, ticker in zip(axes.flatten(), tickers):
    returns[ticker].hist(bins=100, ax=ax, range=(-0.2, 0.3))
    ax.set_title(ticker)
plt.tight_layout()
plt.show()