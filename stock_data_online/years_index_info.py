import os
import sys
import threading
from datetime import datetime, timedelta

import pandas as pd
import tushare as ts

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../../")
from user_interface.stock_data_online.stock_index import key

pro = ts.pro_api(key)


def get_dates_weekly(years=10):
    # 获取当前日期
    today = datetime.now()

    # 计算起始日期：当前日期减去10年
    start_date = today - timedelta(days=years * 365.25)  # 使用365.25来考虑闰年
    # 调整起始日期到周的第一天（例如，取周一）
    start_date = start_date - timedelta(days=start_date.weekday())

    # 初始化日期列表
    dates = []

    # 循环生成每周的日期
    current_date = start_date
    while current_date <= today:
        # 格式化日期为YYYYMMDD
        date_str = current_date.strftime('%Y%m%d')
        dates.append(date_str)
        # 增加一周
        current_date += timedelta(days=7)

    return dates


def func_get_daily_basic(c_date, index_code, data_dict):
    data = pro.index_dailybasic(trade_date=c_date, ts_code=index_code, fields=['trade_date', 'pe', 'pb'])
    if len(data) > 0:
        # datas.append((data.iloc[0][0], data.iloc[0][1], data.iloc[0][2]))
        # print("date:{},pe:{},pb:{}".format(data.iloc[0][0], data.iloc[0][1], data.iloc[0][2]))
        data_dict[c_date] = (data.iloc[0][0], data.iloc[0][1], data.iloc[0][2])


def get_index_pe_pb_for_years(index_name, index_code, years=10):
    days = get_dates_weekly(years)
    datas = []
    datas_dict = {}
    datas_thread = {}
    for day in days:
        c_date = day
        # 可取的字段:fields='ts_code,trade_date,turnover_rate,turnover_rate_f,pe,pe_ttm,pb'
        # data = pro.index_dailybasic(trade_date=c_date, ts_code=index_code, fields=['trade_date', 'pe', 'pb'])
        # if len(data) > 0:
        #     datas.append((data.iloc[0][0], data.iloc[0][1], data.iloc[0][2]))
        #     print("date:{},pe:{},pb:{}".format(data.iloc[0][0], data.iloc[0][1], data.iloc[0][2]))
        datas_thread[day] = (threading.Thread(target=func_get_daily_basic,
                                              args=(c_date, index_code, datas_dict)))
        datas_thread[day].start()

    for key, thread_val in datas_thread.items():
        thread_val.join()

    for day in days:
        if datas_dict.get(day) is not None:
            datas.append(datas_dict[day])
    df = pd.DataFrame(datas, columns=['trade_date', 'pe', 'pb'])
    # df_str = f"{index_name} {years}年pe和pb统计:\n" + str(df)
    # print(df_str)
    return df, days[-1]


def calculate_pe_lower_ratio(df, specified_date):
    # 提取指定日期的pe值
    specified_pe = df.loc[df['trade_date'] == specified_date, 'pe'].values[0]

    # 找出指定日期之前pe值低于指定日期pe值的天数
    lower_pe_count = (df['pe'] < specified_pe).sum()

    # 计算指定日期之前的总天数
    total_days = df.shape[0]

    # 计算比例
    lower_pe_ratio = int((lower_pe_count / total_days) * 100)

    return lower_pe_ratio


if __name__ == '__main__':
    # 获取过去10年，每周一个的日期
    # dates_array = get_dates_weekly(10)
    # print(dates_array)
    print(get_index_pe_pb_for_years("上证", "000001.SH", 5))
