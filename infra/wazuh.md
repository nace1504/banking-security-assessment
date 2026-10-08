# WAZUH01 — SIEM (LAN)

**Trạng thái:** ✅ Hoàn thành (05/10/2026) — snapshot `wazuh01-configured`

## VM
- VMware Workstation, Guest OS: Ubuntu 64-bit
- 2 vCPU, 4096MB RAM, disk 40GB (Split)
- Ubuntu Server 24.04 LTS (guided storage — "Use an entire disk" + LVM)
- 1 NIC: Network Adapter = Custom (VMnet2 Host-only — LAN)

## Interface / IP
- Static qua installer: 10.10.10.20/24
- Gateway: 10.10.10.1 (pfSense LAN)
- DNS: 8.8.8.8
- Dashboard: https://10.10.10.20 (user `admin`)

## Cài đặt Wazuh 4.14.8 (all-in-one)
```bash
curl -sO https://packages.wazuh.com/4.x/wazuh-install.sh
sudo bash ./wazuh-install.sh -a
```
- All-in-one = Wazuh indexer + Wazuh manager + Wazuh dashboard + Filebeat trên cùng 1 node.
- Backend: OpenSearch 2.19.6 (Wazuh indexer dựa trên OpenSearch).

### Sự cố gặp khi cài + cách fix
1. **Dashboard cài lỗi, rollback toàn bộ** (`dpkg returned an error code (1)` khi extract `node_modules`).
   - Nghi ngờ ban đầu: RAM host 16GB chạy 4 VM cùng lúc (Task Manager báo 88%) → tắt bớt WEB01/DC01, chưa hết hẳn.
   - Nguyên nhân thật: **hết dung lượng đĩa** (`No space left on device`, `dpkg-deb: ... Broken pipe`). Ubuntu guided-storage LVM mặc định chỉ cấp ~19GB cho root LV dù đĩa ảo 40GB, phần còn lại nằm "unallocated" trong VG.
   - Fix:
     ```bash
     sudo lvextend -l +100%FREE /dev/mapper/ubuntu--vg-ubuntu--lv
     sudo resize2fs /dev/mapper/ubuntu--vg-ubuntu--lv
     ```
     → root 19GB → 38GB (27GB free).
2. **Cài lại báo "already installed"** vì lần rollback trước bị gián đoạn giữa chừng do hết đĩa → dọn dẹp không hoàn tất.
   - Dùng `-o`/`--overwrite` → lộ thêm lỗi: port 1515/55000 bị chiếm bởi tiến trình cũ (`python3`, `wazuh-authd`) còn sót lại → `sudo kill -9 <pid>`.
   - Gói `wazuh-manager` kẹt ở trạng thái dpkg **purge-incomplete (pi)**, maintainer script `prerm`/`postrm` lỗi vì tham chiếu file/thư mục đã bị xoá (exit code 127/1).
   - Fix: đổi tên để vô hiệu hoá script lỗi, rồi purge bằng cờ ép buộc:
     ```bash
     sudo mv /var/lib/dpkg/info/wazuh-manager.prerm /var/lib/dpkg/info/wazuh-manager.prerm.bak
     sudo mv /var/lib/dpkg/info/wazuh-manager.postrm /var/lib/dpkg/info/wazuh-manager.postrm.bak
     sudo dpkg --purge --force-remove-reinstreq wazuh-manager
     ```
   - Dọn sạch thư mục còn sót (`/var/ossec`, cache apt, `wazuh-install-files.tar`) rồi chạy lại `wazuh-install.sh -a` từ đầu → thành công toàn bộ (indexer + manager + dashboard).

## Đổi mật khẩu admin
- `wazuh-passwords-tool.sh` (trong `wazuh-install-files.tar`) không có trong bản 4.14 → "Not found in archive".
- Đổi qua Dashboard UI ("Reset password for admin") bị từ chối: user `admin` là **reserved** trong OpenSearch Security → `FORBIDDEN: Resource 'admin' is reserved`.
- Cách đúng — sửa trực tiếp qua OpenSearch Security backend:
  ```bash
  export OPENSEARCH_JAVA_HOME=/usr/share/wazuh-indexer/jdk
  /usr/share/wazuh-indexer/plugins/opensearch-security/tools/hash.sh -p '<mật khẩu mới>'
  # copy hash in ra, sửa field "hash:" của block admin trong:
  sudo nano /etc/wazuh-indexer/opensearch-security/internal_users.yml
  # áp dụng cho cluster:
  sudo /usr/share/wazuh-indexer/plugins/opensearch-security/tools/securityadmin.sh \
    -cd /etc/wazuh-indexer/opensearch-security/ \
    -icl -key /etc/wazuh-indexer/certs/admin-key.pem \
    -cert /etc/wazuh-indexer/certs/admin.pem \
    -cacert /etc/wazuh-indexer/certs/root-ca.pem -nhnv
  ```
- Mật khẩu admin: đã đổi thành công qua quy trình trên (xác minh đăng nhập dashboard OK). **Giá trị thật không ghi ở đây** — chỉ dùng trong lab cô lập, không dùng lại cho tài khoản/hệ thống thật.
- **Lưu ý quan trọng**: đổi mật khẩu admin qua `internal_users.yml` KHÔNG tự động cập nhật mật khẩu mà **filebeat** dùng để đẩy log vào indexer. Filebeat lưu credential riêng trong **filebeat keystore** (biến `${username}`/`${password}` trong `/etc/filebeat/filebeat.yml`). Nếu không đồng bộ, filebeat sẽ lỗi `401 Unauthorized` khi gửi log → alert bị mất hoàn toàn mà không có cảnh báo rõ ràng (phát hiện khi làm Kịch bản 1 ATO, xem `grc/reports/incident-01-ato.md`). Fix:
  ```bash
  echo "admin" | sudo filebeat keystore add username --stdin --force
  echo "<mật khẩu admin mới>" | sudo filebeat keystore add password --stdin --force
  sudo systemctl restart filebeat
  ```

## Agent: DC01 (Windows, LAN)
- Deploy qua Dashboard → **Agents management → Deploy new agent** → Windows → MSI.
- Server address: `10.10.10.20`, Agent name: `DC01`.
```powershell
Invoke-WebRequest -Uri https://packages.wazuh.com/4.x/windows/wazuh-agent-4.14.8-1.msi -OutFile $env:tmp\wazuh-agent.msi
msiexec.exe /i $env:tmp\wazuh-agent.msi /q WAZUH_MANAGER='10.10.10.20' WAZUH_AGENT_NAME='DC01'
NET START Wazuh
```
- Sự cố: `Invoke-WebRequest` báo lỗi DNS ("remote name could not be resolved: packages.wazuh.com"). Cô lập từng lớp:
  - Ping 8.8.8.8 / 10.10.10.1 OK (ICMP thông).
  - `nslookup` (cả qua DNS nội bộ lẫn trực tiếp 8.8.8.8) timeout.
  - `Test-NetConnection -Port 443` tới 1.1.1.1/8.8.8.8 đều `TcpTestSucceeded: False`.
  - → chỉ ICMP đi qua được, TCP/UDP bị chặn hoàn toàn ở tầng dưới DC01.
  - Loại trừ lần lượt: Windows Firewall trên DC01 (tắt hẳn vẫn lỗi), firewall rule LAN trên pfSense (đang allow-any), NAT Outbound pfSense (Automatic, đúng subnet). Test trực tiếp từ pfSense (**Diagnostics → Test Port** tới 1.1.1.1:443) cũng fail dù **Status → Gateways** báo WAN Online 0% loss.
  - **Nguyên nhân thật: VMware NAT Service trên máy host (Windows) bị "kẹt"** sau nhiều lần tắt/bật VM liên tục trong lúc debug — ICMP vẫn qua nhưng NAT connection-tracking cho TCP/UDP bị hỏng. Fix: restart **VMware NAT Service** qua `services.msc` trên máy host → `Test-NetConnection` TCP thành công ngay.
  - Cũng thêm forwarder DNS cho AD (`Add-DnsServerForwarder -IPAddress 8.8.8.8,1.1.1.1`) để DC01 tự resolve được tên miền ngoài (cần thiết vì DC01 là DNS server thẩm quyền cho `lab.local`).
- Kết quả: agent DC01 **Active**, IP 10.10.10.10, OS Windows Server 2022 Standard Evaluation.
- Snapshot lại DC01 sau khi cài agent: `dc01-with-wazuh-agent` (snapshot cũ `dc01-configured` không có agent).

## Agent: WEB01 (Ubuntu, DMZ)
- Deploy qua Dashboard → Deploy new agent → Linux → DEB amd64.
- Server address: `10.10.10.20`, Agent name: `WEB01`.
```bash
wget https://packages.wazuh.com/4.x/apt/pool/main/w/wazuh-agent/wazuh-agent_4.14.8-1_amd64.deb
sudo WAZUH_MANAGER='10.10.10.20' WAZUH_AGENT_NAME='WEB01' dpkg -i ./wazuh-agent_4.14.8-1_amd64.deb
sudo systemctl daemon-reload
sudo systemctl enable wazuh-agent
sudo systemctl start wazuh-agent
```
- Không cần mở thêm rule firewall: pfSense đã có sẵn rule DMZ→LAN cho phép WEB01 gửi log tới Wazuh (port 1514–1515), xem `infra/pfsense.md`.
- Cài đặt + start chạy trơn tru ngay lần đầu, không gặp lỗi mạng như DC01 (VMware NAT Service trên host đã được restart trước đó, nên ảnh hưởng không còn).
- Kết quả: agent WEB01 **Active**, IP 10.10.20.10, OS Ubuntu 24.04.4 LTS.
- Snapshot lại WEB01 sau khi cài agent: `web01-with-wazuh-agent` (snapshot cũ `web01-configured` không có agent).

## Bài học rút ra (áp dụng cho các VM sau)
- Luôn kiểm tra dung lượng đĩa thật (`df -h`) trước khi cài phần mềm nặng — installer LVM guided của Ubuntu không tự dùng hết dung lượng đĩa ảo.
- Khi 1 VM đột nhiên mất kết nối TCP/UDP ra ngoài nhưng ICMP vẫn thông, và đã loại trừ hết firewall/NAT trong lab (pfSense + guest OS) → nghi ngờ **VMware NAT Service** trên host bị kẹt, đặc biệt sau nhiều lần bật/tắt VM liên tục — restart service đó trước khi đào sâu hơn.
- User `admin` trong OpenSearch Security là reserved — đổi mật khẩu phải qua `hash.sh` + sửa `internal_users.yml` + `securityadmin.sh`, không đổi được qua UI.

## Custom rule
- Vị trí: `/var/ossec/etc/rules/local_rules.xml` trên WAZUH01 (chưa viết rule tuỳ chỉnh — sẽ bổ sung khi làm Kịch bản 1 ATO, xem `rules/` trong repo và `grc/reports/incident-01-ato.md`).

## Ảnh bằng chứng
- `screenshots/wazuh01-ubuntu-installed-login.png`
- `screenshots/wazuh01-install-success.png`
- `screenshots/wazuh01-dashboard-login-success.png`
- `screenshots/wazuh01-agent-dc01-active.png`
- `screenshots/wazuh01-agents-both-active.png`
- `screenshots/wazuh01-snapshot-configured.png`
- `screenshots/dc01-snapshot-with-wazuh-agent.png`
- `screenshots/web01-snapshot-with-wazuh-agent.png`
