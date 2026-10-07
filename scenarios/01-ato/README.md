# Kịch bản 1 — Chiếm đoạt tài khoản (ATO)

## Tầng 1 — Mô hình đe doạ
- Mô tả: Attacker cố đăng nhập vào tài khoản nhân viên domain `nguyenvana` trên DC01 qua RDP, thử nhiều mật khẩu sai liên tiếp (password guessing). Giả định: attacker đã biết username (qua OSINT/rò rỉ nơi khác), chưa biết mật khẩu. Phân loại STRIDE: **Spoofing** (giả danh người dùng hợp lệ).
- Giả định về vị trí mạng: Lab bỏ qua bước "initial access vào LAN" (compromise máy nội bộ, VPN leak, pivot từ DMZ, hoặc insider đe doạ) — attacker được giả định đã có vị trí mạng trong LAN nội bộ (10.10.10.0/24) từ trước. Kịch bản tập trung kiểm chứng control xác thực + phát hiện + ứng cứu khi có brute-force xảy ra trong mạng nội bộ, không mô phỏng toàn bộ chuỗi tấn công (kill chain) từ bên ngoài vào. Threat "insider" hoặc "máy nội bộ đã bị chiếm quyền" là giả định thực tế, phù hợp với MITRE ATT&CK Tactic "Credential Access" (sau giai đoạn Initial Access/Lateral Movement).
- Khung: OWASP A07:2025 (Identification and Authentication Failures); MITRE T1110.001 (Brute Force: Password Guessing)

## Tầng 2 — Tấn công (lab)
- Thực hiện: Brute-force RDP vào DC01 (10.10.10.10) từ máy trong LAN 10.10.10.0/24, thử sai mật khẩu tài khoản `nguyenvana` nhiều lần liên tiếp cho đến khi tài khoản bị khoá.
- Bằng chứng: screenshots/ (RDP login fail, Event Viewer 4625/4740) — bổ sung sau khi thực hiện.

## Tầng 3 — Hardening
- Biện pháp: GPO Default Domain Policy đã cấu hình từ Giai đoạn 1 — password complexity ≥12 ký tự, account lockout threshold 5 lần/15 phút, audit logon (Success+Failure).
- Trước/sau: không cấu hình thêm cho kịch bản này — mục tiêu là kiểm chứng control đã có hoạt động đúng khi bị tấn công thật, không phải thêm control mới.

## Tầng 4 — Phát hiện
- Rule: ../../rules/ — dùng ruleset Windows mặc định của Wazuh (Event ID 4625 logon failure, 4740 account locked out), chưa cần custom rule cho kịch bản này.
- Cảnh báo (ảnh): bổ sung sau khi chạy tấn công và xem dashboard Wazuh.

## Tầng 5 — Ứng cứu (NIST SP 800-61)
- Báo cáo: ../../grc/reports/incident-01-ato.md

## Tầng 6 — Quản trị
- Sổ rủi ro / gap assessment / TT09: chấm control ISO 27001:2022 **A.8.5** (Secure authentication), **A.5.17** (Authentication information), **A.8.16** (Monitoring activities) — Đạt/Chưa đạt kèm bằng chứng, bổ sung sau khi có kết quả thật.

## Tầng 7 — Khuyến nghị
- (điền sau khi hoàn thành Tầng 1-6 — dự kiến: cân nhắc MFA, cảnh báo real-time thay vì chỉ xem dashboard thủ công)
