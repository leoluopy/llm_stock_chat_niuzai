import sys, os
import json
import re

from bs4 import BeautifulSoup
import io
import base64
import os.path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from pandas.core.interchange.dataframe_protocol import DataFrame

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")

import stock_data_online.baoStock.price_vol_amount_pe_pb as tool_funcs
from llm_subsystem.stock_suffix import add_stock_exchange_suffix


class FuncCallNode:
    def __init__(self):
        self.caller = None
        self.func_name = ""
        self.params = None

    def call(self):
        return self.caller(**self.params)


def plot_data(df, column_name, show=False, tile=None):
    """
    绘制 DataFrame 的图表，横坐标为日期，纵坐标为指定的字段。

    参数:
    df (pd.DataFrame): 包含数据的 DataFrame。
    column_name (str): 要作为纵坐标的字段名。
    """
    font = FontProperties(fname=os.path.dirname(os.path.abspath(__file__)) + '/simhei.ttf', size=10)

    df['日期'] = pd.to_datetime(df['日期'])
    df[column_name] = pd.to_numeric(df[column_name], errors='coerce')
    if column_name not in df.columns:
        print(f"字段 {column_name} 不存在于 DataFrame 中。")
        return

    plt.figure(figsize=(10, 6))
    plt.plot(df['日期'], df[column_name], marker='o', linestyle='-', color='b')
    if tile is not None:
        plt.title(f'{tile}', fontproperties=font)
    plt.xlabel('日期', fontproperties=font)
    plt.ylabel(column_name, fontproperties=font)
    plt.grid(True)
    plt.xticks(rotation=45)  # 旋转日期标签，以便更清晰地显示
    plt.tight_layout()
    if show is True:
        plt.show()
    # Save the plot to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)

    # Convert the plot to base64
    plot_data = base64.b64encode(buf.getvalue()).decode('utf-8')
    image_data = f"data:image/png;base64,{plot_data}"
    return image_data


def load_func_call_list(call_json_str):
    start_pos = call_json_str.find('{')  # 找到第一个空行后的 '{'
    end_pos = call_json_str.rfind('}') + 1  # 找到最后一个 '}'（注意 +1 是为了包含 '}'）
    # 提取 JSON 数据块
    json_substring = call_json_str[start_pos:end_pos]
    data = json.loads(json_substring)
    # print(data)
    return data


def json_to_call_node(call_json_str):
    func_call_nodes = []
    tools_json_list = call_json_str['tools']
    for tool_json in tools_json_list:
        node = FuncCallNode()
        node.func_name = tool_json.get('tool')
        node.params = tool_json.get('tool_input', {})
        if node.params.get('index_code') is not None:
            node.params['index_code'] = add_stock_exchange_suffix(node.params['index_code'], for_cor=False)
        if node.params.get('corporation_code') is not None:
            node.params['corporation_code'] = add_stock_exchange_suffix(node.params['corporation_code'], for_cor=True)

        node.caller = getattr(tool_funcs, node.func_name, None)
        func_call_nodes.append(node)

    return func_call_nodes


if __name__ == '__main__':

    # json_string = 'xx{"name": "Alice", "age": 30, "city": "New York"}'
    # load_func_call_list(json_string)

    # 示例字符串，其中包含嵌套的 JSON 数据
    with open("./resources/functool_exam2.txt") as f:
        # with open("./resources/functool_example.txt") as f:
        text = f.read()
        json_calls = load_func_call_list(text)
        call_nodes = json_to_call_node(json_calls)
        # print(call_nodes)
        for node in call_nodes:
            print("calling {} prams:{}".format(node.func_name, node.params))
            ret = node.call()
            print("ret:{}".format(ret))
