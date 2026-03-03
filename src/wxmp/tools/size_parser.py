import re


def parse_file_size(size_str: str) -> int:
    """
    解析文件大小字符串为字节数

    支持格式：
    - "100" -> 100 bytes
    - "100B" -> 100 bytes
    - "3KB" -> 3072 bytes
    - "1.5MB" -> 1572864 bytes
    - "2GB" -> 2147483648 bytes

    单位不区分大小写

    Args:
        size_str: 文件大小字符串

    Returns:
        字节数（整数）

    Raises:
        ValueError: 格式无效时
    """
    if not size_str or not isinstance(size_str, str):
        raise ValueError(f"无效的文件大小字符串: {size_str}")

    size_str = size_str.strip().upper()

    if not size_str:
        raise ValueError("文件大小字符串不能为空")

    pattern = r"^(\d+\.?\d*)\s*(B|KB|MB|GB|TB)?$"
    match = re.match(pattern, size_str)

    if not match:
        raise ValueError(f"无法解析文件大小: {size_str}")

    value_str, unit = match.groups()
    value = float(value_str)

    unit_multipliers = {
        None: 1,
        "B": 1,
        "KB": 1024,
        "MB": 1024**2,
        "GB": 1024**3,
        "TB": 1024**4,
    }

    multiplier = unit_multipliers.get(unit, 1)
    result = int(value * multiplier)

    return result


def format_file_size(bytes_value: int, precision: int = 2) -> str:
    """
    将字节数格式化为人类可读的字符串

    Args:
        bytes_value: 字节数
        precision: 小数位数

    Returns:
        格式化后的字符串，如 "3.00 KB"
    """
    if bytes_value < 0:
        raise ValueError("字节数不能为负数")

    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(bytes_value)
    unit_index = 0

    while value >= 1024 and unit_index < len(units) - 1:
        value /= 1024
        unit_index += 1

    if unit_index == 0:
        return f"{int(value)} {units[unit_index]}"

    return f"{value:.{precision}f} {units[unit_index]}"
