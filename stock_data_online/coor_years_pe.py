import pandas as pd
from datetime import datetime, timedelta
import tushare as ts

from user_interface.stock_data_online.stock_index import key

# 设置Tushare的API Token
ts.set_token(key)
pro = ts.pro_api()


def get_years_pe_data_for_corporation(stock_code, years=10):
    # 获取当前日期
    today = datetime.today().strftime('%Y%m%d')

    # 计算10年前的日期
    ten_years_ago = (datetime.today() - timedelta(days=years * 365)).strftime('%Y%m%d')

    # 调用pro.daily_basic函数获取数据
    # 注意：这里的pro.daily_basic函数需要事先定义或导入，假设它来自某个金融数据API
    df_data_pe_pb = pro.daily_basic(ts_code=stock_code, start_date=ten_years_ago, end_date=today,
                                    fields=['trade_date', 'pe', 'pb'])

    return df_data_pe_pb, df_data_pe_pb.iloc[0][0]


if __name__ == '__main__':
    # 示例使用
    # 注意：在实际使用前，请确保已经正确配置并导入了pro（如Tushare等API）
    # 并且你的API key（如果有的话）已经正确设置
    # stock_code = '000001.SZ'  # 例如：'000001.SZ'
    stock_code = '601398.SH'
    pe_data, last_trade_day = get_years_pe_data_for_corporation(stock_code)
    print(pe_data)
