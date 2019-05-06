import datetime
import json
import re
import jdatetime
import pandas as pd
import requests

from database import Database


def get_price_history(start_date=None, end_date=None, from_cache=False):
    t = ""
    if from_cache:
        t = _get_gold_history_row_data_offline()
    else:
        t = _get_gold_history_row_data_online()

    data = json.loads(t)
    df = pd.DataFrame(data, columns=["Open", "Lowest", "Highest", "Close", "EnDate", "FaDate", "FaDate2"])
    df.drop(columns=["FaDate2"], inplace=True)
    df["EnDate"] = pd.to_datetime(df["EnDate"], format="%Y/%m/%d")
    df["Close"] = df["Close"].apply(lambda price: re.search("\d+", price.replace(",", "")).group(0))
    df["Open"] = df["Open"].apply(lambda price: price.replace(",", ""))
    df["Lowest"] = df["Lowest"].apply(lambda price:  price.replace(",", ""))
    df["Highest"] = df["Highest"].apply(lambda price: price.replace(",", ""))
    df.set_index("EnDate", inplace=True)
    df.sort_index(ascending=True, inplace=True)
    if start_date:
        try:

            start_date = jdatetime.datetime.strptime(start_date, '%Y-%m-%d').togregorian()

            if end_date:
                end_date = jdatetime.datetime.strptime(end_date, '%Y-%m-%d').togregorian()
            else:
                end_date = datetime.datetime.now()

            df = df.loc[start_date:end_date]
        except Exception as ex:
            print(ex)
    return df


def _get_gold_history_row_data_online():
    d = requests.request("GET", "http://www.tgju.org/chart-summary-ajax/mesghal", timeout=40)
    t = d.text
    return t


def _get_gold_history_row_data_offline():
    db = Database()
    h = db.get_history(id)
    if h:
        return h.history
    return h


if __name__ == "__main__":
    df = get_price_history()
    print(df)
