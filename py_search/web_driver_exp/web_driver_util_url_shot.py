import base64

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
from io import BytesIO

# 设置Chrome选项
chrome_options = Options()
# chrome_options.add_argument("--headless")  # 无头模式，不打开浏览器界面
chrome_options.add_argument("--disable-gpu")  # 适用于某些Linux系统
chrome_options.add_argument("--no-sandbox")  # 忽略操作系统对沙盒的限制（仅限Linux）
chrome_options.add_argument("--disable-dev-shm-usage")  # 适用于有限的/dev/shm分区的Docker容器
chrome_options.add_argument("--start-maximized")  # 默认最大化


def get_url_ROI(url='https://legulegu.com/stockdata/cybPE', save_im_path=None):
    driver = webdriver.Chrome(service=Service('/snap/bin/chromium.chromedriver'), options=chrome_options)
    driver.set_page_load_timeout(6)
    try:
        # 打开百度首页
        driver.get(url)

    except Exception as e:
        print(e)

    finally:
        title = driver.find_element(By.CSS_SELECTOR, '.col-md-6.col-xs-12')
        canvas_element = driver.find_element(By.CSS_SELECTOR, 'canvas[data-zr-dom-id="zr_0"]')

        left = title.location['x']
        top = title.location['y']
        right = canvas_element.location['x'] + canvas_element.size['width']
        bottom = canvas_element.location['y'] + canvas_element.size['height']

        # 截取整个页面并裁剪出目标区域
        screenshot = driver.get_screenshot_as_png()

        image = Image.open(BytesIO(screenshot))
        cropped_image = image.crop((left, top, right, bottom))
        if save_im_path:
            cropped_image.save(save_im_path)

        buffered = io.BytesIO()
        cropped_image.save(buffered, format="JPEG")  # 可以选择其他格式，如PNG
        img_str = buffered.getvalue()

        # 将字节流编码为Base64字符串
        img_base64 = base64.b64encode(img_str).decode('utf-8')
        image_data = f"data:image/png;base64,{img_base64}"
        # 打印Base64字符串
        # print(img_base64)

        chart = driver.find_element(By.CSS_SELECTOR, "div.echarts-for-react")
        chart_parent_element = chart.find_element(By.XPATH, "..")
        comment_paragraph = chart_parent_element.find_element(By.XPATH, 'following-sibling::div[1]')
        text_content = comment_paragraph.text
        # 输出结果
        print(text_content)

        # 关闭浏览器
        driver.quit()
        return image_data, text_content


if __name__ == '__main__':
    get_url_ROI(url='https://legulegu.com/stockdata/cybPE', save_im_path='chuangYe.png')
    get_url_ROI(url='https://legulegu.com/stockdata/a-ttm-lyr', save_im_path='ALL_A.png')
    get_url_ROI(url='https://legulegu.com/stockdata/ke-chuang-ban-pe', save_im_path='ke_chuang.png')
    get_url_ROI(url='https://legulegu.com/stockdata/shanghaiPE', save_im_path='shangZheng.png')
    get_url_ROI(url='https://legulegu.com/stockdata/shenzhenPE', save_im_path='shenZheng.png')
