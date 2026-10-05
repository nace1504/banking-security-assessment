# WEB01 — DVWA (DMZ)

**Trạng thái:** ✅ Hoàn thành (05/10/2026) — snapshot `web01-configured`

## VM
- VMware Workstation, Guest OS: Ubuntu 64-bit
- 2 vCPU, 2048MB RAM, disk 20GB (Split)
- Ubuntu Server 24.04.4 LTS (cài text-mode/subiquity, có OpenSSH server)
- 1 NIC: Network Adapter = Custom (VMnet3 Host-only — DMZ)

## Interface / IP
- ens33: static 10.10.20.10/24
- Gateway: 10.10.20.1 (pfSense DMZ/OPT1)
- DNS: 8.8.8.8 (public DNS — do pfSense chặn DMZ→LAN nên không dùng được DNS nội bộ 10.10.10.10 của DC01)
- Cấu hình qua `/etc/netplan/50-cloud-init.yaml`, sau đó `sudo netplan apply`

## Docker
- Cài theo hướng dẫn chính thức Docker CE (docker.com apt repo): `docker-ce`, `docker-ce-cli`, `containerd.io`, `docker-buildx-plugin`, `docker-compose-plugin`
- Khắc phục lỗi DNS khi pull image (`docker: failed to resolve ... auth.docker.io ... i/o timeout`): tạo `/etc/docker/daemon.json` với `"dns": ["8.8.8.8", "1.1.1.1"]`, sau đó `systemctl restart docker`
- Kiểm tra: `docker run hello-world` chạy thành công

## DVWA Container
```bash
sudo docker run -d --name dvwa -p 80:80 --restart unless-stopped vulnerables/web-dvwa
```
- Image: `vulnerables/web-dvwa` (Apache 2.4.25 + PHP + MySQL, đã tích hợp sẵn)
- Port: map 80:80 (host:container)
- Khởi tạo DB qua `setup.php` → "Create / Reset Database"
- Đăng nhập mặc định: `admin / password`

## Security Level
- Đã set **low** (DVWA Security → Security Level) — dùng để demo tấn công (Kịch bản IDOR/BOLA, v.v.)
- Khi demo khắc phục sẽ chuyển sang **high** — ghi lại trong báo cáo sự cố tương ứng (`grc/reports/`)
- PHPIDS: disabled (mặc định)

## Truy cập
- Trực tiếp trong DMZ: `http://10.10.20.10`
- Qua pfSense NAT (từ mạng ngoài/host): `http://<WAN-IP-pfSense>` (NAT port forward 80 → 10.10.20.10:80, đã cấu hình sẵn trong `infra/pfsense.md`)

## Troubleshooting đã gặp
- Cài Ubuntu: mirror/apt timeout trong lúc cài do DNS trỏ sang DC01 (10.10.10.10) bị pfSense chặn DMZ→LAN — bỏ qua cảnh báo, cài tiếp bình thường (gói cần thiết lấy từ `file:/cdrom`)
- Sau khi đổi DNS sang 8.8.8.8: `ping 8.8.8.8` / `ping 10.10.20.1` báo "Destination Host Unreachable" — nguyên nhân là **FW01 (pfSense) đang tắt máy**, không phải lỗi cấu hình WEB01. Bật lại pfSense → kết nối bình thường (0% packet loss).
- Docker daemon lỗi resolve `auth.docker.io` dù `nslookup`/`apt update` ở host vẫn chạy được — fix bằng cách set DNS cứng cho Docker daemon (`/etc/docker/daemon.json`).

## Ảnh bằng chứng
- `screenshots/web01-vm-create-summary.png`
- `screenshots/web01-ubuntu-installed-login.png`
- `screenshots/web01-docker-hello-world.png`
- `screenshots/web01-dvwa-container-running.png`
- `screenshots/web01-dvwa-login-success.png`
- `screenshots/web01-dvwa-security-low.png`
- `screenshots/web01-snapshot-configured.png`
