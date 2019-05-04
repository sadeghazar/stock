import datetime
import sys
from io import StringIO
import requests
import pandas as pd
import os.path
from os import path

from database import Database
from model import TblHistory
import jdatetime


def get_namad_history_by_id(id, start_date=None, end_date=None, from_cache=False):
    t = ""
    if from_cache:
        t = _get_namad_history_row_data_offline(id)
    else:
        t = _get_namad_history_row_data_online(id)
    d = StringIO(t)
    df = pd.read_csv(d, sep="@")
    df.columns = ["Date", "PriceMax", "PriceMin", "ClosePrice", "LastPrice", "PriceFirst", "PriceYesterday", "Value",
                  "VolumeTrade", "NumberTrade"]
    df["GDATE"] = pd.DatetimeIndex(pd.to_datetime(df["Date"], format="%Y%m%d"))
    df.set_index("GDATE", inplace=True)
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


def _get_namad_history_row_data_online(id):
    d = requests.request("GET", "http://cdn.tsetmc.com/tsev2/data/InstTradeHistory.aspx?i={}&Top=999999&A=1".format(id),
                         timeout=40)
    t = d.text.replace(";", "\n")
    return t


def _get_namad_history_row_data_offline(id):
    db = Database()
    h = db.get_history(id)
    if h:
        return h.history
    return h


def get_market_index(start_date=None, end_date=None):
    d = requests.request("GET", "http://www.tsetmc.com/tsev2/chart/data/Index.aspx?i=32097828799138957&t=value",
                         timeout=40, stream=True)
    t = d.text.replace(";", "\n")
    d = StringIO(t)
    df = pd.read_csv(d, sep=",")
    df.columns = ["Date", "Value"]
    df["GDate"] = df["Date"].apply(lambda date: jdatetime.datetime.strptime(date, '%Y/%m/%d').togregorian())
    df.set_index("GDate", inplace=True)
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


def get_namad_history_by_name(namad, start_date=None, end_date=None, from_cache=False):
    if namad == "index":
        return get_market_index(start_date=None, end_date=None)
    else:
        id = int(_get_namad_id_by_name(namad))
        return get_namad_history_by_id(id, start_date, end_date, from_cache)


def _get_namad_id_by_name(name):
    id = get_namad_list(sync=False)[["ID", "NAMAD"]].set_index("NAMAD").loc[name]["ID"]
    return id


def get_namad_list(sync=False):
    exist = path.exists("./Namads.csv")
    if sync == True or not exist:
        df = _request_namad()
        df.to_csv("./Namads.csv")
        return df
    else:
        return pd.read_csv("./Namads.csv")


def _request_namad():
    r = requests.request("GET", "http://www.fipiran.com/IndexDetails/IndexInstrument?Lval30=32097828799138957",
                         timeout=400, stream=True)
    t = r.text.replace(";", "\n")
    d = StringIO(t)
    df1 = pd.read_html(d)[0]
    df1.columns = ["NAMAD", "last_price", "changes_last_price", "end_price", "changes_end_price", "count", "volume",
                  "value"]
    df1.drop(inplace=True,columns=["last_price", "changes_last_price", "end_price", "changes_end_price", "count", "volume","value"])
    df1.set_index("NAMAD",inplace=True)
    r = requests.request("GET", "http://cdn.tsetmc.com/tsev2/data/MarketWatchInit.aspx?h=0&r=0", timeout=400,
                         stream=True)
    text = r.text.split("@")[2]
    text = text.replace(";", "\n")
    d = StringIO(text)
    df = pd.read_csv(d, sep=",")
    df.columns = ["ID", "ID2", "NAMAD", "DESC", "UN1", "firstprice", "lastprice", "akharinmoamele", "count", "VOLUME",
                  "arzesh", "minprice", "maxprice", "yesterday", "eps", "UN2", "UN3", "tedadekharid", "CAT", "max2",
                  "min2", "UN4", "TYPE"]
    df = df.drop(
        columns=["firstprice", "lastprice", "akharinmoamele", "count", "arzesh", "minprice", "maxprice",
                 "yesterday", "eps", "tedadekharid", "max2", "min2"])
    df.set_index("NAMAD",inplace=True)


    df = df1.join(df)
    df = df[df.ID.notnull()]
    # df = df.dropna()
    return df


def update_namads():
    db = Database()
    lst = get_namad_list(True)
    count = len(lst.values)
    couter = 0
    for n in lst.values:
        try:
            couter += 1
            id = n[0]
            name = n[2]
            history = _get_namad_history_row_data_online(id)
            last_update = datetime.datetime.now()

            h = TblHistory(namad_name=name, namad_id=id,
                           history=history, last_update=last_update, category=n[8])
            db.insert_or_update(h)
            print("-" * 100)
            print("{} of {}".format(couter, count))
            print("{}".format(name))
            print("-" * 100)
        except Exception as ex:
            print(n)


if __name__ == "__main__":
    df = _request_namad()
    print(df)
    # mindex = get_market_index('1390-1-1', '1398-8-1')
    # pass
    # print(mindex)
    # # d = get_namad_history_by_name('جكانه806', start_date='1390-1-1', from_cache=True)
    # # pass
    # # update_namads()
    # # d = get_namad_history_by_id(46982154647719707, from_cache=True, start_date='1390-1-1')
