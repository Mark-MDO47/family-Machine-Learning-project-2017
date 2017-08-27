import pandas as pd
# from pandas import ExcelWriter # only when writing Excel file with info
import numpy as np
import os
import sys
# import time
from datetime import datetime

"""
readStockMarketData_pandasFrame.py
Author: Mark Olson - heavily based on simpler code from https://pythonprogramming.net/getting-data-machine-learning/?completed=/data-acquisition-machine-learning/
   We want to extract more fields from the data than that original code extracted

This routine reads html files from Yahoo Finance to gather information about individual stocks
The information is written to stdout in the format of a *.csv file

The *.html files are stored in a path found in the global DATA_DIRECTORY
    For this exercise we will walk the data found in the _KeyStats subdirectory
The data types that we will collect are found in the global DATA_CATEGORIES
"""

MDO_DEBUG = False # put debug statements inline with data
MDO_META = True # put detailed meta-cell giving status adjacent to data cells

DATA_DIRECTORY = r'.\TestData\intraQuarter'

DATA_CATEGORIES = [
    'Report Date', 'Market Cap', 'Enterprise Value', 'Trailing P/E', 'Forward P/E', 'PEG Ratio',
    'Price/Sales', 'Price/Book', 'Enterprise Value/Revenue', 'Enterprise Value/EBITDA', 'Fiscal Year Ends',
    'Most Recent Quarter', 'Profit Margin', 'Operating Margin', 'Return on Assets', 'Return on Equity',
    'Revenue', 'Revenue Per Share', 'Revenue Growth', 'Qtrly Revenue Growth', 'Gross Profit', 'EBITDA', 'Net Income Avl to Common',
    'Diluted EPS', 'Qtrly Earnings Growth', 'Total Cash', 'Total Cash Per Share', 'From Operations', 'Free Cashflow', 'Total Debt', 'Total Debt/Equity',
    'Current Ratio', 'Book Value Per Share', 'Operating Cash Flow', 'Levered Free Cash Flow', 'Beta', '52-Week Change',
    'S&P500 52-Week Change', '52-Week High', '52-Week Low', '50-Day Moving Average', '200-Day Moving Average',
    'Average Volume', 'Shares Outstanding', 'Float', '% Held by Insiders', '% Held by Institutions', 'Shares Short',
    'Short Ratio', 'Short % of Float', 'Shares Short (prior month)', 'Forward Annual Dividend Rate', 'Forward Annual Dividend Yield',
    'Trailing Annual Dividend Rate', 'Trailing Annual Dividend Yield', '5 Year Average Dividend Yield', 'Payout Ratio',
    '52-Week Change (relative to S&P500)', 'Average Volume (3 month)', 'Average Volume (10 day)', 'Annual Dividend', 'Dividend Yield',
    'Dividend Date', 'Ex-Dividend Date', 'Last Split Factor', 'Last Split Date']

META_BUG_UNKNOWN = 'BUG_convert_string_to_np'
META_DATE_FNAME_SUCCESS = 'DATE_FNAME_SUCCESS'
META_DATE_FNAME_FAIL = 'DATE_FNAME_SUCCESS'
META_DATE_FULL_SUCCESS = 'DATE_FULL_SUCCESS'
META_DATE_REL_SUCCESS = 'DATE_REL_SUCCESS'
META_DATE1_FAIL = 'DATE1_FAIL'
META_DATE1_FULL_FAIL = 'DATE1_FULL_FAIL'
META_DATE1_REL_FAIL = 'DATE1_REL_FAIL'
META_DATE1_REL_UNSPEC_FAIL = 'DATE1_REL_UNSPEC_FAIL'
META_DATE2_FAIL = 'DATE2_FAIL'
META_DATE2_FULL_FAIL = 'DATE2_FULL_FAIL'
META_DATE2_REL_FAIL = 'DATE2_REL_FAIL'
META_DATE2_REL_UNSPEC_FAIL = 'DATE2_REL_UNSPEC_FAIL'
META_NAN__SUCCESS = 'NAN__SUCCESS'
META_NUMERIC_ENDCHAR_SUCCESS = 'NUMERIC_ENDCHAR_SUCCESS'
META_NUMERIC_RATIO_FAIL = 'NUMERIC_RATIO_FAIL'
META_NUMERIC_RATIO_SUCCESS = 'NUMERIC_RATIO_SUCCESS'
META_NUMERIC_SIMPLE_FAIL = 'NUMERIC_SIMPLE_FAIL'
META_NUMERIC_SIMPLE_SUCCESS = 'NUMERIC_SIMPLE_SUCCESS'

"""
ticker_symbols = [
    'a', 'aa', 'aapl', 'abbv', 'abc', 'abt', 'ace', 'aci', 'acn', 'act', 'adbe', 'adi', 'adm', 'adp', 'adsk',
    'adt', 'aee', 'aeo', 'aep', 'aes', 'aet', 'afl', 'agn', 'aig', 'aiv', 'aiz', 'akam', 'all', 'altr', 'alxn',
    'amat', 'amd', 'amgn', 'amp', 'amt', 'amzn', 'an', 'anf', 'ann', 'aon', 'apa', 'apc', 'apd', 'aph', 'apol',
    'arg', 'arna', 'aro', 'ati', 'atvi', 'avb', 'avp', 'avy', 'axp', 'azo', 'ba', 'bac', 'bax', 'bbby', 'bbry',
    'bbt', 'bby', 'bcr', 'bdx', 'beam', 'ben', 'bf-b', 'bhi', 'big', 'biib', 'bk', 'bks', 'blk', 'bll', 'bmc',
    'bms', 'bmy', 'brcm', 'brk-b', 'bsx', 'btu', 'bwa', 'bxp', 'c', 'ca', 'cab', 'cag', 'cah', 'cam', 'camp',
    'cat', 'cb', 'cbg', 'cbs', 'cce', 'cci', 'ccl', 'celg', 'cern', 'cf', 'cfn', 'chk', 'chrw', 'ci', 'cim',
    'cinf', 'cl', 'cldx', 'clf', 'clx', 'cma', 'cmcsa', 'cme', 'cmg', 'cmi', 'cms', 'cnp', 'cnx', 'cof', 'cog',
    'coh', 'col', 'cop', 'cost', 'cov', 'cpb', 'crm', 'csc', 'csco', 'csx', 'ctas', 'ctl', 'ctsh', 'ctxs', 'cvc',
    'cvs', 'cvx', 'd', 'dal', 'dd', 'dds', 'de', 'dell', 'df', 'dfs', 'dg', 'dgx', 'dhi', 'dhr', 'dis', 'disca',
    'dks', 'dlph', 'dltr', 'dlx', 'dnb', 'dnr', 'do', 'dov', 'dow', 'dps', 'dri', 'dsw', 'dte', 'dtv', 'duk',
    'dva', 'dvn', 'ea', 'ebay', 'ecl', 'ecyt', 'ed', 'efx', 'eix', 'el', 'emc', 'emn', 'emr', 'eog', 'eqr', 'eqt',
    'esrx', 'esv', 'etfc', 'etn', 'etr', 'ew', 'exc', 'expd', 'expe', 'expr', 'f', 'fast', 'fb', 'fcx', 'fdo', 'fdx',
    'fe', 'ffiv', 'fhn', 'fis', 'fisv', 'fitb', 'fl', 'flir', 'flr', 'fls', 'flws', 'fmc', 'fosl', 'frx', 'fslr',
    'fti', 'ftr', 'gas', 'gci', 'gd', 'ge', 'ges', 'gild', 'gis', 'glw', 'gm', 'gmcr', 'gme', 'gnw', 'goog', 'gpc',
    'gps', 'grmn', 'grpn', 'gs', 'gt', 'gtn', 'gww', 'hal', 'har', 'has', 'hban', 'hcbk', 'hcn', 'hcp', 'hd', 'hes',
    'hig', 'hog', 'hon', 'hot', 'hov', 'hp', 'hpq', 'hrb', 'hrl', 'hrs', 'hsp', 'hst', 'hsy', 'htz', 'hum', 'ibm',
    'ice', 'iff', 'igt', 'intc', 'intu', 'ip', 'ipg', 'ir', 'irm', 'isrg', 'itw', 'ivz', 'jbl', 'jci', 'jcp', 'jdsu',
    'jec', 'jnj', 'jnpr', 'josb', 'joy', 'jpm', 'jwn', 'k', 'key', 'kim', 'klac', 'kmb', 'kmi', 'kmx', 'ko', 'kr',
    'krft', 'kss', 'ksu', 'l', 'leg', 'len', 'lh', 'life', 'lll', 'lltc', 'lly', 'lm', 'lmt', 'lnc', 'lo', 'low',
    'lrcx', 'lsi', 'ltd', 'luk', 'luv', 'lyb', 'm', 'ma', 'mac', 'mar', 'mas', 'mat', 'mcd', 'mchp', 'mck', 'mco',
    'mcp', 'mdlz', 'mdt', 'met', 'mgm', 'mhfi', 'mjn', 'mkc', 'mmc', 'mmm', 'mnst', 'mo', 'molx', 'mon', 'mos', 'mpc',
    'mrk', 'mro', 'ms', 'msft', 'msi', 'mtb', 'mu', 'mur', 'mwv', 'myl', 'nbl', 'nbr', 'ndaq', 'ne', 'nee', 'nem',
    'nflx', 'nfx', 'ni', 'nile', 'nke', 'nly', 'noc', 'nok', 'nov', 'nrg', 'nsc', 'ntap', 'ntri', 'ntrs', 'nu',
    'nue', 'nus', 'nvda', 'nwl', 'nwsa', 'nyx', 'oi', 'oke', 'omc', 'orcl', 'orly', 'oxy', 'p', 'payx', 'pbct', 'pbi',
    'pcar', 'pcg', 'pcl', 'pcln', 'pcp', 'pdco', 'peg', 'pep', 'petm', 'pets', 'pfe', 'pfg', 'pg', 'pgr', 'ph', 'phm',
    'pki', 'pld', 'pll', 'pm', 'pnc', 'pnr', 'pnw', 'pom', 'ppg', 'ppl', 'prgo', 'pru', 'psa', 'psx', 'pvtb', 'pwr',
    'px', 'pxd', 'qcom', 'qdel', 'qep', 'r', 'rai', 'rdc', 'rf', 'rhi', 'rht', 'rl', 'rok', 'rop', 'rost', 'rrc', 'rsg',
    'rsh', 'rtn', 's', 'sai', 'sbux', 'scg', 'schl', 'schw', 'sd', 'se', 'see', 'sfly', 'shld', 'shw', 'sial', 'siri',
    'sjm', 'sks', 'slb', 'slm', 'sna', 'sndk', 'sne', 'sni', 'snts', 'so', 'spg', 'spls', 'srcl', 'sre', 'sti', 'stj',
    'stt', 'stx', 'stz', 'swk', 'swn', 'swy', 'syk', 'symc', 'syy', 't', 'tap', 'tdc', 'te', 'teg', 'tel', 'ter', 'tgt',
    'thc', 'tibx', 'tif', 'tjx', 'tm', 'tmk', 'tmo', 'trip', 'trow', 'trv', 'tsla', 'tsn', 'tso', 'tss', 'twc', 'twx',
    'txn', 'txt', 'tyc', 'ua', 'unh', 'unm', 'unp', 'ups', 'urbn', 'usb', 'utx', 'v', 'vale', 'var', 'vfc', 'viab', 'vitc',
    'vlo', 'vmc', 'vno', 'vprt', 'vrsn', 'vtr', 'vz', 'wag', 'wat', 'wdc', 'wec', 'wfc', 'wfm', 'wgo', 'whr', 'win',
    'wlp', 'wm', 'wmb', 'wmt', 'wpo', 'wpx', 'wtw', 'wu', 'wy', 'wyn', 'wynn', 'x', 'xel', 'xl', 'xlnx', 'xom', 'xray',
    'xrx', 'xyl', 'yhoo', 'yum', 'zion', 'zlc', 'zmh', 'znga' ]
"""



string_to_np_lastChar = {'B': 1000000000.0, 'M': 1000000.0, 'K': 1000.0, '%': 0.01}
string_to_np_NaN = {'NAN': np.nan, 'NAN%': np.nan, 'N/A': np.nan}
string_to_month = {'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04', 'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08', 'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'}
dtVal_epoch_excel = datetime.strptime('1900-01-01', '%Y-%m-%d')
def convert_string_to_np(theString, thisYear=None):
    """
    function: convert_string_to_np(theString, thisYear)
    Author: Mark Olson
    This routine converts the parameter theString and returns an np.something and a meta describing how the conversion went

    input parameters:
        theString - string to be converted
        thisYear - integer 4-digit year number such as 2017
    returns: return result, result_meta
        result - np.something with result of conversion
            returns np.nan if N/A or NaN found
            multiplies by appropriate number for B, M, K, or % (1.3 B is 1.3E9)
            for : we compute a fraction (such as split factor 2:1 --> 2.0
            for date containing year ('31-Dec-05') returns floating point as per Excel date/time format
            for date not containing year ('24-Sep'; example Fiscal Year Ends); returns same Excel date/time format using parameter thisYear
            if we cannot figure it out we return np.inf
        result_meta - detailed meta string describing how the conversion went
    GLOBAL flags:
        MDO_DEBUG - True if want debug information sent to stdout immediately regarding the conversion

    This routine does not "know" this, but theString comes from one of the DATA_CATEGORIES fields in an html file
        thus the formatting of the fields is quite variable
    The detailed meta information and the MDO_DEBUG information can be quite useful when somebody decides to enter
        a field in a unique way, or has a typo, etc.
    """
    result = np.nan
    result_meta = META_BUG_UNKNOWN # UNKNOWN - bug in routine if returned
    myStringSplit = []
    dateStringSplit = []
    myString = theString.replace(",","") # helps for cases like 'Dec 31, 2011' and '1,180.0B'
    # have to check for date before number to avoid mis-classifying 03-Feb as a number to multiply by billion
    if (myString.find('-') > 0) or (myString.find(' ') > 0):
        # if date string
        # we make dateStringSplit as if they said 31-May-2007
        # other inputs: 31 May 07, Dec 31, 2011, May-31-2007
        # other input not handled: 3/31/2007
        #   replace out ','
        #   replace ' ' with '-'
        #   if '-' --> date
        #   if [0].isalpha: may-31-2007
        #   if [0].isdigit: 31-may-2007 - this is what we analyze
        date_type = None
        dateString = myString
        dateString = dateString.replace(" ","-")
        dateStringSplit = dateString.split("-")
        if not dateString[0].isdigit():
            tmp = dateStringSplit[0]
            dateStringSplit[0] = dateStringSplit[1]
            dateStringSplit[1] = tmp
        # translate July to JUL
        if ((len(dateStringSplit) == 2) or (len(dateStringSplit) == 3)) and (dateStringSplit[1].isalpha()) and (dateStringSplit[1].upper() not in string_to_month):
            for mon in string_to_month.keys():
                if dateStringSplit[1].upper().find(mon) == 0:
                    dateStringSplit[1] = mon
                    break
        date_type = None
        if ((len(dateStringSplit) == 2) or (len(dateStringSplit) == 3)) and (dateStringSplit[1].upper() in string_to_month):
            if len(dateStringSplit) == 3:
                date_type = 'FullDate'
                yr = int(dateStringSplit[2])
                # here we decide the breakpoint for a two-digit year between 19xx and 20xx
                if yr < 80:
                    yr += 2000
                elif yr < 100:
                    yr += 1900
            else:
                if None == thisYear:
                    date_type = 'RelDate_Unspec'
                    yr = np.inf # no bueno
                    if MDO_DEBUG:
                        sys.stdout.write("ERROR: date string %s but no thisYear input\n" % dateString)
                else:
                    date_type = 'RelDate'
                    yr = thisYear
                    if (yr == 1900) and (int(dateStringSplit[0]) == 29) and (int(string_to_month[dateStringSplit[1].upper()]) == 2):
                        # curiously, Excel thinks there was a Feb 29, 1900. Feb 28 is day 59, Feb 29 is day 60, and Mar 01 is day 61
                        # we will just change it to Feb 28
                        dateStringSplit[0] = '28'
                    elif ((thisYear % 4) != 0) and (int(dateStringSplit[0]) == 29) and (int(string_to_month[dateStringSplit[1].upper()]) == 2):
                        if ((thisYear-1) % 4) == 0:
                            yr -= 1
                        else:
                            dateStringSplit[0] = '28'
            if np.inf != yr:
                dtString = "%04d-%s-%02d" % (yr, string_to_month[dateStringSplit[1].upper()], int(dateStringSplit[0]))
                dtVal = datetime.strptime(dtString, '%Y-%m-%d')
                dtDiff = dtVal - dtVal_epoch_excel
                result = np.float64(dtDiff.days+2)
                if date_type == 'FullDate':
                    result_meta = META_DATE_FULL_SUCCESS
                if date_type == 'RelDate':
                    result_meta = META_DATE_REL_SUCCESS
                # print("   DEBUG converted dtString = %s to %s and %0.10f" % (dtString, dtVal, result))
            else:
                if MDO_DEBUG:
                    sys.stdout.write("ERROR:   UNKNOWN FORMAT (date1) OF DATA: %s\n" % dateString)
                result = np.inf
                if date_type == 'RelDate':
                    result_meta = META_DATE1_REL_FAIL
                elif date_type == 'RelDate_Unspec':
                    result_meta = META_DATE1_REL_UNSPEC_FAIL
                elif date_type == 'FullDate':
                    result_meta = META_DATE1_FULL_FAIL
                else:
                    result_meta = META_DATE1_FAIL
        else:
            if MDO_DEBUG:
                sys.stdout.write("ERROR:   UNKNOWN FORMAT (date2) OF DATA: |%s|" % myString)
                for spl in dateStringSplit:
                    sys.stdout.write(" split=|%s|" % spl)
                sys.stdout.write(" no more splits\n")
            result = np.inf
            if date_type == 'RelDate':
                result_meta = META_DATE2_REL_FAIL
            elif date_type == 'RelDate_Unspec':
                result_meta = META_DATE2_REL_UNSPEC_FAIL
            elif date_type == 'FullDate':
                result_meta = META_DATE2_FULL_FAIL
            else:
                result_meta = META_DATE2_FAIL
    elif myString.upper() in string_to_np_NaN:
        result = np.nan
        result_meta = META_NAN__SUCCESS
    elif myString[-1].upper() in string_to_np_lastChar:
        result = np.float64(myString[:-1]) * string_to_np_lastChar[myString[-1].upper()]
        result_meta = META_NUMERIC_ENDCHAR_SUCCESS
    elif myString.find(':') > 0: # example: split factor 2:1
        myStringSplit = myString.split(":")
        numNew = int(myStringSplit[0])
        numOld = int(myStringSplit[1])
        if (numNew > 0) and (numOld > 0):
            fract = (1.0 * numNew) / numOld
            result = np.float64(fract)
            result_meta = META_NUMERIC_RATIO_SUCCESS
        else:
            if MDO_DEBUG:
                sys.stdout.write("ERROR:   UNKNOWN SPLIT FORMAT OF DATA: %s" % myString)
            result = np.inf
            result_meta = META_NUMERIC_RATIO_FAIL
    else:
        try:
            result = np.float64(myString)
            result_meta = META_NUMERIC_SIMPLE_SUCCESS
        except:
            result = np.inf
            result_meta = META_NUMERIC_SIMPLE_FAIL
    return result, result_meta
    ### end of convert_string_to_np(theString, thisYear=None):

def insert_meta(cat_meta, meta_key):
    """
    function insert_meta - utility to put the detailed meta data into the correct position in the meta summary
    """
    if meta_key in cat_meta.keys():
        cat_meta[meta_key] += 1
    else:
        cat_meta[meta_key] = 1
    return cat_meta

def mdoconvertHtmlData(fname="stdio", categories=[]):
    """
    function: mdoconvertHtmlData(fname="stdio", categories=[]):
    Author: Mark Olson
    This routine reads an html file searching for data in the categories

    input parameters:
    returns: return return_data, return_meta, meta_sum_str
    return_data[] matches categories in order
        returns np.inf if not found, np.nan if N/A or NaN found
    return_meta[] matches categories in order
        detailed meta string for each conversion
    meta_sum_str - string with summary of conversion
    """
    return_data = np.empty((len(categories)))
    return_data[:] = np.inf
    return_meta = ["NOT_FOUND" for x in range(len(categories))]
    meta_summary={}
    meta_sum_str = ""

    # special-case filename/url date for return_data[0]
    # this should get to filename for Windows, Unix, or URL
    myfname = fname.replace("/","\\").split("\\")[-1]
    try:
        dtVal_fname = datetime.strptime(myfname, '%Y%m%d%H%M%S.html')
        diff = dtVal_fname - dtVal_epoch_excel
        return_data[0] = np.float64(diff.days + 2 + diff.seconds / 86400.0) # Excel format for date
        return_meta[0] = META_DATE_FNAME_SUCCESS
        meta_sum_str = META_DATE_FNAME_SUCCESS + '=1;'
    except:
        return_data[0] = np.nan
        return_meta[0] = META_DATE_FNAME_FAIL
        meta_sum_str = META_DATE_FNAME_FAIL + '=1;'

    thisYear = 1900 # this will give us days in the year for values like Feb-29

    dfs = pd.read_html(fname)
    """
    # print("%s\n\n\n" % dfs)
    with ExcelWriter('path_to_file.xlsx') as writer:
        for i, df in enumerate(dfs):
            df.to_excel(writer, sheet_name="Sheet%03d" % i)
    """

    state = "looking"
    foundit = -1
    extra_lines_searched = -1
    for df in dfs:
        for row in range(len(df)):
            for col in range(len(df.columns)):
                # skip the entries where there are many in one col/row; don't know why there are these duplicates
                if ("looking" == state) and (("%s" % df[col][row])[-1] == ":"):
                    foundit = -1
                    extra_lines_searched = 0
                    for findit in range(len(categories)):
                        if (("%s" % df[col][row]).find(categories[findit]) != -1) and (return_data[findit] == np.inf):
                            if foundit >= 0: # can be multiple matches; take the longest
                                if len(categories[findit]) > len(categories[foundit]):
                                    foundit = findit
                                    if MDO_DEBUG:
                                        name_col_row_foundit = "|%s|:%s:%s:%s:|%s|" % (df[col][row], col, row, foundit, categories[foundit])
                            else:
                                foundit = findit
                                if MDO_DEBUG:
                                    name_col_row_foundit = "|%s|:%s:%s:%s:|%s|" % (df[col][row], col, row, foundit, categories[foundit])
                            extra_lines_searched = -1
                            state = "get_data"
                            # print("found %s" % df[col][row])
                            # if df[col][row].find(categories[findit]) != -1:
                                # print("    found at character %d" % df[col][row].find(categories[findit]))
                elif ("get_data" == state) and (len("%s" % df[col][row]) > 0):
                    return_data[foundit], meta_key =  convert_string_to_np("%s" % df[col][row], thisYear)
                    return_meta[foundit] = meta_key
                    meta_summary = insert_meta(meta_summary, meta_key)
                    state = "looking"
                    # print("  data = %s" % return_data[foundit])
                elif  "get_data" == state:
                    extra_lines_searched += 1
                    if 5 > extra_lines_searched:
                        state = "looking"
                        # print("    never found data after %d lines" % extra_lines_searched)
    for meta_key in meta_summary.keys():
        meta_sum_str = "%s%s=%d;" % (meta_sum_str, meta_key, meta_summary[meta_key])
    return return_data, return_meta, meta_sum_str

def output_hdr(tkr, categories=[], extra_categories=[], write_meta_columns = True):
    """
    function output_hdr - utility to put csv-style header to stdout
    """
    sys.stdout.write("%s\t" % tkr)
    for idx in range(len(categories)):
        sys.stdout.write("%s\t" % categories[idx])
        if write_meta_columns:
           sys.stdout.write("META %s\t" % categories[idx])
    for idx in range(len(extra_categories)):
        sys.stdout.write("%s\t" % extra_categories[idx])
    sys.stdout.write("\n")

def output_lin(tkr, data=[], extra=[]):
    """
    function output_lin - utility to put csv-style line to stdout - tab is separator
    """
    sys.stdout.write("%s\t" % tkr)
    for idx in range(len(data)):
        sys.stdout.write("%s\t" % data[idx][0])
        sys.stdout.write("%s\t" % data[idx][1])
    for idx in range(len(extra)):
        sys.stdout.write("%s\t" % extra[idx])
    sys.stdout.write("\n")

def walk_path(path, categories=[]):
    """
    function walk_path(path, categories)
    Author: Mark Olson
    This routine goes through the _KeyStats directory reading the html files
    It writes a line to stdout for each file found with data for each category

    input parameters:
        path - string with path (relative or absolute) to the data.
            subdirectories in this path would be _AnnualEarnings, _KeyStats, _QuarterlyEarnings
        categories[] - the categories of data to be extracted from the html files
            this is in the format of a list of strings
    returns:
        does not return a value
        outputs are written to stdout: a file in CSV tab-separated format
    """
    statspath = path+'\\_KeyStats'
    stock_list = [x[0] for x in os.walk(statspath)]

    output_hdr("Ticker", categories=categories, extra_categories=["MetaData"], write_meta_columns = MDO_META)
    for each_dir in stock_list[1:]:
        if MDO_DEBUG:
            each_dir = 'C:\\Users\\mdo\\Documents\\TestData\\intraQuarter\\_KeyStats\\kmx' # DEBUG
        if each_dir.find('kmi') >= 0: # lots of missing data in these
            continue
        each_file = os.listdir(each_dir)
        # ticker = each_dir.split("/")[-1]
        ticker = each_dir.split("\\")[-1]
        # print("$$$$$$$$$$ TICKER = %s $$$$$$$$$$$$" % ticker)
        if len(each_file) > 0:
            for file in each_file:
                full_file_path = each_dir+'\\'+file
                # print("   %s" % full_file_path)
                cat_data, cat_meta, cat_extra = mdoconvertHtmlData(fname=full_file_path, categories=categories)
                if MDO_META:
                   output_lin(ticker, data = list(zip(cat_data, cat_meta)), extra = [cat_extra])
               else:
                   output_lin(ticker, data = list(cat_data), extra = [cat_extra])
        if MDO_DEBUG:
            break           
                    
walk_path(path=DATA_DIRECTORY, categories=DATA_CATEGORIES)
