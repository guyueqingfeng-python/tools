import time
from typing import Dict, List, Optional, Callable, Tuple

import logging
import requests
from lxml import etree
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.service import Service
from selenium.webdriver.remote.webdriver import WebDriverException

logger = logging.getLogger(__name__)

def gain_html(
        url: str,
        request_time: int = 3,
        connect_time: int = 3,
        return_data_time: int = 9,
        retry_wait_time: int = 5,
        custom_headers: Optional[Dict] = None
) -> Optional[etree._Element]:
    """
    用于发送HTTP请求，返回html
    Parameters
    ----------
    url: str
        请求网址
    request_time: int
        最大请求次数
    connect_time: int
        连接网站时间
    return_data_time: int
        返回数据时间
    retry_wait_time: int
          重试等待时间
    custom_headers: Optional[dict] = None
        用于请求的请求头
    Returns
    -------
    etree._Element or None
        成功时返回html，失败时为None
    """
    default_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer': 'https://www.google.com/'
    }
    if custom_headers:
        default_headers.update(custom_headers)
    with requests.Session() as session:
        session.headers.update(default_headers)
        for i in range(1, request_time + 1):
            try:
                logger.info("开始请求")
                response = session.get(url, timeout=(connect_time, return_data_time))
                response.raise_for_status()
                logger.info(f"请求成功{url}")
                return etree.HTML(response.text)

            except requests.exceptions.RequestException as e:
                logger.warning(f"请求超时: {e}", exc_info=True)
                if i < request_time:
                    time.sleep(retry_wait_time)
                else:
                    logger.error(f"尝试{request_time}次后放弃")
                    return None
    return None


def gain_img(
        url: str,
        request_time: int = 3,
        connect_time: int = 3,
        return_data_time: int = 9,
        retry_wait_time: int = 5,
        custom_headers: Optional[Dict] = None
) -> Optional[bytes]:
    """
       用于发送HTTP请求，返回图片二进制
       Parameters
       ----------
       url: str
           请求网址
       request_time: int
           最大请求次数
       connect_time: int
           连接网站时间
       return_data_time: int
           返回数据时间
      retry_wait_time: int
          重试等待时间
       custom_headers: Optional[dict] = None
           用于请求的请求头
       Returns
       -------
       bytes or None
           成功时返回二进制字节，失败时为None
       """
    default_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer': 'https://www.google.com/'
    }
    if custom_headers:
        default_headers.update(custom_headers)
    with requests.Session() as session:
        session.headers.update(default_headers)
        for i in range(1, request_time + 1):
            try:
                logger.info("开始请求")
                response = session.get(url, timeout=(connect_time, return_data_time))
                response.raise_for_status()
                logger.info(f"请求成功{url}")
                return response.content

            except requests.exceptions.RequestException as e:
                logger.warning(f"请求超时: {e}", exc_info=True)
                if i < request_time:
                    time.sleep(retry_wait_time)
                else:
                    logger.error(f"尝试{request_time}次后放弃")
                    return None
    return None

def gain_chrome_driver(
        url: str,
        request_time: int = 3,
        lazy_loading: int = 0,
        retry_wait_time: int = 5,
        headless: bool = False
) -> Optional[WebDriver]:
    """
    请求网址获取网址控制权限driver
    Parameters
    ----------
    url: str
        请求网址
    request_time: int
        最大请求次数
    lazy_loading: int
        懒加载模式, 0为允许, 2为禁止
    retry_wait_time: int
        重试等待时间
    headless: bool
        无头模式
    Returns
    -------
    WebDriver or None
    成功返回网址driver控制权，失败返回None
    """
    options = Options()
    if headless:
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-blink-features=AutomationControlled')
    prefs = {
        "profile.managed_default_content_settings.images": lazy_loading,
        'profile.managed_default_content_settings.stylesheets': 0,
        'profile.managed_default_content_settings.javascript': 0,
        'profile.managed_default_content_settings.popups': 2,
        'profile.managed_default_content_settings.notifications': 2
    }
    options.add_experimental_option('prefs', prefs)
    service = Service()
    for i in range(request_time):
        try:
            driver = webdriver.Chrome(service=service, options=options)
            logger.info("浏览器已打开")
            driver.set_page_load_timeout(20)
            break
        except WebDriverException as e:
            logger.warning("浏览器连接超时：{}".format(e))
            if i < (request_time - 1):
                time.sleep(retry_wait_time)
            else:
                logger.error("尝试{}次放弃".format(request_time))
                return None
    for i in range(request_time):
        try:
            logger.info(f"开始进行请求网址:{url}")
            driver.get(url)
            logger.info(f"请求网址成功:{url}")
            return driver
        except WebDriverException as e:
            logger.warning("网址请求超时：{}".format(e), exc_info=True)
            if i < (request_time - 1):
                driver.quit()
                time.sleep(retry_wait_time)
            else:
                logger.error("尝试{}次放弃".format(request_time))
                driver.quit()
                return None