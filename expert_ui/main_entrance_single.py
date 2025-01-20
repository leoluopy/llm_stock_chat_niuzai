# websocket_server.py
import asyncio
import base64
import io
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


async def handler(websocket, path):
    session_id = str(websocket.id)
    print("Session {} start".format(session_id))
    async for message in websocket:
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
                await websocket.send(buffer)
            await websocket.send("EOS")
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
                await websocket.send(buffer)

            prefix_str = buffer + "\n"
            for part in summary_answer(message, tool_call_data.ref_data, history_msg_wo_meta):
                buffer = prefix_str + part
                await websocket.send(buffer)

            if tool_call_data.ref_data is not None:
                buffer = prefix_str + buffer + "\n" + "参考信息：\n{}".format(tool_call_data.ref_data)
                await websocket.send(buffer)
            await websocket.send("EOS")

        print(" GENERTAED ALL:")
        print(buffer)
        sys.stdout.flush()
        # {'role': 'user', 'content': '市值是什么'},
        #
        # {'role': 'assistant', 'content':
        history_msg_wo_meta.extend([{'role': 'assistant', 'content': f'{buffer}'}])
        history_data = pickle.dumps(history_msg_wo_meta)
        (threading.Thread(target=insert_into_stock_history,
                          args=(session_id, message, buffer, history_data))).start()


# 启动WebSocket服务器
start_server = websockets.serve(handler, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
print("WebSocket server started at ws://localhost:8765")
asyncio.get_event_loop().run_forever()
