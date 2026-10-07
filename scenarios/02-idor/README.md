# Kịch bản 2 — IDOR/BOLA

## Tầng 1 — Mô hình đe doạ
- Mô tả: Trang **SQL Injection** của DVWA (`/vulnerabilities/sqli/?id=X&Submit=Submit#`) trả về dữ liệu theo tham số `id` trong URL mà không kiểm tra người gọi có quyền xem bản ghi đó hay không. Attacker (đã đăng nhập, tài khoản hợp lệ của DVWA) chỉ cần đổi giá trị `id` (không cần payload SQL injection) để xem dữ liệu của "user" khác — đây là lỗ hổng IDOR/BOLA (Broken Object Level Authorization), tách biệt khỏi kỹ thuật SQL Injection thực sự (không tiêm cú pháp SQL).
- Phân loại STRIDE: **Information Disclosure** + **Elevation of Privilege** (truy cập dữ liệu vượt quyền).
- Khung: OWASP A01:2025 (Broken Access Control); API1:2023 (Broken Object Level Authorization); MITRE T1190 (Exploit Public-Facing Application).
- Giả định về vị trí mạng: attacker truy cập DVWA qua `http://192.168.248.136/` (WAN pfSense, NAT port-forward 80→WEB01 trong DMZ 10.10.20.0/24) — mô phỏng user nội bộ/VPN đã có tài khoản DVWA hợp lệ, không phải anonymous.

## Tầng 2 — Tấn công (lab)
- Thực hiện: Đăng nhập DVWA (`http://192.168.248.136/vulnerabilities/sqli/`), lần lượt đổi `id=1` → `id=5` trên URL (≥4 lần trong vòng 30 giây) để quan sát dữ liệu trả về khác nhau theo từng `id`, không kèm payload SQL injection.
- Kết quả quan sát:
  | id | First name | Surname |
  |----|-----------|---------|
  | 1  | admin     | admin   |
  | 2  | Gordon    | Brown   |
  | 3  | Hack      | Me      |
  | 4  | Pablo     | Picasso |
  | 5  | Bob       | Smith   |
- Mỗi `id` trả về đúng 1 bản ghi khác nhau, không có bất kỳ kiểm tra quyền sở hữu nào — xác nhận IDOR thuần (object reference không được bảo vệ), tách biệt khỏi SQL injection.
- Bằng chứng: `screenshots/web01-idor-id1-admin.png`, `screenshots/web01-idor-id5-bobsmith.png`.

## Tầng 3 — Hardening
- Vấn đề thực tế: DVWA **không có cấu hình security level nào sửa được lỗi IDOR này** — kể cả ở mức High, trang SQLi chỉ chống injection (dùng prepared statement), không thêm kiểm tra quyền sở hữu object. Đây là gap cần sửa ở tầng code ứng dụng (kiểm tra `session_user_id == requested_id`), không phải cấu hình hệ thống.
- Risk treatment đề xuất: **Accept** (ngắn hạn, có compensating control giám sát qua Tầng 4) + **Mitigate** (dài hạn, khuyến nghị đội phát triển bổ sung kiểm tra authorization ở code).
- Trước/sau: không có "trước/sau" bằng cấu hình trong lab này — ghi nhận đây là gap không khắc phục được bằng config, cần escalate cho dev team.

## Tầng 4 — Phát hiện
- Vấn đề kỹ thuật: Apache access log của DVWA nằm trong container Docker, Wazuh agent (cài trên OS Ubuntu của WEB01) không đọc trực tiếp được. Đã xử lý:
  1. Tạo lại container DVWA với volume mount log ra ngoài: `docker run -d -p 80:80 -v /var/log/dvwa:/var/log/apache2 --name dvwa vulnerables/web-dvwa`
  2. Thêm `<localfile>` trong `ossec.conf` của agent WEB01 (`log_format apache`, `location /var/log/dvwa/access.log`).
  3. Viết custom rule 2 tầng trong `rules/local_rules.xml`:
     - Rule `100010` (level 3): khớp `decoded_as=web-accesslog` + `url` chứa `/vulnerabilities/sqli/` — rule "đánh dấu" mỗi lần truy cập trang.
     - Rule `100011` (level 10, `frequency="4" timeframe="30"`): dùng `if_matched_sid=100010` + `same_source_ip` — bắn alert khi có ≥4 lần khớp rule 100010 từ cùng 1 IP trong 30 giây → "Nhieu lan truy cap id khac nhau trong thoi gian ngan - nghi ngo IDOR / Object ID enumeration (MITRE T1190)".
- **Sự cố thực tế gặp phải và cách xử lý** (ghi nhận như một phát hiện vận hành, không chỉ là bug lab):
  - Lần chạy đầu: rule 100010 **không hề được Wazuh thử** dù decoder đã nhận diện đúng `web-accesslog` và `url` đúng khớp (`alerts.json` không có alert nào cho rule 100010/100011, kể cả raw search). Dùng `wazuh-logtest -v` (chế độ debug, hiển thị toàn bộ cây rule được thử) phát hiện nguyên nhân: Wazuh đánh giá rule theo **cây cha-con** — log được decode trước tiên khớp rule gốc có sẵn `31100` (Access log messages grouped), và engine **chỉ dò tiếp các rule con của 31100** (các rule có `<if_sid>31100</if_sid>`, ví dụ 31103 SQL injection attempt, 31108 Ignored URLs...). Rule `100010` của mình định nghĩa độc lập bằng `<decoded_as>web-accesslog</decoded_as>` (không phải con của 31100) nên **không bao giờ được thử** sau khi 31100 đã "thắng" làm rule gốc.
  - Khắc phục: sửa rule 100010 thành con thật sự của 31100 — thay `<decoded_as>web-accesslog</decoded_as>` bằng `<if_sid>31100</if_sid>`, giữ nguyên điều kiện `<url>`. Restart `wazuh-manager`, xác nhận lại bằng `wazuh-logtest -v`: rule 100010 xuất hiện trong danh sách "Trying child rules" của 31100 và khớp thành công ("**Alert to be generated**").
  - Bài học: khi viết custom rule cho log loại mới (HTTP/web access log) mà Wazuh đã có ruleset mặc định xử lý decoder đó (apache/web-accesslog), **phải gắn rule mới vào đúng cây rule có sẵn bằng `<if_sid>`** thay vì định nghĩa độc lập bằng `<decoded_as>` — nếu không, rule gốc có sẵn sẽ "chặn" việc dò tiếp sang rule độc lập của mình, dù điều kiện vẫn đúng về mặt logic. Đây là khác biệt quan trọng so với Kịch bản 1 (rule lockout Windows dùng `<if_matched_sid>` nối vào rule có sẵn của Wazuh ngay từ đầu nên không gặp lỗi này).
- Cảnh báo (ảnh): `screenshots/wazuh-dashboard-idor-alert.png` (Threat Hunting dashboard, group `idor_attempt`, Total: 1), `screenshots/wazuh-events-idor-rule100011.png` (Events table, rule.id 100011, level 10, agent WEB01, timestamp 07/10/2026 22:52:41).

## Tầng 5 — Ứng cứu (NIST SP 800-61)
- Báo cáo: ../../grc/reports/incident-02-idor.md

## Tầng 6 — Quản trị
- Chấm control ISO/IEC 27001:2022 Annex A:
  - **A.5.15** (Access control) — **Chưa đạt**: không có kiểm tra object-level authorization ở tầng ứng dụng, cho phép user hợp lệ truy cập dữ liệu của user khác chỉ bằng cách đổi tham số `id`.
  - **A.8.2** (Privileged access rights) — **Đạt có điều kiện**: tài khoản tấn công không có quyền privileged nào bị lạm dụng (đây là lỗi object-level, không phải privilege escalation theo vai trò), nhưng cần giám sát bổ sung vì ranh giới giữa "user thường" và "truy cập ngoài phạm vi" không được enforce.
  - **A.8.9** (Configuration management) — **Đạt**: đã xác nhận không có cấu hình an toàn nào (kể cả security level cao nhất) khắc phục được gap này — kết luận đúng, loại trừ được nguyên nhân "cấu hình sai" khỏi phạm vi trách nhiệm vận hành, khoanh vùng đúng về code ứng dụng.
- Risk treatment: Accept (ngắn hạn, compensating control = Wazuh custom rule 100010/100011 giám sát pattern enumeration) + Mitigate (dài hạn, escalate dev team bổ sung object-ownership check).

## Tầng 7 — Khuyến nghị
- Bổ sung kiểm tra authorization ở code ứng dụng (so khớp `session_user_id` với `id` được yêu cầu) — không chỉ dựa vào network/WAF hay security level của ứng dụng.
- Áp dụng nguyên tắc "never trust client input" cho mọi object reference (ID, file path, resource key) trong toàn bộ ứng dụng, không riêng trang SQLi.
- Về mặt giám sát: khi viết detection rule cho một loại log mới mà Wazuh đã có ruleset mặc định, luôn kiểm tra bằng `wazuh-logtest -v` xem rule có thực sự được cây rule engine thử tới hay không, thay vì chỉ kiểm tra cú pháp XML hợp lệ — đây là lỗi dễ bị bỏ sót vì không gây ra lỗi khi restart service.
