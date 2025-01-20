import asyncio

import ssl
import os
import pickle
import sys
import threading
import time

import numpy as np
import websockets
from matplotlib import pyplot as plt

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../../../")

from user_interface.stock_expert.llm_subsystem.llm_subsys_main import query_classify, general_answer, summary_answer
from user_interface.stock_expert.stock_chat import ToolCallData, get_tool_call_ref
from user_interface.stock_expert.insert_query_stock_his import query_latest_stock_history, insert_into_stock_history


def response(websocket, message):
    async def socket_respond(response_str, websocket):
        await websocket.send(response_str)

    session_id = str(websocket.id)
    user_input = message.strip()
    print(f"Received from client: {user_input}")

    latest_record = query_latest_stock_history(session_id)
    if latest_record:
        print("Latest record for session '{}':".format(session_id))
        for key, value in latest_record.items():
            if key != 'his':
                print("{}: {}".format(key, value))
            else:
                history_msg_wo_meta = pickle.loads(value)
    else:
        history_msg_wo_meta = []

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
            asyncio.run(socket_respond(buffer, websocket))
        asyncio.run(socket_respond("EOS", websocket))
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
            asyncio.run(socket_respond(buffer, websocket))

        prefix_str = buffer + "\n"
        for part in summary_answer(message, tool_call_data.ref_data, history_msg_wo_meta):
            buffer = prefix_str + part
            asyncio.run(socket_respond(buffer, websocket))
        asyncio.run(socket_respond("EOS", websocket))

        if tool_call_data.ref_data is not None and (
                'https' in tool_call_data.ref_data or 'http' in tool_call_data.ref_data):
            buffer = prefix_str + buffer + "\n" + "参考信息：\n{}".format(tool_call_data.ref_data)
            # asyncio.run(socket_respond(buffer, websocket))

            split_msgs = tool_call_data.ref_data.split("标题:");
            for split_msg in split_msgs:
                if len(split_msg) < 10:
                    continue
                asyncio.run(socket_respond("标题:" + split_msg, websocket))
                asyncio.run(socket_respond("EOS", websocket))

        # asyncio.run(socket_respond("EOS", websocket))

        if len(tool_call_data.ref_charts) != 0:
            for chart_data in tool_call_data.ref_charts:
                asyncio.run(socket_respond(chart_data, websocket))
            asyncio.run(socket_respond("EOS", websocket))

    print(" GENERTAED DONE:")
    sys.stdout.flush()
    history_msg_wo_meta.extend([{'role': 'assistant', 'content': f'{buffer}'}])
    history_data = pickle.dumps(history_msg_wo_meta)
    (threading.Thread(target=insert_into_stock_history,
                      args=(session_id, message, buffer, history_data))).start()


async def handler(websocket, path):
    try:
        session_id = str(websocket.id)
        print("Session {} start".format(session_id))
        async for message in websocket:
            (threading.Thread(target=response, args=(websocket, message))).start()
    finally:
        session_id = str(websocket.id)
        print("Session {} CLOSED".format(session_id))


# SSL/TLS 证书文件路径
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
root_path = os.path.dirname(
    os.path.abspath(__file__)) + "/../../../user_interface/chat_basic_css_html/web_socket_response/wss_node_js/"
ssl_context.load_cert_chain(root_path + '/nginx-selfsigned.crt', root_path + '/nginx-selfsigned.key')

# 启动WebSocket服务器（使用WSS）
start_server = websockets.serve(handler, "localhost", 5443, ssl=ssl_context)

asyncio.get_event_loop().run_until_complete(start_server)
print("WebSocket server started at wss://localhost:5443")
asyncio.get_event_loop().run_forever()
