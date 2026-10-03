# pfSense (FW01)
- Card: WAN (NAT) / LAN 10.10.10.1/24 / DMZ 10.10.20.1/24
- Rule DMZ: (1) pass DMZ→10.10.10.20:1514-1515 (2) block DMZ→LAN (3) pass DMZ→any
- Port forward: WAN:22→10.10.20.10:22, WAN:80→10.10.20.10:80
- Ảnh: screenshots/pfsense-*.png
