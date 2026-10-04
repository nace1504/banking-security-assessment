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
