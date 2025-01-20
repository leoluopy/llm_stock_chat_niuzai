import datetime

import threading
import urllib
import pandas as pd
from bs4 import BeautifulSoup
import baostock as bs
import pandas as pd
from dateutil.relativedelta import relativedelta
from py_search.search import baidu_search
from py_search.web_driver_exp.web_driver_util_url_shot import get_url_ROI
from llm_subsystem.llm_subsys_main import summarize_main_content


def html_h_and_p(html_content):
    tile_and_content = ""
    soup = BeautifulSoup(html_content, 'html.parser')

    # 提取所有的<p>标签内容
    p_tags = soup.find_all('p')
    p_contents = [tag.get_text() for tag in p_tags]

    # 提取所有的<h>标签内容
    h_tags = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    h_contents = [tag.get_text() for tag in h_tags]

    tile_and_content += "主要内容标题：\n"
    for content in h_contents:
        tile_and_content += content + "\n"

    tile_and_content += "主要内容详情：\n"
    for content in p_contents:
        tile_and_content += content + "\n"

    # print(tile_and_content)
    return tile_and_content


def date_to_words(date):
    # 定义月份名称
    months = [
        "一月", "二月", "三月", "四月", "五月", "六月",
        "七月", "八月", "九月", "十月", "十一月", "十二月"
    ]

    # 获取日期的各个部分
    day = date.day
    month = months[date.month - 1]
    year = date.year

    # 拼接成文字描述
    date_str = f"{year}年{month}{day}日"

    return date_str


def get_today_date_in_words() -> str:
    """
    get today's date string
    :return: today's date string, eg: '今天是:2014年10月10日'
    """
    # 获取今天的日期
    today = datetime.datetime.today()

    # 将日期转换为文字描述
    return "今天是：" + date_to_words(today) + "\n"


def get_index_pe_trend_line_chart_and_comment(index_name: str) -> str:
    """
    given index name, return the index PE trend line chart 、PE trend description、PE peak value percentage description.
    :param index_name: index name can only be["创业板","科创板","深证成指","上证综指"]
    :return:  return the index PE trend line chart 、PE trend description、PE peak value percentage description.
    """
    comment_str = ""
    im_char_base64 = ""
    if "创业板" in index_name:
        im_char_base64, comment_str = get_url_ROI(url='https://legulegu.com/stockdata/cybPE')
    elif "科创" in index_name:
        im_char_base64, comment_str = get_url_ROI(url='https://legulegu.com/stockdata/ke-chuang-ban-pe')
    elif "深证" in index_name:
        im_char_base64, comment_str = get_url_ROI(url='https://legulegu.com/stockdata/shanghaiPE')
    elif "上证" in index_name:
        im_char_base64, comment_str = get_url_ROI(url='https://legulegu.com/stockdata/shenzhenPE')
    else:
        pass

    return (comment_str, {'pe_chart_base64': im_char_base64})


def get_recent_10_years_index_basic_info(index_name: str, index_code: str) -> str:
    """
    given index name 、index code, return the basic info of index for recent 10 years, basic info has index close price, trade volume, trade amount, trade chg
    :param index_name: stock index name
    :param index_code: stock index code
    :return:  return the basic info of index for recent 10 years, basic info has index close price, trade volume, trade amount, trade chg
    """
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:' + lg.error_code)
    print('login respond  error_msg:' + lg.error_msg)
    today = datetime.datetime.today()
    end_date = f"{today.year}-{today.month}-{today.day}"
    last_10year_today = today - relativedelta(years=10)
    start_date = f"{last_10year_today.year}-{last_10year_today.month}-{last_10year_today.day}"

    # 详细指标参数，参见“历史行情指标参数”章节；“周月线”参数与“日线”参数不同。
    # 周月线指标：date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg
    rs = bs.query_history_k_data_plus(index_code, "date,close,volume,amount,pctChg",
                                      start_date=start_date, end_date=end_date, frequency="m")
    print('query_history_k_data_plus respond error_code:' + rs.error_code)
    print('query_history_k_data_plus respond  error_msg:' + rs.error_msg)

    # 打印结果集
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())

    df_raw = pd.DataFrame(data_list, columns=rs.fields)
    df = pd.DataFrame()
    df['日期'] = df_raw['date']
    df['价格'] = df_raw['close']
    df['成交量（股）'] = df_raw['volume']
    df['成交额（元）'] = df_raw['amount']
    df['涨跌幅'] = df_raw['pctChg']
    # df['股息率 （%）'] = df['dv_ratio']
    # df['流通股本（万股）'] = df['float_share']
    # df['自由流通股本（万股）'] = df['free_share']
    # df['总市值 （万元）'] = df['total_mv']
    # df['流通市值（万元）'] = df['circ_mv']ss

    basic_info_dataframe = df
    # chart_im_data = plot_data(df, '价格', tile=index_name)

    #### 结果集输出到csv文件 ####
    # result.to_csv("./history_A_stock_k_data.csv", index=False)
    basic_info_comment_str = f"{index_name}基本信息：\n"
    basic_info_comment_str += basic_info_dataframe.to_string()
    print(basic_info_comment_str)
    print("records number:{}".format(len(data_list)))
    #### 登出系统 ####
    bs.logout()
    return (basic_info_comment_str, {'records_num': len(data_list), 'data_frame': df})

    # 登出系统
    bs.logout()


def get_recent_10_years_corporation_basic_info(corporation_name: str, corporation_code: str) -> str:
    """
    given corporation name 、corporation code, return the basic info of company for recent 10 years, basic info has company close price, trade volume, trade amount, trade turn, chg， pe, pb
    :param corporation_name: stock corporation name
    :param corporation_code: stock corporation code
    :return: the basic info of company for recent 10 years, basic info has company close price, trade volume, trade amount, trade turn, chg， pe, pb
    """
    # Ref
    # http://baostock.com/baostock/index.php/A%E8%82%A1K%E7%BA%BF%E6%95%B0%E6%8D%AE
    #### 登陆系统 ####
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:' + lg.error_code)
    print('login respond  error_msg:' + lg.error_msg)

    #### 获取沪深A股历史K线数据 ####
    # 详细指标参数，参见“历史行情指标参数”章节；“分钟线”参数与“日线”参数不同。“分钟线”不包含指数。
    # 分钟线指标：date,time,code,open,high,low,close,volume,amount,adjustflag
    # 周月线指标：date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg
    today = datetime.datetime.today()
    end_date = f"{today.year}-{today.month}-{today.day}"
    last_10year_today = today - relativedelta(years=10)
    start_date = f"{last_10year_today.year}-{last_10year_today.month}-{last_10year_today.day}"

    rs = bs.query_history_k_data_plus(
        corporation_code,
        # "date,close,volume,amount,turn,pctChg,peTTM,pbMRQ",
        "date,close,volume,amount,turn,pctChg,peTTM,pbMRQ",
        start_date=start_date, end_date=end_date, frequency="d")
    print('query_history_k_data_plus respond error_code:' + rs.error_code)
    print('query_history_k_data_plus respond  error_msg:' + rs.error_msg)

    #### 打印结果集 ####
    data_list = []
    cnt = 0
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        row_data = rs.get_row_data()
        if cnt % 30 == 0:
            data_list.append(row_data)
        cnt += 1

    df_raw = pd.DataFrame(data_list, columns=rs.fields)
    df = pd.DataFrame()
    df['日期'] = df_raw['date']
    df['价格'] = df_raw['close']
    df['成交量（股）'] = df_raw['volume']
    df['成交额（元）'] = df_raw['amount']
    df['换手率（%）'] = df_raw['turn']
    df['市盈率'] = df_raw['peTTM']
    df['市净率'] = df_raw['pbMRQ']
    df['涨跌幅'] = df_raw['pctChg']
    # df['股息率 （%）'] = df['dv_ratio']
    # df['流通股本（万股）'] = df['float_share']
    # df['自由流通股本（万股）'] = df['free_share']
    # df['总市值 （万元）'] = df['total_mv']
    # df['流通市值（万元）'] = df['circ_mv']ss

    basic_info_dataframe = df
    # chart_im_data = plot_data(df, '价格', tile=corporation_name)

    #### 结果集输出到csv文件 ####
    # result.to_csv("./history_A_stock_k_data.csv", index=False)
    basic_info_comment_str = f"{corporation_name}基本信息：\n"
    basic_info_comment_str += basic_info_dataframe.to_string()
    print(basic_info_comment_str)
    print("records number:{}".format(len(data_list)))
    #### 登出系统 ####
    bs.logout()
    return (basic_info_comment_str, {'records_num': len(data_list), 'data_frame': df})


def get_recent_30_days_index_basic_info(index_name: str, index_code: str) -> str:
    """
    given index name 、index code, return the basic info of index for recent 30 days, basic info has index close price, trade volume, trade amount, trade chg
    :param index_name: stock index name
    :param index_code: stock index code
    :return:  return the basic info of index for recent 30 days, basic info has index close price, trade volume, trade amount, trade chg
    """
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:' + lg.error_code)
    print('login respond  error_msg:' + lg.error_msg)
    today = datetime.datetime.today()
    end_date = f"{today.year}-{today.month}-{today.day}"
    last_month_today = today - relativedelta(months=1)
    start_date = f"{last_month_today.year}-{last_month_today.month}-{last_month_today.day}"

    # 详细指标参数，参见“历史行情指标参数”章节；“周月线”参数与“日线”参数不同。
    # 周月线指标：date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg
    rs = bs.query_history_k_data_plus(index_code, "date,close,volume,amount,pctChg",
                                      start_date=start_date, end_date=end_date, frequency="d")
    print('query_history_k_data_plus respond error_code:' + rs.error_code)
    print('query_history_k_data_plus respond  error_msg:' + rs.error_msg)

    # 打印结果集
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())

    df_raw = pd.DataFrame(data_list, columns=rs.fields)
    df = pd.DataFrame()
    df['日期'] = df_raw['date']
    df['价格'] = df_raw['close']
    df['成交量（股）'] = df_raw['volume']
    df['成交额（元）'] = df_raw['amount']
    df['涨跌幅'] = df_raw['pctChg']
    # df['股息率 （%）'] = df['dv_ratio']
    # df['流通股本（万股）'] = df['float_share']
    # df['自由流通股本（万股）'] = df['free_share']
    # df['总市值 （万元）'] = df['total_mv']
    # df['流通市值（万元）'] = df['circ_mv']ss

    basic_info_dataframe = df
    # chart_im_data = plot_data(df, '价格', tile=index_name)

    #### 结果集输出到csv文件 ####
    # result.to_csv("./history_A_stock_k_data.csv", index=False)
    basic_info_comment_str = f"{index_name}基本信息：\n"
    basic_info_comment_str += basic_info_dataframe.to_string()
    print(basic_info_comment_str)
    print("records number:{}".format(len(data_list)))
    #### 登出系统 ####
    bs.logout()
    return (basic_info_comment_str, {'records_num': len(data_list), 'data_frame': df})

    # 登出系统
    bs.logout()


def get_recent_30_days_corporation_basic_info(corporation_name: str, corporation_code: str) -> str:
    """
    given corporation name 、corporation code, return the basic info of company for recent 30 days, basic info has company close price, trade volume, trade amount, trade turn, chg， pe, pb
    :param corporation_name: stock corporation name
    :param corporation_code: stock corporation code
    :return: the basic info of company for recent 30 days, basic info has company close price, trade volume, trade amount, trade turn, chg， pe, pb
    """
    # Ref
    # http://baostock.com/baostock/index.php/A%E8%82%A1K%E7%BA%BF%E6%95%B0%E6%8D%AE
    #### 登陆系统 ####
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:' + lg.error_code)
    print('login respond  error_msg:' + lg.error_msg)

    #### 获取沪深A股历史K线数据 ####
    # 详细指标参数，参见“历史行情指标参数”章节；“分钟线”参数与“日线”参数不同。“分钟线”不包含指数。
    # 分钟线指标：date,time,code,open,high,low,close,volume,amount,adjustflag
    # 周月线指标：date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg
    today = datetime.datetime.today()
    end_date = f"{today.year}-{today.month}-{today.day}"
    last_month_today = today - relativedelta(months=1)
    start_date = f"{last_month_today.year}-{last_month_today.month}-{last_month_today.day}"

    rs = bs.query_history_k_data_plus(
        corporation_code,
        # "sz.399006",
        # "sh.688981",
        # "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
        "date,close,volume,amount,turn,pctChg,peTTM,pbMRQ",
        start_date=start_date, end_date=end_date,
        frequency="d", adjustflag="3")
    print('query_history_k_data_plus respond error_code:' + rs.error_code)
    print('query_history_k_data_plus respond  error_msg:' + rs.error_msg)

    #### 打印结果集 ####
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())

    df_raw = pd.DataFrame(data_list, columns=rs.fields)
    df = pd.DataFrame()
    df['日期'] = df_raw['date']
    df['价格'] = df_raw['close']
    df['成交量（股）'] = df_raw['volume']
    df['成交额（元）'] = df_raw['amount']
    df['换手率（%）'] = df_raw['turn']
    df['市盈率'] = df_raw['peTTM']
    df['市净率'] = df_raw['pbMRQ']
    df['涨跌幅'] = df_raw['pctChg']
    # df['股息率 （%）'] = df['dv_ratio']
    # df['流通股本（万股）'] = df['float_share']
    # df['自由流通股本（万股）'] = df['free_share']
    # df['总市值 （万元）'] = df['total_mv']
    # df['流通市值（万元）'] = df['circ_mv']ss

    basic_info_dataframe = df
    # chart_im_data = plot_data(df, '价格', tile=corporation_name)

    #### 结果集输出到csv文件 ####
    # result.to_csv("./history_A_stock_k_data.csv", index=False)
    basic_info_comment_str = f"{corporation_name}基本信息：\n"
    basic_info_comment_str += basic_info_dataframe.to_string()
    print(basic_info_comment_str)
    print("records number:{}".format(len(data_list)))
    #### 登出系统 ####
    bs.logout()
    return (basic_info_comment_str, {'records_num': len(data_list), 'data_frame': df})


def search_internet_summarize(key_words: str) -> str:
    """
    search internet for keywords , get the summarized content and reference url
    :param key_words: keywords for search
    :return: summarized content and reference url
    """
    if "股市" not in key_words:
        key_words = "股市 " + key_words
    summarized_content = ""
    search_results = baidu_search(key_words)
    thread_contents = {}
    threads = {}
    launched_thread_cnt = 0
    for result in search_results:
        try:
            Head = (f'\n标题: {result["title"]}, 链接: {result["link"]}')
            # Head = (f'\n标题: {result["title"]}, 链接: ')
            with urllib.request.urlopen(result["link"]) as response:
                # 读取网页内容
                html_content = response.read()
                title_content = html_h_and_p(html_content)

                if launched_thread_cnt > 2:
                    break
                elif len(title_content) > 0:
                    print("Analysing:{}".format(Head))
                    thread_contents[launched_thread_cnt] = Head + "\n"
                    # summary = summarize_main_content(result["title"], tile_content, [])
                    threads[launched_thread_cnt] = (threading.Thread(target=summarize_main_content,
                                                                     args=(
                                                                         result["title"], title_content, [],
                                                                         thread_contents,
                                                                         launched_thread_cnt)))
                    threads[launched_thread_cnt].start()
                    launched_thread_cnt += 1
                else:
                    pass
                # print(summary)

        except Exception as e:
            print(e)

    for i in range(len(threads)):
        if threads.get(i) is not None:
            threads[i].join()
            summarized_content += thread_contents[i]
    # print("======")
    # print(summarized_content)
    return summarized_content


if __name__ == '__main__':
    #
    # print(get_recent_30_days_corporation_basic_info("中芯国际", "sh.688981"))
    # get_recent_30_days_index_basic_info("科创", "sh.000688")
    # get_recent_30_days_index_basic_info("上证", "sh.000001")
    # get_recent_30_days_index_basic_info("创业板指数", "sz.399006")
    # get_recent_10_years_index_basic_info("上证", "sh.000001")
    get_recent_10_years_corporation_basic_info("中芯国际", "sh.688981")
    # get_recent_10_years_corporation_basic_info("平安科技", "sz.000001")

    # 假设你的 DataFrame 已经存在，并且名为 df
    # 这里是示例数据，你可以替换成你的实际数据
    # data = {
    #     '日期': ['2023-10-01', '2023-10-02', '2023-10-03', '2023-10-04', '2023-10-05'],
    #     '价格': [100, 105, 102, 108, 110],
    #     '成交量（股）': [1000, 1500, 1200, 1300, 1400],
    #     '成交额（元）': [100000, 157500, 122400, 137800, 154000],
    #     '换手率（%）': [1.0, 1.5, 1.2, 1.3, 1.4],
    #     '市盈率': [20, 22, 21, 23, 24],
    #     '市净率': [2.5, 2.6, 2.55, 2.65, 2.7],
    #     '涨跌幅': [0.01, 0.02, -0.01, 0.03, 0.02]
    # }
    # df = pd.DataFrame(data)
    # df['日期'] = pd.to_datetime(df['日期'])  # 确保日期是 datetime 类型
    # plot_data(df, '价格', show=True)  # 你可以传入不同的字段名，例如 '成交量（股）'、'成交额（元）' 等
