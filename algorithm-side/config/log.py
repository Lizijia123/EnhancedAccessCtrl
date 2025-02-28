import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,  # 设置日志级别为 INFO，意味着 INFO 及以上级别的日志将被记录
    format='%(asctime)s - %(levelname)s - %(message)s',  # 日志的格式，包括时间、日志级别和消息
    handlers=[
        logging.StreamHandler()  # 使用 StreamHandler 将日志输出到标准输出
    ]
)

# 创建一个日志记录器
LOGGER = logging.getLogger(__name__)
