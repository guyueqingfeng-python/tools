import time
import random
from typing import Dict

import logging
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)

def intervals_input(driver: WebDriver, data: str) -> None:
    """
    进行模拟人类输入：空格，英文，中文间隔时间不同
    Parameters
    ----------
    driver: WebElement
        浏览器驱动实例
    data: str
        需要输入的内容
    Returns
    -------
    None
    """
    data = list(data)
    while data:
        i = data.pop(0)
        driver.send_keys(i)
        if not data:
            break
        else:
            if '\u4e00' <= data[0] <= '\u9fff':
                time.sleep(random.uniform(0.5, 2.0))
            elif 'a' <= data[0].lower() <= 'z':
                time.sleep(random.uniform(0.1, 0.5))
            else:
                time.sleep(random.uniform(0.2, 0.8))
    return None

def switch_handle(driver: WebDriver) -> None:
    """
    进行浏览器句柄切换，切换至最新页面
    Parameters
    ----------
    driver: WebDriver
        浏览器驱动实例
    Returns
    -------

    """
    i = driver.window_handles
    driver.switch_to.window(i[-1])
    logger.info("已切换句柄致最新页面")
    return None

def wait_page_form(wait: WebDriverWait, config: Dict, max_attempts: int = 3) -> bool:
    """
    进行等待页面加载成功，以一个HTML为标准进行等待
    Parameters
    ----------
    wait: WebDriverWait
        wait等待的查找容器
    config: Dict
        {by: "", value: ""} 用于传入get_by函数解析查找方式与值
    max_attempts: int
        最大查找次数
    Returns
    -------

    """
    for i in range(1, max_attempts+1):
        try:
            logger.info("等待页面加载")
            wait.until(
                EC.presence_of_element_located((get_by(config)))
            )
            logger.info("页面加载成功")
            return True
        except TimeoutException as e:
            logger.warning(f"第{i}次加载超时")
            if i < max_attempts:
                time.sleep(4)
            else:
                logger.error(f"尝试{i}次后放弃")
        except Exception as e:
            logger.warning(f"获取其他错误：{type(e).__name__} - {e}", exc_info=True)
    logger.error("页面加载错误")
    raise NoSuchElementException("页面加载错误")

def get_by(config: Dict):
    """
    进行查找方式与值的解析
    Parameters
    ----------
    config: Dict
        {by: "", value: ""} 解析查找方式与值
    Returns
    -------

    """
    by_map = {
        "id": By.ID,
        "class_name": By.CLASS_NAME,
        "xpath": By.XPATH,
        "name": By.NAME,
        "css": By.CSS_SELECTOR,
        "tag_name": By.TAG_NAME,
        "link_text": By.LINK_TEXT,
        "partial_link_text": By.PARTIAL_LINK_TEXT,
    }

    by_type = by_map.get(config["by"])
    if not by_type:
        raise ValueError(f"不支持的定位方式: {config['by']}")
    return by_type, config["value"]
