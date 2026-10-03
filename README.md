# Đánh giá bảo mật kênh Mobile Banking — Ngân hàng X (giả lập)

> Dự án cá nhân · Doãn Hữu Nguyên · PTIT – An toàn thông tin

## Tóm tắt
Đánh giá 2 mối đe doạ trọng yếu của kênh Mobile/Internet Banking, mỗi kịch bản đi đủ 7 tầng
từ mô hình đe doạ đến tuân thủ:

1. **ATO** — chiếm đoạt tài khoản qua trục xác thực
2. **IDOR/BOLA** — truy cập dữ liệu khách khác qua trục phân quyền

## Phương pháp 7 tầng
Mô hình đe doạ → tấn công (lab) → hardening (CIS) → phát hiện (custom rule Wazuh) →
ứng cứu (NIST SP 800-61) → quản trị (ISO 27001 + TT09) → khuyến nghị.

| Mục đích | Khung tham chiếu |
|---|---|
| Tấn công & phát hiện | OWASP Top 10:2025, OWASP API Top 10:2023, OWASP Mobile Top 10:2024, MITRE ATT&CK |
| Hardening | CIS Benchmarks |
| Quản trị & tuân thủ | ISO/IEC 27001:2022, Thông tư 09/2020/TT-NHNN |
| Ứng cứu sự cố | NIST SP 800-61 |

## Sơ đồ mạng lab
_(chèn ảnh: screenshots/network-diagram.png)_

| Máy | Vai trò | Mạng |
|---|---|---|
| pfSense | Bảo vệ biên, phân vùng LAN/DMZ | WAN/LAN/DMZ |
| DC01 (AD) | Định danh & phân quyền | LAN 10.10.10.10 |
| WEB01 (DVWA) | Ứng dụng Mobile/Internet Banking (mô phỏng) | DMZ 10.10.20.10 |
| Wazuh | SOC / log tập trung | LAN 10.10.10.20 |

## Phạm vi
Xem `00-context.md`. Chỉ 2 kịch bản, chỉ kênh Mobile/Internet Banking (mô phỏng bằng DVWA
trong lab cô lập). Core banking, thẻ, SWIFT nằm ngoài phạm vi.

## Cấu trúc repo
- `00-context.md` — bối cảnh, phạm vi, ranh giới
- `infra/` — cấu hình (dạng chữ) + ghi chú CIS
- `scenarios/01-ato/`, `scenarios/02-idor/` — mỗi thư mục kể trọn 7 tầng
- `rules/` — custom rule Wazuh
- `grc/` — risk register, gap assessment, TT09, policies, reports, báo cáo tổng, dashboard
- `scripts/` — script Python tóm tắt cảnh báo
- `docs/` — lộ trình, khung tham chiếu, lab runbook, nhật ký
- `jira/`, `screenshots/` — ảnh/ export

## Liên kết nhanh
- Kịch bản 1 (ATO): [scenarios/01-ato/README.md](scenarios/01-ato/README.md)
- Kịch bản 2 (IDOR): [scenarios/02-idor/README.md](scenarios/02-idor/README.md)
- Báo cáo tổng: [grc/assessment-report.md](grc/assessment-report.md)

## Tài liệu
- [**Kế hoạch & checklist**](docs/ke-hoach.md) · [Lộ trình](docs/lo-trinh-du-an.md) · [Khung tham chiếu](docs/khung-tham-chieu.md) · [Lab runbook](docs/lab-runbook.md) · [Nhật ký](docs/nhat-ky.md)
