import copy
import re
import threading
import time
from typing import Dict, List

import gradio as gr
import sys, os

from pandas import DataFrame

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../../")

from user_interface.stock_expert.llm_subsystem.stock_util import load_func_call_list, \
    json_to_call_node, plot_data, FuncCallNode
from user_interface.stock_expert.insert_thread import insert_record_into_database
from user_interface.stock_expert.llm_subsystem.llm_subsys_main import general_answer, query_classify, cot_rewrite, \
    tool_call, summary_answer, query_chart_classify
from user_interface.stock_data_online.baoStock.price_vol_amount_pe_pb import get_recent_10_years_index_basic_info, \
    get_recent_10_years_corporation_basic_info, get_recent_30_days_index_basic_info, \
    get_recent_30_days_corporation_basic_info


def process_history(history):
    history = copy.deepcopy(history)
    for item in history:
        item.pop('metadata', None)
    return history


class ToolCallData:
    def __init__(self):
        self.has_data = False
        self.ref_data = None
        self.lock = threading.Lock()
        self.ref_charts = []


def post_process_for_chart(node: FuncCallNode, message: str, df_data_frame: DataFrame):
    if node.caller in [get_recent_10_years_index_basic_info, get_recent_10_years_corporation_basic_info,
                       get_recent_30_days_index_basic_info, get_recent_30_days_corporation_basic_info]:
        classify_ret = query_chart_classify(message)
        if node.params.get('corporation_name') is not None:
            title_name = node.params.get('corporation_name')
        elif node.params.get('index_name') is not None:
            title_name = node.params.get('index_name')
        else:
            title_name = ""

        chart_im_data = ""
        if 'A' in classify_ret and (df_data_frame.get('价格') is not None):
            chart_im_data = plot_data(df_data_frame, '价格', tile=title_name)
        elif 'B' in classify_ret and (df_data_frame.get('市盈率') is not None):
            chart_im_data = plot_data(df_data_frame, '市盈率', tile=title_name)
        elif 'C' in classify_ret and (df_data_frame.get('市净率') is not None):
            chart_im_data = plot_data(df_data_frame, '市净率', tile=title_name)
        else:
            pass
        return chart_im_data
    else:
        return None


def get_tool_call_ref(message: str, history: List[{}], tool_call_data: ToolCallData):
    tool_call_json_str = tool_call(message, history)
    print("TOOL CALL JSON: " + tool_call_json_str)
    json_calls = load_func_call_list(tool_call_json_str)
    call_nodes = json_to_call_node(json_calls)
    tool_call_ref_str = ""
    tool_call_ref_charts = []
    for node in call_nodes:
        print("\nCalling {} prams:{}\n".format(node.func_name, node.params))
        ret = node.call()
        if isinstance(ret, tuple):
            tool_call_ref_str += ret[0] + "\n"
            if ret[1].get('data_frame') is not None:
                chart_im_data = post_process_for_chart(node, message, ret[1]['data_frame'])
                tool_call_ref_charts.append(chart_im_data)
            if ret[1].get('pe_chart_base64') is not None:
                chart_im_data = ret[1]['pe_chart_base64']
                tool_call_ref_charts.append(chart_im_data)
        else:
            tool_call_ref_str += ret
        print(ret)
    with tool_call_data.lock:
        tool_call_data.ref_data = tool_call_ref_str
        tool_call_data.has_data = True
        tool_call_data.ref_charts = tool_call_ref_charts


def generate_wrapper(message: str, history: List[List[str]]) -> str:
    history_msg_wo_meta = process_history(history)
    buffer = ""
    prefix_str = ""
    # Classify
    print("User ask: {}".format(message))
    print("History: {}".format(history_msg_wo_meta))
    classify_ret = query_classify(message)
    print("Classify Ret:{}".format(classify_ret))
    if 'A' in classify_ret:
        for part in general_answer(message, history_msg_wo_meta):
            buffer = prefix_str + part
            yield buffer

    else:
        tool_call_data = ToolCallData()
        (threading.Thread(target=get_tool_call_ref, args=(message, history_msg_wo_meta, tool_call_data))).start()
        for i in range(20):
            buffer = "正在搜索互联网和数据库信息：{}%".format(i * 5)
            time.sleep(1.5)
            with tool_call_data.lock:
                flag = tool_call_data.has_data
            if flag is True:
                buffer = ""
                break
            yield buffer

        prefix_str = buffer + "\n"
        for part in summary_answer(message, tool_call_data.ref_data, history):
            buffer = prefix_str + part
            yield buffer

        if tool_call_data.ref_data is not None:
            if 'https' in tool_call_data.ref_data or 'http' in tool_call_data.ref_data:
                buffer = prefix_str + buffer + "\n" + "参考信息：\n{}".format(tool_call_data.ref_data)
                yield buffer

        print(" GENERTAED ALL:")
        print(buffer)
        sys.stdout.flush()
        (threading.Thread(target=insert_record_into_database,
                          args=(str(message), str(history), str(buffer)))).start()


if __name__ == "__main__":
    demo = gr.ChatInterface(
        fn=generate_wrapper,
        analytics_enabled=False,
        type="messages",
        examples=[
            "现在股市合适入场吗？",
            "今日大盘情况？",
            '美国大选对A股的影响 ',
            '推荐几只芯片股？ ',
            '创业板估值如何？ ',
            '科创板前途怎么样？ ',
            '医药板块当前趋势是什么？ ',
            '芯片板块怎么样？ ',
            '价值板块当前是低估值吗？',
            '10月前后的暴涨暴跌是怎么回事？ ',
            '特朗普最近出台了什么针对中国的新政策吗？对A股什么影响？ ',
            '中芯国际这家公司值得投资吗？ ',
            '给我推荐几只股票 ',
            '工商银行估值偏高不？ ',
            '大A整体市盈率是多少 ',
            'A股有多少支破净的公司 ',
            "市盈率是什么？",
            "如何判断公司基本面？",
            '瑞芯微最近走势',
            '从最近10年看创业板是低估的吗？',
        ],
        title="牛仔助手，问大盘、基金、个股趋势，问通用理财知识",
    )
    demo.launch(share=True)
