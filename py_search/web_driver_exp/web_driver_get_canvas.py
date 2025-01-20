from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from PIL import Image
from selenium.webdriver.common.keys import Keys
import time
import io
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
driver.set_page_load_timeout(5)
try:
    # 打开百度首页
    url = 'https://legulegu.com/stockdata/cybPE'
    driver.get(url)

except Exception as e:
    print(e)

finally:
    canvas = driver.find_element(By.CSS_SELECTOR, 'canvas[data-zr-dom-id="zr_0"]')
    # 获取canvas的截图
    png = canvas.screenshot_as_png
    base_64 = canvas.screenshot_as_base64

    # 使用PIL库将截图保存为图像文件或进一步处理
    image = Image.open(io.BytesIO(png))
    image.save('canvas_image.png')  # 保存为PNG文件

    print(base_64)
    # 关闭浏览器
    driver.quit()
