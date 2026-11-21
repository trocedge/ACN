#!/usr/bin/env python3
"""Generate static pages for the whitelist competitions.

The WASM app renders conference deadlines only, so the 84 competitions would
otherwise stay invisible on the deployed site. This script publishes them as
plain HTML next to the conference pages: one index grouped by category plus
one page per competition. All links are relative, so the pages work both on
the root domain and on a GitHub Pages project site served from a sub-path.
"""

import argparse
import re
from html import escape
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "competition" / "whitelist.yml"
TYPES = ROOT / "competition" / "types.yml"

CSS = """
body { font-family: -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif;
       max-width: 920px; margin: 0 auto; padding: 32px 20px; color: #1f2328;
       line-height: 1.7; background: #fff; }
a { color: #5f4695; text-decoration: none; }
a:hover { text-decoration: underline; }
h1 { font-size: 26px; margin-bottom: 4px; }
h2 { font-size: 19px; margin-top: 36px; border-bottom: 1px solid #d8dee4;
     padding-bottom: 6px; }
.meta { color: #59636e; font-size: 14px; }
table { border-collapse: collapse; width: 100%; margin-top: 12px; }
td, th { text-align: left; padding: 8px 10px; border-bottom: 1px solid #eaeef2;
         font-size: 15px; vertical-align: top; }
th { color: #59636e; font-weight: 600; font-size: 13px; }
td:last-child, th:last-child, td:nth-child(3), th:nth-child(3) { white-space: nowrap; }
td.seq { color: #59636e; width: 44px; }
.tag { display: inline-block; background: #f3eefc; color: #5f4695;
       border-radius: 12px; padding: 1px 10px; font-size: 13px; }
.back { font-size: 14px; }
footer { margin-top: 48px; padding-top: 16px; border-top: 1px solid #d8dee4;
         color: #59636e; font-size: 13px; }
"""


def slug(seq: int) -> str:
    # 中文标题转不了 slug，直接用官方序号，稳定且跟官方目录一一对应
    return f"c{seq:02d}"


def page(title: str, body: str) -> str:
    return (
        "<!DOCTYPE html>\n<html lang=\"zh-CN\">\n<head>\n"
        "<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{escape(title)} - 白名单竞赛 - ACN</title>\n"
        f"<style>{CSS}</style>\n</head>\n<body>\n{body}\n</body>\n</html>\n"
    )


def deadline_text(item: dict) -> str:
    deadline = item.get("deadline")
    if not deadline:
        return "待官网公告"
    # ISO 8601 "YYYY-MM-DDTHH:mm:ss" -> "YYYY-MM-DD HH:mm"
    return re.sub(r"T", " ", str(deadline), count=1)


def detail_page(item: dict, category: str) -> str:
    site = item.get("site")
    site_html = f'<a href="{escape(site)}" rel="noopener">{escape(site)}</a>' if site else "暂未收录"
    body = f"""
<p class="back"><a href="../">← 返回竞赛目录</a></p>
<h1>{escape(item['title'])}</h1>
<p class="meta">官方目录序号 {item['seq']} · <span class="tag">{escape(category)}</span></p>
<table>
<tr><th>竞赛名称</th><td>{escape(item['title'])}</td></tr>
<tr><th>官方序号</th><td>{item['seq']}</td></tr>
<tr><th>分类</th><td>{escape(category)}</td></tr>
<tr><th>官方网站</th><td>{site_html}</td></tr>
<tr><th>报名时间</th><td>{deadline_text(item)}</td></tr>
</table>
<footer>数据来源：中国高等教育学会《2024 全国普通高校大学生竞赛分析报告》竞赛目录。
未核实的信息一律留空，以官方通知为准。</footer>
"""
    return page(item["title"], body)


def index_page(items: list[dict], categories: dict[str, str]) -> str:
    groups: dict[str, list[dict]] = {}
    for item in items:
        groups.setdefault(item["sub"], []).append(item)
    sections = []
    for sub in sorted(groups, key=lambda s: min(i["seq"] for i in groups[s])):
        name = categories.get(sub, sub)
        rows = []
        for item in sorted(groups[sub], key=lambda i: i["seq"]):
            site = item.get("site")
            site_html = f'<a href="{escape(site)}" rel="noopener">官网</a>' if site else "—"
            rows.append(
                f'<tr><td class="seq">{item["seq"]}</td>'
                f'<td><a href="{slug(item["seq"])}/">{escape(item["title"])}</a></td>'
                f'<td>{deadline_text(item)}</td><td>{site_html}</td></tr>'
            )
        sections.append(
            f'<h2>{escape(name)}（{len(groups[sub])} 项）</h2>\n'
            '<table><tr><th>序号</th><th>竞赛名称</th><th>报名时间</th><th>官网</th></tr>\n'
            + "\n".join(rows) + "\n</table>"
        )
    body = f"""
<p class="back"><a href="../">← 返回 ACN 主页</a></p>
<h1>白名单竞赛目录</h1>
<p class="meta">共 {len(items)} 项 · 来源：中国高等教育学会《2024 全国普通高校大学生竞赛分析报告》竞赛目录</p>
{"".join(sections)}
<footer>竞赛按官方目录分类分组，序号与官方目录一致。
报名时间以各竞赛官方公告为准，未核实的留空不编造。</footer>
"""
    return page("目录", body)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    args = parser.parse_args()

    items = yaml.safe_load(SOURCE.read_text(encoding="utf-8"))
    categories = {t["sub"]: t["name"] for t in yaml.safe_load(TYPES.read_text(encoding="utf-8"))}

    out = args.output / "competition"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(index_page(items, categories), encoding="utf-8")
    for item in items:
        directory = out / slug(item["seq"])
        directory.mkdir(exist_ok=True)
        (directory / "index.html").write_text(
            detail_page(item, categories.get(item["sub"], item["sub"])), encoding="utf-8"
        )
    print(f"Generated competition index + {len(items)} detail pages under {out}")


if __name__ == "__main__":
    main()
