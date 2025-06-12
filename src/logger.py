import logging
import os
import sys

# 获取程序运行目录
if getattr(sys, 'frozen', False):
    # 如果是打包后的 exe
    LOG_DIR = os.path.dirname(sys.executable)
else:
    # 如果是开发环境
    LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# 确保日志目录存在
os.makedirs(LOG_DIR, exist_ok=True)

# 日志文件路径
LOG_PATH = os.path.join(LOG_DIR, "searchDrawingDog.log")

# 配置日志
logging.basicConfig(
    level=logging.INFO,  # 默认INFO级别
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8", mode='a'),  # 追加模式
        logging.StreamHandler()  # 如需彻底无控制台，可删掉这一行
    ]
)

log = logging.getLogger("searchDrawingDog")
