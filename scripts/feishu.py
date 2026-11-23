import base64
import hashlib
import hmac
import os
import time
from datetime import datetime
from pathlib import Path
import requests
import yaml
ROOT = Path(__file__).resolve().parent.parent

SITE_URL = os.environ.get("SITE_URL", "")


# ===== 配置 =====
YAML_PATH = Path(os.environ.get("COMPETITION_YAML") or ROOT / "competition" / "whitelist.yml")
SITE_URL = os.environ.get("SITE_URL", "")   # 站点全量清单地址，由 C 组部署后提供
DUE_DAYS = 30                               # 临近截止阈值：30 天内
SUMMARY_LIMIT = 5                           # 卡片里最多放几条摘要

# 标签色 + 背景色必须成套（飞书枚举）
COLOR_POOL = [
    ("blue", "blue-50"),
    ("violet", "violet-50"),
    ("green", "green-50"),
    ("orange", "orange-50"),
    ("turquoise", "turquoise-50"),
    ("indigo", "indigo-50"),
    ("neutral", "grey-50"),
]

DEADLINE_FMT = "%Y-%m-%d %H:%M:%S"


def parse_deadline(text):
    """兼容 '2027-03-01 23:59:59' 和 '2026-12-01' 两种写法，解析失败返回 None。"""
    for fmt in (DEADLINE_FMT, "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt)
        except (ValueError, TypeError):
            continue
    return None


def load_competitions(path):
    """读取竞赛白名单 YAML，转成卡片能用的统一结构。"""
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or []

    today = datetime.now().date()
    competitions = []
    for item in raw:
        deadline_raw = item.get("deadline")
        dt = parse_deadline(deadline_raw) if deadline_raw else None
        competitions.append({
            "name": item.get("title", ""),
            "sub": item.get("sub", ""),
            "category": item.get("category", ""),
            "url": item.get("site") or "",
            "deadline": deadline_raw,
            "days_left": (dt.date() - today).days if dt else None,
        })
    return competitions


def upcoming(competitions, max_days=DUE_DAYS):
    """只保留：有截止时间、未过期、且在 max_days 内的条目。"""
    return [
        c for c in competitions
        if c["days_left"] is not None and 0 <= c["days_left"] <= max_days
    ]


def pick_summary(competitions):
    """挑卡片摘要：优先临近截止；没有就退取前几条做预览。返回 (列表, 模式)。"""
    due = upcoming(competitions)
    if due:
        return due[:SUMMARY_LIMIT], "due"
    return competitions[:SUMMARY_LIMIT], "preview"


def build_item(name, category, deadline, days_left, url, tag_color, bg_color):
    lines = [f"**{name}** <text_tag color='{tag_color}'>{category}</text_tag>"]

    if deadline and days_left is not None:
        lines.append(f"截止：{deadline}（还剩 **{days_left} 天**）")
    else:
        lines.append("截止时间：待公布")

    if url:
        lines.append(f"[查看详情]({url})")

    return {
        "tag": "column_set",
        "flex_mode": "stretch",
        "horizontal_spacing": "8px",
        "horizontal_align": "left",
        "columns": [
            {
                "tag": "column",
                "width": "auto",
                "background_style": bg_color,
                "elements": [
                    {
                        "tag": "markdown",
                        "content": "\n".join(lines),
                        "text_align": "left",
                    }
                ],
                "padding": "10px 12px 10px 12px",
                "vertical_spacing": "6px",
                "horizontal_align": "left",
                "vertical_align": "top",
            }
        ],
        "margin": "0px 0px 0px 0px",
    }


def build_card(title, competitions, site_url=""):
    elements = []
    for i, c in enumerate(competitions):
        key = c.get("sub") or c.get("category") or ""
        index = len(key) % len(COLOR_POOL)
        tag_color, bg_color = COLOR_POOL[index]

        elements.append(build_item(
            name=c["name"],
            category=c["category"],
            deadline=c["deadline"],
            days_left=c["days_left"],
            url=c["url"],
            tag_color=tag_color,
            bg_color=bg_color,
        ))

        if i < len(competitions) - 1:
            elements.append({"tag": "hr"})

    # 卡片底部：站点全量清单入口
    if site_url:
        elements.append({"tag": "hr"})
        elements.append({
            "tag": "markdown",
            "content": f"[👉 在站点查看全部比赛]({site_url})",
            "text_align": "center",
        })

    return {
        "schema": "2.0",
        "config": {"update_multi": True},
        "header": {
            "title": {"tag": "plain_text", "content": title},
            "subtitle": {"tag": "plain_text", "content": ""},
            "template": "orange",
            "padding": "12px 8px 12px 8px",
        },
        "body": {"elements": elements},
    }


def gen_sign(timestamp, secret):
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(
        string_to_sign.encode("utf-8"),
        msg=b"",
        digestmod=hashlib.sha256,
    ).digest()
    return base64.b64encode(hmac_code).decode("utf-8")


def send_card(webhook, secret, card):
    timestamp = str(int(time.time()))
    sign = gen_sign(timestamp, secret)
    payload = {
        "timestamp": timestamp,
        "sign": sign,
        "msg_type": "interactive",
        "card": card,
    }
    resp = requests.post(webhook, json=payload, timeout=10)
    result = resp.json()
    if result.get("code") != 0:
        raise RuntimeError(f"发送失败：{result}")
    print("[OK] 消息已发送")


def main():
    webhook = os.environ.get("FEISHU_WEBHOOK")
    secret = os.environ.get("FEISHU_SECRET")
    if not webhook or not secret:
        print("请先设置 FEISHU_WEBHOOK 和 FEISHU_SECRET 环境变量")
        return

    competitions = load_competitions(YAML_PATH)
    print(f"共读取 {len(competitions)} 条竞赛")

    summary, mode = pick_summary(competitions)
    if not summary:
        print("竞赛列表为空，不发送卡片。")
        return

    title = "⏰ 近期比赛与活动倒计时" if mode == "due" else "📋 比赛一览（预览）"
    print(f"推送模式：{mode}，摘要 {len(summary)} 条")

    card = build_card(title, summary, site_url=SITE_URL)
    send_card(webhook, secret, card)


if __name__ == "__main__":
    main()
