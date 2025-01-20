import tushare as ts
import pandas as pd
from datetime import datetime, timedelta

from user_interface.stock_data_online.stock_index import key

# 设置 Tushare 的 API Token
ts.set_token(key)
pro = ts.pro_api()

# 获取当前日期
today = datetime.today().strftime('%Y%m%d')

# 计算10年前的日期
ten_years_ago = (datetime.today() - timedelta(days=10 * 365)).strftime('%Y%m%d')

# 获取指数数据，这里以000001.SH（上证指数）为例
# 注意：实际使用中，你可能需要根据具体指数代码进行修改
index_code = '000001.SH'
df = pro.index_daily(ts_code=index_code, start_date=ten_years_ago, end_date=today)

# 计算最高和最低值
high_value = df['high'].max()
low_value = df['low'].min()

print(f"近10年 {index_code} 的最高值为: {high_value}")
print(f"近10年 {index_code} 的最低值为: {low_value}")