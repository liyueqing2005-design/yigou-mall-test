import glob
import html
import json
import os
from collections import defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(ROOT, "allure-results")
OUTPUT = os.path.join(ROOT, "allure-report", "index.html")

STATUS_TEXT = {
    "passed": "通过",
    "failed": "失败",
    "broken": "异常",
    "skipped": "跳过",
    "unknown": "未知",
}
STATUS_COLOR = {
    "passed": "#67c23a",
    "failed": "#f56c6c",
    "broken": "#e6a23c",
    "skipped": "#909399",
    "unknown": "#909399",
}


def label_of(result, name):
    for l in result.get("labels", []):
        if l.get("name") == name:
            return l.get("value")
    return None


def xfail_reason(result):
    msg = (result.get("statusDetails") or {}).get("message") or ""
    if not msg.startswith("XFAIL"):
        return None
    first = msg.splitlines()[0]
    return first.replace("XFAIL", "").strip() or "预期失败"


def main():
    results = []
    for path in glob.glob(os.path.join(RESULTS_DIR, "*-result.json")):
        with open(path, encoding="utf-8") as fp:
            results.append(json.load(fp))

    total = len(results)
    passed = sum(1 for r in results if r.get("status") == "passed")
    failed = sum(1 for r in results if r.get("status") in ("failed", "broken"))
    xfailed = sum(1 for r in results if r.get("status") == "skipped" and xfail_reason(r))
    skipped = sum(1 for r in results if r.get("status") == "skipped" and not xfail_reason(r))

    grouped = defaultdict(list)
    for r in results:
        grouped[label_of(r, "feature") or "未分类"].append(r)
    ordered = sorted(grouped.items(), key=lambda kv: (-len(kv[1]), kv[0]))

    def duration(r):
        ms = max(0, (r.get("stop") or 0) - (r.get("start") or 0))
        return f"{ms / 1000:.2f}s"

    sections = []
    for feat, items in ordered:
        p = sum(1 for r in items if r.get("status") == "passed")
        f = sum(1 for r in items if r.get("status") in ("failed", "broken"))
        x = sum(1 for r in items if r.get("status") == "skipped" and xfail_reason(r))
        s = len(items) - p - f - x
        rows = []
        for r in sorted(items, key=lambda i: i.get("name", "")):
            st = r.get("status", "unknown")
            reason = xfail_reason(r)
            if st == "skipped" and reason:
                badge = '<span class="badge" style="background:#e6a23c">预期失败</span>'
                note = f'<div class="note">{html.escape(reason)}</div>'
            else:
                badge = f'<span class="badge" style="background:{STATUS_COLOR.get(st, "#909399")}">{STATUS_TEXT.get(st, st)}</span>'
                note = ""
            rows.append(
                f'<tr><td class="tname">{html.escape(r.get("name", ""))}</td>'
                f'<td class="tstatus">{badge}</td>'
                f'<td class="tdur">{duration(r)}</td></tr>'
                + (f'<tr class="note-row"><td colspan="3">{note}</td></tr>' if note else "")
            )
        sections.append(
            f'<div class="feature"><div class="fhead"><span class="fname">{html.escape(feat)}</span>'
            f'<span class="fcounts">共 {len(items)} ｜ 通过 {p} ｜ 失败 {f} ｜ 预期失败 {x} ｜ 跳过 {s}</span></div>'
            f'<table><thead><tr><th>用例</th><th>结果</th><th>耗时</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>'
        )

    rate = (passed / total * 100) if total else 0
    html_doc = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>易购商城自动化测试报告</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; font-family: -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif; background: #f5f7fa; color: #303133; }}
  .wrap {{ max-width: 1080px; margin: 0 auto; padding: 24px 16px 48px; }}
  h1 {{ font-size: 22px; margin: 0 0 4px; }}
  .sub {{ color: #909399; font-size: 13px; margin-bottom: 20px; }}
  .cards {{ display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 24px; }}
  .card {{ flex: 1 1 120px; background: #fff; border-radius: 8px; padding: 16px; text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,.06); }}
  .card .num {{ font-size: 28px; font-weight: 700; }}
  .card .lab {{ color: #909399; font-size: 13px; margin-top: 4px; }}
  .feature {{ background: #fff; border-radius: 8px; margin-bottom: 16px; box-shadow: 0 1px 4px rgba(0,0,0,.06); overflow: hidden; }}
  .fhead {{ display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; border-bottom: 1px solid #ebeef5; }}
  .fname {{ font-weight: 700; }}
  .fcounts {{ color: #909399; font-size: 12px; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th, td {{ text-align: left; padding: 10px 16px; font-size: 14px; }}
  thead th {{ background: #fafafa; color: #909399; font-weight: 500; }}
  tbody tr {{ border-top: 1px solid #f0f2f5; }}
  .tname {{ word-break: break-all; }}
  .tstatus {{ width: 110px; }}
  .tdur {{ width: 90px; color: #909399; }}
  .badge {{ display: inline-block; padding: 2px 10px; border-radius: 10px; color: #fff; font-size: 12px; }}
  .note {{ color: #e6a23c; font-size: 12px; padding: 2px 16px 8px; }}
  .note-row td {{ border-top: none; padding-top: 0; }}
</style>
</head>
<body>
<div class="wrap">
  <h1>易购商城自动化测试报告</h1>
  <div class="sub">生成时间：{__import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S")} ｜ 数据来源：allure-results</div>
  <div class="cards">
    <div class="card"><div class="num">{total}</div><div class="lab">总计</div></div>
    <div class="card"><div class="num" style="color:#67c23a">{passed}</div><div class="lab">通过</div></div>
    <div class="card"><div class="num" style="color:#f56c6c">{failed}</div><div class="lab">失败</div></div>
    <div class="card"><div class="num" style="color:#e6a23c">{xfailed}</div><div class="lab">预期失败</div></div>
    <div class="card"><div class="num" style="color:#909399">{skipped}</div><div class="lab">跳过</div></div>
    <div class="card"><div class="num">{rate:.1f}%</div><div class="lab">通过率</div></div>
  </div>
  {''.join(sections)}
</div>
</body>
</html>
"""
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as fp:
        fp.write(html_doc)
    print(f"已导出自包含报告：{OUTPUT}（共 {total} 用例，可直接双击打开）")


if __name__ == "__main__":
    main()
