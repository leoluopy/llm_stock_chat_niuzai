from zhipuai import ZhipuAI
from config_key import ConfigKey

# class ConfigKey:
#     zhipuai_key="xxx"

client = ZhipuAI(api_key=f"{ConfigKey.zhipuai_key}")  # 请填写您自己的APIKey


# check your key at:
# https://open.bigmodel.cn/usercenter/apikeys

# messages = [
#     {"role": "user", "content": "作为一名营销专家，请为我的产品创作一个吸引人的口号"},
#     {"role": "assistant", "content": "当然，要创作一个吸引人的口号，请告诉我一些关于您产品的信息"},
#     {"role": "user", "content": "智谱AI开放平台"},
#     {"role": "assistant", "content": "点燃未来，智谱AI绘制无限，让创新触手可及！"},
#     {"role": "user", "content": "创作一个更精准且吸引人的口号"}
# ]
class LLMZhiPu:
    def chat(self,input_msg):
        self.messages.append({"role": "user", "content": f"{input_msg}"})
        response = client.chat.completions.create(
            # model="glm-4",
            model="glm-4-flash",
            messages=self.messages,
        )
        print(len(self.messages))
        print(response.choices[0].message.content)
        self.messages.append({"role": "assistant", "content": f"{response.choices[0].message}"})
        return response.choices[0].message.content

    def __init__(self):
        self.messages = [
            {"role": "system", "content": "你是一位股市分析与投资专家，总是能给出非常权威和有深度的投资与股票分析建议"},
        ]

if __name__ == '__main__':
    llm = LLMZhiPu()
    llm.chat("请帮我分析一下中国股市炒股需要注意什么")
    llm.chat('帮我推荐几只股票吧')