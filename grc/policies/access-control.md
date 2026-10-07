# Chính sách kiểm soát truy cập

## Mục đích
Đảm bảo quyền truy cập vào hệ thống, ứng dụng và dữ liệu được cấp phát theo đúng nguyên tắc tối thiểu cần thiết (least privilege) và được kiểm soát ở cả tầng mạng, tầng hệ thống lẫn tầng ứng dụng/dữ liệu, nhằm ngăn chặn truy cập trái phép và lạm dụng quyền.

## Phạm vi
Áp dụng cho toàn bộ truy cập vào hạ tầng mạng (phân vùng LAN/DMZ), hệ thống (Active Directory, máy chủ), và ứng dụng nghiệp vụ (bao gồm quyền truy cập dữ liệu theo từng đối tượng/bản ghi).

## Quy định
1. **Phân vùng mạng**: tách biệt vùng DMZ (chứa ứng dụng tiếp xúc bên ngoài) khỏi vùng LAN nội bộ (chứa hệ thống quản trị, dữ liệu nhạy cảm) bằng firewall; mọi kết nối từ WAN vào DMZ phải qua rule NAT port-forward được kiểm soát rõ ràng, không mở trực tiếp vào LAN (tham chiếu `infra/pfsense.md`).
2. **Phân quyền theo nhóm (RBAC)**: tài khoản người dùng được tổ chức theo OU (Organizational Unit) và gán quyền qua GPO tương ứng với vai trò công việc (ví dụ nhóm HR, nhóm IT) — tham chiếu `infra/ad-gpo.md`.
3. **Nguyên tắc tối thiểu cần thiết**: chỉ cấp quyền đủ để thực hiện công việc được giao; quyền đặc quyền (privileged access) chỉ cấp cho tài khoản quản trị, có ghi nhận lý do và thời hạn.
4. **Rà soát định kỳ (access recertification)**: quyền truy cập phải được rà soát tối thiểu mỗi 6 tháng hoặc khi có thay đổi vai trò/nhân sự, nhằm loại bỏ quyền dư thừa (tham chiếu sổ rủi ro R7 — hiện chưa có chu kỳ rà soát chính thức, cần thiết lập).
5. **Kiểm soát truy cập ở tầng ứng dụng/dữ liệu (object-level authorization)**: mọi chức năng trả về dữ liệu theo định danh (ID, mã hồ sơ...) bắt buộc phải kiểm tra người dùng hiện tại có quyền truy cập đúng đối tượng được yêu cầu hay không, không chỉ dựa vào việc đã đăng nhập thành công. Đây là yêu cầu bắt buộc rút ra trực tiếp từ lỗ hổng IDOR/BOLA phát hiện trên ứng dụng DVWA trong Kịch bản 2 (tham chiếu `scenarios/02-idor/README.md`, `grc/reports/incident-02-idor.md`) — một tài khoản hợp lệ, không có quyền đặc biệt, vẫn có thể xem dữ liệu của tài khoản khác chỉ bằng cách đổi tham số định danh trên URL.
6. **Giám sát truy cập bất thường**: các hành vi truy cập lặp lại bất thường vào tài nguyên theo nhiều định danh khác nhau trong thời gian ngắn (dấu hiệu dò quét/enumeration) phải được giám sát và cảnh báo (tham chiếu rule Wazuh 100010/100011).

## Vai trò
| Vai trò | Trách nhiệm |
|---|---|
| Quản trị hạ tầng mạng | Cấu hình, rà soát định kỳ rule firewall/NAT giữa các vùng mạng |
| Quản trị hạ tầng AD | Thiết lập OU, GPO, thực hiện rà soát quyền định kỳ |
| Đội phát triển ứng dụng | Triển khai kiểm tra object-level authorization ở mọi endpoint trả dữ liệu theo ID |
| SOC / Quản trị SIEM | Giám sát hành vi truy cập bất thường, xử lý cảnh báo liên quan |

## Ngày hiệu lực
Bản thảo — chưa phê duyệt chính thức. Dự kiến trình phê duyệt và áp dụng từ ngày ban hành chính thức, rà soát lại định kỳ hàng năm hoặc khi có thay đổi lớn về hạ tầng/ứng dụng.

## Control đáp ứng (ISO A.5.15, A.5.18, A.8.3)
- **A.5.15 Access control**: mục 2, 3, 4.
- **A.5.18 Access rights**: mục 3, 4.
- **A.8.3 Information access restriction**: mục 5, 6.
- Bằng chứng thực thi: `infra/pfsense.md`, `infra/ad-gpo.md`, `scenarios/02-idor/README.md`, `grc/reports/incident-02-idor.md`.
