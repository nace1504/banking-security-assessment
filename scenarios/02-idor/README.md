# Kịch bản 2 — IDOR/BOLA

## Tầng 1 — Mô hình đe doạ
- Mô tả: Trang **SQL Injection** của DVWA (`/vulnerabilities/sqli/?id=X&Submit=Submit#`) trả về dữ liệu theo tham số `id` trong URL mà không kiểm tra người gọi có quyền xem bản ghi đó hay không. Attacker (đã đăng nhập, tài khoản hợp lệ của DVWA) chỉ cần đổi giá trị `id` (không cần payload SQL injection) để xem dữ liệu của "user" khác — đây là lỗ hổng IDOR/BOLA (Broken Object Level Authorization), tách biệt khỏi kỹ thuật SQL Injection thực sự (không tiêm cú pháp SQL).
- Phân loại STRIDE: **Information Disclosure** + **Elevation of Privilege** (truy cập dữ liệu vượt quyền).
- Khung: OWASP A01:2025 (Broken Access Control); API1:2023 (Broken Object Level Authorization); MITRE T1190 (Exploit Public-Facing Application).

## Tầng 2 — Tấn công (lab)
- Thực hiện: Đăng nhập DVWA (WEB01, `http://10.10.20.10/vulnerabilities/sqli/`), lần lượt đổi `id=1`, `id=2`, `id=3`... trên URL để quan sát dữ liệu trả về khác nhau theo từng `id`, không kèm payload SQL injection.
- Bằng chứng: screenshots/ (các response theo từng `id` khác nhau) — bổ sung sau khi thực hiện.

## Tầng 3 — Hardening
- Vấn đề thực tế: DVWA **không có cấu hình security level nào sửa được lỗi IDOR này** — kể cả ở mức High, trang SQLi chỉ chống injection (dùng prepared statement), không thêm kiểm tra quyền sở hữu object. Đây là gap cần sửa ở tầng code ứng dụng (kiểm tra `session_user_id == requested_id`), không phải cấu hình hệ thống.
- Risk treatment đề xuất: **Accept** (ngắn hạn, có compensating control giám sát qua Tầng 4) + **Mitigate** (dài hạn, khuyến nghị đội phát triển bổ sung kiểm tra authorization ở code).
- Trước/sau: không có "trước/sau" bằng cấu hình trong lab này — ghi nhận đây là gap không khắc phục được bằng config, cần escalate cho dev team.

## Tầng 4 — Phát hiện
- Vấn đề kỹ thuật: Apache access log của DVWA nằm trong container Docker, Wazuh agent (cài trên OS Ubuntu của WEB01) không đọc trực tiếp được. Cần:
  1. Tạo lại container DVWA với volume mount log ra ngoài: `-v /var/log/dvwa:/var/log/apache2`
  2. Thêm `<localfile>` trong `ossec.conf` của agent WEB01, trỏ vào `/var/log/dvwa/access.log` (log_format `apache`)
  3. Viết **custom rule** trong `rules/local_rules.xml`: phát hiện truy cập lặp lại vào `/vulnerabilities/sqli/?id=` với nhiều giá trị `id` khác nhau trong thời gian ngắn từ cùng 1 nguồn (frequency-based correlation rule, cùng kỹ thuật với rule lockout ở Kịch bản 1) → alert "Object ID enumeration detected / Possible IDOR attempt".
- Rule: `../../rules/local_rules.xml` (bổ sung custom rule khi thực hiện — khác Kịch bản 1 vì không có ruleset Windows mặc định nào xử lý IDOR qua HTTP log).
- Cảnh báo (ảnh): bổ sung sau khi chạy tấn công và xem dashboard Wazuh.

## Tầng 5 — Ứng cứu (NIST SP 800-61)
- Báo cáo: ../../grc/reports/incident-02-idor.md

## Tầng 6 — Quản trị
- Sổ rủi ro / gap assessment / TT09: chấm control ISO 27001:2022 **A.8.2** (Privileged access rights), **A.5.15** (Access control), **A.8.9** (Configuration management) — Đạt/Chưa đạt kèm bằng chứng, bổ sung sau khi có kết quả thật. Dự kiến A.5.15/A.8.2 ghi nhận **Chưa đạt** (thiếu object-level authorization ở tầng ứng dụng).

## Tầng 7 — Khuyến nghị
- (điền sau khi hoàn thành Tầng 1-6 — dự kiến: bổ sung kiểm tra authorization ở code ứng dụng, không chỉ dựa vào network/WAF; áp dụng nguyên tắc "never trust client input" cho mọi object reference)
