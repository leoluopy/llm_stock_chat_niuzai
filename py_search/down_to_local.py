import urllib.request


def download_webpage(url, filename):
    try:
        # 打开URL
        with urllib.request.urlopen(url) as response:
            # 读取网页内容
            html_content = response.read()

            # 将内容写入本地文件
            with open(filename, 'wb') as file:
                file.write(html_content)

        print(f"网页已成功保存到 {filename}")
    except urllib.error.URLError as e:
        print(f"下载网页时出错: {e.reason}")
    except Exception as e:
        print(f"发生了一个错误: {e}")

if __name__ == '__main__':
    # 示例使用
    url = "https://www.163.com/dy/article/JGFD0K1C05118ARK.html"
    filename = "example.html"
    download_webpage(url, filename)
