# DC01 — Active Directory & GPO

**Trạng thái:** ✅ Hoàn thành (05/10/2026)

## Thông tin domain
- Domain: lab.local | NetBIOS: LAB | IP DC01: 10.10.10.10/24 (DNS, Global Catalog)
- VM: Windows Server 2022 Standard Evaluation (Desktop Experience), 2 CPU, 4096MB RAM, 60GB disk, 1 NIC (VMnet2 - LAN)
- Password Administrator (local/domain): tự đặt lúc cài — không ghi ở đây

## OU
- IT
- HR

## User mẫu (chỉ dùng trong lab cô lập, không phải dữ liệu thật)
| OU | User logon | Full name | Password (lab only) |
|---|---|---|---|
| IT | nguyenvana@lab.local | Nguyen Van A | DHNace@ |
| HR | tranthib@lab.local | Tran Thi B | DHNace@ |

> ⚠️ Lưu ý: mật khẩu test này chỉ dùng trong máy ảo lab cô lập (không nối Internet thật ngoài NAT). Không tái sử dụng mật khẩu này cho tài khoản thật.

## GPO — Default Domain Policy
### Password Policy
| Setting | Giá trị |
|---|---|
| Minimum password length | 12 characters |
| Password must meet complexity requirements | Enabled |

### Account Lockout Policy
| Setting | Giá trị |
|---|---|
| Account lockout threshold | 5 invalid logon attempts |
| Account lockout duration | 15 minutes |
| Reset account lockout counter after | 15 minutes |

### Advanced Audit Policy Configuration
| Subcategory | Giá trị |
|---|---|
| Audit Logon (Logon/Logoff) | Success and Failure |
| Audit User Account Management (Account Management) | Success and Failure |

- CIS tham chiếu: Account Lockout Policy, Password Policy, Audit Policy (CIS Microsoft Windows Server 2022 Benchmark)

## Ảnh bằng chứng (screenshots/)
- `dc01-vm-create-summary.png` — tổng kết tạo VM
- `dc01-static-ip-configured.png` — đặt IP tĩnh 10.10.10.10
- `dc01-ipconfig-verified.png` — xác nhận ipconfig /all
- `dc01-promoted-domain-controller.png` — promote domain controller thành công
- `dc01-server-manager-ad-dns.png` — Server Manager hiện AD DS + DNS
- `dc01-ou-it-user-created.png`, `dc01-ou-hr-user-created.png` — OU IT/HR + user mẫu
- `dc01-gpo-password-policy.png` — Password Policy (12 ký tự, complexity)
- `dc01-gpo-account-lockout-policy.png` — Account Lockout Policy (5/15/15)
- `dc01-gpo-audit-logon.png`, `dc01-gpo-audit-account-management.png` — Advanced Audit Policy
