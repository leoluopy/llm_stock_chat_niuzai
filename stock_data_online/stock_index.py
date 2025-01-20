import tushare as ts
import datetime

key='1a1b4cdeb8459be8b428b1788c5677583f361fe7f0cf800fd556972f'
# 设置你的Tushare API Token
ts.set_token(key)

if __name__ == '__main__':

    # 名称	类型	描述
    # ts_code	str	TS指数代码
    # trade_date	str	交易日
    # close	float	收盘点位
    # open	float	开盘点位
    # high	float	最高点位
    # low	float	最低点位
    # pre_close	float	昨日收盘点
    # change	float	涨跌点
    # pct_chg	float	涨跌幅（%）
    # vol	float	成交量（手）
    # amount	float	成交额（千元）

    pro = ts.pro_api()
    # df = pro.index_daily(ts_code='399300.SZ')
    #或者按日期取
    import datetime

    # 获取今天的日期
    today = datetime.datetime.today().strftime('%Y%m%d')
    print(f"Today's date: {today}")

    # 将今天的日期转换为 datetime 对象以便进行计算
    today_datetime = datetime.datetime.strptime(today, '%Y%m%d')

    # 计算上一周的日期（即今天减去7天）
    last_week_date = today_datetime - datetime.timedelta(days=30)

    # 将计算得到的日期格式化为字符串
    last_week_date_str = last_week_date.strftime('%Y%m%d')
    print(f"Last week's date: {last_week_date_str}")

    # df = pro.index_daily(ts_code='399300.SZ', start_date=last_week_date_str, end_date=today)
    df = pro.index_daily(ts_code='399006.SZ', start_date=last_week_date_str, end_date=today)

    print(df.to_string())
    print(df[['trade_date','close']].to_string(index=False))
