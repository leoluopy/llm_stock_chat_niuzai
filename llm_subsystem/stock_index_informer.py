import sys, os

import tushare as ts
import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../../")

from user_interface.stock_data_online.years_index_info import get_index_pe_pb_for_years, calculate_pe_lower_ratio
from user_interface.stock_data_online.coor_years_pe import get_years_pe_data_for_corporation

token = '1a1b4cdeb8459be8b428b1788c5677583f361fe7f0cf800fd556972f'
ts.set_token(token)
pro = ts.pro_api(token)


def get_corporation_pe_lower_than_today_ratio(corporation_name: str, corporation_code: str, years: int) -> float:
    """
    given corporation name 、corporation code and years , get the recent year's database,calculate the days percentage that the corporation's pe value lower than today
    :param corporation_name: stock corporation name
    :param corporation_code: stock corporation code
    :param years: years range time for calculate
    :return: percentage number (from 0-100)
    """
    df, last_trade_day = get_years_pe_data_for_corporation(corporation_code, years)
    pe_ratio_lower_than_today = calculate_pe_lower_ratio(df, last_trade_day)
    last_trade_day_pe = df.loc[df['trade_date'] == last_trade_day, 'pe'].values[0]
    comment_str = f"在过去的{years}年中，{corporation_name}({corporation_code})的PE水位线，低于最近一次交易日的比例有{pe_ratio_lower_than_today}%，这个数值越低说明公司股票越被低估，当前PE数值是：{last_trade_day_pe}"
    return comment_str


def get_index_pe_lower_than_today_ratio(index_name: str, index_code: str, years: int) -> float:
    """
    given index name 、index code and years , get the recent year's database,calculate the days percentage that the index's pe value lower than today
    :param index_name: stock index name
    :param index_code: stock index code
    :param years: years range time for calculate
    :return: percentage number (from 0-100)
    """
    df, last_trade_day = get_index_pe_pb_for_years(index_name, index_code, years)
    pe_ratio_lower_than_today = calculate_pe_lower_ratio(df, last_trade_day)
    last_trade_day_pe = df.loc[df['trade_date'] == last_trade_day, 'pe'].values[0]
    comment_str = f"在过去的{years}年中，{index_name}({index_code})的PE水位线，低于最近一次交易日的比例有{pe_ratio_lower_than_today}%，这个数值越低说明指数越被低估，当前PE数值是：{last_trade_day_pe}"
    return comment_str


def get_last_trade_date() -> str:
    """
    get the last trade date
    :return: last trade date
    """
    today = datetime.datetime.today().strftime('%Y%m%d')
    today_datetime = datetime.datetime.strptime(today, '%Y%m%d')
    last_week_date = today_datetime - datetime.timedelta(days=7)
    last_week_date_str = last_week_date.strftime('%Y%m%d')
    df = pro.index_daily(ts_code='399006.SZ', start_date=last_week_date_str, end_date=today)
    # 获取最近一次交易日的日期
    today = df['trade_date'].iloc[0]
    # print("last trade day is : {}".format(today))
    return today


def get_last_30_days_corporation_trade_info(corporation_name: str, corporation_code: str) -> str:
    """
    given corporation name 、corporation code , get the stock's close price,turn over rate and volume ratio from the recent 30 days
    :param corporation_name: stock corporation name
    :param corporation_code: stock corporation code
    :return: stock's close price,turn over rate and volume ratio from the recent 30 days
    """
    start_date = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y%m%d')
    end_date = datetime.datetime.now().strftime('%Y%m%d')
    df = pro.daily_basic(ts_code=corporation_code, start_date=start_date, end_date=end_date)
    df['日期'] = df['trade_date']
    df['价格'] = df['close']
    df['换手率（%）'] = df['turnover_rate']
    df['量比'] = df['volume_ratio']
    # df['市盈率'] = df['pe']
    # df['市净率'] = df['pb']
    # df['市销率'] = df['ps']
    # df['股息率 （%）'] = df['dv_ratio']
    # df['流通股本（万股）'] = df['float_share']
    # df['自由流通股本（万股）'] = df['free_share']
    # df['总市值 （万元）'] = df['total_mv']
    # df['流通市值（万元）'] = df['circ_mv']
    # print(df)
    str = f"{corporation_name} 近1个月走势如下：\n {df[['日期', '价格', '换手率（%）', '量比']].to_string(index=False)}"
    return str


# '399006.SZ'
def get_last_30_days_index_close_value(index_name: str, index_code: str) -> str:
    """
    given index name and index code , get the index close value for last 30 days
    :param index_name: stock index name
    :param index_code: stock index code
    :return: table string for dates and values
    """
    # 获取今天的日期
    today = datetime.datetime.today().strftime('%Y%m%d')
    # print(f"Today's date: {today}")
    # 将今天的日期转换为 datetime 对象以便进行计算
    today_datetime = datetime.datetime.strptime(today, '%Y%m%d')
    last_week_date = today_datetime - datetime.timedelta(days=30)
    last_week_date_str = last_week_date.strftime('%Y%m%d')
    # print(f"Last week's date: {last_week_date_str}")
    df = pro.index_daily(ts_code=index_code, start_date=last_week_date_str, end_date=today)
    # print(df.to_string())
    df['日期'] = df['trade_date']
    df['价格'] = df['close']
    # print(df)
    str = f"{index_name} 近1个月走势如下：\n {df[['日期', '价格']].to_string(index=False)}"
    return str



if __name__ == '__main__':
    # today_date_str = get_today_date_in_words()
    # print(today_date_str)
    print(get_last_trade_date())

    # print(get_last_30_days_index_close_value('创业板', '399006.SZ'))
    # print(get_last_30_days_index_close_value('上证指数', '000001.SH'))
    # get_percentage_lower_than_today('000001.SH')
    # get_percentage_lower_than_today('创业板', '399006.SZ')
    # print(search_internet_summarize("特朗普 AI芯片 影响"))
    # print(get_last_30_days_corporation_trade_info("平安银行", "000001.SZ"))
    pass
