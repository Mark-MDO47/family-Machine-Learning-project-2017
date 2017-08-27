#
# from https://mktstk.com/2015/03/03/sic-lookup-by-stock-symbol/
#
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen

# No doubt there are more robust ways to do this; if the SEC adds or subtracts a link this will need adjustment.
# Nevertheless we thought this quick and dirty method would provide value, as our own Google searches on the subject did not yield any useful results.
# NOTE: mdo modified to make it work on Python 3.x and eliminate warnings from Beautiful Soup
def query_sic(symbol):
  print("Looking for symbol %s" % symbol)
  url = 'https://www.sec.gov/cgi-bin/browse-edgar?CIK=' + symbol.upper()
  url += '&Find=Search&owner=exclude&action=getcompany'
  res = urlopen(url)
  res = res.read()
  soup = bs(res, "lxml")
  # if (soup.p.text.find('No matching Ticker Symbol') >= 0) or (soup.p.text.find('State location') == -1):
  if soup.p.text.find('State location') == -1:
    print("UNKNOWN result for %s" % symbol)
    return "UNKNOWN", -1
  else:
    readable = soup.p.text.split(' - ')[1].split('State location')[0]
    codenum = int(soup.find_all('a')[9].contents[0])
    return readable, codenum

# This is my code - mdo

import pandas as pd

# Import the excel file
xls_file = pd.ExcelFile('./mdo.xlsx')
df = xls_file.parse(xls_file.sheet_names[0])
sticker_symbols = df.iloc[:, df.columns.get_loc('Ticker')]
symb = ""
sic_nam_list = []
sic_num_list = []
for idx in range(len(sticker_symbols)):
    if sticker_symbols[idx] != symb:
        symb = sticker_symbols[idx]
        sic_name, sic_num = query_sic(symb)
    sic_nam_list.append(sic_name)
    sic_num_list.append(sic_num)

df['SIC_name_list'] = sic_nam_list
df['SIC_num_list'] = sic_num_list

df.to_excel('./mdo_updated.xlsx', sheet_name='Stocks')

