import json
import re
from pathlib import Path
from typing import Union


def sanitize_filename(filename: str, max_length: int = 200) -> str:
    """
    清理文件名，移除非法字符

    Args:
        filename: 原始文件名
        max_length: 最大文件名长度

    Returns:
        清理后的合法文件名
    """
    # Windows 不允许的字符: \ / : * ? " < > |
    illegal_chars = r'[\\/:*?"<>|]'

    # 移除非法字符
    filename = re.sub(illegal_chars, "_", filename)

    # 移除控制字符
    filename = "".join(char for char in filename if ord(char) >= 32)

    # 移除首尾空格和点
    filename = filename.strip(". ")

    # 限制文件名长度
    if len(filename) > max_length:
        filename = filename[:max_length]

    # 如果文件名为空，使用默认名称
    if not filename:
        filename = "untitled"

    return filename


def load_json(file_path: Union[str, Path]) -> dict:
    file_path = Path(file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: dict, file_path: Union[str, Path]):
    file_path = Path(file_path)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_html(file_path: Union[str, Path]) -> str:
    file_path = Path(file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def save_html(html: str, file_path: Union[str, Path]):
    file_path = Path(file_path)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)


def load_text(file_path: Union[str, Path]) -> str:
    file_path = Path(file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def save_text(text: str, file_path: Union[str, Path]):
    file_path = Path(file_path)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)


def load_markdown(file_path: Union[str, Path]) -> str:
    file_path = Path(file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def save_markdown(markdown: str, file_path: Union[str, Path]):
    file_path = Path(file_path)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(markdown)
