import time
import random
from typing import Tuple

import logging
from selenium.webdriver.remote.webelement import WebElement

logger = logging.getLogger(__name__)

def install_intervals_input() -> None:
    """
    进行intervals_input方法添加，在WebElement类上打补丁
    Returns
    -------
    None
    """
    if hasattr(WebElement, 'intervals_input'):
        logger.info("已有方法intervals_input")
        return None
    def intervals_input(self: WebElement, sentence: str) -> None:
        """
        进行模拟人类输入：空格，英文，中文间隔时间不同
        Parameters
        ----------
        self: WebElement
            进行打补丁的类
        sentence: str
            需要输入的内容
        Returns
        -------
        None
        Examples
        --------
        driver.intervals_input(data)
        """
        sentence = list(sentence)
        while sentence:
            i = sentence.pop(0)
            self.send_keys(i)
            if not sentence:
                break
            else:
                if '\u4e00' <= sentence[0] <= '\u9fff':
                    time.sleep(random.uniform(0.5, 2.0))
                elif 'a' <= sentence[0].lower() <= 'z':
                    time.sleep(random.uniform(0.1, 0.5))
                else:
                    time.sleep(random.uniform(0.2, 0.8))
    WebElement.intervals_input = intervals_input
    logger.info("添加intervals_input方法成功")
    return None

def preserve_wait(
        wait_normally: Tuple[float|int, ...] = (5.0, 9.0),
        wait_long: Tuple[float|int, ...] = (15.0, 25.0),
        wait_quick: Tuple[float|int, ...] = (3.0, 5.0)
) -> None:
    """
    点开页面后的随机等待
    Parameters
    ----------
    wait_normally: [float|int, ...]
        正常的等待时间
    wait_long: [float|int, ...]
        长的等待时间
    wait_quick: [float|int, ...]
        短的等待时间
    Returns
    -------
    None
    """
    wait_time = random.random()
    lose_interest = 0.2
    # 0.3比0.2大0.1实际上就是0.1
    interest = 0.3
    # 剩下的0.7为正常时间
    if wait_time < lose_interest:
        time.sleep(random.uniform(*wait_quick))
    elif wait_time < interest:
        time.sleep(random.uniform(*wait_long))
    else:
        time.sleep(random.uniform(*wait_normally))