import inspect
import json
from typing import get_type_hints
import sys, os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../../../")

from user_interface.stock_expert.llm_subsystem.extract_param_doc import extract_docstring_params


def get_type_name(t):
    name = str(t)
    if "list" in name or "dict" in name:
        return name
    else:
        return t.__name__


def function_to_json(func):
    signature = inspect.signature(func)
    type_hints = get_type_hints(func)

    # print(func.__doc__)
    # print(type_hints)
    params_dict = extract_docstring_params(func.__doc__)
    function_info = {
        "name": func.__name__,
        "description": func.__doc__,
        "parameters": {},
        "returns": {
            "type": type_hints.get("return", "void").__name__,
            "description": params_dict['return']
        }
    }
    for name, _ in signature.parameters.items():
        param_type = get_type_name(type_hints.get(name, type(None)))
        function_info["parameters"][name] = {
            "type": param_type,
            "description": params_dict.get(name, ""),
        }

    return json.dumps(function_info, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    from user_interface.stock_data_online.baoStock.price_vol_amount_pe_pb import \
        get_recent_30_days_corporation_basic_info, get_recent_30_days_index_basic_info, get_today_date_in_words, \
        search_internet_summarize, get_recent_10_years_index_basic_info, get_recent_10_years_corporation_basic_info, \
        get_index_pe_trend_line_chart_and_comment

    print('[')
    print(function_to_json(get_today_date_in_words))
    print(",", end='')
    print(function_to_json(get_index_pe_trend_line_chart_and_comment))
    print(",", end='')
    print(function_to_json(get_recent_30_days_corporation_basic_info))
    print(",", end='')
    print(function_to_json(get_recent_30_days_index_basic_info))
    print(",", end='')
    print(function_to_json(search_internet_summarize))
    print(",", end='')
    print(function_to_json(get_recent_10_years_index_basic_info))
    print(",", end='')
    print(function_to_json(get_recent_10_years_corporation_basic_info))
    print(']')
