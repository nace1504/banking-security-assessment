# Chính sách mật khẩu

## Mục đích
Đảm bảo thông tin xác thực (mật khẩu) của tài khoản người dùng và tài khoản dịch vụ được tạo lập, lưu trữ và sử dụng an toàn, giảm thiểu rủi ro chiếm đoạt tài khoản (Account Takeover) qua các hình thức brute-force, credential stuffing hoặc đoán mật khẩu.

## Phạm vi
Áp dụng cho toàn bộ tài khoản truy cập vào hệ thống công nghệ thông tin của tổ chức, bao gồm: tài khoản domain (Active Directory), tài khoản quản trị hệ thống, tài khoản ứng dụng nghiệp vụ. Không áp dụng cho tài khoản demo/lab dùng riêng cho mục đích huấn luyện và kiểm thử nội bộ (ví dụ môi trường DVWA trong lab đánh giá bảo mật).

## Quy định
1. **Độ dài và độ phức tạp**: mật khẩu tối thiểu 8 ký tự, bắt buộc kết hợp chữ hoa, chữ thường, số và ký tự đặc biệt (áp dụng qua GPO Password Policy trên Domain Controller).
2. **Tuổi thọ mật khẩu**: tối đa 90 ngày, tối thiểu 1 ngày trước khi được phép đổi lại (chống đổi mật khẩu dồn dập để quay lại mật khẩu cũ).
3. **Lịch sử mật khẩu**: lưu tối thiểu 5 mật khẩu gần nhất, không cho phép đặt lại trùng.
4. **Ngưỡng khoá tài khoản (Account Lockout)**: khoá tài khoản sau 5 lần đăng nhập sai liên tiếp, thời gian khoá tối thiểu 15 phút, tự động reset bộ đếm sau 15 phút không có lần đăng nhập sai nào.
5. **Không dùng mật khẩu mặc định**: mọi tài khoản dịch vụ/ứng dụng phải đổi mật khẩu mặc định của nhà sản xuất ngay khi triển khai (tham chiếu sổ rủi ro R4 — rủi ro tồn dư ở tài khoản demo ứng dụng).
6. **Lưu trữ**: mật khẩu không được lưu dạng plaintext; hệ thống xác thực và các thành phần phụ trợ (ví dụ credential store của công cụ giám sát) phải được đồng bộ khi có thay đổi mật khẩu dùng chung, tránh lỗi "lệch credential" gây gián đoạn giám sát (tham chiếu bài học vận hành tại `grc/reports/incident-01-ato.md`).
7. **Giám sát**: mọi hành vi đăng nhập sai nhiều lần trong thời gian ngắn phải được SIEM ghi nhận và cảnh báo (tham chiếu rule Wazuh 60115/60122).

## Vai trò
| Vai trò | Trách nhiệm |
|---|---|
| Quản trị hạ tầng AD | Cấu hình và duy trì GPO Password Policy, Account Lockout Policy |
| SOC / Quản trị SIEM | Giám sát cảnh báo brute-force, xử lý sự cố liên quan xác thực |
| Người dùng cuối | Tuân thủ quy định đặt mật khẩu, không chia sẻ thông tin xác thực |
| Đội vận hành ứng dụng | Đổi mật khẩu mặc định cho mọi tài khoản dịch vụ/ứng dụng trước khi đưa vào sử dụng |

## Ngày hiệu lực
Bản thảo — chưa phê duyệt chính thức. Dự kiến trình phê duyệt và áp dụng từ ngày ban hành chính thức, rà soát lại định kỳ hàng năm hoặc khi có thay đổi lớn về hạ tầng/quy định.

## Control đáp ứng (ISO A.5.17, A.8.5)
- **A.8.5 Secure authentication**: mục 1, 2, 4, 7.
- **A.5.17 Authentication information**: mục 3, 5, 6.
- Bằng chứng thực thi: `infra/ad-gpo.md`, `scenarios/01-ato/README.md`, `grc/reports/incident-01-ato.md`.
