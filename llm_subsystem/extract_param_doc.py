import ast
import re
from typing import Dict, Any


def extract_docstring_params(func_source: str) -> Dict[str, Any]:
    """
    从函数源代码中提取注释中的参数说明并保存到字典。

    参数:
    func_source (str): 包含函数定义的源代码字符串。

    返回:
    Dict[str, Any]: 参数名到参数说明的字典。
    """
    try:
        # 使用ast模块解析函数源代码
        func_source = re.sub(r'\t', '    ', func_source)
        # tree = ast.parse(func_source)
        #
        # # 找到函数定义节点
        # for node in ast.walk(tree):
        #     if isinstance(node, ast.FunctionDef):
        #         docstring = ast.get_docstring(node)
        #         break
        # else:
        #     raise ValueError("No function definition found in the source code.")

        docstring = func_source
        param_pattern = re.compile(r':param (\w+): (.+?)(?=\n:param |:return |:rtype |$)', re.DOTALL | re.MULTILINE)
        matches = param_pattern.findall(docstring)
        params_dict = {match[0]: match[1].strip() for match in matches}

        return_pattern = re.compile(r':return: (.+?)(?:\n|$)', re.MULTILINE | re.DOTALL)
        matches = return_pattern.findall(docstring)
        params_dict['return'] = matches[0]

        return params_dict
    except Exception as e:
        print(e)
        return {}

if __name__ == '__main__':

    # 示例函数源代码
    func_source = """  
def example_function(param1: int, param2: str) -> None:  
    \"\"\"
    given index name and index code , get the index close value for last 30 days
    :param index_name: stock index name
    :param index_code: stock index code
    :return: table string for dates and values
    \"\"\"  
    """

    # 提取参数说明
    params_dict = extract_docstring_params(func_source)
    print(params_dict)