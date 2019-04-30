import sys
from io import StringIO
import requests
import pandas as pd
import os.path
from os import path


def get_namad_history_by_id(id,start_date = None):
    d = requests.request("GET", "http://cdn.tsetmc.com/tsev2/data/InstTradeHistory.aspx?i={}&Top=999999&A=1".format(id),
                         timeout=40)
    d = StringIO(d.text.replace(";", "\n"))
    df = pd.read_csv(d, sep="@")
    df.columns = ["Date", "PriceMax", "PriceMin", "ClosePrice", "LastPrice", "PriceFirst", "PriceYesterday", "Value",
                  "VolumeTrade", "NumberTrade"]
    df["GDATE"] = pd.DatetimeIndex(pd.to_datetime(df["Date"], format="%Y%m%d"))
    return df

def get_namad_history_by_name(namad,start_date = None):
    id = _get_namad_id_by_name(namad)
    return get_namad_history_by_id(id,start_date)

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
    return df



if __name__ == "__main__":
 pass
