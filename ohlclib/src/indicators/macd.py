import pandas as pd
import talib
from yahoo_fin.stock_info import get_data


def macd(data: pd.DataFrame, fastperiod=12, slowperiod=26, signalperiod=9, column_name_prefix=None):
    """
    Calculate macd indicator
    :param data:
    :param fastperiod:
    :param slowperiod:
    :param signalperiod:
    :param column_name_prefix:
    :return: Tuple(macd, signal, hist)
    """
    column_macd = f'{column_name_prefix}_macd' if column_name_prefix is not None else 'macd'
    column_signal = f'{column_name_prefix}_macdsignal' if column_name_prefix is not None else 'macdsignal'
    column_hist = f'{column_name_prefix}_macdhist' if column_name_prefix is not None else 'macdhist'
    data[column_macd], data[column_signal], data[column_hist] = talib.MACD(
        data.close,
        fastperiod=fastperiod,
        slowperiod=slowperiod,
        signalperiod=signalperiod
    )


def macd_increasing(data: pd.DataFrame, count=2, keep_macd=True, column_name_prefix=None, fastperiod=12, slowperiod=26, signalperiod=9):
    """
    Calculate macd increasing or decreasing number of count consecutively.
    :param data:
    :param count:
    :param keep_macd:
    :param column_name_prefix:
    :param fastperiod:
    :param slowperiod:
    :param signalperiod:
    :return:
    If increasing consecutively for [count] bars, then return 1
    if decreasing consecutively for [count] bars, then return -1
    else return 0
    note：if count=2，then only possible return is 1 or -1.
    """
    _data = data.copy()
    _data['macd'], _, _ = talib.MACD(_data.close,
                                     fastperiod=fastperiod,
                                     slowperiod=slowperiod,
                                     signalperiod=signalperiod)

    def cal(ser):
        # suppose it is increasing
        result = 1

        # if there is 1 bar is not increasing, set result = 0
        for i in range(count - 1):
            if ser[i] > ser[i + 1]:
                result = 0

        # if result == 0, then check if it is keep decreasing
        if result == 0:
            result = -1
            for i in range(count - 1):
                if ser[i] < ser[i + 1]:
                    result = 0

        return result

    column_name = f"{column_name_prefix}_macd_increasing_{count}" \
        if column_name_prefix is not None else f"macd_increasing_{count}"

    if keep_macd:
        data["macd"] = _data["macd"]
    data[column_name] = _data.macd.rolling(window=count + 1, axis=0).apply(cal, raw=True).fillna(0).astype(int)


if __name__ == "__main__":
    pd.options.display.max_rows = 2000
    pd.options.display.max_columns = 200
    pd.set_option('max_colwidth', 120)
    pd.options.display.width = 2080

    data = get_data('tsla', interval="1d")
    hist_data = data.tail(300).copy()
    macd_increasing(data=hist_data, count=2)
    # macd(data=hist_data)

    print(hist_data)
