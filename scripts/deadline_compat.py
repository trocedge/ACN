# -*- coding: utf-8 -*-
"""老链路空格日期与新表 ISO 8601 的双轨兼容解析。

过渡期前端可复用本模块，无需等待老链路切换格式；不改写任何源档案。
"""
from datetime import datetime

FORMATS = ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d")


def parse_deadline(value):
    """返回 datetime；TBD / 空值 / 非法格式一律返回 None，不猜测。"""
    if value is None:
        return None
    s = str(value).strip()
    if not s or s.upper() == "TBD":
        return None
    for fmt in FORMATS:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def to_iso(value):
    """统一成 ISO 8601；无法解析时原样返回，便于展示层做兜底。"""
    dt = parse_deadline(value)
    return dt.strftime("%Y-%m-%dT%H:%M:%S") if dt else value
