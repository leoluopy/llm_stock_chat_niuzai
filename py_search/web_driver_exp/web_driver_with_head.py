from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.keys import Keys
import time

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

try:
    # 打开百度首页
    driver.get('https://www.baidu.com')

    # 查找搜索框元素 (通常可以通过检查网页找到元素的选择器或ID)
    search_box = driver.find_element('name', 'wd')  # 百度搜索框的名字是'wd'

    # 在搜索框中输入搜索关键词
    search_box.send_keys('特朗普 AI 芯片')

    # 模拟按下回车键进行搜索
    search_box.send_keys(Keys.RETURN)

    # 等待几秒以查看结果
    time.sleep(5)  # 这里使用time.sleep等待，实际项目中建议使用WebDriverWait

finally:
    # 关闭浏览器
    driver.quit()
