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
