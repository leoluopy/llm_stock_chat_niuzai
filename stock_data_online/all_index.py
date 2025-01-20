import tushare as ts

pro = ts.pro_api()
df = pro.index_basic(market='SW')
print(df.to_string())