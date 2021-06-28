This app for default will use the file 'portfolio.csv' as portfolio. In case it has another name, you can use it as an argument. Otherwise the application will not run.

_Note: Current price has ~15' delay._

```python
└─$ python main.py
Stock    Current    Diff      Variation
-------  ---------  --------  -----------
AGRO.BA  $ 24.0     $ -1.2    [-]
ADGO.BA  $ 3515.5   $ -315.0  [-]
AMZN.BA  $ 4024.0   $ 14.0    [+]
BABA.BA  $ 4346.5   $ 248.5   [+]
GLNT.BA  $ 6422.5   $ 0.0     [+]
MELI.BA  $ 4370.5   $ 57.0    [+]
TSLA.BA  $ 7596.5   $ -23.0   [-]
GOLD.BA  $ 3570.5   $ 0.0     [+]
LMT.BA   $ 3274.0   $ 74.0    [+]
MSFT.BA  $ 4538.5   $ 24.5    [+]
JPM.BA   $ 5274.0   $ 100.5   [+]
X.BA     $ 1359.5   $ -11.5   [-]
```

```python
└─$ python main.py portfolio.csv
Stock    Current    Diff      Variation
-------  ---------  --------  -----------
AGRO.BA  $ 24.0     $ -1.2    [-]
ADGO.BA  $ 3515.5   $ -315.0  [-]
AMZN.BA  $ 4024.0   $ 14.0    [+]
BABA.BA  $ 4346.5   $ 248.5   [+]
GLNT.BA  $ 6422.5   $ 0.0     [+]
MELI.BA  $ 4370.5   $ 57.0    [+]
TSLA.BA  $ 7596.5   $ -23.0   [-]
GOLD.BA  $ 3570.5   $ 0.0     [+]
LMT.BA   $ 3274.0   $ 74.0    [+]
MSFT.BA  $ 4538.5   $ 24.5    [+]
JPM.BA   $ 5274.0   $ 100.5   [+]
X.BA     $ 1359.5   $ -11.5   [-]
```

```python
└─$ python main.py portfoliosdfs.csv
File portfoliosdfs.csv not found.
```
