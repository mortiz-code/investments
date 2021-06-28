# usr/bin/env python3
# -*- coding: utf-8 -*-


__author__ = "Matias Ortiz"
__email__ = "matias.ortiz@bvstv.com"
__webpage__ = "https://github.com/mortiz-code"
__version__ = "1.1.0"
__copyright__ = "Copyright (c) 2021, all rights reserved."
__license__ = "BSD 3-Clause License."


import yfinance as yf
from csv import reader
from tabulate import tabulate
from sys import argv
from os.path import isfile


def info(stocks_list):
    d, e, f, h = [], [], [], []
    for stock in stocks_list:
        data = yf.download(
            tickers=stock,
            period="1d",
            interval="1m",
            progress=False,
            auto_adjust=False,
            prepost=True,
            rounding=True,
        )
        actual_price = data.tail(1)["Close"][0]
        d.append(f"{stock}".upper())
        e.append(f"$ {actual_price}")
        symbol = yf.Ticker(stock)
        data = symbol.history(period="2d")
        yerterday_close_price = data["Close"][0]
        diff = round(actual_price - yerterday_close_price, 2)
        f.append(f"$ {diff}")
    for i in f:
        if "-" in i:
            h.append(f"[-]")
        else:
            h.append(f"[+]")
    g = zip(d, e, f, h)
    print(
        tabulate(
            list(g),
            headers=["Stock", "Current", "Diff", "Variation"],
            tablefmt="simple",
        )
    )


def read(file):
    try:
        with open(file, "r") as f:
            data = reader(f)
            for i in data:
                info(i)
    except FileNotFoundError:
        print(f"File {file} not found.")
        exit()


def main():
    if len(argv) == 2:
        file = argv[1]
        read(file)
    elif isfile("portfolio.csv"):
        read("portfolio.csv")
    else:
        print("CSV file not found.")
        exit()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        exit()
