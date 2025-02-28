import logging
import os
# 配置日志
logging.basicConfig(
    level=logging.INFO,  # 设置日志级别为 INFO，意味着 INFO 及以上级别的日志将被记录
    format='%(asctime)s - %(levelname)s - %(message)s',  # 日志的格式，包括时间、日志级别和消息
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app_log.log')),  # 使用 FileHandler 将日志输出到名为 app.log 的文件
        logging.StreamHandler()  # 使用 StreamHandler 将日志输出到标准输出
    ]
)

# 创建一个日志记录器
LOGGER = logging.getLogger(__name__)

# # 示例日志记录
# LOGGER.info('This is an info message.')
# LOGGER.warning('This is a warning message.')

# sudo /bin/python3 /home/ubuntu/graduation-design/EnhancedAccessCtrl/algorithm-side-interfaces/app.py