import sys, os


def add_stock_exchange_suffix(code, for_cor=True):
    if isinstance(code, str) and code.isdigit():
        code_prefix = code[:3]

        if (
                code_prefix.startswith('600')
                or code_prefix.startswith('601')
                or code_prefix.startswith('603')
                or code_prefix.startswith('688')
        ):
            return 'sh.' + code
        elif (
                code_prefix.startswith('002')
                or code_prefix.startswith('300')
                or code_prefix.startswith('399')
        ):
            return 'sz.' + code
        elif (
                code_prefix.startswith('000') and (for_cor is True)
        ):
            return 'sz.' + code
        elif (
                code_prefix.startswith('000') and (for_cor is False)
        ):
            return 'sh.' + code
        else:
            return 'unknown.' + code  # 未知前缀情况
    else:
        return code


if __name__ == '__main__':
    # 测试代码
    test_codes = ['600000', '000001', '300002', '603000', '002001', '123456', 'ABCDEF']

    for code in test_codes:
        suffixed_code = add_stock_exchange_suffix(code)
        print(f"股票代码 {code} 添加了后缀后变为 {suffixed_code}")
