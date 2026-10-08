# Báo cáo đánh giá bảo mật — Kênh Mobile/Internet Banking (Ngân hàng X — môi trường mô phỏng)

**Người thực hiện:** Doãn Hữu Nguyên
**Vai trò mô phỏng:** Security Assessor / SOC Analyst / GRC Analyst
**Thời gian thực hiện:** 04/10/2026 – 08/10/2026
**Môi trường:** Lab ảo hoá cá nhân (VMware Workstation), cô lập hoàn toàn khỏi Internet thật ngoài NAT
**Phạm vi:** Xem chi tiết đầy đủ tại `00-context.md`

---

## 1. Tóm tắt điều hành (Executive Summary)

Báo cáo này trình bày kết quả một đợt đánh giá bảo mật mô phỏng cho kênh Mobile/Internet Banking của một ngân hàng số giả định ("Ngân hàng X"), được thực hiện trên một hạ tầng lab cá nhân gồm 4 máy ảo đóng vai trò tường lửa biên (pfSense), máy chủ danh mục/định danh nội bộ (Active Directory), ứng dụng web mô phỏng lớp dịch vụ khách hàng (DVWA, đại diện cho các lỗ hổng lớp ứng dụng thường gặp trong ứng dụng ngân hàng số), và một hệ thống giám sát an ninh tập trung (Wazuh SIEM).

Mục tiêu không phải là chứng minh kỹ thuật tấn công phức tạp, mà là **xây dựng và kiểm chứng một chu trình đánh giá bảo mật đầy đủ, khép kín**: từ mô hình hoá đe doạ, triển khai kiểm soát (hardening), thực hiện tấn công có kiểm soát để kiểm chứng kiểm soát đó, phát hiện qua SIEM, ứng cứu sự cố theo chuẩn, và cuối cùng là chuyển hoá phát hiện kỹ thuật thành các sản phẩm quản trị rủi ro (GRC) có thể dùng trong thực tế vận hành ngân hàng: sổ rủi ro, đánh giá khoảng cách kiểm soát (gap assessment) theo ISO/IEC 27001:2022, và ánh xạ tuân thủ Thông tư 09/2020/TT-NHNN.

Hai kịch bản tấn công được thực hiện và xác minh đầy đủ bằng bằng chứng thực tế (log, cảnh báo SIEM, ảnh chụp màn hình):

| Kịch bản | Kỹ thuật | Kết quả kiểm soát | Kết quả phát hiện |
|---|---|---|---|
| 1 — Chiếm đoạt tài khoản (ATO) | Brute-force mật khẩu qua RDP (MITRE T1110.001) | **Thành công** — GPO Account Lockout tự động khoá tài khoản sau 5 lần sai | **Thành công** (sau khi khắc phục 1 sự cố vận hành SIEM) — rule 60122/60115 |
| 2 — IDOR/BOLA | Truy cập trái phép dữ liệu người dùng khác qua thay đổi tham số `id` (OWASP A01:2025, API1:2023, MITRE T1190) | **Không thể khắc phục bằng cấu hình hệ thống** — lỗi tầng code ứng dụng | **Thành công** (sau khi khắc phục 1 lỗi kỹ thuật viết rule SIEM) — rule tuỳ chỉnh 100010/100011 |

Điểm đáng chú ý nhất của đợt đánh giá, về mặt phương pháp luận, là cả hai kịch bản đều phát sinh **sự cố vận hành thực tế trong chính quá trình xây dựng khả năng phát hiện** (không phải lỗi giả định) — một lỗi đồng bộ credential khiến SIEM câm lặng mà không cảnh báo, và một lỗi kiến trúc rule engine khiến rule tùy chỉnh không bao giờ được thực thi dù cú pháp hợp lệ. Cả hai được chẩn đoán, khắc phục, và ghi nhận lại như bài học vận hành — phản ánh đúng thực tế vận hành SOC: control đúng về mặt lý thuyết không đồng nghĩa với việc nó đang hoạt động đúng trong thực tế, và cần được kiểm chứng bằng tấn công thật và công cụ chẩn đoán phù hợp (`wazuh-logtest -v`).

Kết quả đánh giá khoảng cách kiểm soát theo ISO/IEC 27001:2022 Annex A (9 control được chấm điểm, xem Mục 5) cho thấy: 4 control Đạt, 3 Đạt có điều kiện, 2 Chưa đạt — phản ánh một hồ sơ kiểm soát tương đối tốt ở tầng hạ tầng/định danh, nhưng còn khoảng cách rõ ràng ở tầng kiểm soát truy cập đối tượng (object-level authorization) trong ứng dụng.

---

## 2. Phương pháp luận

Đánh giá được thực hiện theo mô hình 7 tầng, áp dụng nhất quán cho cả hai kịch bản:

| Tầng | Nội dung | Khung tham chiếu |
|---|---|---|
| 1. Mô hình đe doạ | Xác định actor, mục tiêu, giả định vị trí mạng | STRIDE, MITRE ATT&CK |
| 2. Tấn công (lab) | Thực hiện tấn công có kiểm soát, ghi log/ảnh làm bằng chứng | OWASP Top 10, MITRE ATT&CK |
| 3. Hardening | Kiểm soát phòng ngừa đã/cần triển khai | CIS Benchmark, ISO 27001 Annex A |
| 4. Phát hiện | Rule SIEM, cảnh báo, log tương ứng | Wazuh ruleset, custom rule |
| 5. Ứng cứu sự cố | Báo cáo sự cố theo 5 bước chuẩn | NIST SP 800-61 |
| 6. Quản trị | Chấm điểm control ISO 27001:2022 Annex A | ISO/IEC 27001:2022 |
| 7. Khuyến nghị | Đề xuất cải thiện dựa trên gap phát hiện được | — |

Toàn bộ môi trường, phạm vi, và ranh giới đánh giá (in-scope/out-of-scope) được xác định trước khi bắt đầu — xem `00-context.md`. Đáng lưu ý: phạm vi loại trừ core banking, hệ thống thẻ, SWIFT, và kiểm thử ứng dụng di động thật — đây là một bài tập mô phỏng có kiểm soát trên hạ tầng cá nhân, không phải một pentest thật đối với hệ thống ngân hàng.

---

## 3. Hạ tầng đánh giá

| Máy | Vai trò | Hệ điều hành | IP | Mạng |
|---|---|---|---|---|
| FW01 | Tường lửa biên (pfSense) | pfSense CE 2.9.0 | WAN: DHCP (NAT); LAN: 10.10.10.1/24; DMZ: 10.10.20.1/24 | WAN / LAN / DMZ |
| DC01 | Active Directory + DNS (domain `lab.local`) | Windows Server 2022 Standard | 10.10.10.10/24 | LAN |
| WEB01 | Ứng dụng web (DVWA trong Docker) | Ubuntu Server 24.04 LTS | 10.10.20.10/24 | DMZ |
| WAZUH01 | SIEM (Wazuh 4.14.8 all-in-one: manager + indexer + dashboard + filebeat) | Ubuntu Server 24.04 LTS | 10.10.10.20/24 | LAN |

**Kiến trúc phân vùng mạng:** pfSense phân tách rõ 3 vùng (WAN/LAN/DMZ), với rule tường lửa tường minh: cho phép WEB01 (DMZ) gửi log tới WAZUH01 (LAN) qua cổng 1514–1515, **chặn hoàn toàn DMZ→LAN cho mọi lưu lượng khác**, và cho phép DMZ ra ngoài. Đây là mô hình phân vùng điển hình cho một ứng dụng web công khai (tương tự lớp Internet Banking front-end) không được phép truy cập trực tiếp vào hạ tầng nội bộ nhạy cảm (tương tự core banking/AD).

**Kiểm soát nền tảng đã triển khai trước khi thực hiện 2 kịch bản tấn công** (Giai đoạn 1–2, tham chiếu CIS Benchmark):
- GPO Password Policy: độ dài tối thiểu 12 ký tự, bắt buộc độ phức tạp.
- GPO Account Lockout Policy: khoá sau 5 lần sai, khoá 15 phút, reset counter sau 15 phút.
- GPO Advanced Audit Policy: ghi log Logon (Success+Failure), User Account Management (Success+Failure).
- Agent Wazuh triển khai đầy đủ trên cả DC01 và WEB01, trạng thái Active.

Quá trình xây dựng hạ tầng này bản thân cũng phát sinh nhiều sự cố kỹ thuật thực tế có giá trị học tập (xem `infra/wazuh.md`, `infra/dvwa.md`), trong đó đáng chú ý nhất:
- Lỗi cài đặt Wazuh dashboard do **hết dung lượng đĩa** (LVM guided-storage không tự dùng hết dung lượng đĩa ảo) — chẩn đoán sai ban đầu (nghi ngờ thiếu RAM) trước khi xác định đúng nguyên nhân.
- Lỗi kết nối TCP/UDP từ DC01 ra ngoài dù ICMP thông — sau khi loại trừ toàn bộ firewall/NAT trong lab, xác định nguyên nhân là **VMware NAT Service trên máy host bị kẹt** sau nhiều lần bật/tắt VM liên tục.
- Đổi mật khẩu `admin` reserved trong OpenSearch Security phải thực hiện qua `hash.sh` + sửa trực tiếp `internal_users.yml` + `securityadmin.sh`, không thể qua giao diện Dashboard.

Những sự cố này tuy không phải là kết quả "mong muốn" của đánh giá, nhưng phản ánh trung thực các vấn đề vận hành thật sự gặp phải khi triển khai một SOC/SIEM pipeline nhiều thành phần — và trực tiếp dẫn tới bài học quan trọng nhất của Kịch bản 1 (xem Mục 4.1).

---

## 4. Kết quả đánh giá theo kịch bản

### 4.1. Kịch bản 1 — Chiếm đoạt tài khoản (Account Takeover)

**Mô hình đe doạ:** Kẻ tấn công đã có vị trí mạng trong LAN nội bộ (giả định: máy nội bộ bị chiếm quyền, VPN leak, hoặc insider — initial access không nằm trong phạm vi mô phỏng), biết trước username `nguyenvana` (qua OSINT/rò rỉ nơi khác), thử đoán mật khẩu qua RDP. Phân loại: STRIDE Spoofing; OWASP A07:2025 (Identification and Authentication Failures); MITRE T1110.001.

**Tấn công:** 5 lần đăng nhập RDP sai liên tiếp vào DC01 (07/10/2026, 18:38:16–18:38:42 giờ VN), cách nhau ~6–7 giây.

**Kết quả kiểm soát:** GPO Account Lockout Policy hoạt động **đúng như thiết kế** — tài khoản `nguyenvana` bị khoá tự động ngay sau lần sai thứ 5, không cần can thiệp thủ công.

**Kết quả phát hiện:** Rule mặc định Wazuh — 60122 "Logon Failure - Unknown user or bad password" (level 5, Event ID 4625) và 60115 "User account locked out" (level 9, Event ID 4740) — ghi nhận đầy đủ, chính xác ở lần tấn công thứ hai.

**Sự cố vận hành phát hiện trong quá trình kiểm chứng (bài học quan trọng nhất của kịch bản này):** Lần tấn công đầu tiên (18:01 giờ VN) **hoàn toàn không được ghi nhận alert**, không phải vì control thất bại, mà vì pipeline SIEM (manager/indexer/dashboard) chưa khởi động xong tại thời điểm đó. Sau khi restart service, phát hiện thêm lỗi filebeat trả về `401 Unauthorized` — nguyên nhân là mật khẩu lưu trong **filebeat keystore** không được đồng bộ sau khi mật khẩu `admin` OpenSearch bị đổi thủ công trước đó (đổi qua `internal_users.yml` không tự động cập nhật credential mà filebeat dùng để đẩy log). Khắc phục bằng cách cập nhật lại keystore (`filebeat keystore add username/password --force`) và restart filebeat.

**Ý nghĩa đối với vận hành SOC thật:** Đây là minh hoạ rõ ràng cho một rủi ro vận hành dễ bị bỏ qua — **"silent monitoring failure"**: hệ thống giám sát có thể ngừng nhận log một cách âm thầm, không phát sinh lỗi rõ ràng cho người vận hành, trong khi dashboard vẫn "nhìn" bình thường. Nếu không có bước kiểm chứng bằng tấn công thật (thay vì chỉ tin vào cấu hình lý thuyết), sự cố này hoàn toàn có thể bị bỏ sót.

Báo cáo sự cố đầy đủ (theo NIST SP 800-61): `grc/reports/incident-01-ato.md`.

### 4.2. Kịch bản 2 — IDOR / Broken Object Level Authorization (BOLA)

**Mô hình đe doạ:** Người dùng đã đăng nhập hợp lệ vào ứng dụng, cố truy cập dữ liệu thuộc về người dùng khác bằng cách thay đổi trực tiếp tham số định danh đối tượng (`id`) trong URL — không cần khai thác lỗ hổng kỹ thuật phức tạp. Phân loại: OWASP A01:2025 (Broken Access Control), API1:2023 (BOLA); MITRE T1190 (Exploit Public-Facing Application); STRIDE: Information Disclosure + Elevation of Privilege.

**Tấn công:** Truy cập tuần tự `GET /vulnerabilities/sqli/?id=1..5&Submit=Submit` trên DVWA (WEB01), không dùng payload SQL injection. Mỗi lần trả về một bản ghi người dùng khác nhau mà không có bất kỳ kiểm tra quyền sở hữu nào:

| id | Dữ liệu trả về |
|---|---|
| 1 | admin |
| 2 | Gordon Brown |
| 3 | Hack Me |
| 4 | Pablo Picasso |
| 5 | Bob Smith |

**Kết quả kiểm soát:** **Không có control cấu hình/hardening nào khắc phục được** — kể cả đặt DVWA ở mức bảo mật cao nhất (Security Level: High), lỗi vẫn tồn tại vì nguyên nhân gốc nằm ở tầng code ứng dụng (trang không kiểm tra `session_user_id` có khớp với `id` được yêu cầu hay không). Đây là ranh giới rõ ràng giữa trách nhiệm vận hành (có thể giám sát, phát hiện) và trách nhiệm phát triển ứng dụng (phải sửa tận gốc — secure coding).

**Kết quả phát hiện:** Custom rule 2 tầng được xây dựng riêng (Wazuh không có ruleset IDOR mặc định):
- Rule `100010` (level 3): đánh dấu mỗi lần truy cập trang SQLi.
- Rule `100011` (level 10, `frequency="4" timeframe="30"`, cùng nguồn IP): bắn cảnh báo khi ≥4 lần truy cập `id` khác nhau trong 30 giây.

Alert thực tế bắn lúc 07/10/2026 22:52:41 giờ VN, nhóm `idor_attempt`, xác nhận qua cả Wazuh dashboard và script độc lập `wazuh_summary.py` (xem Mục 6).

**Sự cố kỹ thuật phát hiện trong quá trình xây dựng rule (bài học kỹ thuật quan trọng nhất của toàn bộ đợt đánh giá):** Phiên bản đầu tiên của rule 100010 dùng `<decoded_as>web-accesslog</decoded_as>` làm điều kiện độc lập. Rule **không bao giờ được engine thử tới**, dù cú pháp XML hợp lệ và service Wazuh restart sạch, không báo lỗi. Nguyên nhân: Wazuh đánh giá rule theo cây (tree) bắt đầu từ các rule gốc (root/parentless); một khi log khớp với rule gốc có sẵn (ở đây là rule built-in `31100` "Access log messages grouped"), engine **chỉ** tiếp tục dò các rule con của `31100` (dùng `<if_sid>31100</if_sid>`) — **không** thử thêm các rule gốc độc lập khác dù điều kiện logic của chúng hoàn toàn đúng. Chẩn đoán dứt điểm bằng `sudo /var/ossec/bin/wazuh-logtest -v` (chế độ debug, hiển thị toàn bộ "Rule debugging" — danh sách đầy đủ mọi rule được thử) — công cụ quyết định cho lớp lỗi này, vì cú pháp hợp lệ và log hệ thống không ghi nhận lỗi nào. Khắc phục: đổi điều kiện rule thành `<if_sid>31100</if_sid>` để biến nó thành con thật sự của rule gốc đã khớp.

**Ý nghĩa đối với kỹ sư SIEM:** Khi viết custom rule cho một loại log mà Wazuh đã có ruleset mặc định xử lý (ví dụ Apache access log), bắt buộc phải gắn rule mới vào đúng cây rule có sẵn bằng `<if_sid>`, không định nghĩa độc lập bằng `<decoded_as>` — nếu không, rule có sẵn sẽ "thắng" trước mà không có bất kỳ dấu hiệu lỗi nào để nhận biết.

Báo cáo sự cố đầy đủ (theo NIST SP 800-61): `grc/reports/incident-02-idor.md`.

---

## 5. Kết quả đánh giá khoảng cách kiểm soát (Gap Assessment — ISO/IEC 27001:2022 Annex A)

9 control được chấm điểm dựa trên bằng chứng thực tế thu thập từ 2 kịch bản và hạ tầng nền (chi tiết đầy đủ: `grc/gap-assessment.xlsx`):

| Control | Tên | Kết quả | Nguồn bằng chứng |
|---|---|---|---|
| A.8.5 | Secure authentication | Đạt | Kịch bản 1 — GPO lockout chặn brute-force thành công |
| A.5.17 | Authentication information | Đạt | GPO password policy ≥12 ký tự |
| A.8.16 | Monitoring activities | Đạt có điều kiện | Phát hiện đúng khi pipeline khoẻ, nhưng từng mất log âm thầm (Kịch bản 1) |
| A.5.15 | Access control | Chưa đạt | Kịch bản 2 — IDOR, không kiểm tra object-level authorization |
| A.8.2 | Privileged access rights | Đạt có điều kiện | Chưa có recertification định kỳ |
| A.8.9 | Configuration management | Đạt | Rule SIEM, GPO được quản lý có tài liệu |
| A.5.1 | Policies for information security | Đạt có điều kiện | Có policy draft (`grc/policies/`), chưa phê duyệt chính thức |
| A.8.3 | Information access restriction | Chưa đạt | Cùng gap với A.5.15 — thiếu kiểm soát ở tầng ứng dụng |
| A.5.37 | Documented operating procedures | Đạt | Tài liệu vận hành đầy đủ (`infra/*.md`, nhật ký sự cố) |

**Tổng kết:** 4/9 Đạt, 3/9 Đạt có điều kiện, 2/9 Chưa đạt (≈44% Đạt hoàn toàn).

**Nhận định:** Khoảng cách lớn nhất và nhất quán nhất là kiểm soát truy cập ở tầng đối tượng dữ liệu (object-level authorization) trong ứng dụng — không thể đóng bằng cấu hình hạ tầng/hardening, đòi hỏi can thiệp vào vòng đời phát triển phần mềm (SDLC) của đội phát triển ứng dụng.

---

## 6. Sổ rủi ro (Risk Register)

8 rủi ro được xác định, chấm điểm theo ma trận Khả năng × Tác động (chi tiết: `grc/risk-register.xlsx`):

| ID | Rủi ro | Điểm | Mức |
|---|---|---|---|
| R1 | Chiếm đoạt tài khoản (ATO) | 16 | Rất cao |
| R2 | IDOR — truy cập trái phép dữ liệu khách hàng | 12 | Cao |
| R3 | Gián đoạn pipeline SIEM (mất log âm thầm) | 12 | Cao |
| R4 | Mật khẩu yếu/mặc định | 9 | Trung bình |
| R5 | Thiếu rà soát định kỳ phân vùng mạng | 10 | Cao |
| R6 | Ứng dụng web chưa vá lỗi | 12 | Cao |
| R7 | Thiếu recertification quyền truy cập | 8 | Trung bình |
| R8 | Điểm mù giám sát container/log | 9 | Trung bình |

R1 (ATO) được chấm mức rủi ro cao nhất về lý thuyết (khả năng xảy ra cao do kỹ thuật phổ biến, tác động cao nếu không có lockout) — mặc dù trong lab control đã chứng minh hoạt động hiệu quả; điểm rủi ro phản ánh **rủi ro gốc (inherent risk)** trước kiểm soát, không phải rủi ro còn lại (residual risk) sau khi đã xác minh control. R3 (gián đoạn SIEM) được thêm trực tiếp từ sự cố vận hành thực tế phát hiện trong Kịch bản 1 — một ví dụ cho thấy sổ rủi ro cần được cập nhật dựa trên sự cố vận hành thật, không chỉ dựa trên đánh giá lý thuyết ban đầu.

---

## 7. Ánh xạ tuân thủ Thông tư 09/2020/TT-NHNN

10 Điều của Thông tư 09/2020/TT-NHNN được ánh xạ với control ISO 27001 tương ứng và bằng chứng dự án (chi tiết: `grc/tt09-mapping.xlsx`), bao gồm: Điều 6 (Quy chế an toàn thông tin), Điều 22 (Sao lưu dự phòng), Điều 26 (Giám sát và ghi nhật ký), Điều 28 (Kiểm soát truy cập/mật khẩu), Điều 29 (Quản lý truy cập mạng nội bộ), Điều 30 (Quản lý truy cập hệ thống và ứng dụng), Điều 38 (An toàn bảo mật ứng dụng), Điều 43 (Quản lý điểm yếu kỹ thuật), Điều 45 (Quy trình xử lý sự cố), Điều 48 (Hoạt động ứng cứu sự cố).

Việc ánh xạ sang một văn bản pháp quy thật (không phải khung quốc tế chung chung) minh hoạ khả năng kết nối giữa phát hiện kỹ thuật cụ thể và yêu cầu tuân thủ đặc thù của ngành ngân hàng Việt Nam — điểm mà một ứng viên vị trí GRC trainee cần thể hiện được.

---

## 8. Công cụ hỗ trợ: `scripts/wazuh_summary.py`

Để xác minh kết quả phát hiện độc lập với giao diện dashboard, một script Python (thư viện chuẩn, không phụ thuộc ngoài) được viết để đọc trực tiếp log `alerts.json`/log lưu trữ của Wazuh và tổng hợp theo mức độ (level), agent, và rule phổ biến nhất.

Chạy trên log lưu trữ đầy đủ ngày 07/10/2026 (`ossec-alerts-07.json`, bao gồm cả 2 kịch bản): **570 alert**, 3 agent (DC01: 386, wazuh01: 119, WEB01: 65). Kết quả xác nhận độc lập: rule 60122 (ATO) xuất hiện 10 lần, rule 100010 (IDOR — tagging) 9 lần, và **rule 100011 (IDOR — frequency alert) xuất hiện đúng 1 lần** — khớp hoàn toàn với kết quả đã xác nhận qua dashboard. Kết quả đầy đủ: `scripts/wazuh-summary-sample.md`.

Việc xây dựng công cụ này cũng tái hiện một vấn đề vận hành SOC thực tế: log hiện hành (`alerts.json`) chỉ giữ dữ liệu gần nhất do cơ chế rotate theo ngày; để lấy đầy đủ bằng chứng lịch sử phải truy cập log lưu trữ (`/var/ossec/logs/alerts/YYYY/Mon/`) — một chi tiết vận hành dễ bị bỏ sót nếu chỉ dựa vào file log "mặc định".

---

## 9. Bài học tổng hợp

1. **Control đúng về lý thuyết ≠ control đang hoạt động đúng trong thực tế.** Cả hai kịch bản đều phát hiện sự cố vận hành chỉ vì có bước kiểm chứng bằng tấn công thật — không dừng ở việc mô tả cấu hình.
2. **Giám sát có thể thất bại âm thầm.** Pipeline SIEM nhiều thành phần (manager → filebeat → indexer → dashboard) có thể ngừng nhận log mà không phát sinh lỗi rõ ràng cho người vận hành (Kịch bản 1).
3. **Rule engine có hành vi không hiển nhiên ngay cả khi cú pháp đúng.** Cơ chế cây rule của Wazuh khiến một rule hợp lệ về cú pháp có thể không bao giờ được thực thi; cần công cụ debug chuyên dụng (`wazuh-logtest -v`) để xác minh, không chỉ kiểm tra khởi động dịch vụ (Kịch bản 2).
4. **Không phải mọi lỗ hổng đều khắc phục được bằng cấu hình hệ thống.** IDOR là ví dụ rõ ràng cho ranh giới giữa trách nhiệm vận hành/SOC (giám sát, phát hiện) và trách nhiệm phát triển phần mềm (secure coding, sửa tận gốc) — một phân biệt quan trọng khi đề xuất risk treatment (Accept/Mitigate ngắn hạn kết hợp Mitigate/Avoid dài hạn qua escalation cho dev team).
5. **Quy trình thay đổi credential dùng chung cần checklist đồng bộ.** Đổi mật khẩu ở một nơi (OpenSearch admin) có thể âm thầm phá vỡ một thành phần phụ thuộc khác (filebeat keystore) không được cập nhật cùng lúc.
6. **Sổ rủi ro và gap assessment cần được nuôi dưỡng bằng sự cố vận hành thật**, không chỉ là tài liệu tĩnh lập ra một lần — ví dụ R3 trong sổ rủi ro được bổ sung trực tiếp từ bài học Kịch bản 1.

---

## 10. Khuyến nghị tổng hợp

| # | Khuyến nghị | Ưu tiên | Loại |
|---|---|---|---|
| 1 | Bổ sung kiểm tra object-level authorization ở tầng code (escalate cho đội phát triển) | Cao | Khắc phục gốc (dev) |
| 2 | Thiết lập health-check/self-monitoring cho pipeline SIEM (manager/indexer/filebeat) | Cao | Vận hành SOC |
| 3 | Cân nhắc triển khai MFA cho tài khoản truy cập hệ thống nhạy cảm, không chỉ dựa vào lockout policy | Trung bình | Kiểm soát xác thực |
| 4 | Thiết lập cảnh báo real-time (email/Slack/Telegram) từ Wazuh thay vì chỉ xem dashboard thủ công | Trung bình | Vận hành SOC |
| 5 | Xây dựng checklist đồng bộ credential khi đổi mật khẩu dùng chung giữa các service phụ thuộc | Trung bình | Quản lý thay đổi |
| 6 | Phê duyệt chính thức các policy đã soạn thảo (`grc/policies/`) — hiện ở trạng thái draft | Trung bình | GRC/Quản trị |
| 7 | Thiết lập rà soát định kỳ (recertification) quyền truy cập và phân vùng mạng | Thấp | GRC/Vận hành |
| 8 | Khi viết custom rule SIEM cho loại log đã có ruleset mặc định, luôn kiểm tra bằng `wazuh-logtest -v` trước khi coi là hoàn thành | Thấp | Kỹ thuật SIEM |

---

## 11. Kết luận

Đợt đánh giá đã hoàn thành đầy đủ chu trình 7 tầng cho 2 kịch bản tấn công đại diện cho hai lớp rủi ro khác nhau trong kênh ngân hàng số (xác thực/định danh và kiểm soát truy cập ứng dụng), với bằng chứng thực tế đầy đủ ở mọi bước — không dừng ở lý thuyết. Các sản phẩm GRC đi kèm (sổ rủi ro, gap assessment, ánh xạ TT09, policy) được xây dựng trực tiếp từ dữ liệu và phát hiện thật của lab, không phải nội dung mẫu generic — đây là điểm khác biệt chính của dự án so với một bài tập lý thuyết thuần tuý, và là nền tảng để trình bày trong hồ sơ ứng tuyển vị trí GRC Trainee.

---
*Báo cáo này là một phần của dự án portfolio cá nhân "banking-security-assessment", thực hiện trên hạ tầng lab ảo hoá cô lập, phục vụ mục đích học tập và minh hoạ năng lực đánh giá bảo mật/GRC.*
