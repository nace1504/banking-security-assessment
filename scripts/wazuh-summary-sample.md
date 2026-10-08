# Báo cáo tóm tắt cảnh báo Wazuh

- Tổng số alert: **570**
- Khoảng thời gian: `2026-10-07T11:11:03.062+0000` → `2026-10-07T15:54:29.685+0000`
- Số agent có alert: **3**

## Theo mức độ (rule.level)

| Level | Số lượng |
|---|---|
| 10 | 1 |
| 9 | 9 |
| 5 | 14 |
| 4 | 12 |
| 3 | 534 |

## Theo agent

| Agent | Số alert |
|---|---|
| DC01 | 386 |
| wazuh01 | 119 |
| WEB01 | 65 |

## Top 10 rule xuất hiện nhiều nhất

| rule.id | Mô tả | Số lần |
|---|---|---|
| 60106 | Windows Logon Success | 341 |
| 5502 | PAM: Login session closed. | 54 |
| 5501 | PAM: Login session opened. | 51 |
| 5402 | Successful sudo to ROOT executed. | 48 |
| 60642 | Software protection service scheduled successfully. | 13 |
| 60122 | Logon Failure - Unknown user or bad password | 10 |
| 52004 | Apparmor DENIED mknod operation. | 10 |
| 100010 | DVWA: Truy cap trang SQL Injection (id) - ghi nhan de theo doi IDOR | 9 |
| 19011 | CIS Microsoft Windows Server 2022 Benchmark v2.0.0: Ensure 'Reset account lockout counter after' is set to '15 or more minute(s)'.: Status changed from passed to failed | 6 |
| 502 | Wazuh server started. | 5 |

## Top 10 group (phân loại rule)

| Group | Số lần |
|---|---|
| authentication_success | 393 |
| windows | 377 |
| windows_security | 355 |
| syslog | 176 |
| pam | 107 |
| sudo | 49 |
| local | 20 |
| windows_application | 19 |
| authentication_failed | 11 |
| ossec | 10 |

---
Ghi chú: báo cáo sinh tự động bởi `scripts/wazuh_summary.py`, chạy trực tiếp trên WAZUH01 với
`python3 wazuh_summary.py --input /var/ossec/logs/alerts/2026/Oct/ossec-alerts-07.json --top 10 --output wazuh-summary-07oct.md`
đối chiếu toàn bộ log ngày 07/10/2026 (bao gồm cả Kịch bản 1 — ATO và Kịch bản 2 — IDOR/BOLA).
Rule 100011 (frequency IDOR, level 10) xuất hiện 1 lần, khớp với kết quả đã xác nhận qua dashboard ở Kịch bản 2.
