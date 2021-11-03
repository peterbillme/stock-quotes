import os
import pathlib

from yahoo_fin.stock_info import get_data, tickers_sp500
import pandas as pd

from ohlclib.src.indicators.ema import ema_in_order, ema
from ohlclib.src.patterns.engulfing import engulfing
from ohlclib.src.patterns.hammer import hammer
from ohlclib.src.patterns.morning_evening_star import morning_evening_star


def get_pickle_file_name(symbol, interval):
    _script_folder = pathlib.Path().absolute()
    _pickle_folder = os.path.join(_script_folder, "pickle", "quotes")
    os.makedirs(_pickle_folder, exist_ok=True)
    _pickle_file = os.path.join(_pickle_folder, f"{symbol}_{interval}.pkl")

    return _pickle_file


def load_quotes(symbol, interval):
    df = pd.read_pickle(get_pickle_file_name(symbol, interval))
    return df


def update_quotes_pickle(symbol, interval):
    hist_data = get_data(symbol, interval=interval)
    hist_data["adj_ratio"] = hist_data["adjclose"] / hist_data["close"]
    hist_data["adjopen"] = hist_data["open"] * hist_data["adj_ratio"]
    hist_data["adjhigh"] = hist_data["high"] * hist_data["adj_ratio"]
    hist_data["adjlow"] = hist_data["low"] * hist_data["adj_ratio"]

    df: pd.DataFrame = hist_data[
        ['ticker', 'open', 'high', 'low', 'close', 'adjopen', 'adjhigh', 'adjlow', 'adjclose', 'volume']]
    # target_path =
    df.to_pickle(get_pickle_file_name(symbol, interval))


def update_quotes_spx500():
    spx500_tickers = tickers_sp500(True)
    num_total = spx500_tickers.shape[0]
    i = 1
    for row in spx500_tickers.itertuples():
        print(f"Updating {row.Symbol}({i}/{num_total}) ...")
        update_quotes_pickle(row.Symbol, '1d')
        print("Interval 1d done.")
        update_quotes_pickle(row.Symbol, '1wk')
        print("Interval 1wk done.")
        print("**** All Done! ****\n")
        i += 1


if __name__ == '__main__':
    pd.options.display.max_rows = 200
    pd.options.display.max_columns = 200
    pd.set_option('max_colwidth', 120)
    pd.options.display.width = 2080

    # update_quotes_spx500()

    # df = load_quotes('MMM', '1d')

    spx500_tickers = tickers_sp500(True)
    num_total = spx500_tickers.shape[0]
    i = 1
    for row in spx500_tickers.itertuples():
        # print(f"{i}: {row.Symbol}")
        df = load_quotes(row.Symbol, "1d").tail(800).copy()
        i += 1

        ema_in_order(data=df, periods=[60, 120, 338])
        ema(data=df, periods=[21])
        engulfing(data=df)
        hammer(data=df)
        morning_evening_star(data=df)
        last_row = df.iloc[-1]
        second_last_row = df.iloc[-2]
        if last_row.ema_in_order and last_row.ema_60_close > last_row.close > last_row.ema_120_close and last_row.close > second_last_row.close:
            print(f"{row.Symbol}: Got it!")


