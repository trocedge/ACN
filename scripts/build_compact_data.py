# -*- coding: utf-8 -*-
"""ACN 数据格式转换与增强。

将 conference/ 下的散装会议档案合并为一份适合行式展示的精简数据视图，
并补充面向全校同学使用所需的派生字段（状态、双时区、中文辅助字段）。

设计原则：
  1. 本项目数据均为学术会议，不采用参考站的三表分类方案，只产出一份表。
  2. 保持原有数据链路：老档案只读，贡献方式（改 yml 提 PR）不变。
  3. 字段先全保留：界面展示范围属展示层决策，数据层不做不可逆删减。
  4. 时区保留原值并补可确定的 UTC 偏移，不做静态时区替换。
  5. 派生字段只做「可确定规则的换算」，无法确定一律留空并计入报告，绝不推测或编造。

用法：
    python scripts/build_compact_data.py                  # 产出 data/conferences.yml
    python scripts/build_compact_data.py --out public/data/conferences.yml
    python scripts/build_compact_data.py --check          # 仅校验，不落盘

字段规范见 docs/data-format-specification.md 与 docs/field-contract.md。
"""
import argparse
import io
import json
import re
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "conference"
ACCEPT_DIR = ROOT / "accept_rates"
DEFAULT_OUT = ROOT / "data" / "conferences.yml"

# 数据格式版本：字段结构变更时递增，供展示层判断兼容性
SCHEMA_VERSION = "1.1"

# 时区口径：AoE 定义即 UTC-12；PT 有夏令时，不固定，留空由展示层按日期判
FIXED_OFFSET = {"AoE": -12, "UTC": 0, "UTC+0": 0}
_UTC_RE = re.compile(r"^UTC([+-])(\d{1,2})$")
DATE_SPACE = re.compile(r"^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2})$")
DATE_ONLY = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ISO_DT = re.compile(r"^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})$")

# 英文月份 → 中文数字。只覆盖标准月份名与常见缩写，其余不猜测
MONTHS = {
    "january": 1, "jan": 1, "february": 2, "feb": 2, "march": 3, "mar": 3,
    "april": 4, "apr": 4, "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7,
    "august": 8, "aug": 8, "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10, "november": 11, "nov": 11,
    "december": 12, "dec": 12,
}
# 英文日期范围，例：June 12-17, 2022 / June 12, 2022
DATE_EN = re.compile(r"^([A-Za-z]+)\.?\s+(\d{1,2})(?:\s*-\s*(\d{1,2}))?,?\s*(\d{4})(?:\s*[\[(].*)?$")

# 国家/地区白名单：只翻译能确定的国家名，城市名保留原文（不编造中文译名）
COUNTRIES = {
    "usa": "美国", "united states": "美国", "u.s.a.": "美国", "us": "美国",
    "china": "中国", "japan": "日本", "uk": "英国", "united kingdom": "英国",
    "germany": "德国", "france": "法国", "canada": "加拿大",
    "australia": "澳大利亚", "italy": "意大利", "spain": "西班牙",
    "switzerland": "瑞士", "netherlands": "荷兰", "singapore": "新加坡",
    "south korea": "韩国", "korea": "韩国", "india": "印度",
    "austria": "奥地利", "sweden": "瑞典", "portugal": "葡萄牙",
    "greece": "希腊", "poland": "波兰", "israel": "以色列",
    "brazil": "巴西", "mexico": "墨西哥", "cyprus": "塞浦路斯",
    "denmark": "丹麦", "ireland": "爱尔兰", "new zealand": "新西兰",
    "turkey": "土耳其", "czech republic": "捷克", "finland": "芬兰",
    "vietnam": "越南", "belgium": "比利时", "malaysia": "马来西亚",
    "estonia": "爱沙尼亚", "norway": "挪威", "croatia": "克罗地亚",
    "slovenia": "斯洛文尼亚", "serbia": "塞尔维亚", "romania": "罗马尼亚",
    "luxembourg": "卢森堡", "iceland": "冰岛", "hungary": "匈牙利",
    "ukraine": "乌克兰", "argentina": "阿根廷", "chile": "智利",
    "south africa": "南非", "egypt": "埃及", "thailand": "泰国",
    "taiwan, china": "中国台湾", "hong kong, china": "中国香港",
    "macao, china": "中国澳门", "taiwan": "中国台湾",
    "hong kong": "中国香港", "macao": "中国澳门", "macau": "中国澳门",
    "uae": "阿联酋", "united arab emirates": "阿联酋",
    "republic of korea": "韩国", "russia": "俄罗斯",
    "the netherlands": "荷兰", "england": "英国", "scotland": "英国",
}
ONLINE_WORDS = {"online", "virtual", "线上", "remote", "hybrid"}
US_STATE_CODES = {
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA",
    "KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
    "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT",
    "VA","WA","WV","WI","WY","DC",
}

REQUIRED = ("title", "description", "sub", "confs")
TIMEZONE_ALIAS_PATH = ROOT / "docs" / "timezone-alias.json"
PLACE_ALIAS_PATH = ROOT / "docs" / "place-aliases.yml"
TBD_REVIEW_DAYS = 30


def utc_offset(tz):
    """能确定的才返回数字，不能确定（PT / 未知）返回 None，宁可留空也不错算。"""
    if not tz:
        return None
    tz = str(tz).strip()
    if tz in FIXED_OFFSET:
        return FIXED_OFFSET[tz]
    m = _UTC_RE.match(tz)
    if m:
        return (1 if m.group(1) == "+" else -1) * int(m.group(2))
    return None


def load_timezone_alias():
    """读取时区别名表，仅用于归一化建议，不改写源数据原值。"""
    if not TIMEZONE_ALIAS_PATH.is_file():
        return {}
    try:
        return json.loads(io.open(TIMEZONE_ALIAS_PATH, encoding="utf-8").read()) or {}
    except Exception:
        return {}


def load_place_alias():
    """读取人工确认的地点译名表；脚本只查表，不做推测翻译。"""
    if not PLACE_ALIAS_PATH.is_file():
        return {}
    try:
        data = yaml.safe_load(io.open(PLACE_ALIAS_PATH, encoding="utf-8").read()) or {}
        return data.get("cities", {}) or {}
    except Exception:
        return {}


PLACE_ALIAS = load_place_alias()


def pacific_offset(iso_local):
    """按具体日期判定美国太平洋时区偏移：夏令时 UTC-7，其余 UTC-8。

    规则：3 月第二个周日 02:00 起至 11 月第一个周日 02:00 止。
    只用于 PT 条目的推算值，结果标注 dst_basis，不写成官方公布时间。
    """
    dt = parse_iso(iso_local)
    if dt is None:
        return None
    def nth_sunday(year, month, n):
        first = datetime(year, month, 1)
        return first + timedelta(days=(6 - first.weekday()) % 7 + 7 * (n - 1))
    start = nth_sunday(dt.year, 3, 2).replace(hour=2)
    end = nth_sunday(dt.year, 11, 1).replace(hour=2)
    return -7 if start <= dt < end else -8


def make_sort_key(status, timeline):
    """行式列表排序键：状态优先 + 最晚截止时刻，只用已有字段计算。"""
    rank = {"active": 0, "tbd": 1, "past": 2, "unknown": 3}.get(status, 3)
    latest = max([str(p.get("deadline_beijing") or p.get("deadline_beijing_dst")
                      or p.get("deadline") or "") for p in timeline] or [""])
    return "%d|%s" % (rank, latest)


def norm_deadline(value):
    """空格分隔 → ISO 8601 带 T；只有日期的按仓库约定补 23:59:59；TBD 原样保留。"""
    if value is None:
        return value, "empty"
    s = str(value).strip()
    if s == "TBD" or not s:
        return s, "tbd"
    m = DATE_SPACE.match(s)
    if m:
        return m.group(1) + "T" + m.group(2), "space_to_T"
    if DATE_ONLY.match(s):
        return s + "T23:59:59", "date_only_padded"
    if ISO_DT.match(s):
        return s, "already_iso"
    return s, "unrecognized"


def parse_iso(s):
    """把 ISO 时刻解析成 naive datetime；解析不了返回 None。"""
    if not s:
        return None
    m = ISO_DT.match(str(s).strip())
    if not m:
        return None
    try:
        return datetime.strptime(m.group(1) + " " + m.group(2), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def to_beijing(iso_local, offset):
    """按可确定的 UTC 偏移换算成北京时间（UTC+8）。

    local → UTC = local - offset；UTC → 北京 = UTC + 8，合计 local + (8 - offset)。
    AoE(-12) 即 +20 小时。offset 为 None 时返回 None，展示层需按日期自行判夏令时。
    """
    dt = parse_iso(iso_local)
    if dt is None or offset is None:
        return None
    return (dt + timedelta(hours=8 - offset)).strftime("%Y-%m-%dT%H:%M:%S")


def to_zh_date(text):
    """英文人类可读日期 → 中文日期；已是中文或格式不匹配则返回原值 / None。

    只做结构化转换，不做语义猜测：June 12-17, 2022 → 2022 年 6 月 12 日 - 17 日。
    """
    if not text:
        return None
    s = str(text).strip()
    if "年" in s:
        return s  # 原本就是中文，原样保留
    m = DATE_EN.match(s)
    if not m:
        # 跨月区间，例：March 31-April 2, 2027 / June 28 - July 2, 2027
        cm = re.match(r"^([A-Za-z]+)\.?\s+(\d{1,2})\s*-\s*([A-Za-z]+)\.?\s+(\d{1,2}),?\s*(\d{4})$", s)
        if cm:
            m1, m2 = MONTHS.get(cm.group(1).lower()), MONTHS.get(cm.group(3).lower())
            if m1 and m2:
                return "%s 年 %d 月 %s 日 - %d 月 %s 日" % (
                    cm.group(5), m1, cm.group(2), m2, cm.group(4))
        return None
    month = MONTHS.get(m.group(1).lower())
    if month is None:
        return None
    year, day1, day2 = m.group(4), m.group(2), m.group(3)
    head = "%s 年 %d 月 %s 日" % (year, month, day1)
    return head + (" - %s 日" % day2 if day2 else "")


def to_zh_place(text):
    """地点中文化：只翻译白名单国家，城市名保留原文，避免编造译名。

    Philadelphia, PA, USA → 美国 · Philadelphia；格式不明确则返回 None。
    """
    if not text:
        return None
    s = str(text).strip()
    # 去掉括号补充（Hybrid / Online / Virtual）与 "and Online" 混合写法，只留主地点
    s = re.sub(r"\s*\([^)]*\)\s*$", "", s).strip()
    s = re.sub(r"\s+(?:and|&|/)\s+(?:online|virtual|hybrid)\s*$", "", s, flags=re.I).strip()
    low = s.lower()
    if low == "tbd" or not s:
        return None
    if low in ONLINE_WORDS or low in {"virtual conference", "online conference",
                                      "virtual only", "online event"}:
        return "线上"
    if s in PLACE_ALIAS:
        return PLACE_ALIAS[s]
    if "年" not in s and re.search(r"[\u4e00-\u9fff]", s):
        return s  # 已含中文，原样保留
    parts = [p.strip() for p in s.split(",") if p.strip()]
    if not parts:
        return None
    country = COUNTRIES.get(parts[-1].lower())
    if country is None and len(parts) >= 2 and parts[-1].upper() in US_STATE_CODES:
        country = "美国"  # 州缩写是公开标准代码，只用于确定国家，城市名仍保留原文
    if country is None:
        return None
    city = parts[0] if len(parts) > 1 else ""
    return country + (" · " + city if city and city.lower() != parts[-1].lower() else "")


def compute_status(timeline, now):
    """按最晚截止日判断届次状态：active / past / tbd / unknown。

    优先用换算后的北京时间；无换算值时退化为本地时间直比，并在 status_basis 标注，
    避免把未换算时间伪装成已换算。TBD 不参与比较。
    """
    parsed, naive, pt_seen = [], [], []
    has_tbd = False
    for p in timeline:
        dl = p.get("deadline")
        if dl == "TBD" or not dl:
            has_tbd = True
            continue
        bj = p.get("deadline_beijing")
        dt = parse_iso(bj) if bj else None
        if dt is not None:
            parsed.append(dt)
            continue
        dst = p.get("deadline_beijing_dst")
        ddt = parse_iso(dst) if dst else None
        if ddt is not None:
            parsed.append(ddt)
            pt_seen.append(True)
            continue
        local_dt = parse_iso(dl)
        if local_dt is not None:
            naive.append(local_dt)
    basis = ("pt_dst" if pt_seen else "beijing") if parsed else ("local_naive" if naive else "none")
    pool = parsed or naive
    if not pool:
        return ("tbd" if has_tbd else "unknown"), basis
    return ("past" if max(pool) < now else "active"), basis


def load_entries():
    """扫描散装会议档案，返回 (会议列表, 统计计数器)。"""
    entries, stats = [], Counter()
    for path in sorted(SRC_DIR.glob("**/*.yml")):
        if path.name == "types.yml":
            continue
        stats["files"] += 1
        try:
            data = yaml.safe_load(io.open(path, encoding="utf-8").read())
        except Exception as e:
            stats["parse_error"] += 1
            print("  [解析失败] %s: %s" % (path.relative_to(ROOT), e), file=sys.stderr)
            continue
        if not isinstance(data, list):
            stats["not_list"] += 1
            continue
        for item in data:
            if isinstance(item, dict):
                stats["conferences"] += 1
                entries.append((path, item))
    return entries, stats


def convert(entries, stats, now):
    """老结构 → 精简大表。老字段一律保留，派生字段按可确定规则生成。"""
    out = []
    for path, item in entries:
        for key in REQUIRED:
            if key not in item:
                stats["missing_" + key] += 1

        events = []
        for conf in (item.get("confs") or []):
            if not isinstance(conf, dict):
                continue
            stats["editions"] += 1
            tz = conf.get("timezone")
            off = utc_offset(tz)
            stats["tz_total"] += 1
            if off is None:
                stats["tz_unresolved"] += 1

            timeline = []
            for point in (conf.get("timeline") or []):
                if not isinstance(point, dict):
                    continue
                stats["timeline_points"] += 1
                new_point = dict(point)
                dl, how = norm_deadline(point.get("deadline"))
                new_point["deadline"] = dl
                stats["date_" + how] += 1
                bj = to_beijing(dl, off)
                new_point["deadline_beijing"] = bj
                if bj:
                    stats["bj_converted"] += 1
                elif dl and dl != "TBD":
                    stats["bj_unresolved"] += 1
                # PT 类：按日期判夏令时，产出独立推算字段，不覆盖确定性换算值
                if str(tz).strip() == "PT":
                    pdst = pacific_offset(dl)
                    new_point["deadline_beijing_dst"] = to_beijing(dl, pdst)
                    new_point["dst_basis"] = "pt_dst" if pdst is not None else "unknown"
                    stats["pt_dst"] += 1
                # TBD：只补可推导的跟踪信息，不推测任何日期
                if dl == "TBD":
                    new_point["tbd_review"] = (now + timedelta(days=TBD_REVIEW_DAYS)).strftime("%Y-%m-%d")
                    new_point["tbd_review_note"] = "建议复查日（非官方公布）"
                    new_point["tbd_source"] = conf.get("link")
                    new_point["tbd_owner"] = "data-maintainer"
                    stats["tbd_tracked"] += 1
                timeline.append(new_point)

            status, basis = compute_status(timeline, now)
            stats["status_" + status] += 1
            stats["basis_" + basis] += 1

            date_zh = to_zh_date(conf.get("date"))
            place_zh = to_zh_place(conf.get("place"))
            stats["date_zh_ok"] += 1 if date_zh else 0
            stats["place_zh_ok"] += 1 if place_zh else 0

            event = {
                "year": conf.get("year"),
                "id": conf.get("id"),
                "link": conf.get("link"),
                "timeline": timeline,
                "timezone": tz,                    # 原值，绝不硬替换
                "timezone_utc_offset": off,        # PT 等留 None
                "date": conf.get("date"),          # 英文原值保留
                "date_zh": date_zh,                # 无法确定则为 None
                "place": conf.get("place"),
                "place_zh": place_zh,
                "status": status,
                "status_basis": basis,
            }
            for k, v in conf.items():
                if k not in event and k not in ("timeline", "timezone"):
                    event[k] = v
            event["sort_key"] = make_sort_key(status, timeline)
            events.append(event)

        row = {
            "schema_version": SCHEMA_VERSION,
            "status_as_of": now.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00",
            "title": item.get("title"),
            "description": item.get("description"),
            "sub": item.get("sub"),                # 学科，筛选用
            "rank": item.get("rank"),             # CCF 评级，项目内核
            "dblp": item.get("dblp"),
            "source_file": str(path.relative_to(ROOT)).replace("\\", "/"),
            "events": events,                    # confs → events
            "sort_key": make_sort_key(
                min((e["status"] for e in events), key=lambda x: {"active":0,"tbd":1,"past":2,"unknown":3}.get(x,3), default="unknown"),
                [p for e in events for p in e["timeline"]]),
        }
        for k, v in item.items():
            if k not in row and k != "confs":
                row[k] = v
        out.append(row)
    return out


def validate(rows, stats):
    """返回问题列表；空列表表示校验通过。"""
    problems = []
    ids = [e.get("id") for r in rows for e in r["events"]]
    dup = [k for k, v in Counter(i for i in ids if i).items() if v > 1]
    if dup:
        problems.append("重复 id %d 个：%s" % (len(dup), dup[:5]))
    if not rows:
        problems.append("产出为空")
    if stats.get("parse_error"):
        problems.append("%d 个文件解析失败" % stats["parse_error"])
    if stats.get("date_unrecognized"):
        problems.append("%d 条日期格式无法识别" % stats["date_unrecognized"])
    if len(rows) != stats["files"]:
        problems.append("产出条数 %d 与源档案数 %d 不一致" % (len(rows), stats["files"]))
    for r in rows:
        if not r.get("title"):
            problems.append("有条目缺 title：%s" % r.get("source_file"))
            break
    return problems


def check_accept_rates():
    """检查录取率档案与会议档案的关联，返回 (总数, 未匹配列表, 会议档案数)。

    仓库实际以文件名 stem 关联：accept_rates/AI/nips.yml 对应 conference/AI/nips.yml，
    后者 title 却是 NeurIPS。只按标题比会产生大量假阳性，故以 stem 为主判据。
    """
    if not ACCEPT_DIR.is_dir():
        return 0, [], 0
    stems = set()
    for path in SRC_DIR.glob("**/*.yml"):
        if path.name != "types.yml":
            stems.add(path.stem.strip().lower())
    total, broken = 0, []
    for path in sorted(ACCEPT_DIR.glob("**/*.yml")):
        total += 1
        if path.stem.strip().lower() not in stems:
            broken.append(str(path.relative_to(ROOT)).replace("\\", "/"))
    return total, broken, len(stems)


def main():
    ap = argparse.ArgumentParser(description="ACN 数据格式转换与校验")
    ap.add_argument("--out", default=str(DEFAULT_OUT), help="输出路径")
    ap.add_argument("--check", action="store_true", help="仅校验，不落盘")
    args = ap.parse_args()

    now = datetime.now(timezone(timedelta(hours=8))).replace(tzinfo=None)
    entries, stats = load_entries()
    rows = convert(entries, stats, now)
    problems = validate(rows, stats)

    print("=== ACN 数据格式转换报告（schema %s）===" % SCHEMA_VERSION)
    print("扫描档案      : %d" % stats["files"])
    print("会议条目      : %d" % stats["conferences"])
    print("届次 events   : %d" % stats["editions"])
    print("timeline 节点 : %d" % stats["timeline_points"])
    print("日期规范化    : 空格转T %d / 补时刻 %d / 已ISO %d / TBD %d / 未识别 %d" % (
        stats["date_space_to_T"], stats["date_date_only_padded"],
        stats["date_already_iso"], stats["date_tbd"], stats["date_unrecognized"]))
    print("时区          : 共 %d 条，无法固定换算 %d 条（PT 等，保留原值）" % (
        stats["tz_total"], stats["tz_unresolved"]))
    print("北京时间换算  : 成功 %d 条 / 未换算 %d 条（不做静态替换）" % (
        stats["bj_converted"], stats["bj_unresolved"]))
    print("状态分布      : active %d / past %d / tbd %d / unknown %d" % (
        stats["status_active"], stats["status_past"], stats["status_tbd"], stats["status_unknown"]))
    print("状态依据      : 北京时间 %d / 夏令时推算 %d / 本地近似 %d / 无日期 %d" % (
        stats["basis_beijing"], stats["basis_pt_dst"],
        stats["basis_local_naive"], stats["basis_none"]))
    print("中文字段覆盖  : 日期 %d/%d，地点 %d/%d（未覆盖留空，不编造）" % (
        stats["date_zh_ok"], stats["editions"], stats["place_zh_ok"], stats["editions"]))
    acc_total, acc_broken, acc_titles = check_accept_rates()
    print("录取率关联    : 文件 %d 份 / 会议档案标识 %d 个 / 未匹配 %d 份" % (
        acc_total, acc_titles, len(acc_broken)))
    if acc_broken:
        print("                样例：%s" % ", ".join(acc_broken[:3]))
    print("PT 夏令时推算 : %d 条（独立字段，不覆盖确定性换算）" % stats["pt_dst"])
    print("TBD 跟踪字段  : %d 条" % stats["tbd_tracked"])
    print("别名表        : 时区 %d 项 / 地点 %d 项" % (len(load_timezone_alias()), len(PLACE_ALIAS)))
    print("AoE 原值保留  : 是（UTC-12，绝不替换成 Asia/Shanghai）")
    print("校验问题      : %s" % (problems if problems else "无"))

    if args.check:
        print("\n[校验模式] 未写文件。")
        return 1 if problems else 0

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with io.open(out, "w", encoding="utf-8") as f:
        yaml.safe_dump(rows, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
    print("\n已产出: %s (%.1f KB)" % (out, out.stat().st_size / 1024.0))
    print("老文件未改动 : %s" % (SRC_DIR.exists() and "conference/ 仍在"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
