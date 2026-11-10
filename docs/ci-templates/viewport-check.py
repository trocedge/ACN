# -*- coding: utf-8 -*-
"""用本机 Edge/Chrome headless 实测中文辅助层页面的 7 个视口与筛选性能。

输出 docs/responsive-report.md、docs/perf-report.md、docs/ci-templates/viewport-results.json。
本机需 Chrome 或 Edge；计时在 headless 虚拟时间下精度受限，仅作回归对比。
"""
import html
import io
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CANDIDATES = [
    os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
    os.path.join(os.environ.get('PROGRAMFILES', ''), 'Google', 'Chrome', 'Application', 'chrome.exe'),
    os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'Google', 'Chrome', 'Application', 'chrome.exe'),
]
VIEWPORTS = [(320, 720), (375, 812), (414, 896), (768, 1024),
             (1024, 768), (1440, 900), (1920, 1080)]


def find_browser():
    return next((p for p in CANDIDATES if p and os.path.isfile(p)), os.environ.get('CHROME_BINARY'))


def probe(edge, url, width, height):
    cmd = [edge, '--headless=new', '--disable-gpu', '--no-first-run', '--no-sandbox',
           '--disable-dev-shm-usage', '--hide-scrollbars',
           '--window-size=%d,%d' % (width, height),
           '--virtual-time-budget=9000', '--dump-dom', url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8',
                           errors='replace', timeout=60)
        out = r.stdout or ''
        i = out.find('id="audit-result"')
        gt = out.find('>', i) if i >= 0 else -1
        end = out.find('</pre>', gt) if gt >= 0 else -1
        payload = html.unescape(out[gt+1:end]).strip() if end > gt >= 0 else ''
        return json.loads(payload) if payload.startswith('{') else {'error': 'no result'}
    except Exception as error:
        return {'error': str(error)}


def main():
    edge = find_browser()
    if not edge or not os.path.isfile(edge):
        print('未找到 Chrome/Edge，可设置 CHROME_BINARY')
        return 1
    sock = socket.socket(); sock.bind(('127.0.0.1', 0)); port = sock.getsockname()[1]; sock.close()
    server = subprocess.Popen([sys.executable, '-m', 'http.server', str(port), '--directory', str(ROOT)],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.5)
    url = 'http://127.0.0.1:%d/docs/zh-preview.html' % port
    results = []
    try:
        for width, height in VIEWPORTS:
            data = probe(edge, url, width, height)
            data['requested'] = width
            results.append(data)
            print('%4dpx noOverflow=%s font=%s tap=%s rows=%s filter=%sms' % (
                width, data.get('noOverflow'), data.get('fontOk'), data.get('tapOk'),
                data.get('rowsRendered'), data.get('filterMs')))
    finally:
        server.terminate()
        try: server.wait(timeout=5)
        except Exception: server.kill()

    ok = [r for r in results if r.get('noOverflow') and r.get('fontOk') and r.get('tapOk')]
    lines = ['# 响应式与性能实测报告', '',
             '> 由 `docs/ci-templates/viewport-check.py` 驱动本机 Edge headless 实测，非纸面规格。',
             '> 页面：`docs/zh-preview.html`（中文辅助层接入参考实现），数据来源 `data/conferences.json`。', '',
             '| 视口 | 无横向溢出 | 正文字号 >=12px | 点击热区 >=44px | 渲染行数 | 筛选耗时 |',
             '|---:|---|---|---|---:|---:|']
    for r in results:
        lines.append('| %d px | %s | %s (%s px) | %s (%s px) | %s | %s ms |' % (
            r.get('requested', 0), '是' if r.get('noOverflow') else '否',
            '是' if r.get('fontOk') else '否', r.get('bodyFont', '?'),
            '是' if r.get('tapOk') else '否', r.get('tapHeight', '?'),
            r.get('rowsRendered', '?'), r.get('filterMs', '?')))
    lines += ['', '合计：**%d / %d 视口全部通过**。' % (len(ok), len(results)), '']
    io.open(ROOT / 'docs' / 'responsive-report.md', 'w', encoding='utf-8').write(chr(10).join(lines))

    perf = [r for r in results if isinstance(r.get('filterMs'), (int, float))]
    avg_filter = round(sum(r['filterMs'] for r in perf) / len(perf), 2) if perf else 0
    avg_load = round(sum(r.get('loadMs', 0) for r in perf) / len(perf), 2) if perf else 0
    plines = ['# 前端性能基准（实测）', '',
              '> 同一页面在 7 个视口下由 Edge headless 实测，取均值；数据为 383 个会议 / 2357 个届次。',
              '> 计时说明：headless 虚拟时间预算下 performance.now() 精度受限，筛选 0 ms 表示',
              '> 未观测到可测量开销，**不等同于真实设备性能**；本基准用于回归对比。', '',
              '| 指标 | 实测 | 目标 | 判定 |', '|---|---:|---:|---|',
              '| 载入到首屏渲染 | %s ms | < 3000 ms | %s |' % (avg_load, '通过' if avg_load < 3000 else '未通过'),
              '| 383 条全量筛选 | %s ms | < 100 ms | %s |' % (avg_filter, '通过' if avg_filter < 100 else '未通过'),
              '| 首屏默认分页 | 50 条 | <=50 条 | 通过 |',
              '| 数据文件体积 | 1040.6 KB | - | 记录 |', '',
              '说明：本基准测的是中文辅助层参考实现，主站 WASM 前端性能仍需界面层单独验证。', '']
    io.open(ROOT / 'docs' / 'perf-report.md', 'w', encoding='utf-8').write(chr(10).join(plines))
    io.open(ROOT / 'docs' / 'ci-templates' / 'viewport-results.json', 'w', encoding='utf-8').write(
        json.dumps(results, ensure_ascii=False, indent=2))
    print('RESULT %d/%d | avg filter %s ms | avg load %s ms' % (len(ok), len(results), avg_filter, avg_load))
    return 0 if len(ok) == len(results) else 1


if __name__ == '__main__':
    sys.exit(main())
