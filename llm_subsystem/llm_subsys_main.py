import copy
import sys, os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")

from config_key import ConfigKey
from llm_subsystem.prompts_template import prompt_classify, prompt_cot, prompt_tool_call, \
    prompt_chart_classify


def query_chart_classify(message):
    buffer = ""
    from zhipuai import ZhipuAI

    prompt_sys = prompt_chart_classify

    client = ZhipuAI(api_key=f"{ConfigKey.zhipuai_key}")  # 请填写您自己的APIKey
    response = client.chat.completions.create(
        model="glm-4-flash",  # 请填写您要调用的模型名称
        messages=[
            {"role": "system",
             "content": f"{prompt_sys}"},
            {"role": "user",
             "content": f"用户输入是：\n{message}"},
        ],
        stream=False,
    )

    return response.choices[0].message.content


def query_classify(message):
    buffer = ""
    from zhipuai import ZhipuAI

    prompt_sys = prompt_classify

    client = ZhipuAI(api_key=f"{ConfigKey.zhipuai_key}")  # 请填写您自己的APIKey
    response = client.chat.completions.create(
        model="glm-4-flash",  # 请填写您要调用的模型名称
        messages=[
            {"role": "system",
             "content": f"{prompt_sys}"},
            {"role": "user",
             "content": f"用户输入是：\n{message}"},
        ],
        stream=False,
    )

    return response.choices[0].message.content


def cot_rewrite(message):
    buffer = ""
    from zhipuai import ZhipuAI

    prompt_sys = prompt_cot

    client = ZhipuAI(api_key=f"{ConfigKey.zhipuai_key}")

    llm_messages = [
        {"role": "system",
         "content": f"{prompt_sys}"},
        {"role": "user",
         "content": f"用户问题是：\n{message}"},
    ]
    response = client.chat.completions.create(
        model="glm-4-flash",  # 请填写您要调用的模型名称
        messages=llm_messages,
        stream=True,
    )

    for chunk in response:
        # print(chunk.choices[0].delta.content, end="")
        buffer = buffer + chunk.choices[0].delta.content
        yield buffer

    print(f"{cot_rewrite.__name__}\n {str(llm_messages)}")


def general_answer(message, history):
    buffer = ""
    from zhipuai import ZhipuAI
    history.extend([
        {"role": "system",
         "content": "你是一位股市分析与投资专家，总是能给出非常权威和有深度的投资与股票分析建议。你的回答需要保持简洁，保持在100个字以内。"},
        {"role": "user",
         "content": f"{message}"},
    ])
    client = ZhipuAI(api_key=f"{ConfigKey.zhipuai_key}")  # 请填写您自己的APIKey
    response = client.chat.completions.create(
        model="glm-4-flash",  # 请填写您要调用的模型名称
        messages=history,
        stream=True,
    )

    for chunk in response:
        # print(chunk.choices[0].delta.content, end="")
        buffer = buffer + chunk.choices[0].delta.content
        yield buffer


def summarize_main_content(title, message, history, out_dict, i):
    from zhipuai import ZhipuAI

    history.extend([
        {"role": "system",
         "content": "针对这一次回答，你是一位资深的媒体新闻工作者，总能从一段文字中提取重点信息，但是又不会遗漏关键信息"},
        {"role": "user",
         "content": f"""
已知新闻标题是：{title},100个字以内，总结不多于3条下面网页新闻中的核心内容：\n{message}\n
你必须按照下面的参考方式来回答，例如你可以如下方式回答：
‘
资讯<<xxx>>的主要内容如下：
1. xxxxxx
2. xxxxxx
3. xxxxxx
’
注意：你的输出不能大于100字，请简洁的回答
"""},
    ])
    client = ZhipuAI(api_key=f"{ConfigKey.zhipuai_key}")  # 请填写您自己的APIKey
    response = client.chat.completions.create(
        model="glm-4-flash",  # 请填写您要调用的模型名称
        messages=history,
        stream=False,
    )
    ret = response.choices[0].message.content
    # print(ret)
    # for chunk in response:
    #     print(chunk.choices[0].delta.content, end="")
    #     buffer = buffer + chunk.choices[0].delta.content
    #     yield buffer
    out_dict[i] = out_dict[i] + ret + "\n"
    return ret


def summary_answer(message, ref, history_in):
    buffer = ""
    from zhipuai import ZhipuAI
    history = [node for node in history_in if node['role'] not in "system"]

    history.extend([
        {"role": "system",
         "content": """
             你是一位股市分析与投资专家，总是能给出非常权威和有深度的投资与股票分析建议,你的回答应该按照如下格式：
             '根据已经查询到的数据库信息，xxx'
             注意：xxx请替换为你根据参考信息的实际分析内容
             如果用户让你画图、画表，你直接根据数据库的参考信息分析和回复即可，不用绘
             如果没有给你参考信息，你应该如下回答： 
             '暂时没有从数据库查询到参考信息，我们会留意你的问题，并添加和更新数据库'
             适当的列举关键的参考数据库或者网络搜索内容，你的回答需要保持简洁，保持在300个字以内,
             """
         },
        {"role": "assistant",
         "content": f"数据库可参考信息是:{ref}制"},
        {"role": "user",
         "content": f"结合历史问答过程，以及数据库信息，请回答问题 :\n{message}"},
    ])

    client = ZhipuAI(api_key=f"{ConfigKey.zhipuai_key}")  # 请填写您自己的APIKey
    response = client.chat.completions.create(
        model="glm-4-flash",  # 请填写您要调用的模型名称
        messages=history,
        stream=True,
    )

    for chunk in response:
        print(chunk.choices[0].delta.content, end="")
        buffer = buffer + chunk.choices[0].delta.content
        yield buffer


def tool_call(message, history_in):
    buffer = ""
    from zhipuai import ZhipuAI
    # history = copy.deepcopy(history_in)
    history = [node for node in history_in if node['role'] in "user"]
    prompt_sys = prompt_tool_call
    history.extend([
        {"role": "system",
         "content": f"{prompt_sys}"},
        {"role": "user",
         "content": f"User Query：\n{message}"},
    ])
    client = ZhipuAI(api_key=f"{ConfigKey.zhipuai_key}")  # 请填写您自己的APIKey
    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=history,
    )
    return response.choices[0].message.content


if __name__ == '__main__':
    for part in tool_call(
            """
    获取上证指数和深证成指今日的收盘点数和涨跌幅。
    查看主要行业板块的涨跌情况。
    分析今日市场成交量及北向资金流向。
    结合以上信息，给出今日大盘的整体情况。
        """, []):
        pass
