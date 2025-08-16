import requests
from bs4 import BeautifulSoup
import re

# 目标URL
url = "https://www.sse.com.cn/market/price/report/"

# 发送HTTP请求
response = requests.get(url)
response.encoding = "utf-8"  # 东方财富网使用GBK编码
if response.status_code == 200:
    print("请求成功！")
else:
    print(f"请求失败，状态码：{response.status_code}")
html_content = response.text
# 解析HTML
soup = BeautifulSoup(html_content, "html.parser")
print(soup.find("div", {"class": "common_con"}))