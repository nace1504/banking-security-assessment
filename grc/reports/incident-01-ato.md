# Báo cáo sự cố — ATO
Ngày: 07/10/2026 | Người xử lý: Doãn Hữu Nguyên | Mức: Trung bình (lab mô phỏng, không ảnh hưởng hệ thống thật)

## 1. Phát hiện
- Thời gian: 07/10/2026, 18:38:16–18:38:42 (giờ VN, UTC+7) / 11:38:16–11:38:42 UTC
- Nguồn phát hiện: Wazuh SIEM (WAZUH01), agent DC01, qua Windows Security Event Log (eventchannel)
- Alert: rule.id **60122** "Logon Failure - Unknown user or bad password" (level 5) — 5 lần liên tiếp, cách nhau ~6-7 giây; sau đó rule.id **60115** "User account locked out (multiple login errors)" (level 9)
- Tài khoản bị target: `LAB\nguyenvana`
- Nguồn tấn công: Caller Computer Name `ADMIN-PC`, IP 10.10.10.100 (máy host, qua adapter VMnet2 — LAN nội bộ)
- Bằng chứng: screenshots/dc01-rdp-account-locked.png, dc01-eventviewer-4625-logon-failed.png, dc01-eventviewer-4740-account-locked.png, wazuh-dashboard-ato-alerts.png, wazuh-events-table-ruleid.png

## 2. Phân tích
- Kỹ thuật: MITRE T1110.001 (Brute Force: Password Guessing); OWASP A07:2025 (Identification and Authentication Failures); STRIDE: Spoofing
- Mô tả: 5 lần đăng nhập RDP sai mật khẩu liên tiếp vào tài khoản domain `nguyenvana` trên DC01, dẫn đến tài khoản bị khoá tự động theo GPO Account Lockout Policy (threshold 5 lần/15 phút).
- Mức độ nghiêm trọng: Thấp trong phạm vi lab, vì control hoạt động đúng và ngăn chặn kịp thời. Trong môi trường thật, nếu thiếu lockout policy hoặc giám sát, kỹ thuật này có thể dẫn đến chiếm đoạt tài khoản (ATO) thành công khi mật khẩu yếu/dễ đoán.
- Phạm vi ảnh hưởng: 1 tài khoản (`nguyenvana`), không ghi nhận dấu hiệu lateral movement hay truy cập trái phép nào khác.
- Sự cố vận hành trong quá trình thực hiện: lần tấn công đầu tiên (18:01 giờ VN) không được ghi nhận alert vì tại thời điểm đó wazuh-manager/indexer/dashboard trên WAZUH01 chưa khởi động xong (dashboard báo "not ready"). Sau khi restart toàn bộ service Wazuh, phát hiện thêm lỗi filebeat `401 Unauthorized` — nguyên nhân do mật khẩu lưu trong filebeat keystore không khớp với mật khẩu admin OpenSearch đã đổi thủ công trước đó. Đã khắc phục bằng cách cập nhật lại `filebeat keystore` (username/password) rồi restart filebeat. Tấn công lần 2 (18:38) được ghi nhận đầy đủ, chính xác.

## 3. Ngăn chặn
- Control tự động: GPO Default Domain Policy (Account Lockout Policy) đã tự khoá tài khoản `nguyenvana` ngay sau lần đăng nhập sai thứ 5 — không cần can thiệp thủ công để ngăn chặn.
- Không thực hiện thêm hành động ngăn chặn bổ sung (chặn IP, cô lập máy...) vì đây là môi trường lab nội bộ, nguồn tấn công là máy host được kiểm soát hoàn toàn.

## 4. Khôi phục
- Mở khoá tài khoản `nguyenvana` qua Active Directory Users and Computers (Properties → tab Account → tick "Unlock account").
- Xác nhận agent Wazuh trên DC01 và pipeline SIEM (manager, indexer, filebeat) hoạt động ổn định trở lại sau khi xử lý sự cố vận hành ở mục 1.
- Khuyến nghị bổ sung (chưa thực hiện): kiểm thử đăng nhập lại bằng mật khẩu đúng sau khi mở khoá để xác nhận tài khoản hoạt động bình thường hoàn toàn.

## 5. Bài học
- Control xác thực (GPO lockout) hoạt động đúng như thiết kế, được kiểm chứng bằng tấn công brute-force thật — không chỉ dựa trên cấu hình lý thuyết.
- Phát hiện tự động qua Wazuh hoạt động chính xác khi toàn bộ pipeline (manager → filebeat → indexer → dashboard) sẵn sàng, nhưng phụ thuộc hoàn toàn vào việc tất cả các thành phần này phải "khoẻ mạnh" cùng lúc — một khâu lỗi âm thầm (ví dụ sai credential sau khi đổi mật khẩu) có thể khiến toàn bộ log bị mất mà không có cảnh báo nào cho người vận hành biết.
- Quy trình thay đổi mật khẩu dùng chung (shared credential) cần có checklist đồng bộ ở mọi service phụ thuộc, tránh gây gián đoạn giám sát ngoài ý muốn.
- Khuyến nghị chi tiết: xem Tầng 7, `scenarios/01-ato/README.md`.
