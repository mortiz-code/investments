# usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Matias Ortiz"
__email__ = "matias.ortiz@bvstv.com"
__webpage__ = "https://github.com/mortiz-code"
__version__ = "0.1.0"
__copyright__ = "Copyright (c) 2021, all rights reserved."
__license__ = "BSD 3-Clause License."

"""
 Doc: https://colab.research.google.com/drive/1qPNREasgE0vhVKttNL0YyMdZE84n28_H?usp=sharing
 import datetime
 now = datetime.datetime.now().strftime("%Y-%m-%d")
 import investpy
 investpy.get_stock_historical_data(stock='AGRO',country='argentina',from_date=end, to_date=now,interval='Daily')
"""

import yfinance as yf
import pandas as pd
import datetime


def read_excel():
    excel_file = "/mnt/c/Users/mortiz/Dropbox/Inversion.xlsx"
    df = pd.read_excel(excel_file, sheet_name="Cedears")
    data_from_excel_stock = df.iloc[1:11, 0]
    data_from_excel_q = df.iloc[1:11, 1]
    data_from_excel_pc = df.iloc[1:11, 3]
    stocks_list = data_from_excel_stock.tolist()
    q_list = data_from_excel_q.tolist()
    pc_list = data_from_excel_pc.tolist()

    # Listado de cedears tener el cuenta los nombres porque en BBVA no aparecen los standards de Yahoo Finance.
    # result = [i + ".ba" for i in stocks_list]
    # Por el momento uso lista manual porque falla excel.
    stocks_list = [
        "AGRO.BA",
        "ADGO.BA",
        "AMZN.BA",
        "BABA.BA",
        "GLNT.BA",
        "MELI.BA",
        "TSLA.BA",
        "GOLD.BA",
        "LMT.BA",
        "MSFT.BA",
    ]

    return stocks_list, q_list, pc_list


def get_latest_price(stocks_list):
    print("")
    print(f" Variacion del precio de cierre ".center(80, "-"))
    prices = []
    for stock in stocks_list:
        symbol = yf.Ticker(stock)
        try:
            data = symbol.history(period="2d")
            close_price = round(data["Close"][0], 2)
            yesterday_close_price = round(data["Close"][1], 2)
            diff = close_price - round(yesterday_close_price, 2)
            print(f"* {symbol.ticker} > Pt-1: $ {close_price} | Pt-1 - Pt2: $ {diff}")
            prices.append(close_price)
        except IndexError:
            print(f"* {symbol.ticker} > Precio de cierre: $ {close_price}")
            prices.append(close_price)

    return prices


def beneficio(prices, q_list, pc_list, stocks_list):
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    total = 0
    k = [x * y for x, y in zip(prices, q_list)]
    for i in k:
        total += i
    print("")
    print(" Diferencia con respecto al precio de compra ".center(80, "-"))
    a = zip(stocks_list, prices, pc_list)
    for i in a:
        print(f"* {i[0]} > $ {round(i[1] - i[2],2)} == {round((i[1]-i[2])/i[2],2)}%")

    print("")
    print(f" El capital en renta viable a la fecha {now} es de $ {total} ".center(80, "-"))


def get_real_price(stocks_list):
    print("")
    print(f" Precio actual (15 de delay) ".center(80, "-"))
    for arg in stocks_list:
        a = yf.download(
            tickers=arg,
            period="1d",
            interval="1m",
            progress=False,
            auto_adjust=False,
            prepost=True,
            rounding=True,
        )

        arg2 = a.tail(1)["Close"][0]
        print(f"* {arg} > $ {arg2}")


def main():
    stocks_list, q_list, pc_list = read_excel()
    prices = get_latest_price(stocks_list)
    get_real_price(stocks_list)
    beneficio(prices, q_list, pc_list, stocks_list)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        exit()
