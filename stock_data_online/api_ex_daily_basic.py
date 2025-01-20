import tushare as ts
import pandas as pd
import datetime

from user_interface.stock_data_online.stock_index import key

# 设置Tushare的API Token
ts.set_token(key)
pro = ts.pro_api()

# 定义股票代码和开始日期（10年前）
stock_code = '000001.SZ'  # 示例：平安银行
start_date = (datetime.datetime.now() - datetime.timedelta(days=365 * 10)).strftime('%Y%m%d')
end_date = datetime.datetime.now().strftime('%Y%m%d')

# 获取个股的市盈率数据
pe_df = pro.daily_basic(ts_code=stock_code, start_date=start_date, end_date=end_date)

# 由于daily_basic不包含PE数据，我们需要使用其他接口，比如financial_indicator
pe_indicator_df = pro.fina_indicator(ts_code=stock_code, start_date=start_date, end_date=end_date, indicators='pe')

print(pe_df.columns)
print(pe_indicator_df.columns)

# Index(['ts_code', 'trade_date', 'close', 'turnover_rate', 'turnover_rate_f',
#        'volume_ratio', 'pe', 'pe_ttm', 'pb', 'ps', 'ps_ttm', 'dv_ratio',
#        'dv_ttm', 'total_share', 'float_share', 'free_share', 'total_mv',
#        'circ_mv'],
#       dtype='object')
# Index(['ts_code', 'ann_date', 'end_date', 'eps', 'dt_eps', 'total_revenue_ps',
#        'revenue_ps', 'capital_rese_ps', 'surplus_rese_ps', 'undist_profit_ps',
#        ...
#        'ocf_yoy', 'roe_yoy', 'bps_yoy', 'assets_yoy', 'eqt_yoy', 'tr_yoy',
#        'or_yoy', 'q_sales_yoy', 'q_op_qoq', 'equity_yoy'],
#       dtype='object', length=108)
