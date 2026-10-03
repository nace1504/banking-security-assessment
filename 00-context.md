# Bối cảnh & phạm vi

## Ngân hàng X (giả lập)
Ngân hàng số cung cấp kênh Mobile/Internet Banking cho khách hàng cá nhân. Lab mô phỏng
backend bằng DVWA trong môi trường ảo hoá cô lập — không có dữ liệu thật, không kết nối
hệ thống thật.

## Mục tiêu đánh giá
Chứng minh quy trình đánh giá bảo mật end-to-end cho 2 rủi ro trọng yếu, có bằng chứng
trước/sau và map sang khung tuân thủ ngành ngân hàng.

## Ranh giới phạm vi (scope)
**Trong phạm vi:** kênh Mobile/Internet Banking; 2 kịch bản ATO và IDOR/BOLA; tầng web,
API và định danh.

**Ngoài phạm vi (hướng mở rộng):** core banking, hệ thống thẻ, SWIFT, test trên app điện
thoại thật, hạ tầng mạng vật lý.

> Nêu rõ giới hạn phạm vi là cách làm chuyên nghiệp — giúp người đọc hiểu đúng những gì
> đã và chưa được kiểm tra.

## Môi trường
Toàn bộ thực hiện trong lab ảo cá nhân (VMware), 4 máy, mạng host-only. Mục tiêu là **sinh
log và minh hoạ control**, không phải tối ưu kỹ thuật tấn công.
