"""
Cron 表达式解析器 - 支持标准 6 字段 Cron
格式：* * * * * *
字段：秒 分 时 日 月 周
"""

import re
from datetime import datetime, timedelta
from typing import List, Set, Dict, Any


class CronParser:
    """Cron 表达式解析器"""

    FIELD_NAMES = ['second', 'minute', 'hour', 'day', 'month', 'weekday']
    FIELD_RANGES = {
        'second': (0, 59),
        'minute': (0, 59),
        'hour': (0, 23),
        'day': (1, 31),
        'month': (1, 12),
        'weekday': (0, 6)
    }

    MONTH_NAMES = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }

    WEEKDAY_NAMES = {
        'sun': 0, 'mon': 1, 'tue': 2, 'wed': 3, 'thu': 4, 'fri': 5, 'sat': 6
    }

    def __init__(self, expression: str):
        self.expression = expression.strip()
        self.fields = self._parse_expression()

    def _parse_expression(self) -> Dict[str, Set[int]]:
        parts = self.expression.split()
        if len(parts) != 6:
            raise ValueError(f"无效的 Cron 表达式：需要 6 个字段，当前 {len(parts)} 个")

        result = {}
        for i, field_name in enumerate(self.FIELD_NAMES):
            result[field_name] = self._parse_field(parts[i], field_name)

        return result

    def _parse_field(self, field_str: str, field_name: str) -> Set[int]:
        min_val, max_val = self.FIELD_RANGES[field_name]

        if field_name == 'month':
            for name, num in self.MONTH_NAMES.items():
                field_str = field_str.lower().replace(name, str(num))
        elif field_name == 'weekday':
            for name, num in self.WEEKDAY_NAMES.items():
                field_str = field_str.lower().replace(name, str(num))

        values = set()

        for part in field_str.split(','):
            values.update(self._parse_part(part, min_val, max_val))

        return values

    def _parse_part(self, part: str, min_val: int, max_val: int) -> Set[int]:
        if part == '*':
            return set(range(min_val, max_val + 1))

        if part.startswith('*/'):
            step = int(part[2:])
            return set(range(min_val, max_val + 1, step))

        if '-' in part and '/' not in part:
            start, end = part.split('-')
            start = int(start)
            end = int(end)
            if start < min_val or end > max_val:
                raise ValueError(f"值超出范围 [{min_val}-{max_val}]: {part}")
            return set(range(start, end + 1))

        match = re.match(r'(\d+)-(\d+)/(\d+)', part)
        if match:
            start, end, step = map(int, match.groups())
            if start < min_val or end > max_val:
                raise ValueError(f"值超出范围 [{min_val}-{max_val}]: {part}")
            return set(range(start, end + 1, step))

        val = int(part)
        if val < min_val or val > max_val:
            raise ValueError(f"值超出范围 [{min_val}-{max_val}]: {val}")
        return {val}

    def next_run_time(self, after: datetime = None) -> datetime:
        if after is None:
            after = datetime.now()

        current = after.replace(microsecond=0) + timedelta(seconds=1)

        for _ in range(5 * 365 * 24 * 60 * 60):
            matches = (
                current.second in self.fields['second'] and
                current.minute in self.fields['minute'] and
                current.hour in self.fields['hour'] and
                current.day in self.fields['day'] and
                current.month in self.fields['month'] and
                current.weekday() in self.fields['weekday']
            )
            if matches:
                return current

            current += timedelta(seconds=1)

        raise ValueError("找不到下一次运行时间")

    def should_run(self, dt: datetime = None) -> bool:
        if dt is None:
            dt = datetime.now()

        return (
            dt.second in self.fields['second'] and
            dt.minute in self.fields['minute'] and
            dt.hour in self.fields['hour'] and
            dt.month in self.fields['month'] and
            dt.weekday() in self.fields['weekday']
        )

    def __str__(self) -> str:
        return self.expression


def format_next_runs(expression: str, count: int = 5) -> List[datetime]:
    parser = CronParser(expression)
    runs = []
    current = datetime.now()

    for _ in range(count):
        next_run = parser.next_run_time(current)
        runs.append(next_run)
        current = next_run

    return runs
