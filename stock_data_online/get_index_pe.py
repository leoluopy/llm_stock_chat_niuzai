import datetime
import os
import sys

import tushare as ts
import pandas as pd
from time import *

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../../")

from user_interface.stock_data_online.stock_index import key

from matplotlib import pyplot as plt

begin_time = time()
# 用your token初始化pro接口
pro = ts.pro_api(key)
df = pd.DataFrame()
# 指数代码： joinquant -> tushare
jq_symbol = '399001.XSHE'
ts_symbol = jq_symbol.replace('XSHE', 'SZ').replace('XSHG', 'SH')
ts_symbol = '000001.SH'

# 交易日
today = datetime.datetime.today().strftime('%Y%m%d')
today_datetime = datetime.datetime.strptime(today, '%Y%m%d')
last_week_date = today_datetime - datetime.timedelta(days=30)
last_week_date_str = last_week_date.strftime('%Y%m%d')
df = pro.index_daily(ts_code='399006.SZ', start_date=last_week_date_str, end_date=today)
# 获取最近一次交易日的日期
days = df['trade_date']
# days = ['20241111', '20241110']
for day in days:
    c_date = day
    # 可取的字段:fields='ts_code,trade_date,turnover_rate,turnover_rate_f,pe,pe_ttm,pb'
    data = pro.index_dailybasic(trade_date=c_date, ts_code=ts_symbol, fields=['trade_date', 'pe', 'pb'])
    if len(data) > 0:
        print("data:{},pe:{},pb:{}".format(data.iloc[0][0], data.iloc[0][1], data.iloc[0][2]))
