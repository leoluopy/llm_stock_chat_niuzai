import urllib.request

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# 设置Chrome选项
chrome_options = Options()
# chrome_options.add_argument("--headless")  # 无头模式，不打开浏览器界面
chrome_options.add_argument("--disable-gpu")  # 适用于某些Linux系统
chrome_options.add_argument("--no-sandbox")  # 忽略操作系统对沙盒的限制（仅限Linux）
chrome_options.add_argument("--disable-dev-shm-usage")  # 适用于有限的/dev/shm分区的Docker容器

# 指定chromedriver的路径（如果它在你的系统路径中，则不需要）
# service = Service('/path/to/chromedriver')

# 1.确认Chrome浏览器是否已安装 ,命令:     chromium-browser -version
# 2.如果没有安装，使用以下命令进行安装：  sudo apt-get install chromium-browser
driver = webdriver.Chrome(service=Service('/snap/bin/chromium.chromedriver'), options=chrome_options)

# 定义URL
url = 'https://news.qq.com/search?query=AI%E8%8A%AF%E7%89%87&page=1'

# 打开URL
driver.get(url)

try:
    # 等待页面上某个特定的元素加载完成（例如，等待ID为"main-content"的div元素可见）
    # 你可以根据需要替换下面的元素定位器和等待条件
    wait = WebDriverWait(driver, 1)  # 最多等待10秒
    element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".card-margin.img-text-card")))

    # 获取页面源代码（此时应该已经包含了动态加载的内容）
    html_content = driver.page_source

    soup = BeautifulSoup(html_content, 'html.parser')

    # 使用 CSS 选择器选择具有特定 class 的 div 元素
    div_elements = soup.select('div.card-margin.img-text-card')
    for card_div in div_elements:
        link = card_div.find('a', class_='hover-link')['href']
        title = card_div.find('p', class_='title').get_text(strip=True)
        print("标题:", title)
        print("URL:", link)

        with urllib.request.urlopen(link) as response:
            html_content_news = response.read()
            soup = BeautifulSoup(html_content, 'html.parser')

            # 提取所有的<p>标签内容
            p_tags = soup.find_all('p')
            p_contents = [tag.get_text() for tag in p_tags]

            # 提取所有的<h>标签内容
            h_tags = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            h_contents = [tag.get_text() for tag in h_tags]

            print("\n<h>标签内容:")
            for content in h_contents:
                print(content)

            # 打印提取的内容
            print("<p>标签内容:")
            for content in p_contents:
                print(content)




finally:
    # 关闭浏览器（无论是否出现异常都会执行）
    driver.quit()
