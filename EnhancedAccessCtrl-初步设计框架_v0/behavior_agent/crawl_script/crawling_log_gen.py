from browsermobproxy import Server
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
import json
import time
browsermob_proxy_path = "B:\\browsermob-proxy-2.1.4-bin\\browsermob-proxy-2.1.4\\bin\\browsermob-proxy.bat"  # 替换为 BrowserMob Proxy 的实际路径
server = Server(browsermob_proxy_path)
server.start()
proxy = server.create_proxy()
edge_options = Options()
edge_options.add_argument('--proxy-server={0}'.format(proxy.proxy))  # 使用代理
edge_options.add_argument('--headless')  # 无头模式，可选
edge_options.add_argument('--disable-gpu')  # 禁用GPU加速，可选
edge_driver_path = "C:\\Users\\hp\\miniconda3\\msedgedriver.exe"  # 替换为 Edge WebDriver 的实际路径
service = Service(edge_driver_path)
driver = webdriver.Edge(service=service, options=edge_options)
proxy.new_har("example_com", options={"captureHeaders": True, "captureContent": True})

# 打开目标网页
driver.get("http://8.130.20.137:8081")

# 获取流量记录（HAR格式）
har_data = proxy.har  # 获取 HAR 文件（HTTP Archive 格式）

# 打印流量记录
for entry in har_data['log']['entries']:
    request = entry['request']
    response = entry['response']
    print(request)

# 等待页面加载完成
time.sleep(5)

# 关闭浏览器和代理
driver.quit()
server.stop()
