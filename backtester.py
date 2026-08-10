import argparse
import helpers


def main():
    parser = argparse.ArgumentParser(description="Simple trading signal backtester")
    parser.add_argument('--tickers', default='AAPL MSFT GOOG SPY VOO',
                         help="Space-separated tickers, e.g. 'AAPL MSFT'")
    parser.add_argument('--start-date', default='2015-01-01')
    parser.add_argument('--end-date', default='2026-01-01')
    parser.add_argument('--mode', choices=['single', 'all'], default='single')
    parser.add_argument('--ticker', default='AAPL', help="Used only when --mode single")
    parser.add_argument('--strategy', choices=['ma', 'mr'], default='ma')
    parser.add_argument('--ma-short', type=int, default=20)
    parser.add_argument('--ma-long', type=int, default=100)
    parser.add_argument('--mr-window', type=int, default=20)
    parser.add_argument('--mr-entry', type=float, default=-1.0)
    parser.add_argument('--mr-exit', type=float, default=0.0)
    parser.add_argument('--plot', action='store_true', help="Show plots")

    args = parser.parse_args()

    data = helpers.get_data(args.tickers, args.start_date, args.end_date)

    if args.strategy == 'ma':
        signal_params = {'short': args.ma_short, 'long': args.ma_long}
    else:
        signal_params = {'window': args.mr_window, 'entry': args.mr_entry, 'exit': args.mr_exit}

    if args.mode == 'single':
        result = helpers.run_backtest(data, args.ticker, args.strategy, signal_params, plot=args.plot)
        for k, v in result.items():
            print(f"{k}: {v}")
    else:
        results_table = helpers.run_all(data, args.tickers.split(), args.strategy, signal_params, plot=args.plot)
        print(results_table.to_string(index=False))


if __name__ == '__main__':
    main()