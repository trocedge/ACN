import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
ROOT = Path(__file__).resolve().parent.parent

# 读上一步的 JSON 产物
JSON_PATH = Path(os.environ.get("COMPETITION_JSON") or ROOT / "public" / "competition" / "whitelist.json")
# 输出 RSS
OUT_PATH = Path(os.environ.get("COMPETITION_RSS") or ROOT / "public" / "competition" / "competitions.xml")
SITE_URL = os.environ.get("SITE_URL", "").strip()


ATOM_NS = "http://www.w3.org/2005/Atom"
ET.register_namespace("atom", ATOM_NS)


def load_items(path):
    """读上一步导出的 JSON，返回 items 列表。"""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return data.get("items", [])


def detail_link(seq):
    slug = f"c{int(seq):02d}" if seq is not None else ""
    return f"{SITE_URL.rstrip('/')}/competition/{slug}/"



def build_item(entry):
    item = ET.Element("item")
    seq = entry.get("seq")
    title = entry.get("title", "")
    category = entry.get("category", "")
    sub = entry.get("sub", "")
    site = entry.get("site") or ""
    deadline = entry.get("deadline")

    # 标题：比赛名 + 分类
    ET.SubElement(item, "title").text = f"{title}（{category}）" if category else title

    # 链接：官网优先，没有就回退详情页
    ET.SubElement(item, "link").text = site or detail_link(seq)

    # 描述：分类、截止时间、官网
    desc_lines = []
    if category:
        desc_lines.append(f"分类：{category}（{sub}）")
    if deadline:
        desc_lines.append(f"截止时间：{deadline}")
    if site:
        desc_lines.append(f"官网：{site}")
    ET.SubElement(item, "description").text = "\n".join(desc_lines)

    # 分类标签用短码
    if sub:
        ET.SubElement(item, "category").text = sub

    # guid：用序号拼稳定标识，标题以后改了也不变
    guid = ET.SubElement(item, "guid", isPermaLink="false")
    domain = urlparse(SITE_URL).netloc or SITE_URL.rstrip("/")
    guid.text = f"competition-{seq}@{domain}"

    return item


def build_feed(items):
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "大学生竞赛目录"
    ET.SubElement(channel, "link").text = SITE_URL
    ET.SubElement(channel, "description").text = "近期大学生竞赛信息汇总"
    ET.SubElement(channel, "language").text = "zh-CN"

    for entry in items:
        channel.append(build_item(entry))
    return rss


def main():
    if not SITE_URL:
        raise SystemExit("SITE_URL 未设置：生成的订阅链接会指向 example.com，已中止")
    items = load_items(JSON_PATH)
    rss = build_feed(items)

    tree = ET.ElementTree(rss)
    ET.indent(tree, space="  ")
    out = Path(OUT_PATH)
    out.parent.mkdir(parents=True, exist_ok=True)
    tree.write(out, encoding="utf-8", xml_declaration=True)
    print(f"已生成 {len(items)} 条 RSS -> {out}")


if __name__ == "__main__":
    main()
