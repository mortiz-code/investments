# usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "mcode"
__email__ = "matcode@pm.me"
__webpage__ = "https://github.com/mortiz-code"
__version__ = "1.1.0"
__copyright__ = "Copyright (c) 2021, all rights reserved."
__license__ = "BSD 3-Clause License."

import requests as req
import pandas as pd
import streamlit as st
import urllib3
from csv import reader
from os.path import isfile

urllib3.disable_warnings()

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Referer-Policy": "no-referrer-when-downgrade",
}


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
                    "moneda": "Moneda",
                    "fechaDevenganIntereses": "Devenga interes",
                }
            )
            df = df.set_index(["Emisor"])
            df = df.iloc[0]
            df["Devenga interes"] = pd.to_datetime(df["Devenga interes"]).date()
            df = df.dropna()
            return df
        except KeyError:
            st.warning("La ON no cuenta con informacion disponible.")
    else:
        st.warning(f"Especie no encontrada {symbol}.\nLlamar al banco y/o buscar código ISIN.")


def highlight_variation(val):
    if val > 0:
        return "color: green"
    elif val < 0:
        return "color: red"
    else:
        return ""


def format_data():
    response = get_data()
    if response.status_code == 200:
        df = pd.DataFrame(response.json())
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
        pd.options.display.float_format = "{:.2f}".format
        df = df.set_index(["Ticket"])
        df["Variacion"] = df["Variacion"] * 100
        (
            col1,
            col2,
            col3,
            col4,
            col5,
        ) = st.columns(5)
        df = options(df, col1, col2, col3, col4, col5)
        dfstyle = df.style.applymap(highlight_variation, subset=["Variacion"])
        st.dataframe(dfstyle, use_container_width=True)
        st.code(f'Cantidad de oblicaciones negociables disponibles: {df["Variacion"].count()}')
        st.markdown("---")
        (
            col1,
            col2,
        ) = st.columns(2)
        more_options(df, col1, col2)
    else:
        st.error(f"Error: {response.status_code}")


def more_options(df, col1, col2):
    with col2:
        agree = st.checkbox("Más info:")
        if agree:
            deepsearch(df, agree)
    with col1:
        agree = st.checkbox("Cartera.")
        if agree:
            cartera()


def get_data():
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
    response = req.post(URL, timeout=10, json=DATA, headers=HEADERS, stream=False, verify=False)
    return response


def options(df, col1, col2, col3, col4, col5):
    with col4:
        agree = st.checkbox("Mediano plazo")
        if agree:
            df = df.query("Vencimiento >= 600")
    with col5:
        agree = st.checkbox("Largo plazo")
        if agree:
            df = df.query("Vencimiento >= 1500")
    with col1:
        agree = st.checkbox("Ocultar inactivas.")
        if agree:
            df = df[df["Ultimo operado"] != 0]
    with col2:
        agree = st.checkbox("Pesos")
        if agree:
            df = df[df["Moneda"] == "ARS"]
    with col3:
        agree = st.checkbox("Dolares")
        if agree:
            df = df[df["Moneda"] == "USD"]

    return df


def deepsearch(df, agree):
    if agree:
        ticket = []
        for i in df.index:
            ticket.append(i)
        ticket = st.selectbox("", ticket)
        with st.spinner("In progress..."):
            df = get_detail(ticket)
            st.dataframe(df, use_container_width=True)


def cartera():
    file = "on.csv"
    if isfile(file):
        try:
            with open("on.csv", "r", encoding="utf-8") as file:
                data = reader(file)
                for i in data:
                    ticket = st.selectbox("ON en posesión:", i)
                    with st.spinner("In progress..."):
                        df = get_detail(ticket)
                        st.dataframe(df, use_container_width=True)
        except FileNotFoundError:
            st.error(f"File {file} not found.")
    else:
        st.error("CSV file not found.")


def main():
    format_data()


if __name__ == "__main__":
    main()
