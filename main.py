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

urllib3.disable_warnings()

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Referer-Policy": "no-referrer-when-downgrade",
}


def test_details(symbol):
    st.code(f" {symbol} ".center(80, "-"))


def get_detail(symbol):
    DATA = {"symbol": symbol, "Content-Type": "application/json"}
    URL = "https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free/bnown/fichatecnica/especies/general"
    r = req.post(URL, timeout=10, json=DATA, headers=HEADERS, verify=False)
    # st.code(f" {symbol} ".center(80, "-"))
    if r.status_code == 200:
        try:
            df = pd.DataFrame(r.json()["data"])
            df = df.loc[
                :,
                [
                    "emisor",
                    "interes",
                    "denominacionMinima",
                    "formaAmortizacion",
                    "paisLey",
                    "default",
                    "fechaDevenganIntereses",
                    "moneda",
                ],
            ]
            df = df.rename(
                columns={
                    "emisor": "Emisor",
                    "denominacionMinima": "Lamina",
                    "formaAmortizacion": "Amortizacion",
                    "paisLey": "Ley",
                    "fechaDevenganIntereses": "Devenga interes",
                }
            )
            df = df.set_index(["Emisor"])
            df = df.iloc[0]
            df["Devenga interes"] = pd.to_datetime(df["Devenga interes"]).date()
            return df
        except KeyError:
            st.warning(f"La ON no cuenta con informacion disponible.")
    else:
        st.error(f"Error: {r.status_code}")


def highlight_variation(val):
    if val > 0:
        return "color: green"
    elif val < 0:
        return "color: red"
    else:
        return ""


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
        df = df.rename(
            columns={
                "symbol": "Ticket",
                "denominationCcy": "Moneda",
                "daysToMaturity": "Vencimiento",
                "settlementPrice": "Ultimo operado",
                "imbalance": "Variacion",
            }
        )
        pd.options.display.float_format = "{:,0f}".format
        df = df.set_index(["Ticket"])
        df["Variacion"] = df["Variacion"] * 100
        agree = st.checkbox("Mayores a 2 años.")
        if agree:
            df = df.query("Vencimiento >= 365")
            # df["Vencimiento"] = df["Vencimiento"] / 365
        dfstyle = df.style.applymap(highlight_variation, subset=["Variacion"])
        st.dataframe(dfstyle, use_container_width=True)
        # st.markdown("""---""")
        agree = st.checkbox("Más info:")
        deepsearch(df, agree)
    else:
        st.error(f"Error: {r.status_code}")


def deepsearch(df, agree):
    if agree:
        ticket = []
        for i in df.index:
            ticket.append(i)
        ticket = st.selectbox("", ticket)
        with st.spinner("In progress..."):
            df = get_detail(ticket)
            st.dataframe(df, use_container_width=True)


def main():
    on()


if __name__ == "__main__":
    main()
