# usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "mcode"
__email__ = "matcode@pm.me"
__webpage__ = "https://github.com/mortiz-code"
__version__ = "1.1.0"
__copyright__ = "Copyright (c) 2021, all rights reserved."
__license__ = "BSD 3-Clause License."


from csv import reader
from os.path import isfile
import os
from streamlit_extras.customize_running import center_running
from streamlit_extras.colored_header import colored_header
import streamlit_antd_components as sac
import requests as req
import pandas as pd
import streamlit as st
import urllib3

urllib3.disable_warnings()


TOKEN = st.secrets["TOKEN"]

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Referer-Policy": "no-referrer-when-downgrade",
}


@st.cache_data(experimental_allow_widgets=True)
def get_detail(symbol):
    with st.spinner("In progress..."):
        DATA = {"symbol": symbol, "Content-Type": "application/json"}
        URL = "https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free/bnown/fichatecnica/especies/general"
        r = req.post(URL, timeout=10, json=DATA, headers=HEADERS, verify=False)
        if r.status_code == 200:
            try:
                return format_response(r)
            except KeyError:
                st.warning("La ON no cuenta con informacion disponible.")
        else:
            st.warning(
                f"Especie no encontrada {symbol}.\nLlamar al banco y/o buscar código ISIN."
            )


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
            "fechaVencimiento": "Vencimiento en días",
            "fechaDevenganIntereses": "Devenga interes",
        }
    )
    df = df.set_index(["Emisor"])
    df = df.iloc[0]
    df["Devenga interes"] = pd.to_datetime(df["Devenga interes"]).date()
    df["Vencimiento en días"] = pd.to_datetime(df["Vencimiento en días"]).date()
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
    with st.spinner("In progress..."):
        response = get_data()
        if response.status_code == 200:
            df = pd.DataFrame(response.json())
            df = df.loc[
                :,
                [
                    "symbol",
                    "denominationCcy",
                    "daysToMaturity",
                    "trade",
                    "imbalance",
                ],
            ]
            df = df.rename(
                columns={
                    "symbol": "Oblicación Negociable",
                    "denominationCcy": "Moneda",
                    "daysToMaturity": "Vencimiento en días",
                    "trade": "Ultimo valor operado",
                    "imbalance": "Variacion",
                }
            )
            df = df.set_index(["Oblicación Negociable"])
            df["Variacion"] = df["Variacion"] * 100
            df["Ultimo valor operado"] = df["Ultimo valor operado"] / 100
            (
                col1,
                col2,
                col3,
                col4,
                col5,
                col6,
            ) = st.columns(6)
            df = options(df, col1, col2, col3, col4, col5, col6)
            on_count = df["Variacion"].count()
            styled_df = df.style.format(precision=2, decimal=",", thousands=".")
            styled_df = styled_df.map(highlight_variation, subset=["Variacion"])
            with st.container(border=True):
                st.dataframe(styled_df, use_container_width=True)
            with st.container(border=True):
                st.code(f"Cantidad de oblicaciones negociables disponibles: {on_count}")
            more_options(df)
        else:
            st.error(f"Error: {response.status_code}")


def more_options(df):
    (
        col1,
        col2,
    ) = st.columns(2)
    with col1:
        with st.container(border=True):
            if agree := st.checkbox("Más info:"):
                colored_header(
                    label="Detalles de ON",
                    description="_Informacion de amortizacion, interes, lamina, vencimiento, moneda..._",
                    color_name="violet-70",
                )
                deepsearch(df)
    with col2:
        with st.container(border=True):
            if agree := st.checkbox("Cartera."):
                cartera()


@st.cache_data(show_spinner=True)
def get_data():
    DATA = {
        "excludeZeroPFAndQty": True,
        "T2": True,
        "T1": False,
        "T0": False,
        "Content-Type": "application/json",
    }
    URL = "https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free/negociable-obligations"
    return req.post(
        URL, timeout=10, json=DATA, headers=HEADERS, stream=False, verify=False
    )


def bcra_usd():
    HEADER = {"Authorization": f"BEARER {TOKEN}"}
    URL = "https://api.estadisticasbcra.com/usd"
    r = req.get(URL, timeout=3, headers=HEADER)
    return r.json()[-1]["v"]


def options(df, col1, col2, col3, col4, col5, col6):
    with st.container(border=True):
        with col1:
            if on := st.toggle("Activas"):
                df = df.loc[df["Ultimo valor operado"] != 0]
        with col2:
            if on := st.toggle("En pesos"):
                df = df.loc[df["Moneda"] == "ARS"]
                with col3:
                    if on := st.checkbox("Precio de referencia"):
                        usd_price = bcra_usd()
                        if price := st.number_input(
                            "Precio",
                            value=usd_price,
                            step=100,
                            label_visibility="collapsed",
                        ):
                            df = df.loc[df["Ultimo valor operado"] > price]
        with col4:
            if on := st.toggle("En dolares"):
                df = df.loc[df["Moneda"] == "USD"]
        with col5:
            if on := st.toggle("Mediano plazo"):
                df = df.query("`Vencimiento en días` >= 600")
                df.loc[:, "Vencimiento años"] = (
                    df["Vencimiento en días"] / 365
                ).round(2)
        with col6:
            if on := st.toggle("Largo plazo"):
                df = df.query("`Vencimiento en días` >= 1500")
                df.loc[:, "Vencimiento años"] = (
                    df["Vencimiento en días"] / 365
                ).round(2)
        return df


def deepsearch(df):
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
    option = sac.buttons(
        [
            sac.ButtonsItem(label="Licitaciones Activas.", color="#6499cb"),
            sac.ButtonsItem(label="Licitaciones Futuras.", color="#c1a5e4"),
            sac.ButtonsItem(
                label="Listado Completo",
                icon="share-fill",
                href="https://www.mae.com.ar/mercado-primario/licitaciones#/P",
            ),
        ],
        align="center",
        radius="xl",
        gap="md",
        return_index=True,
    )
    with st.container(border=True):
        if option == 0:
            licitacion(periodo="A")
        elif option == 1:
            licitacion(periodo="P")


def highlight_colocador(val):
    if "Santander" in val:
        return "color: red"
    elif "BBVA" in val:
        return "color: blue"
    elif "Cocos" in val:
        return "color: blue"
    else:
        return ""


def licitacion(periodo):
    with st.spinner("Procesando.."):
        url = f"https://www.mae.com.ar/mercado-primario/licitaciones/LicitacionesbyEstado/{periodo}"
        try:
            r = req.get(url, timeout=10, headers=HEADERS)
            df = pd.DataFrame(r.json()["data"])
            df = df.loc[
                :,
                [
                    "Emisor",
                    "FechaInicio",
                    "Moneda",
                    "Observaciones",
                    "Descripcion",
                    "Colocador",
                ],
            ]  # FechaInicio/FechaVencimiento/FechaLiquidacion/Titulo/Emisor/Industria/Descripcion/Moneda/AmpliableHasta/MontoaLicitar/Rueda/Modalidad/Liquidador/Estado/Tipo/Colocador/Observaciones/Resultados/InformacionAdicional/Monto_Adjudicado/Sistema_Adjudicacion/Valor_Corte/Duration/ID/ExisteArchivo/Comentario
            df = df.rename(columns={"FechaInicio": "Fecha"})
            df = df[
                df["Colocador"].str.contains(
                    "SANTANDER|BBVA|Cocos", case=False, na=False
                )
            ]
            dfstyle = df.style.map(highlight_colocador, subset=["Colocador"])
            if not df.empty:
                st.dataframe(dfstyle, use_container_width=True)
                st.markdown(
                    f"\n* Para más información [MAE](https://www.mae.com.ar/mercado-primario/licitaciones#/{periodo})"
                )
            else:
                st.warning(
                    "*_No hay licitaciones disponibles en Santander, BBVA ni Cocos Capital._*"
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
    center_running()
    clean_html()
    # fmt: off
    colored_header(
        label="Dashboar de inversión.",
        description="_Pagina personal para analisis de inversiones._",
        color_name="green-70",
    )
    option = sac.segmented(
        items=[
        sac.SegmentedItem(label='📈 MAE'),
        sac.SegmentedItem(label="🗃 BYMA"),
        ], format_func='upper', align='center', size='sm', radius='xl', divider=False, use_container_width=True, return_index=True
    )
    if option == 0:
        colored_header(
        label="Mercado Abierto Electrónico",
        description="_Licitaciones que tienen como colocador de deuda a BBVA, Cocos o Santander._",
        color_name="violet-70",
    )
        mae()
    elif option == 1:
        colored_header(
        label="Bolsas y Mercados Argentinos",
        description="_Los precios que figuran en el panel tienen un retraso de ~15 minutos._",
        color_name="red-70",
    )
        byma()


def clean_html():
    hide_st_style = """
                <style>
                MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
    st.markdown(hide_st_style, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
