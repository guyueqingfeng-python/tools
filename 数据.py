def data_clean(data: object) -> str:
    """
    进行基础数据清洗，一般是空格符的清洗
    Parameters
    ----------
    data: object
        所要清洗的数据
    Returns
    -------
    str
    """
    if isinstance(data, str):
        return " ".join(data.split())
    elif isinstance(data, list):
        data = [data_clean(itme) for itme in data if itme and str(itme).strip()]
        return " ".join(data)
    return str(data).strip()