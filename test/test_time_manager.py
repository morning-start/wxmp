"""测试 time_manager 模块"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import pytest

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from wxmp.tools.time_manager import TimeManager, TimeRange


class ChangeTracker:
    """跟踪 TimeManager 状态变化"""

    def __init__(self, manager: TimeManager):
        self.old_meta = manager.meta.model_dump()
        self.manager = manager

    def capture_change(self) -> dict:
        """捕获变化并返回对比信息"""
        new_meta = self.manager.meta.model_dump()
        return {
            "old": self.old_meta,
            "new": new_meta,
            "changes": self._get_changes(self.old_meta, new_meta),
        }

    def _get_changes(self, old: dict, new: dict) -> dict:
        """获取变化的字段"""
        changes = {}
        for key in old:
            if old[key] != new[key]:
                changes[key] = {"from": old[key], "to": new[key]}
        return changes

    def print_changes(self, result: TimeRange | None = None):
        """打印变化信息"""
        info = self.capture_change()
        print("\n=== 状态变化 ===")
        print(f"原始 meta: {info['old']}")
        print(f"新 meta:    {info['new']}")
        if info["changes"]:
            print("\n变更项:")
            for key, change in info["changes"].items():
                print(f"  {key}: {change['from']} -> {change['to']}")
        else:
            print("\n无变更")
        if result:
            print(f"\n返回结果: {result.model_dump()}")


class TestTimeRange:
    """测试 TimeRange 类"""

    def test_end_default_value_format(self):
        """测试 end 默认值是否与 YYYY-MM-DD 序列化格式一致"""
        # 创建 TimeRange 实例，使用默认 end 值
        time_range = TimeRange(begin=datetime(2026, 3, 1))

        # 获取 end 的默认值
        end_default = time_range.end

        # 序列化后的值
        serialized = time_range.model_dump()
        serialized_end = serialized["end"]

        print(f"\n=== 测试 end 默认值格式 ===")
        print(f"end 默认值 (datetime): {end_default}")
        print(f"end 默认值类型: {type(end_default)}")
        print(f"序列化后的 end: {serialized_end}")
        print(f"序列化后的 end 类型: {type(serialized_end)}")

        # 验证序列化格式为 YYYY-MM-DD
        assert isinstance(serialized_end, str), "序列化后的 end 应该是字符串"
        assert (
            len(serialized_end) == 10
        ), "序列化后的 end 应该是 YYYY-MM-DD 格式 (10个字符)"
        assert serialized_end.count("-") == 2, "序列化后的 end 应该包含两个横线"

        # 验证 end 默认值的时间部分是否为 00:00:00
        assert (
            end_default.hour == 0
        ), f"end 默认值小时应该是 0，实际是 {end_default.hour}"
        assert (
            end_default.minute == 0
        ), f"end 默认值分钟应该是 0，实际是 {end_default.minute}"
        assert (
            end_default.second == 0
        ), f"end 默认值秒应该是 0，实际是 {end_default.second}"
        assert (
            end_default.microsecond == 0
        ), f"end 默认值微秒应该是 0，实际是 {end_default.microsecond}"

        # 验证序列化后的值与原始值一致（日期部分）
        expected_date_str = end_default.strftime("%Y-%m-%d")
        assert (
            serialized_end == expected_date_str
        ), f"序列化值 {serialized_end} 应该等于 {expected_date_str}"

        print(f"✅ end 默认值格式测试通过")

    def test_serialization_format(self):
        """测试序列化格式"""
        time_range = TimeRange(
            begin=datetime(2026, 3, 14, 10, 30, 45), end=datetime(2026, 3, 15, 8, 0, 0)
        )

        serialized = time_range.model_dump()

        print(f"\n=== 测试序列化格式 ===")
        print(f"原始 begin: {time_range.begin}")
        print(f"原始 end: {time_range.end}")
        print(f"序列化结果: {serialized}")

        assert serialized["begin"] == "2026-03-14"
        assert serialized["end"] == "2026-03-15"

        print(f"✅ 序列化格式测试通过")

    def test_contains_datetime(self):
        """测试 __contains__ 方法对 datetime 的支持"""
        time_range = TimeRange(begin=datetime(2026, 3, 1), end=datetime(2026, 3, 31))

        # 测试包含的日期
        assert datetime(2026, 3, 15) in time_range
        assert datetime(2026, 3, 1) in time_range  # 边界值
        assert datetime(2026, 3, 31) in time_range  # 边界值

        # 测试不包含的日期
        assert datetime(2026, 2, 28) not in time_range
        assert datetime(2026, 4, 1) not in time_range

        print(f"✅ __contains__ 方法测试通过")


class TestMatchRemainingTimeRange:
    """测试 match_remaining_time_range 方法"""

    def test_no_overlap_need_time_after_meta(self):
        """测试 need_time 在 meta 之后，无重叠"""
        # meta: 2026-01-01 到 2026-01-10
        # need_time: 2026-01-15 到 2026-01-20
        meta = TimeRange(begin=datetime(2026, 1, 1), end=datetime(2026, 1, 10))
        need_time = TimeRange(begin=datetime(2026, 1, 15), end=datetime(2026, 1, 20))

        manager = TimeManager.new()
        manager.meta = meta

        # 创建变化跟踪器
        tracker = ChangeTracker(manager)

        print(f"\n=== 测试 need_time 在 meta 之后 ===")
        print(f"初始状态: meta={meta.model_dump()}, need_time={need_time.model_dump()}")
        print(f"条件: meta.end ({meta.end}) <= need_time.begin ({need_time.begin})")

        result = manager.match_remaining_time_range(need_time)

        tracker.print_changes(result)

        # 应该返回整个 need_time
        assert result is not None
        assert result.begin == need_time.begin
        assert result.end == need_time.end

        # meta 应该被更新为 need_time
        assert manager.meta.begin == need_time.begin
        assert manager.meta.end == need_time.end

        print(f"✅ need_time 在 meta 之后测试通过")

    def test_no_overlap_need_time_before_meta(self):
        """测试 need_time 在 meta 之前，无重叠"""
        # meta: 2026-01-15 到 2026-01-20
        # need_time: 2026-01-01 到 2026-01-10
        meta = TimeRange(begin=datetime(2026, 1, 15), end=datetime(2026, 1, 20))
        need_time = TimeRange(begin=datetime(2026, 1, 1), end=datetime(2026, 1, 10))

        manager = TimeManager.new()
        manager.meta = meta

        tracker = ChangeTracker(manager)

        print(f"\n=== 测试 need_time 在 meta 之前 ===")
        print(f"初始状态: meta={meta.model_dump()}, need_time={need_time.model_dump()}")
        print(f"条件: need_time.end ({need_time.end}) <= meta.begin ({meta.begin})")

        result = manager.match_remaining_time_range(need_time)

        tracker.print_changes(result)

        # 应该返回整个 need_time
        assert result is not None
        assert result.begin == need_time.begin
        assert result.end == need_time.end

        # meta 应该被更新为 need_time
        assert manager.meta.begin == need_time.begin
        assert manager.meta.end == need_time.end

        print(f"✅ need_time 在 meta 之前测试通过")

    def test_partial_overlap_need_time_extends_end(self):
        """测试部分重叠，need_time 向后延伸

        条件: meta.begin < need_time.begin < meta.end < need_time.end
        即: 2026-01-01 < 2026-01-10 < 2026-01-15 < 2026-01-20
        """
        # meta: 2026-01-01 到 2026-01-15
        # need_time: 2026-01-10 到 2026-01-20
        # 预期剩余: 2026-01-15 到 2026-01-20
        meta = TimeRange(begin=datetime(2026, 1, 1), end=datetime(2026, 1, 15))
        need_time = TimeRange(begin=datetime(2026, 1, 10), end=datetime(2026, 1, 20))

        # 验证条件: meta.begin < need_time.begin < meta.end < need_time.end
        assert meta.begin < need_time.begin, f"条件不满足: {meta.begin} < {need_time.begin}"
        assert need_time.begin < meta.end, f"条件不满足: {need_time.begin} < {meta.end}"
        assert meta.end < need_time.end, f"条件不满足: {meta.end} < {need_time.end}"

        manager = TimeManager.new()
        manager.meta = meta

        tracker = ChangeTracker(manager)

        print(f"\n=== 测试 need_time 向后延伸 ===")
        print(f"条件验证: {meta.begin} < {need_time.begin} < {meta.end} < {need_time.end}")
        print(f"初始状态: meta={meta.model_dump()}, need_time={need_time.model_dump()}")

        result = manager.match_remaining_time_range(need_time)

        tracker.print_changes(result)

        # 应该返回剩余部分
        assert result is not None
        assert result.begin == datetime(2026, 1, 15)
        assert result.end == datetime(2026, 1, 20)

        # meta.end 应该被扩展，但 meta.begin 保持不变
        assert manager.meta.begin == datetime(2026, 1, 1)  # 保持不变
        assert manager.meta.end == datetime(2026, 1, 20)  # 被扩展

        print(f"✅ need_time 向后延伸测试通过")

    def test_partial_overlap_need_time_extends_begin(self):
        """测试部分重叠，need_time 向前延伸

        条件: need_time.begin < meta.begin < need_time.end < meta.end
        即: 2026-01-01 < 2026-01-10 < 2026-01-15 < 2026-01-20
        """
        # meta: 2026-01-10 到 2026-01-20
        # need_time: 2026-01-01 到 2026-01-15
        # 预期剩余: 2026-01-01 到 2026-01-10
        meta = TimeRange(begin=datetime(2026, 1, 10), end=datetime(2026, 1, 20))
        need_time = TimeRange(begin=datetime(2026, 1, 1), end=datetime(2026, 1, 15))

        # 验证条件: need_time.begin < meta.begin < need_time.end < meta.end
        assert need_time.begin < meta.begin, f"条件不满足: {need_time.begin} < {meta.begin}"
        assert meta.begin < need_time.end, f"条件不满足: {meta.begin} < {need_time.end}"
        assert need_time.end < meta.end, f"条件不满足: {need_time.end} < {meta.end}"

        manager = TimeManager.new()
        manager.meta = meta

        tracker = ChangeTracker(manager)

        print(f"\n=== 测试 need_time 向前延伸 ===")
        print(f"条件验证: {need_time.begin} < {meta.begin} < {need_time.end} < {meta.end}")
        print(f"初始状态: meta={meta.model_dump()}, need_time={need_time.model_dump()}")

        result = manager.match_remaining_time_range(need_time)

        tracker.print_changes(result)

        # 应该返回剩余部分
        assert result is not None
        assert result.begin == datetime(2026, 1, 1)
        assert result.end == datetime(2026, 1, 10)

        # meta.begin 应该被扩展，但 meta.end 保持不变
        assert manager.meta.begin == datetime(2026, 1, 1)  # 被扩展
        assert manager.meta.end == datetime(2026, 1, 20)  # 保持不变

        print(f"✅ need_time 向前延伸测试通过")

    def test_need_time_inside_meta(self):
        """测试 need_time 完全在 meta 内部"""
        # meta: 2026-01-01 到 2026-01-20
        # need_time: 2026-01-10 到 2026-01-15
        # 预期: 无剩余
        meta = TimeRange(begin=datetime(2026, 1, 1), end=datetime(2026, 1, 20))
        need_time = TimeRange(begin=datetime(2026, 1, 10), end=datetime(2026, 1, 15))

        manager = TimeManager.new()
        manager.meta = meta

        tracker = ChangeTracker(manager)

        print(f"\n=== 测试 need_time 完全在 meta 内部 ===")
        print(f"初始状态: meta={meta.model_dump()}, need_time={need_time.model_dump()}")

        result = manager.match_remaining_time_range(need_time)

        tracker.print_changes(result)

        # 应该返回 None（无剩余）
        assert result is None

        # meta 应该保持不变
        assert manager.meta.begin == datetime(2026, 1, 1)
        assert manager.meta.end == datetime(2026, 1, 20)

        print(f"✅ need_time 完全在 meta 内部测试通过")

    def test_meta_inside_need_time(self):
        """测试 meta 完全在 need_time 内部"""
        # meta: 2026-01-10 到 2026-01-15
        # need_time: 2026-01-01 到 2026-01-20
        # 这种情况应该返回 None（因为两端都有重叠）
        meta = TimeRange(begin=datetime(2026, 1, 10), end=datetime(2026, 1, 15))
        need_time = TimeRange(begin=datetime(2026, 1, 1), end=datetime(2026, 1, 20))

        manager = TimeManager.new()
        manager.meta = meta

        tracker = ChangeTracker(manager)

        print(f"\n=== 测试 meta 完全在 need_time 内部 ===")
        print(f"初始状态: meta={meta.model_dump()}, need_time={need_time.model_dump()}")

        result = manager.match_remaining_time_range(need_time)

        tracker.print_changes(result)

        # 这种情况应该返回 None
        assert result is None

        print(f"✅ meta 完全在 need_time 内部测试通过")


class TestTimeManager:
    """测试 TimeManager 类"""

    def test_new(self):
        """测试创建新实例"""
        manager = TimeManager.new()

        assert manager.meta.begin == datetime.min
        assert manager.meta.end == datetime.min
        assert list(manager.data.columns) == ["title", "create_time"]

        print(f"✅ new() 方法测试通过")

    def test_include_time_range(self):
        """测试 include_time_range 方法"""
        manager = TimeManager.new()
        manager.meta = TimeRange(begin=datetime(2026, 3, 1), end=datetime(2026, 3, 31))

        # 测试包含的时间范围
        inner_range = TimeRange(begin=datetime(2026, 3, 10), end=datetime(2026, 3, 20))
        assert manager.include_time_range(inner_range) is True

        # 测试不包含的时间范围（超出）
        outer_range = TimeRange(begin=datetime(2026, 2, 1), end=datetime(2026, 4, 1))
        assert manager.include_time_range(outer_range) is False

        # 测试部分重叠（begin 超出）
        partial_begin = TimeRange(
            begin=datetime(2026, 2, 15), end=datetime(2026, 3, 15)
        )
        assert manager.include_time_range(partial_begin) is False

        # 测试部分重叠（end 超出）
        partial_end = TimeRange(begin=datetime(2026, 3, 15), end=datetime(2026, 4, 15))
        assert manager.include_time_range(partial_end) is False

        print(f"✅ include_time_range 方法测试通过")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
