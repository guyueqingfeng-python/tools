import os
from typing import Optional, Tuple, List
from io import TextIOWrapper
import hashlib

import re
import json
import pandas as pd
import logging
import shutil

logger = logging.getLogger(__name__)

def establish_folder_path(name: str, assign_path: Optional[str]=None) -> Optional[str]:
    """
    进行文件夹路径检查，选择合适的文件夹路径
    Parameters
    ----------
    name: str
        文件夹名字
    assign_path: Optional[str]
        用户指定文件夹路径
    Returns
    -------
    str or None
        成功返回文件夹路径，失败时抛出异常
    """

    default_path = [
        ("用户数据目录", os.environ.get("APPDATA") or os.path.expanduser("~/local/share")),
        ("程序目录",  os.path.dirname(__file__)),
        ("桌面文件夹", os.path.expanduser(r"~\Desktop")),
        ("系统临时目录", os.environ.get("TEMP", "/tep"))
    ]
    if assign_path:
        assign = ("用户指定目录", assign_path)
        default_path.insert(0, assign)

    for path_name, path in default_path:
        try:
            if os.access(path, os.W_OK):
                os.makedirs(path, exist_ok=True)
                try:
                    ise = shutil.disk_usage(path)
                    free_gb = ise.free / (1024 ** 3)
                    if free_gb <= 0.1:
                        logger.warning(f"{path_name}所在{path[:1]}磁盘空间不足, 还有{free_gb:.2f}GB")
                        continue
                except FileNotFoundError as e:
                    logger.warning(f"指定路径不存在：{type(e).__name__} - {e}", exc_info=True)
                    continue
                except PermissionError as e:
                    logger.warning(f"{path_name}无权限写入：{type(e).__name__} - {e}", exc_info=True)
                    continue
                fold = os.path.join(path, name)
                os.makedirs(fold, exist_ok=True)
                logger.info(f"写入{path_name}路径文件夹")
                return fold
            else:
                logger.warning(f"{path_name}无写入权限")
        except Exception as e:
            logger.warning(f"未知错误：{type(e).__name__} - {e}", exc_info=True)
            continue
    logger.warning("目前适合路径都不可用")
    end = os.getcwd()
    logger.info(f"使用{end}")
    try:
        if os.access(end, os.W_OK):
            ise = shutil.disk_usage(end)
            free_gb = ise.free / (1024 ** 3)
            if free_gb <= 0.1:
                logger.warning(f"{end}磁盘空间不足, 还有{free_gb:.2f}GB")
                logger.error("目前文件内存没有空余")
                raise OSError("目前文件内存没有空余")
            logger.info(f"写入{end}路径文件夹")
            return os.path.join(end, name)
        else:
            logger.warning(f"运行目录无写入权限")
    except Exception as e:
        logger.warning(f"未知错误：{type(e).__name__} - {e}", exc_info=True)
    logger.error("目前无写入文件权限")
    raise PermissionError("目前无写入文件权限")

def filename_rationality(filename: str) -> str:
    """
    检查文件名字的合理性
    Parameters
    ----------
    filename: str
        需要检查文件的名字
    Returns
    -------
    str
        返回合理的文件名字
    """

    filename = filename.replace('..', '')
    file = re.sub(r'[<>:"/\\\'|?*]', '_', filename)
    file = file.strip().rstrip('.')
    name_part = file.split('.')[0].upper()
    if name_part in ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3',
                     'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
                     'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']:
        logger.info(f"含有特殊名字{name_part}")
        file = '_' + file

    if not file:
        logger.info("文件名为空，使用默认名'unnamed'")
        return 'unnamed'
    return file

def file_duplication_process(path: str, start_num:int = 1) -> str:
    """
    进行文件命名，若重复进行(1)递增迭代
    Parameters
    ----------
    path: str
        进行判断的路径
    start_num: int
        起始重复文件编号
    Returns
    -------
        str
    """
    if not os.path.exists(path):
        return path
    fold = os.path.dirname(path)
    file = os.path.basename(path)
    name, ext = os.path.splitext(file)
    match = re.search(r"\((\d+)\)$", name)
    counter = start_num
    if match:
        counter = int(match.group(1))
        name = name[:match.start()]
    while True:
        new_path = os.path.join(fold, f"{name}({counter}){ext}")
        if not os.path.exists(new_path):
            return new_path
        counter += 1


def save_excel(data: object, file_path: str, sheet_name: str="Sheet1", excel: str="csv") -> None:
    """
    进行Excel类型文件保存，可保存为csv和xlsx类型文件
    Parameters
    ----------
    data: object
        要保存的数据，可以为字典，或者是DataFrame，或者是由字典组成的列表
    file_path: str
        保存的文件路径
    sheet_name: str
        工作表的名字，存为xlsx需要，默认为Sheet1
    excel: str
        仅支持csv和xlsx两种文件类型，默认为csv
    Returns
    -------
    None
    """
    if isinstance(data, dict):
        df = pd.DataFrame(data)
    elif isinstance(data, list) and all(isinstance(itme, dict) for itme in data):
        df = pd.DataFrame(data)
    elif isinstance(data, pd.DataFrame):
        df = data
    else:
        raise ValueError(logger.error(f"数据类型错误，不支持:{type(data)}"))
    if excel == "csv":
        df.to_csv(file_path, index=False, encoding="utf-8-sig")
    elif excel == "xlsx":
        df.to_excel(file_path, index=False, sheet_name=sheet_name)
    else:
        raise ValueError(logger.error(f"参数输入错误, 不是可储存文件类型"))
    return None


def save_txt(data: object, file_path: str, mode: str = "w") -> None:
    """
    存为txt类型文件
    Parameters
    ----------
    data: object
        可以为任意数据类型
    file_path: str
        保存文件的路径
    mode: str
        决定写入方式
    Returns
    -------
    None
    """
    with open(file_path, mode, encoding="utf-8") as f:

        def save(data: object, f: TextIOWrapper, indent_level: int=0) -> None:
            """
            进行txt文件写入，主要为文件类型嵌套使用
            Parameters
            ----------
            data: object
                写入的数据，可以为任意数据类型
            f：TextIOWrapper
                为with的上下文管理器
            indent_level: int
                文件写入的初始缩进
            Returns
            -------
            None
            """
            indent = "    " * indent_level

            if isinstance(data, dict):
                for key, value in data.items():
                    f.write(f"{indent}{key}:\n")
                    if isinstance(value, (dict, list)):
                        save(value, f, indent_level + 1)
                    else:
                        if value is None:
                            f.write(f"None\n")
                        else:
                            f.write(f"{value}\n")

            elif isinstance(data, list):
                if not data:
                    f.write("None\n")
                else:
                    for content in data:
                        if isinstance(content, (dict, list)):
                            save(content, f, indent_level)
                        else:
                            f.write(f"{indent}- {content}\n")
            elif isinstance(data, str):
                f.write(f"{indent}{data}\n")

            elif data is None:
                f.write(f"None\n")

            else:
                f.write(f"{indent}{data}\n")

        save(data, f)
    return None


def save_binary(data: bytes, file_path: str) -> None:
    """
    进行照片存入文件
    Parameters
    ----------
    data: bytes
        为爬取完照片的二进制字节
    file_path: str
        存入照片的路径
    Returns
    -------
    None
    """
    with open(file_path, "wb") as f:
        f.write(data)


def save_json(data : object, file_path: str) -> None:
    """
    将数据存为json文件形式
    Parameters
    ----------
    data: object
        可以为字典，或者由字典组成的列表
    file_path: str
        存入文件的路径
    Returns
    -------
    None
    """
    if isinstance(data, dict) or (isinstance(data, list) and all(isinstance(item, dict) for item in data)):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    else:
        raise ValueError(logger.error(f"数据类型错误，不支持:{type(data)}"))


def file_save_type(
        data: object,
        file_path: str,
        file_type: str = "txt",
        mode: str = "w",
        sheet_name: str="Sheet1"
) -> None:
    """
    进行文件保存，可存为["csv", "txt", "jnp", "log", "xlsx", "json"]
    Parameters
    ----------
    data: object or bytes
        存入的数据
    file_path: str
        存入文件的路径
    file_type: str
        需要保存的文件类型可以为["csv", "txt", "jnp", "log", "xlsx", "json"]
    mode: str
        如果要写入txt，决定的写入方式
    sheet_name: str
        若存为xlsx文件需要工作表名字，默认为Sheet1
    Returns
    -------
    None
    """
    file_type_list = ["csv", "txt", "jnp", "log", "xlsx", "json"]
    file_type = file_type.lower()
    if file_type in file_type_list:
        if file_type == "csv":
            save_excel(data, file_path, excel="csv")
        elif file_type in ("txt", "log"):
            save_txt(data, mode, file_path)
        elif file_type == "jnp":
            save_binary(data, file_path)
        elif file_type == "xlsx":
            save_excel(data, file_path, sheet_name, excel="xlsx", )
        elif file_type == "json":
            save_json(data, file_path)
    else:
        raise ValueError(f"不支持的格式: {file_type}")

def check_excessive_path(path: str, max_length: int=240) -> Tuple| str:
    """
    进行检查是否有长度过长的路径，如果有进行替换
    Parameters
    ----------
    path: str
        需要检查的路径
    max_length: int
        最大的路径长度
    Returns
    -------
    Tuple or str
        若为正确路径，则为str，出现错误的为Tuple
    """
    path = os.path.normpath(path)
    path = os.path.abspath(path)
    data = []
    def reconstruct_path(path: str) -> str:
        """
        用递归的方式进行路径替换
        Parameters
        ----------
        path: str
            需要替换的路径
        Returns
        -------
        str
        """
        dir_path = os.path.dirname(path)
        if dir_path == path:
            return path
        basic_name = os.path.basename(path)
        new_path, new_name = reconstruct_name(path)
        data.append(basic_name)
        data.append(new_name)
        if len(new_path) > max_length:
            logger.info(f"{basic_name}不符合长度标准")
            short_path = reconstruct_path(dir_path)
            full_path = os.path.join(short_path, new_name)
            return full_path
        else:
            return new_path

    if len(path) > max_length:
        new_path = reconstruct_path(path)
        return new_path, data
    return path


def reconstruct_name(path: str) -> Tuple:
    """
    进行文件名字重构，返回路径和改后的名字
    Parameters
    ----------
    path: str
        需要缩小的文件(夹)路径
    Returns
    -------
    Tuple
    """
    basic_path = os.path.dirname(path)
    basic_name = os.path.basename(path)
    name, ext = os.path.splitext(basic_name)
    if ext:
        new_name = hashlib.md5(name.encode()).hexdigest()[:8]
        logger.info(f"将文件{name}替换为{new_name}")
        new_name = f"{new_name}{ext}"
    else:
        new_name = hashlib.md5(name.encode()).hexdigest()[:6]
        logger.info(f"将文件夹{name}替换为{new_name}")
    new_path = os.path.join(basic_path, new_name)
    return new_path, new_name

def creat_excessive_file(
        data: List,
        max_length: int,
        long_filename: str = "too_long_name.txt",
        long_dirname: str = "too_long",
        long_path: Optional[str] = None,
) -> None:
    """
    进行过长文件的原文件名字和替换的文件名字记录
    Parameters
    ----------
    data: List
        需要记录的数据
    max_length: int
        最大长度
    long_filename: str
        记录长文件的名字
    long_dirname:
        记录长文件夹的名字
    long_path: Optional[str]
        自定义的记录长文件的路径
    Returns
    -------
    None
    """
    dirpath = establish_folder_path(long_dirname, assign_path=long_path)
    filepath = os.path.join(dirpath, long_filename)
    logger.info(f"出现大于{max_length}个字符的文件，保存长名字文件已开启")
    if os.path.exists(filepath):
        file_save_type(data, filepath, file_type="txt", mode="a")
    else:
        file_save_type(data, filepath, file_type="txt")



def check_path_length(path: str, max_length: int = 240, long_filename: str = "too_long_name.txt", long_path: Optional[str] = None) -> str:
    """
    检查文件路径的长度
    Parameters
    ----------
    path: str
        需要检查的路径
    max_length: int
        最大长度
    long_filename: str
        记录过长文件的名字
    long_path: Optional[str]
        自定义的记录长文件的路径
    Returns
    -------
    str
    """
    new_path, data = check_excessive_path(path, max_length)
    if data:
        creat_excessive_file(data, max_length, long_filename, long_path=long_path)
    return new_path