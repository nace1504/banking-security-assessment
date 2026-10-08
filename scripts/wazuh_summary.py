#!/usr/bin/env python3
"""
wazuh_summary.py — Đọc file cảnh báo Wazuh (alerts.json, định dạng JSON Lines)
và tổng hợp thành báo cáo tóm tắt dạng Markdown.

Dùng cho: báo cáo nhanh về tình trạng cảnh báo trên Wazuh manager, phục vụ
phần GRC (đối chiếu với risk-register.xlsx / gap-assessment.xlsx) mà không
cần đăng nhập dashboard.

Cách dùng:
    python3 wazuh_summary.py [--input /var/ossec/logs/alerts/alerts.json]
                             [--output wazuh-summary.md]
                             [--top 10]
                             [--agent WEB01]
                             [--since 2026-10-07T00:00:00]

Không cần thư viện ngoài (chỉ dùng thư viện chuẩn của Python 3).
"""

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--input", default="/var/ossec/logs/alerts/alerts.json",
                   help="Đường dẫn file alerts.json (mặc định: đường dẫn chuẩn trên Wazuh manager)")
    p.add_argument("--output", default=None,
                   help="Ghi báo cáo ra file Markdown thay vì in ra màn hình")
    p.add_argument("--top", type=int, default=10,
                   help="Số lượng rule/agent xuất hiện nhiều nhất hiển thị trong báo cáo (mặc định 10)")
    p.add_argument("--agent", default=None,
                   help="Chỉ thống kê cảnh báo của 1 agent cụ thể (theo tên, ví dụ WEB01)")
    p.add_argument("--since", default=None,
                   help="Chỉ thống kê cảnh báo từ thời điểm này trở đi (định dạng ISO, ví dụ 2026-10-07T00:00:00)")
    return p.parse_args()


def load_alerts(path, agent_filter=None, since=None):
    """Đọc file alerts.json theo định dạng JSON Lines (mỗi dòng 1 object JSON).
    Bỏ qua dòng lỗi định dạng (log có thể bị cắt dòng cuối nếu Wazuh đang ghi dở)."""
    alerts = []
    skipped = 0
    since_dt = datetime.fromisoformat(since) if since else None

    try:
        f = open(path, "r", encoding="utf-8", errors="replace")
    except OSError as e:
        print(f"Lỗi: không mở được file '{path}': {e}", file=sys.stderr)
        sys.exit(1)

    with f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                skipped += 1
                continue

            agent_name = obj.get("agent", {}).get("name", "unknown")
            if agent_filter and agent_name != agent_filter:
                continue

            if since_dt:
                ts_raw = obj.get("timestamp", "")
                try:
                    # Wazuh timestamp dạng: 2026-10-07T22:52:41.656+0000
                    ts_norm = ts_raw[:19]
                    ts_dt = datetime.fromisoformat(ts_norm)
                    if ts_dt < since_dt:
                        continue
                except ValueError:
                    pass

            alerts.append(obj)

    return alerts, skipped


def build_report(alerts, top_n):
    total = len(alerts)
    by_rule = Counter()
    by_rule_desc = {}
    by_level = Counter()
    by_agent = Counter()
    by_group = Counter()
    timestamps = []

    for a in alerts:
        rule = a.get("rule", {})
        rule_id = rule.get("id", "?")
        by_rule[rule_id] += 1
        by_rule_desc[rule_id] = rule.get("description", "")
        by_level[rule.get("level", "?")] += 1
        by_agent[a.get("agent", {}).get("name", "unknown")] += 1
        for g in rule.get("groups", []) or []:
            by_group[g] += 1
        ts = a.get("timestamp")
        if ts:
            timestamps.append(ts)

    timestamps.sort()
    time_range = (timestamps[0], timestamps[-1]) if timestamps else (None, None)

    lines = []
    lines.append("# Báo cáo tóm tắt cảnh báo Wazuh")
    lines.append("")
    lines.append(f"- Tổng số alert: **{total}**")
    if time_range[0]:
        lines.append(f"- Khoảng thời gian: `{time_range[0]}` → `{time_range[1]}`")
    lines.append(f"- Số agent có alert: **{len(by_agent)}**")
    lines.append("")

    lines.append("## Theo mức độ (rule.level)")
    lines.append("")
    lines.append("| Level | Số lượng |")
    lines.append("|---|---|")
    for level, count in sorted(by_level.items(), key=lambda x: str(x[0]), reverse=True):
        lines.append(f"| {level} | {count} |")
    lines.append("")

    lines.append("## Theo agent")
    lines.append("")
    lines.append("| Agent | Số alert |")
    lines.append("|---|---|")
    for agent, count in by_agent.most_common(top_n):
        lines.append(f"| {agent} | {count} |")
    lines.append("")

    lines.append(f"## Top {top_n} rule xuất hiện nhiều nhất")
    lines.append("")
    lines.append("| rule.id | Mô tả | Số lần |")
    lines.append("|---|---|---|")
    for rule_id, count in by_rule.most_common(top_n):
        desc = by_rule_desc.get(rule_id, "")
        lines.append(f"| {rule_id} | {desc} | {count} |")
    lines.append("")

    lines.append(f"## Top {top_n} group (phân loại rule)")
    lines.append("")
    lines.append("| Group | Số lần |")
    lines.append("|---|---|")
    for group, count in by_group.most_common(top_n):
        lines.append(f"| {group} | {count} |")
    lines.append("")

    return "\n".join(lines)


def main():
    args = parse_args()
    alerts, skipped = load_alerts(args.input, agent_filter=args.agent, since=args.since)

    if not alerts:
        print("Không có alert nào khớp điều kiện lọc (kiểm tra lại --input / --agent / --since).",
              file=sys.stderr)
        sys.exit(2)

    report = build_report(alerts, args.top)

    if skipped:
        report += f"\n> Lưu ý: bỏ qua {skipped} dòng không parse được JSON (có thể do log đang được ghi dở).\n"

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Đã ghi báo cáo vào: {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
