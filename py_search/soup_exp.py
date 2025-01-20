from bs4 import BeautifulSoup

# 假设你有以下 HTML 内容
html_content = '''
<html>
    <body>
        <div class="card-margin img-text-card">
            <p>Some content here</p>
        </div>
        <div class="another-class">
            <p>Another content here</p>
        </div>
    </body>
</html>
'''

# 使用 BeautifulSoup 解析 HTML
soup = BeautifulSoup(html_content, 'html.parser')

# 使用 CSS 选择器选择具有特定 class 的 div 元素
div_elements = soup.select('div.card-margin.img-text-card')

# 输出选择的元素
for div in div_elements:
    print(div)
    # 你也可以获取元素内部的文本或属性
    print(div.get_text())