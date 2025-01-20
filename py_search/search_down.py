import sys, os

from py_gen.py_search.down_to_local import download_webpage
from py_gen.py_search.search import baidu_search

if __name__ == '__main__':
    # 使用示例
    out_path = 'down'
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    search_results = baidu_search('特朗普 AI芯片 影响')
    for result in search_results:
        print(f'Title: {result["title"]}, Link: {result["link"]}')
        download_webpage(result["link"], os.path.join(out_path, result["title"] + ".html"))
