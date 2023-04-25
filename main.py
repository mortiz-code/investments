# usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Matias Ortiz"
__email__ = "matias.ortiz@bvstv.com"
__webpage__ = "https://github.com/mortiz-code"
__version__ = "1.1.0"
__copyright__ = "Copyright (c) 2021, all rights reserved."
__license__ = "BSD 3-Clause License."

import requests as req
import pandas as pd
import streamlit as st
import urllib3
from ratelimit import limits, sleep_and_retry

urllib3.disable_warnings()

# URL = "https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free/market-time"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Referer-Policy": "no-referrer-when-downgrade",
}


def test_details(symbol):
    st.code(f" {symbol} ".center(80, "-"))


@sleep_and_retry
@limits(calls=10, period=30)
def details(symbol):
    DATA = {"symbol": symbol, "Content-Type": "application/json"}
    URL = "https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free/bnown/fichatecnica/especies/general"
    r = req.post(URL, timeout=10, json=DATA, headers=HEADERS, stream=False, verify=False)
    # st.json(r.json()["data"][0])  # Json crudo
    st.code(f" {symbol} ".center(80, "-"))
    if r.status_code == 200:
        df = pd.DataFrame(r.json()["data"])
        df = df.loc[
            :,
            [
                "emisor",
                "moneda",
                "interes",
                "denominacionMinima",
                "formaAmortizacion",
                "paisLey",
                "default",
                "fechaDevenganIntereses",
            ],
        ]
        df = df.iloc[0]
        st.dataframe(df, use_container_width=True)
    else:
        st.error(f"Error: {r.status_code}")


def on():
    DATA = {
        "excludeZeroPFAndQty": True,
        "T2": True,
        "T1": False,
        "T0": False,
        "Content-Type": "application/json",
    }
    URL = (
        "https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free/negociable-obligations"
    )
    r = req.post(URL, timeout=10, json=DATA, headers=HEADERS, stream=False, verify=False)
    if r.status_code == 200:
        df = pd.DataFrame(r.json())
        df = df.loc[
            :, ["symbol", "denominationCcy", "daysToMaturity", "settlementPrice", "imbalance"]
        ]
        # for i in range(5): # Test las primeros 5 ON
        #     details(df.symbol.iloc[i])
        st.dataframe(df, use_container_width=True)
        with st.spinner("In progress..."):
            for i in df.symbol:
                details(i)
    else:
        st.error(f"Error: {r.status_code}")


def main():
    on()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        exit()
