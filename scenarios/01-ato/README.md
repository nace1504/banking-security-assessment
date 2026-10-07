# Kịch bản 1 — Chiếm đoạt tài khoản (ATO)

## Tầng 1 — Mô hình đe doạ
- Mô tả: Attacker cố đăng nhập vào tài khoản nhân viên domain `nguyenvana` trên DC01 qua RDP, thử nhiều mật khẩu sai liên tiếp (password guessing). Giả định: attacker đã biết username (qua OSINT/rò rỉ nơi khác), chưa biết mật khẩu. Phân loại STRIDE: **Spoofing** (giả danh người dùng hợp lệ).
- Giả định về vị trí mạng: Lab bỏ qua bước "initial access vào LAN" (compromise máy nội bộ, VPN leak, pivot từ DMZ, hoặc insider đe doạ) — attacker được giả định đã có vị trí mạng trong LAN nội bộ (10.10.10.0/24) từ trước. Kịch bản tập trung kiểm chứng control xác thực + phát hiện + ứng cứu khi có brute-force xảy ra trong mạng nội bộ, không mô phỏng toàn bộ chuỗi tấn công (kill chain) từ bên ngoài vào. Threat "insider" hoặc "máy nội bộ đã bị chiếm quyền" là giả định thực tế, phù hợp với MITRE ATT&CK Tactic "Credential Access" (sau giai đoạn Initial Access/Lateral Movement).
- Khung: OWASP A07:2025 (Identification and Authentication Failures); MITRE T1110.001 (Brute Force: Password Guessing)

## Tầng 2 — Tấn công (lab)
- Thực hiện: Brute-force RDP vào DC01 (10.10.10.10) từ máy host (10.10.10.100, qua VMnet2 LAN), đăng nhập tài khoản `nguyenvana` với 5 mật khẩu sai liên tiếp (07/10/2026, 18:38:16–18:38:42 giờ VN), khiến tài khoản bị khoá tự động theo GPO.
- Bằng chứng:
  - `screenshots/dc01-rdp-account-locked.png` — màn hình RDP báo tài khoản bị khoá
  - `screenshots/dc01-eventviewer-4625-logon-failed.png` — Event Viewer DC01, Event ID 4625 (Account Name: nguyenvana, Failure Reason: Unknown user name or bad password)
  - `screenshots/dc01-eventviewer-4740-account-locked.png` — Event Viewer DC01, Event ID 4740 (Account Locked Out: LAB\nguyenvana, Caller Computer Name: ADMIN-PC)

## Tầng 3 — Hardening
- Biện pháp: GPO Default Domain Policy đã cấu hình từ Giai đoạn 1 — password complexity ≥12 ký tự, account lockout threshold 5 lần/15 phút, audit logon (Success+Failure).
- Trước/sau: không cấu hình thêm cho kịch bản này — mục tiêu là kiểm chứng control đã có hoạt động đúng khi bị tấn công thật, không phải thêm control mới.
- Kết quả kiểm chứng: Control hoạt động đúng như thiết kế — tài khoản bị khoá chính xác sau lần sai thứ 5, không cần can thiệp thủ công.

## Tầng 4 — Phát hiện
- Rule: ruleset Windows mặc định của Wazuh — rule.id **60122** "Logon Failure - Unknown user or bad password" (level 5, Event ID 4625) và rule.id **60115** "User account locked out (multiple login errors)" (level 9, Event ID 4740). Không cần viết custom rule cho kịch bản này.
- Cảnh báo (ảnh):
  - `screenshots/wazuh-dashboard-ato-alerts.png` — Wazuh dashboard, 13 alert tổng, 12 authentication failure, rule groups windows_security/authentication_failed/account_changed
  - `screenshots/wazuh-events-table-ruleid.png` — bảng chi tiết từng alert với rule.id, rule.level, timestamp, agent.name
- Sự cố vận hành gặp phải (và đã fix): lần tấn công đầu tiên (18:01) KHÔNG được ghi nhận alert vì Wazuh manager/indexer/dashboard chưa khởi động xong lúc đó. Sau khi restart toàn bộ service, phát hiện thêm lỗi filebeat `401 Unauthorized` do mật khẩu trong filebeat keystore không khớp với mật khẩu admin OpenSearch đã đổi trước đó (xem `infra/wazuh.md`) — đã fix bằng `filebeat keystore add username/password --force` rồi restart filebeat. Lần tấn công thứ 2 (18:38) được ghi nhận đầy đủ.

## Tầng 5 — Ứng cứu (NIST SP 800-61)
- Báo cáo: ../../grc/reports/incident-01-ato.md

## Tầng 6 — Quản trị
- Chấm control ISO 27001:2022:
  - **A.8.5** (Secure authentication): **Đạt** — GPO lockout threshold 5 lần/15 phút ngăn chặn thành công brute-force, kiểm chứng bằng tấn công thật.
  - **A.5.17** (Authentication information): **Đạt** — password policy complexity ≥12 ký tự đã cấu hình qua GPO (Giai đoạn 1), phù hợp thực tiễn bảo vệ thông tin xác thực.
  - **A.8.16** (Monitoring activities): **Đạt có điều kiện** — hệ thống giám sát (Wazuh) phát hiện đúng và đầy đủ khi hoạt động bình thường, NHƯNG lần đầu tấn công bị mất log hoàn toàn do SIEM pipeline (manager/indexer/filebeat) chưa sẵn sàng, không có cơ chế cảnh báo khi chính hệ thống giám sát bị lỗi/gián đoạn. Đây là gap thực tế cần ghi nhận: monitoring cần có "self-monitoring"/health-check riêng.

## Tầng 7 — Khuyến nghị
- Cân nhắc triển khai MFA cho các tài khoản truy cập RDP/hệ thống nhạy cảm, không chỉ dựa vào lockout policy.
- Thiết lập cảnh báo real-time (email/Slack/Telegram) từ Wazuh thay vì chỉ xem dashboard thủ công, để rút ngắn thời gian phát hiện (MTTD).
- Bổ sung health-check định kỳ cho pipeline SIEM (manager, indexer, filebeat) — bài học thực tế từ chính lab: khi SIEM "âm thầm" không nhận log, không có gì cảnh báo cho người vận hành biết.
- Khi thay đổi mật khẩu credential dùng chung (vd. admin OpenSearch), cần quy trình/checklist cập nhật đồng bộ ở mọi service phụ thuộc (filebeat keystore, v.v.) để tránh gián đoạn giám sát ngoài ý muốn.
