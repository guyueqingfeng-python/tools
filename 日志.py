import os
from typing import Optional

import logging

from tools.保存 import establish_folder_path

logger = logging.getLogger(__name__)

def basic_logging() -> logging.Logger:
    """
    进行基础日志调节，就是写代码时所用的日志
    Returns
    -------
    logging.Logger
    """
    logger.setLevel(logging.DEBUG)
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    logger.addHandler(console)
    return logger


def logging_configuration(
        name: str,
        level: int=logging.INFO,
        error: bool=True,
        log_dir: str="logging",
        fmt: Optional[str]=None
) -> logging.Logger:
    """
    日志设置，进行日志格式，日志文件名字，错误日志设置
    Parameters
    ----------
    name: str
        日志文件名字
    level: int
        日志最低等级
    error: bool
        是否开启错误日志
    log_dir: str
        日志文件夹名字
    fmt: str
        日志格式
    Returns
    -------
    logging.Logger
    返回日志对象
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if logger.handlers:
        return logger
    log_dir = establish_folder_path(log_dir)
    log_file = os.path.join(log_dir, f"{name}.log")
    normal_handler = logging.FileHandler(log_file, encoding="UTF-8")
    console = logging.StreamHandler()
    if fmt is None:
        fmt = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(message)s'
    formatter = logging.Formatter(fmt)
    normal_handler.setFormatter(formatter)
    console.setFormatter(formatter)
    normal_handler.setLevel(level)
    console.setLevel(level)
    logger.addHandler(normal_handler)
    logger.addHandler(console)
    logger.info("日志已开启")

    def add_error_handler() -> None:
        """
        增加错误日志设置
        Returns
        -------
        None
        """
        log_file = os.path.join(log_dir, f"error{name}.log")
        error_handler = logging.FileHandler(log_file, encoding="UTF-8")
        error_handler.setFormatter(formatter)
        error_handler.setLevel(logging.WARNING)
        logger.addHandler(error_handler)
        logger.info("错误日志已开启")
        return None

    if error:
        add_error_handler()
    return logger
