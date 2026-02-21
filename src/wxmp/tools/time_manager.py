import time
from datetime import datetime
from pathlib import Path
from typing import Generic, Literal, NamedTuple, TypeVar

import pandas as pd
from loguru import logger
from pydantic import BaseModel, field_serializer
from tqdm import tqdm

from wxmp.tools.file import save_json


class TimeRange(BaseModel):
    """文章时间范围，用于缓存管理"""

    begin: datetime
    end: datetime = datetime.today()

    @field_serializer("begin", "end")
    def serialize_datetime(self, dt: datetime) -> str:
        """将 datetime 对象序列化为 YYYY-MM-DD 格式字符串"""
        return dt.strftime("%Y-%m-%d")


T = TypeVar("T", bound=TimeRange)


class TimeManager(Generic[T]):
    def __init__(self, meta: T, df: pd.DataFrame):
        self.meta = meta
        self.data = df

    @staticmethod
    def check_file_exist(file_name: str, file_dir: Path) -> None:
        """检查文件是否存在"""
        json_path = file_dir / f"{file_name}.json"
        csv_path = file_dir / f"{file_name}.csv"
        if not json_path.exists() or not csv_path.exists():
            raise FileNotFoundError(f"文件不存在: {json_path} 或 {csv_path}")

    @classmethod
    def new(cls, meta_class: type[T] = TimeRange) -> "TimeManager[T]":
        """创建新的 TimeManager 实例"""
        # 时间创建为 最开始的时间，min_value
        meta = meta_class(begin=datetime.min, end=datetime.min)
        df = pd.DataFrame(columns=["title", "create_time"])
        return cls(meta, df)

    @classmethod
    def load_file(
        cls, file_name: str, file_dir: Path, meta_class: type[T] = TimeRange
    ) -> "TimeManager[T]":
        """加载文件"""
        json_path = file_dir / f"{file_name}.json"
        csv_path = file_dir / f"{file_name}.csv"
        cls.check_file_exist(file_name, file_dir)
        meta = meta_class(**load_json(json_path))
        df = pd.read_csv(csv_path)
        return cls(meta, df)

    def match_remaining_time_range(self, need_time: T) -> T | None:
        """
        获取剩余的时间范围

        Args:
            meta_time: 元数据时间范围
            need_time: 需要获取的时间范围

        Returns:
            剩余的时间范围
        """
        if self.meta.end <= need_time.begin or need_time.end <= self.meta.begin:
            self.meta.begin = need_time.begin
            self.meta.end = need_time.end
            return need_time
        elif self.meta.begin < need_time.begin < self.meta.end < need_time.end:
            remaining_range = type(need_time)(begin=self.meta.end, end=need_time.end)
            self.meta.end = need_time.end
            return remaining_range
        elif need_time.begin < self.meta.begin < need_time.end < self.meta.end:
            remaining_range = type(need_time)(
                begin=need_time.begin, end=self.meta.begin
            )
            self.meta.begin = need_time.begin
            return remaining_range
        else:
            return None

    def fliter_data(self, time_range: T, time_col: str = "create_time") -> pd.DataFrame:
        """
        过滤数据

        Args:
            time_range: 时间范围
            time_col: 时间列名

        Returns:
            过滤后的数据
        """
        if time_col not in self.data.columns:
            raise ValueError(f"{time_col} 不在数据框中")
        try:
            time_ser = pd.to_datetime(self.data[time_col])
        except ValueError:
            raise ValueError(f"{time_col} 不是时间格式")
        return self.data[(time_ser >= time_range.begin) & (time_ser <= time_range.end)]

    def save_file(self, file_name: str, file_dir: Path):
        """保存文件"""
        json_path = file_dir / f"{file_name}.json"
        csv_path = file_dir / f"{file_name}.csv"
        # 保存元数据
        save_json(self.meta.model_dump(), json_path)
        self.data.to_csv(csv_path, index=False, encoding="utf-8-sig")

    def append_data(
        self, df: pd.DataFrame, id_col: str = "title", time_col: str = "create_time"
    ):
        """追加数据"""
        # 去重
        df = df.drop_duplicates(subset=[id_col], keep="first", ignore_index=True)
        # 按照时间排序
        df[time_col] = pd.to_datetime(df[time_col])
        df = df.sort_values(by=time_col, ascending=False, ignore_index=True)
        self.data = pd.concat([self.data, df], ignore_index=True)

    def in_time_range(self, t: datetime) -> bool:
        """
        判断时间是否在范围中

        Args:
            time: 时间

        Returns:
            是否在范围中
        """
        return self.meta.begin <= t <= self.meta.end
