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
from dotenv import load_dotenv
from os import getenv
from datetime import date, datetime

urllib3.disable_warnings()

load_dotenv()

TOKEN = getenv("TOKEN")

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Referer-Policy": "no-referrer-when-downgrade",
}


def get_detail(symbol):
    DATA = {"symbol": symbol, "Content-Type": "application/json"}
    URL = "https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free/bnown/fichatecnica/especies/general"
    r = req.post(URL, timeout=10, json=DATA, headers=HEADERS, verify=False)
    if r.status_code == 200:
        try:
            return format_response(r)
        except KeyError:
            st.warning("La ON no cuenta con informacion disponible.")
    else:
        st.warning(f"Especie no encontrada {symbol}.\nLlamar al banco y/o buscar código ISIN.")


def format_response(r):
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
            "fechaVencimiento",
            "moneda",
        ],
    ]
    df = df.rename(
        columns={
            "emisor": "Emisor",
            "denominacionMinima": "Lamina",
            "paisLey": "Ley",
            "moneda": "Moneda",
            "formaAmortizacion": "Amortizacion",
            "fechaVencimiento": "Vencimiento",
            "fechaDevenganIntereses": "Devenga interes",
        }
    )
    df = df.set_index(["Emisor"])
    df = df.iloc[0]
    df["Devenga interes"] = pd.to_datetime(df["Devenga interes"]).date()
    df["Vencimiento"] = pd.to_datetime(df["Vencimiento"]).date()
    df = df.dropna()
    return df


def highlight_variation(val):
    if val > 0:
        return "color: green"
    elif val < 0:
        return "color: red"
    else:
        return ""


def byma():
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
            col6,
        ) = st.columns(6)
        df = options(df, col1, col2, col3, col4, col5, col6)
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
        if agree := st.checkbox("Más info:"):
            deepsearch(df, agree)
    with col1:
        if agree := st.checkbox("Cartera."):
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
    return req.post(URL, timeout=10, json=DATA, headers=HEADERS, stream=False, verify=False)


def bcra_usd():
    HEADER = {"Authorization": f"BEARER {TOKEN}"}
    URL = "https://api.estadisticasbcra.com/usd"
    r = req.get(URL, timeout=3, headers=HEADER)
    return r.json()[-1]["v"]


def options(df, col1, col2, col3, col4, col5, col6):
    with st.expander("Opciones"):
        with col1:
            if agree := st.checkbox("Activas"):
                df = df[df["Ultimo operado"] != 0]
        with col2:
            if agree := st.checkbox("En pesos"):
                df = df[df["Moneda"] == "ARS"]
                with col3:
                    if agree := st.checkbox("Precio de referencia"):
                        usd_price = bcra_usd()
                        if price := st.number_input(
                            "Precio",
                            value=usd_price * 100,
                            step=100,
                            label_visibility="collapsed",
                        ):
                            df = df[df["Ultimo operado"] > price]
        with col4:
            if agree := st.checkbox("En dolares"):
                df = df[df["Moneda"] == "USD"]
        with col5:
            if agree := st.checkbox("Mediano plazo"):
                df = df.query("Vencimiento >= 600")
                df["Vencimiento años"] = (df["Vencimiento"] / 365).round(2)
        with col6:
            if agree := st.checkbox("Largo plazo"):
                df = df.query("Vencimiento >= 1500")
                df["Vencimiento años"] = (df["Vencimiento"] / 365).round(2)
    return df


def deepsearch(df, agree):
    if agree:
        ticket = list(df.index)
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


def mae():
    col1, col2 = st.columns(2)
    with col1:
        periodo = "A" if st.button("Licitaciones Activas.") else None
    with col2:
        periodo = "P" if st.button("Licitaciones Futuras.") else None
    with st.spinner("Procesando.."):
        if periodo is not None:
            licitacion(periodo)
        else:
            licitacion()
    st.markdown("---")


def highlight_colocador(val):
    if "SANTANDER" in val:
        return "color: red"
    elif "BBVA" in val:
        return "color: blue"
    else:
        return ""


def licitacion(periodo="A"):
    url = f"https://www.mae.com.ar/mercado-primario/licitaciones/LicitacionesbyEstado/{periodo}"
    try:
        r = req.get(url, timeout=10, headers=HEADERS)
        df = pd.DataFrame(r.json()["data"])
        df = df.loc[
            :, ["Emisor", "FechaInicio", "Moneda", "Observaciones", "Descripcion", "Colocador"]
        ]  # FechaInicio/FechaVencimiento/FechaLiquidacion/Titulo/Emisor/Industria/Descripcion/Moneda/AmpliableHasta/MontoaLicitar/Rueda/Modalidad/Liquidador/Estado/Tipo/Colocador/Observaciones/Resultados/InformacionAdicional/Monto_Adjudicado/Sistema_Adjudicacion/Valor_Corte/Duration/ID/ExisteArchivo/Comentario
        df = df.rename(columns={"FechaInicio": "Fecha"})
        df = df[df["Colocador"].str.contains("SANTANDER|BBVA", case=False, na=False)]
        # df = df.set_index(["Emisor"]).reset_index()
        dfstyle = df.style.applymap(highlight_colocador, subset=["Colocador"])
        st.dataframe(dfstyle, use_container_width=True)
        st.markdown(
            f"\n* Para más información [MAE](https://www.mae.com.ar/mercado-primario/licitaciones#/{periodo})"
        )
    except KeyError:
        st.warning(
            "No hay licitaciones activas en este momento.\n\nRevisar las futuras licitaciones."
        )


def main():
    st.set_page_config(
        page_title="Inversiones App",
        page_icon="🧊",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    clean_html()
    tab1, tab2 = st.tabs(["📈 Mercado Abierto Electronico", "🗃 Bolsas y Mercados Argentinos"])
    with tab1:
        mae()
    with tab2:
        byma()


def clean_html():
    hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
    st.markdown(hide_st_style, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
