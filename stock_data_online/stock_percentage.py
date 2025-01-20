import tushare as ts
import pandas as pd
from datetime import datetime, timedelta

from user_interface.stock_data_online.stock_index import key

# 设置 Tushare 的 API Token
ts.set_token(key)
pro = ts.pro_api()

today = datetime.today().strftime('%Y%m%d')
today_datetime = datetime.strptime(today, '%Y%m%d')
last_week_date = today_datetime - timedelta(days=7)
last_week_date_str = last_week_date.strftime('%Y%m%d')
df = pro.index_daily(ts_code='399006.SZ', start_date=last_week_date_str, end_date=today)
# 获取最近一次交易日的日期
today = df['trade_date'].iloc[0]
# today = '2023908'  # 使用指定日期，例如2023年10月10日

# 计算10年前的日期
ten_years_ago = (datetime.strptime(today, '%Y%m%d') - timedelta(days=10 * 365)).strftime('%Y%m%d')

# 获取指数数据，这里以000001.SH（上证指数）为例
index_code = '000001.SH'
df = pro.index_daily(ts_code=index_code, start_date=ten_years_ago, end_date=today)

# 确保数据按日期排序
df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
df = df.sort_values('trade_date')

# 获取今天的收盘价（注意：这里假设today是交易日，且数据中包含该日的数据）
today_close = df[df['trade_date'] == pd.to_datetime(today, format='%Y%m%d')]['close'].values[0]

# 计算低于今天收盘价的天数
below_today_count = (df['close'] < today_close).sum()

# 计算百分比
percentage_below_today = (below_today_count / len(df)) * 100

print(f"在今天（{today}）之前近10年内，{index_code} 的收盘价有 {percentage_below_today:.2f}% 的时间是低于今天的收盘价的。")
