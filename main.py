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

# import pandas as pd

# excel_file = "/mnt/c/Users/mortiz/Dropbox/Inversion.xlsx"

# df = pd.read_excel(excel_file, sheet_name="Cedears")

# data_from_excel = df.iloc[1:11, 0]

# stocks_list = data_from_excel.tolist()
# import datetime
# now = datetime.datetime.now().strftime("%Y-%m-%d")
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

for stock in stocks_list:
    symbol = yf.Ticker(stock)
    data = symbol.history(period="2d")
    close_price = round(data["Close"][0], 2)
    try:
        yesterday_close_price = round(data["Close"][1], 2)
        diff = close_price - yesterday_close_price
        print(
            f"* {symbol.ticker} > Precio de cierre (Pt-1): {close_price} | Pt-2: {yesterday_close_price} | Diff: {diff}"
        )
    except:
        print(f"* {symbol.ticker} > Precio de cierre (Pt-1): {close_price}")
