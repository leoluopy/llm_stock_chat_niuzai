import requests
from bs4 import BeautifulSoup


def baidu_search(query):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    params = {
        'wd': query,
        'ie': 'utf-8'
    }
    response = requests.get('https://www.baidu.com/s', headers=headers, params=params)
    # response = requests.get('https://www.google.com/', headers=headers, params=params)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # 解析搜索结果，例如提取标题链接
        results = []
        for item in soup.select('.t a'):
            href = item['href']
            title = item.text
            results.append({'title': title, 'link': href})
        return results
    else:
        return None

if __name__ == '__main__':

    # 使用示例
    search_results = baidu_search('特朗普 AI芯片 影响')
    for result in search_results:
        print(f'Title: {result["title"]}, Link: {result["link"]}')