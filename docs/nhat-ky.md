# Nhật ký dự án

## 2026-10-03
- Dựng khung repo + docs.
- Việc tiếp: xem docs/ke-hoach.md (Giai đoạn 0).
- Tải xong VMware Workstation Pro, pfSense CE, Windows Server 2022 Eval, Ubuntu Server 24.04, Kali (VM dựng sẵn).
- Xong Giai đoạn 0. Bắt đầu Giai đoạn 1: dựng lab.

## 04/10/2026
- Dựng xong FW01 (pfSense CE 2.9.0): VMnet2 (LAN 10.10.10.0/24), VMnet3 (DMZ 10.10.20.0/24), WAN NAT.
- Cấu hình: đổi pass admin, unblock WAN reserved networks, đổi tên OPT1→DMZ, 3 firewall rule DMZ (allow Wazuh log, block DMZ→LAN, allow DMZ outbound), 2 NAT port forward (22, 80 → WEB01 10.10.20.10).
- Snapshot `pfsense-configured`. Đã ghi chi tiết vào `infra/pfsense.md`.
- Tiếp theo: dựng DC01 (AD/GPO) hoặc WEB01 (DVWA).

## 05/10/2026
- Dựng xong DC01 (Windows Server 2022 Standard Desktop Experience, 4GB RAM, 1 NIC VMnet2).
- AD DS + DNS, domain lab.local lên thành công.
- OU IT, HR; user mẫu nguyenvana (IT), tranthib (HR).
- GPO Default Domain Policy: password >=12 ký tự + complexity, lockout 5 lần/15 phút, audit logon + account management (Success+Failure).
- Snapshot dc01-configured. Đã ghi chi tiết vào infra/ad-gpo.md.
- Tiếp theo: WEB01 (DVWA qua Docker) hoặc Wazuh.

## 05/10/2026 (tiếp — WEB01/DVWA)
- Dựng xong WEB01 (Ubuntu Server 24.04.4 LTS, 2 vCPU/2GB RAM, DMZ 10.10.20.10).
- Cài Docker CE, deploy container DVWA (`vulnerables/web-dvwa`), map port 80:80.
- Fix lỗi DNS Docker daemon (`/etc/docker/daemon.json` → 8.8.8.8/1.1.1.1).
- Set Security Level = low; đăng nhập admin/password thành công qua NAT WAN pfSense.
- Sự cố gặp giữa chừng: FW01 (pfSense) bị tắt máy → WEB01 mất kết nối gateway/DNS hoàn toàn; bật lại pfSense là hết.
- Snapshot `web01-configured`. Đã ghi chi tiết vào `infra/dvwa.md`.
- Tiếp theo: Wazuh + agent DC01, WEB01 → `infra/wazuh.md`.


## 05/10/2026 (tiếp — Wazuh)
- Dựng xong WAZUH01 (Ubuntu Server 24.04 LTS, 2 vCPU/4GB RAM/40GB disk, LAN 10.10.10.20).
- Cài Wazuh 4.14.8 all-in-one (indexer + manager + dashboard). Gặp 2 sự cố lớn:
  - Hết dung lượng đĩa (LVM guided-storage chỉ cấp 19/40GB) → fix bằng `lvextend` + `resize2fs`.
  - Gói wazuh-manager kẹt dpkg purge-incomplete do prerm/postrm lỗi → vô hiệu hoá script, purge ép buộc, cài sạch lại.
- Đổi mật khẩu admin (UI không cho vì user reserved) → đổi qua OpenSearch Security backend (hash.sh + sửa internal_users.yml + securityadmin.sh).
- Deploy agent DC01 (Windows): gặp sự cố mạng lạ (ICMP thông nhưng TCP/UDP outbound bị chặn hết) → cô lập từng lớp, cuối cùng phát hiện **VMware NAT Service trên máy host bị kẹt** sau nhiều lần bật/tắt VM — restart service là hết. Agent DC01 lên Active.
- Deploy agent WEB01 (Ubuntu/DMZ): chạy trơn tru, không cần thêm rule pfSense (đã có sẵn từ trước). Agent WEB01 lên Active.
- Snapshot `wazuh01-configured`. Đã ghi chi tiết vào `infra/wazuh.md`.
- **Hoàn thành toàn bộ Giai đoạn 1 (dựng lab)**: FW01, DC01, WEB01/DVWA, WAZUH01 đều xong + snapshot + docs.
- Tiếp theo: Kịch bản 1 (ATO) — mô hình đe doạ, sinh sự kiện, viết rule Wazuh, `grc/reports/incident-01-ato.md`.


## 07/10/2026 (Kịch bản 1 — ATO)
- Soạn kế hoạch 7 tầng cho Kịch bản 1 (ATO): brute-force RDP vào tài khoản domain `nguyenvana` trên DC01, tận dụng GPO lockout + audit logon đã có từ Giai đoạn 1, không cần viết custom rule Wazuh (dùng ruleset Windows mặc định).
- Sự cố mạng: adapter "VMware Network Adapter VMnet2" trên máy host bị mất IP tĩnh (rơi về APIPA 169.254.x.x) sau khi restart — đặt lại static `10.10.10.100/24`, gateway `10.10.10.1` là hết.
- Thực hiện brute-force RDP lần 1 (18:01): tài khoản `nguyenvana` bị khoá đúng như kỳ vọng, Event Viewer DC01 ghi nhận đầy đủ 4625/4740 — nhưng Wazuh dashboard KHÔNG có alert, vì lúc đó wazuh-manager/indexer/dashboard trên WAZUH01 chưa khởi động xong.
- Restart toàn bộ service Wazuh (indexer, manager, dashboard, filebeat) → phát hiện thêm lỗi filebeat `401 Unauthorized` (mật khẩu trong filebeat keystore không khớp mật khẩu admin OpenSearch đã đổi trước đó) → fix bằng `filebeat keystore add username/password --force` rồi restart filebeat.
- Mở khoá tài khoản, thực hiện lại brute-force RDP lần 2 (18:38): Wazuh dashboard ghi nhận đầy đủ 13 alert (rule.id 60122 Logon Failure x5, rule.id 60115 Account locked out), đúng kỳ vọng.
- Hoàn thành đầy đủ 7 tầng của `scenarios/01-ato/README.md`, viết `grc/reports/incident-01-ato.md` theo cấu trúc NIST SP 800-61, chấm control ISO 27001 A.8.5/A.5.17/A.8.16 (Đạt, Đạt, Đạt có điều kiện — ghi nhận gap về health-check SIEM).
- Bài học quan trọng: pipeline SIEM (manager→filebeat→indexer→dashboard) có thể "âm thầm" mất log nếu một khâu lỗi (ví dụ sai credential sau khi đổi mật khẩu dùng chung) mà không có cảnh báo — đưa vào khuyến nghị Tầng 7.
- **Hoàn thành Kịch bản 1 (ATO)** — còn lại: đẩy lên GitHub (thủ công).

## 07/10/2026 (Kịch bản 2 — IDOR/BOLA)
- Chọn trang SQL Injection của DVWA (`/vulnerabilities/sqli/?id=X`) làm kịch bản IDOR: đổi `id` không kèm payload SQL injection để xem dữ liệu user khác — lỗ hổng Broken Object Level Authorization tách biệt khỏi kỹ thuật SQLi.
- Recreate container DVWA với volume mount log ra host (`-v /var/log/dvwa:/var/log/apache2`) để Wazuh agent đọc được Apache access log (trước đó log nằm trong container, agent không thấy).
- Thêm `<localfile>` (log_format apache) vào `ossec.conf` của agent WEB01.
- Viết custom rule 2 tầng trong `local_rules.xml` (rule 100010 "đánh dấu" truy cập trang sqli + rule 100011 frequency="4" timeframe="30" phát hiện enumeration).
- **Sự cố kỹ thuật**: rule 100010 ban đầu định nghĩa độc lập bằng `<decoded_as>web-accesslog</decoded_as>` — không bao giờ được Wazuh thử vì log đã khớp trước rule có sẵn `31100`, engine chỉ dò cây con của rule đã khớp. Dùng `wazuh-logtest -v` chẩn đoán ra nguyên nhân, sửa rule 100010 thành con thật sự của 31100 bằng `<if_sid>31100</if_sid>` → hoạt động đúng.
- Thực hiện tấn công thật: id=1→5 trên trình duyệt, xác nhận DVWA trả về 5 user khác nhau (admin, Gordon Brown, Hack Me, Pablo Picasso, Bob Smith) không cần SQL injection.
- Wazuh dashboard ghi nhận đúng alert rule.id 100011 (level 10, group idor_attempt) lúc 22:52:41 — xác nhận detection hoạt động end-to-end.
- Hoàn thành đầy đủ 7 tầng `scenarios/02-idor/README.md`, viết `grc/reports/incident-02-idor.md` theo NIST SP 800-61, chấm control ISO 27001 A.5.15 (Chưa đạt), A.8.2 (Đạt có điều kiện), A.8.9 (Đạt).
- Bài học quan trọng: khi viết custom rule cho log loại Wazuh đã có ruleset mặc định xử lý, phải gắn vào đúng cây rule có sẵn bằng `<if_sid>` thay vì dùng `<decoded_as>` độc lập — nếu không rule có sẵn sẽ "chặn" việc dò tiếp, lỗi này không gây crash/lỗi config nên rất dễ bỏ sót, chỉ phát hiện được bằng `wazuh-logtest -v`.
- **Hoàn thành Kịch bản 2 (IDOR/BOLA)** — còn lại: đẩy lên GitHub (thủ công).

## 07/10/2026 (GRC — sổ rủi ro, gap assessment, TT09, policy)
- Đọc cấu trúc thật của Thông tư 09/2020/TT-NHNN (57 Điều, 3 Chương, 10 Mục) để ánh xạ chính xác, không suy đoán số điều.
- `grc/risk-register.xlsx`: 8 rủi ro rút ra trực tiếp từ 2 kịch bản đã thực hiện + quan sát vận hành (ATO, IDOR, sự cố pipeline SIEM, mật khẩu mặc định, phân vùng mạng, lỗ hổng kỹ thuật chưa vá, thiếu review quyền định kỳ, blind spot giám sát container). Công thức Điểm rủi ro = Khả năng × Ảnh hưởng, Mức rủi ro tính tự động theo ngưỡng (Thấp/Trung bình/Cao/Rất cao), kèm sheet ma trận 5×5 có màu.
- `grc/gap-assessment.xlsx`: chấm 9 control ISO 27001:2022 Annex A (A.8.5, A.5.17, A.8.16, A.5.15, A.8.2, A.8.9, A.5.1, A.8.3, A.5.37) — 4 Đạt, 3 Đạt có điều kiện, 2 Chưa đạt, có công thức tự đếm và tỷ lệ Đạt.
- `grc/tt09-mapping.xlsx`: ánh xạ 10 Điều liên quan của TT09 (6, 22, 26, 28, 29, 30, 38, 43, 45, 48) sang control ISO tương ứng và bằng chứng thực tế trong dự án.
- Hoàn thiện 2 chính sách `grc/policies/password.md` và `grc/policies/access-control.md` — đầy đủ Mục đích/Phạm vi/Quy định/Vai trò/Ngày hiệu lực, có tham chiếu trực tiếp tới bằng chứng và bài học từ 2 kịch bản (đặc biệt mục 5 của access-control.md viết thẳng từ bài học IDOR).
- Tất cả file Excel đã chạy qua recalc (LibreOffice), xác nhận 0 lỗi công thức.
- Checkbox Giai đoạn 3 (risk-register, gap-assessment, tt09-mapping + policy) hoàn thành sớm hơn kế hoạch (dự kiến 13-15/10, xong 07/10).

## 08/10/2026 (Giai đoạn 4 — scripts/wazuh_summary.py)
- Viết `scripts/wazuh_summary.py`: đọc `alerts.json` (JSON Lines), tổng hợp theo rule.level, agent, top rule, top group — không cần thư viện ngoài. Test với dữ liệu mẫu trước khi deploy (đúng với --agent, --since).
- Không dán được clipboard vào `nano` trên console WAZUH01 (VMware clipboard sharing không hoạt động) → chuyển sang cách chia base64 thành 22 đoạn, ghép qua `echo >>` rồi `base64 -d` giải mã — vẫn là giải pháp ổn định nhất cho giới hạn paste của console VM.
- Gặp lỗi quyền đọc `/var/ossec/logs/alerts/alerts.json` (cần root) — xử lý bằng `sudo su`; lưu ý khi đổi user, biến `~` đổi theo home mới nên các bước tạo file tạm (`wsummary.b64`) phải thực hiện trước khi đổi sang root, hoặc dùng đường dẫn tuyệt đối.
- `alerts.json` hiện tại chỉ còn log mới (rotate theo ngày) — tìm thấy log lưu trữ đầy đủ ngày 07/10 tại `/var/ossec/logs/alerts/2026/Oct/ossec-alerts-07.json`, chạy script trên file này ra kết quả đầy đủ: 570 alert, 3 agent (DC01 386, WEB01 65, wazuh01 119), bao gồm cả rule 60122 (ATO) và rule 100010/100011 (IDOR) — xác nhận lại 2 kịch bản bằng 1 công cụ độc lập với dashboard.
- Lưu output thật vào `scripts/wazuh-summary-sample.md` và ảnh chụp console vào `screenshots/` làm bằng chứng script chạy được trên dữ liệu thật.

## 08/10/2026 (Giai đoạn 4 — grc/assessment-report.md)
- Viết báo cáo tổng hợp (~7 trang) tổng hợp toàn bộ dự án: phương pháp luận 7 tầng, hạ tầng, 2 kịch bản (ATO, IDOR) kèm 2 bài học vận hành/kỹ thuật quan trọng nhất (filebeat keystore mất log âm thầm; rule engine tree của Wazuh khiến rule hợp lệ không bao giờ được thử), kết quả gap assessment (4 Đạt/3 Đạt có điều kiện/2 Chưa đạt), sổ rủi ro, ánh xạ TT09, kết quả script wazuh_summary.py, khuyến nghị tổng hợp.
- Đọc lại infra/*.md (ad-gpo, dvwa, pfsense, wazuh) và 2 báo cáo sự cố để đảm bảo số liệu/chi tiết kỹ thuật chính xác trước khi viết, tránh suy diễn.

## 08/10/2026 (Giai đoạn 4 — README + rà soát bảo mật repo)
- README.md: kiểm tra lại toàn bộ, đã đủ nội dung; tạo thêm `screenshots/network-diagram.png` (sơ đồ FW01/LAN/DMZ/WAN, IP, luồng log được phép) vì file này được README tham chiếu nhưng chưa tồn tại.
- Rà soát bảo mật repo trước khi public: phát hiện `infra/wazuh.md` đang ghi mật khẩu admin Wazuh THẬT (`151004Nguyen@`) ở dạng plaintext, không có cảnh báo "chỉ dùng lab" như các mật khẩu khác trong `ad-gpo.md` — đã xoá giá trị thật, chỉ ghi lại đã đổi thành công qua quy trình.
- Kiểm tra thêm: không có email/số điện thoại thật, mã số sinh viên, hay IP công khai thật nào khác bị lộ trong nội dung repo (chỉ có IP private lab và email tác giả trong git log commit — bình thường với repo GitHub công khai).
