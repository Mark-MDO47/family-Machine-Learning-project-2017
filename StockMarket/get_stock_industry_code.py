#
# data from http://www.nasdaq.com/screening/companies-by-industry.aspx?region=North+America&country=United%20States
#

# This is my code - mdo

import pandas as pd

# Import the excel file that we will be sectorialating
xls_name = './mdo_updated.xlsx'
xls_file = pd.ExcelFile(xls_name)
print("Reading %s sheet %s" % (xls_name, xls_file.sheet_names[0]))
df = xls_file.parse(xls_file.sheet_names[0])
sticker_symbols = df.iloc[:, df.columns.get_loc('Ticker')]

# Import the excel file with the sector and industry names
sector_name = './IndustryList/US_AllIndustries.xlsx'
xls_sector = pd.ExcelFile(sector_name)
print("Reading %s sheet %s" % (sector_name, xls_sector.sheet_names[0]))
df_sector =  xls_sector.parse(xls_sector.sheet_names[0])
sector_symbols = df_sector.iloc[:, df_sector.columns.get_loc('Symbol')]
sector_names = df_sector.iloc[:, df_sector.columns.get_loc('Sector')]
indus_names  = df_sector.iloc[:, df_sector.columns.get_loc('Industry')]
xlate = {}
for idx in range(len(sector_names)):
    xlate[sector_symbols[idx]] = {'sector': sector_names[idx], 'industry': indus_names[idx]}

sector_list = []
indus_list = []
unk = ""
for idx in range(len(sticker_symbols)):
    symb = sticker_symbols[idx].upper()
    if symb in xlate.keys():
        sector_list.append(xlate[symb]['sector'])
        indus_list.append(xlate[symb]['industry'])
    else:
        if unk != symb:
            unk = symb
            print("UNKNOWN symbol %s" % symb)
        sector_list.append('UNKNOWN')
        indus_list.append('UNKNOWN')

df['SECTOR_list'] = sector_list
df['INDUSTRY_list'] = indus_list

df.to_excel('./mdo_sectorialated.xlsx', sheet_name='Stocks')

