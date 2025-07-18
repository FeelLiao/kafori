
import os
import logging

def init_global_logger(log_file='logs/project_analysis.log', level=logging.INFO):
    logger = logging.getLogger()  # 根 logger，全局唯一
    logger.setLevel(level)

    if not logger.handlers:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 控制台输出
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # 文件输出
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
