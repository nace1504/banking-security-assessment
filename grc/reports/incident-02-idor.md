# Báo cáo sự cố — IDOR
Ngày: 07/10/2026 | Người xử lý: Doãn Hữu Nguyên | Mức: Trung bình (level 10 — single-source enumeration, không có dữ liệu nhạy cảm thực tế bị rò rỉ ngoài phạm vi lab)

## 1. Phát hiện
- Nguồn phát hiện: Wazuh SIEM, rule tùy chỉnh `100011` (level 10, nhóm `idor_attempt`), dựa trên Apache access log của DVWA (agent WEB01, id 002).
- Thời điểm bắn alert: 07/10/2026 22:52:41 (giờ địa phương UTC+7) — tương ứng khoảng 15:52:41 UTC.
- Nội dung alert: "DVWA: Nhieu lan truy cap id khac nhau trong thoi gian ngan - nghi ngo IDOR / Object ID enumeration (MITRE T1190)".
- Điều kiện kích hoạt: ≥4 lần truy cập `GET /vulnerabilities/sqli/?id=X&Submit=Submit` với các giá trị `id` khác nhau, từ cùng 1 địa chỉ nguồn (192.168.248.1 — NAT/WAN pfSense), trong vòng 30 giây.

## 2. Phân tích
- Hành vi quan sát được ở tầng ứng dụng: lần lượt truy cập `id=1` đến `id=5`, mỗi lần trả về một bản ghi người dùng DVWA khác nhau (admin, Gordon Brown, Hack Me, Pablo Picasso, Bob Smith) mà không cần payload SQL injection — xác nhận đây là lỗi **IDOR/BOLA** (object reference không được kiểm tra quyền sở hữu), không phải SQL injection.
- Phân loại: OWASP A01:2025 (Broken Access Control), API1:2023 (BOLA); MITRE ATT&CK T1190 (Exploit Public-Facing Application); STRIDE: Information Disclosure + Elevation of Privilege.
- Root cause ở tầng ứng dụng: trang SQLi của DVWA không kiểm tra `session_user_id` có khớp với `id` được yêu cầu hay không — bất kỳ user đã đăng nhập nào cũng xem được dữ liệu của user khác.
- **Phát hiện vận hành trong quá trình xây dựng detection (xem chi tiết tại `scenarios/02-idor/README.md` → Tầng 4)**: lần đầu viết custom rule độc lập bằng `<decoded_as>web-accesslog</decoded_as>`, rule không bao giờ được Wazuh engine thử tới vì log đã khớp trước với rule gốc có sẵn `31100` (Access log messages grouped) — engine chỉ dò tiếp cây con của rule đã khớp. Phải sửa rule thành con thật sự của 31100 bằng `<if_sid>31100</if_sid>` thì mới hoạt động. Dùng `wazuh-logtest -v` (chế độ debug hiển thị toàn bộ cây rule được thử) là công cụ quyết định để chẩn đoán vấn đề này.

## 3. Ngăn chặn
- Đây là bài tập mô phỏng có kiểm soát trong lab, không cần hành động ngăn chặn khẩn cấp (không có dữ liệu thật bị lộ ra ngoài).
- Trong môi trường thực tế, hành động ngăn chặn tương ứng: tạm thời rate-limit/throttle theo IP ở WAF hoặc reverse proxy khi phát hiện pattern enumeration tương tự, và vô hiệu hoá session của tài khoản liên quan nếu nghi ngờ bị chiếm dụng.

## 4. Khôi phục
- Không cần khôi phục dữ liệu/hệ thống (không có thay đổi/phá hoại dữ liệu, chỉ có truy xuất đọc trái phép).
- Hành động khắc phục thực tế đã thực hiện trong lab: xác nhận không có cấu hình an toàn (kể cả security level cao nhất của DVWA) nào vá được lỗi này → kết luận cần escalate cho đội phát triển ứng dụng bổ sung kiểm tra authorization ở tầng code, không xử lý được bằng cấu hình hệ thống hay rule mạng.

## 5. Bài học
- **Kỹ thuật phát hiện (SIEM)**: khi viết custom rule cho một loại log mà Wazuh đã có ruleset mặc định xử lý (ví dụ Apache/web-accesslog), bắt buộc phải gắn rule mới vào đúng cây rule có sẵn bằng `<if_sid>` thay vì định nghĩa độc lập bằng `<decoded_as>` — nếu không, rule có sẵn sẽ "thắng" trước và chặn việc dò tiếp sang rule riêng, dù điều kiện logic hoàn toàn đúng và XML hợp lệ (không có lỗi khi restart service, nên rất dễ bị bỏ sót). Luôn xác minh bằng `wazuh-logtest -v` xem rule có thực sự được thử hay không, không chỉ kiểm tra cú pháp.
- **Quản trị (GRC)**: IDOR là lớp lỗ hổng không thể khắc phục bằng cấu hình/hardening hệ thống — đây là ranh giới rõ ràng giữa trách nhiệm vận hành (operations/SOC, có thể phát hiện và giám sát) và trách nhiệm phát triển (secure coding, phải sửa tận gốc). Risk treatment phù hợp là Accept (ngắn hạn, có compensating control giám sát) kết hợp Mitigate (dài hạn, escalate dev team).
- So sánh với Kịch bản 1 (ATO): Kịch bản 1 tận dụng được rule có sẵn của Wazuh cho lockout Windows; Kịch bản 2 phải tự viết toàn bộ rule cho log HTTP vì không có ruleset IDOR mặc định — bộc lộ rõ hơn các "bẫy" kỹ thuật của chính cơ chế rule engine mà một ruleset có sẵn thường che giấu.
