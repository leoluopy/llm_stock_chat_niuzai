from baidusearch.baidusearch import search

results = search('文字新闻 特朗普 AI芯片 影响')  # 返回10个或更少的结果
for result in results:
    print(result['title'], result['url'])