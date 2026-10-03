# Lab runbook

Ghi lại từng bước dựng 4 máy (copy lệnh thật vào đây khi làm). Mỗi máy: làm xong → snapshot.

## Chuẩn bị
- VMware Workstation Pro, bật ảo hoá trong BIOS
- ISO: pfSense CE, Windows Server 2022 Eval, Ubuntu Server 24.04

## Mạng ảo
VMnet2 host-only 10.10.10.0/24 (LAN) · VMnet3 10.10.20.0/24 (DMZ) · VMnet8 NAT (WAN)

## Checklist
- [ ] pfSense  - [ ] DC01 (AD + GPO)  - [ ] WEB01  - [ ] Wazuh + 2 agent Active

## Lỗi gặp phải
(điền khi làm)
