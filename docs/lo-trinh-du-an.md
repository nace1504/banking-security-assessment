# Lộ trình dự án (tóm tắt)

Bản đầy đủ: file PDF "Lộ trình dự án – Bảo mật kênh Mobile Banking" (giữ ngoài repo).

## Phạm vi
2 kịch bản, chỉ kênh Mobile/Internet Banking của "Ngân hàng X" giả lập: xác thực (ATO) và phân quyền (IDOR/BOLA).

## 7 tầng cho mỗi kịch bản
1. Mô hình đe doạ  2. Mô phỏng trong lab  3. Hardening (CIS)  4. Phát hiện (rule Wazuh)
5. Ứng cứu (NIST)  6. Quản trị (ISO 27001 + TT09)  7. Khuyến nghị

## Lab (4 máy)
pfSense (biên, LAN/DMZ) · DC01 (AD, định danh) · WEB01 (ứng dụng mô phỏng, DMZ) · Wazuh (SIEM)

## Công cụ
VMware, pfSense, Windows AD/GPO, Docker, Wazuh, SQL, Python, Jira, Power BI, Git

## Sản phẩm
Sổ rủi ro, gap assessment, map TT09, 2 báo cáo sự cố, 2 rule, 2 policy, dashboard, script Python, báo cáo tổng, README.

## Lịch
- 3–5/10: dựng lab + Kịch bản 1
- 6–12/10: Kịch bản 2, báo cáo tổng, README, đẩy GitHub
