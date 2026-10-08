# Kế hoạch thực hiện (theo dõi bằng checkbox)

Mục tiêu: đến 01/11/2026 nộp đủ ~20 nơi, repo hoàn chỉnh trên GitHub, được gọi 3–5 buổi phỏng vấn.
Ưu tiên #1: MB Trainee – InfoSec GRC (hạn 25/10, nộp trước 17/10).
Cập nhật: tick `[x]` khi xong, ghi chú vào `nhat-ky.md`.

## Mốc quan trọng
| Mốc | Nội dung | Xong khi |
|---|---|---|
| 5/10 | Lab chạy + Kịch bản 1 + README | có 1 cảnh báo Wazuh + ảnh |
| 12/10 | Kịch bản 2 xong | báo cáo sự cố + rule + control chấm xong |
| 17/10 | Nộp MB | hồ sơ + CV GRC hoàn chỉnh |
| 24/10 | Repo hoàn thiện | dashboard, Jira, báo cáo tổng |
| 1/11 | Kết thúc đợt nộp | đủ ~20 nơi |

## Giai đoạn 0 — Tối 3/10: khởi động
- [ ] Hoàn thiện CV kỹ thuật, xuất PDF
- [ ] Gửi Sun Group
- [ ] Nộp CyStack (form web)
- [x] Tải VMware, pfSense, Windows Server 2022 Eval, Ubuntu 24.04, Kali; kiểm tra BIOS ảo hoá
- [x] `git init` repo, commit khung đầu tiên
- [x] Ôn mạng nền: TCP/IP, subnet, NAT, DMZ, firewall rule

## Giai đoạn 1 — 4–5/10: lab + Kịch bản 1
**Chủ nhật 4/10 (dựng lab)**
- [x] Mạng ảo VMnet2/VMnet3 + pfSense → snapshot → ghi `infra/pfsense.md`
- [x] DC01: AD, OU, user, GPO mật khẩu + khoá tài khoản, audit → snapshot → `infra/ad-gpo.md`
- [x] WEB01 + DVWA (Docker) → snapshot → `infra/dvwa.md`
- [x] Wazuh + agent DC01, WEB01 (Active) → snapshot → `infra/wazuh.md`
- [x] Chụp ảnh vào `screenshots/` suốt quá trình

**Thứ Hai 5/10 (Kịch bản 1 — ATO)**
- [x] Tầng 1–4: mô hình đe doạ, sinh sự kiện, ghi cấu hình CIS, viết rule Wazuh
- [x] Tầng 5: `grc/reports/incident-01-ato.md`
- [x] Tầng 6–7: 1 dòng sổ rủi ro, chấm A.8.5 / A.5.17 / A.8.16, khuyến nghị
- [x] Đẩy GitHub, README có sơ đồ + ảnh cảnh báo
- [ ] Thêm dòng dự án vào 2 CV

> Điều kiện tối thiểu sang giai đoạn 2: lab chạy + 1 cảnh báo + README.

## Giai đoạn 2 — 6–9/10: rải CV đợt 1 (~12 nơi)
- [ ] 6/10: CMC Cyber Security (TopCV), VNPT-Net (tuyendung.vnpt.vn)
- [ ] 7/10: VNCS Global, FoxAI
- [ ] 8/10: KNT – TTS System; nhóm B: CMC Telecom, FPT IS, NTQ
- [ ] 9/10: VNPT TTS ATTT, VNPT Trung tâm ATTT, Rikkeisoft
- [ ] 9/10: kiểm tra điều kiện Vietcombank đợt VII
- [ ] Cập nhật cột Trạng thái trong danh sách ứng tuyển
- Học kèm: NIST ứng cứu + SOC tier (6/10) · OWASP Top 10:2025 A01/A05/A07/A09 (7/10) · ISO 27001 điều khoản 4–10 + Annex A (8/10)

## Giai đoạn 3 — 10–17/10: Kịch bản 2 + GRC + nộp MB
- [x] 10-11/10: Kịch bản 2 (IDOR/BOLA) tầng 1-7, bằng chứng trước/sau, `incident-02-idor.md` (xong 07/10, sớm hơn kế hoạch)
- [ ] 12/10: nộp Vietcombank (nếu đủ điều kiện; hạn 14/10) · đọc TT09
- [x] 13-15/10: `risk-register.xlsx` (8 dòng + ma trận 5×5) — xong 07/10, sớm hơn kế hoạch
- [x] 13-15/10: `gap-assessment.xlsx` (9 control, có Đạt/Chưa đạt, có bằng chứng) — xong 07/10
- [x] 13-15/10: `tt09-mapping.xlsx` + 2 policy (`password.md`, `access-control.md`) — xong 07/10
- [ ] 16/10: sửa mẫu Excel MB, hoàn thiện CV GRC
- [ ] 17/10: nộp MB (NV1 GRC, NV2 AI Engineer) · bắt đầu kiểm tra email + Spam mỗi ngày

## Giai đoạn 4 — 18–24/10: hoàn thiện + ôn phỏng vấn
- [ ] Power BI dashboard từ gap assessment + sổ rủi ro
- [ ] Jira: 2 ticket sự cố, chụp luồng trạng thái → `jira/`
- [x] `scripts/wazuh_summary.py` hoàn chỉnh — đã chạy thật trên WAZUH01, output tại `scripts/wazuh-summary-sample.md`
- [ ] `grc/assessment-report.md` (6–8 trang) → xuất PDF
- [ ] README hoàn chỉnh; rà repo không có mật khẩu/thông tin thật
- [ ] (Tuỳ chọn) video demo 2–3 phút
- [ ] 19–23/10: nộp nhóm C (GTSC, VSEC, Bkav, VNCS, NCS, NetNam, Nam Trường Sơn, Vina Aspire, ISOCERT, Robusta, Viện CNTT ĐHQGHN)
- [ ] Soạn câu trả lời STAR (giới thiệu, dự án, vì sao ATTT/GRC, điểm yếu, vì sao công ty này)
- [ ] Luyện demo lab 5 phút từ snapshot
- [ ] Ôn câu SOC và câu GRC

## Giai đoạn 5 — 25/10–1/11: phỏng vấn
- [ ] Mỗi ngày: kiểm tra email + điện thoại, xác nhận lịch trong 24 giờ
- [ ] Trước mỗi buổi: đọc lại JD, chuẩn bị 2 câu hỏi ngược
- [ ] Sau mỗi buổi: ghi câu bị hỏi + chỗ yếu vào `nhat-ky.md`
- [ ] Sapo CTV ATTT (hạn 31/10): chỉ nộp nếu đủ tự tin
- [ ] Gọi hotline các nơi chưa phản hồi sau 5–7 ngày

## Hạn cứng
| Hạn | Nơi | Nộp trước |
|---|---|---|
| 14/10 | Vietcombank đợt VII | 12/10 |
| 18/10 | VNPT-Net | 8/10 |
| 21/10 | VNCS Global | 8/10 |
| 25/10 | MB GRC + AI Engineer | 17/10 |
| 28/10 | FoxAI | 9/10 |
| 29/10 | CMC Cyber Security | 7/10 |
| 31/10 | Sapo | 22/10 |
| 01/11 | KNT | 9/10 |
| Liên tục | CyStack, nhóm B, nhóm C | sớm nhất có thể |
