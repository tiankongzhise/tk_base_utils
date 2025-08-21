import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from tk_base_utils.tk_logger import logger_wrapper,set_logger_config_path,get_logger
from tk_base_utils import find_file

if __name__ == "__main__":
    log_config_path = find_file('test_log_config.toml')
    set_logger_config_path(log_config_path)
    logger = get_logger()
    logger.debug("这是一条debug日志")
    logger.info_config("这是一条info_config日志")
    logger.info_utils("这是一条info_utils日志")
    logger.info_database("这是一条info_database日志")
    logger.info_kernel("这是一条info_kernel日志")
    logger.info_core("这是一条info_core日志")
    logger.info_service("这是一条info_service日志")
    logger.info_control("这是一条info_control日志")
    logger.info("这是一条info日志")
    logger.warning("这是一条warning日志")
    logger.error("这是一条error日志")
    logger.critical("这是一条critical日志")





