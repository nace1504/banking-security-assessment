# pfSense (FW01)

**Trạng thái:** ✅ Hoàn thành (04/10/2026) — snapshot `pfsense-configured`

## VM
- VMware Workstation, Guest OS: FreeBSD 64-bit
- 1 vCPU, 2048MB RAM, disk 20GB (ZFS/GPT, Stripe)
- pfSense CE 2.9.0-RELEASE
- 3 NIC: card1=NAT(WAN)=em0, card2=VMnet2 Host-only(LAN)=em1, card3=VMnet3 Host-only(DMZ)=em2

## Interface / IP
- WAN (em0): DHCP (NAT) — ví dụ 192.168.248.136/24
- LAN (em1): 10.10.10.1/24, DHCP range 10.10.10.100–200
- DMZ/OPT1 (em2): 10.10.20.1/24, không bật DHCP server

## Hardening
- Đổi mật khẩu admin webConfigurator (System → User Manager)
- WAN → Reserved Networks: bỏ chặn private/bogon (để lab NAT dùng dải private vẫn vào được)
- OPT1 → đổi Description thành "DMZ"

## Firewall Rules (DMZ tab)
| # | Action | Protocol | Source | Destination | Mô tả |
|---|---|---|---|---|---|
| 1 | Pass | TCP | Any | 10.10.10.20 : 1514-1515 | Allow WEB01 to Wazuh log |
| 2 | Block | Any | Any | 10.10.10.0/24 | Block DMZ to LAN |
| 3 | Pass | Any | Any | Any | Allow DMZ outbound |

Thứ tự rule quan trọng (match từ trên xuống): cho phép gửi log Wazuh trước, chặn DMZ→LAN, rồi mới cho DMZ ra ngoài (WAN/Internet).

## NAT Port Forward
| Interface | Protocol | Dest. port | Redirect IP | Redirect port | Mô tả |
|---|---|---|---|---|---|
| WAN | TCP | 22 (SSH) | 10.10.20.10 | 22 (SSH) | WAN SSH to WEB01 |
| WAN | TCP | 80 (HTTP) | 10.10.20.10 | 80 (HTTP) | WAN HTTP to WEB01 |

(Rule lọc liên kết tự sinh theo NAT, trỏ vào WEB01 trong DMZ — máy này sẽ dựng ở bước tiếp theo.)

## Lưu ý triển khai
- VMnet2 cần bật "Connect a host virtual adapter" trong Virtual Network Editor để máy host truy cập được GUI pfSense (10.10.10.1) khi cấu hình; có thể tắt sau khi xong.
- Ảnh bằng chứng: `screenshots/pfsense-interfaces-assigned.png`, `pfsense-wan-configured.png`, `pfsense-dmz-renamed.png`, `pfsense-dmz-firewall-rules.png`, `pfsense-nat-port-forward.png`
