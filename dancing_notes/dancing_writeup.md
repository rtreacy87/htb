# Dancing Box Writeup

## Task 1: What does the 3-letter acronym SMB stand for?
SMB stands for Server Message Block.

## Task 2: What port does SMB use to operate at?
SMB typically operates on port 445.

## Task 3: What is the service name for port 445 that came up in our Nmap scan?
The service name for port 445 is microsoft-ds.

## Task 4: What is the 'flag' or 'switch' that we can use with the smbclient utility to 'list' the available shares on Dancing?
The flag to list available shares with smbclient is `-L`.

## Task 5: How many shares are there on Dancing?
Based on the smbclient output, there are 4 shares on Dancing.

## Task 6: What is the name of the share we are able to access in the end with a blank password?
The share that can be accessed with a blank password is "WorkShares".

## Task 7: What is the command we can use within the SMB shell to download the files we find?
The command to download files within the SMB shell is `get`.

## Detailed Walkthrough

### Initial Enumeration
First, let's scan the target with Nmap to identify open ports and services:

```bash
nmap -sV <target-ip>
```
The `-sV` flag in Nmap stands for "service version detection." When you use this flag, Nmap does more than just identify open ports - it attempts to determine:

1. What service is running on each open port
2. The specific version of that service
3. The underlying application name
4. Sometimes even the operating system

For example, instead of just reporting "port 445 is open," with `-sV` Nmap might report "port 445 is running Microsoft SMB version X.Y on Windows Server."

This information is valuable during penetration testing because:
- Specific service versions may have known vulnerabilities
- Version information helps prioritize which services to investigate
- It provides more context for planning your attack strategy

The `-sV` scan works by sending various probes to each open port and analyzing the responses to fingerprint the service.


The scan reveals port 445 is open with the microsoft-ds service running, confirming this is an SMB server.

Having port 445 open with the microsoft-ds service running is a strong indicator that the target is running an SMB server because:

1. Port 445 is the standard port for SMB (Server Message Block) direct over TCP/IP
2. The "microsoft-ds" service name specifically refers to Microsoft Directory Services, which is Microsoft's implementation of SMB

An SMB server is a network file sharing system that allows applications and users on a network to:

1. Access shared files, folders, and printers on remote systems
2. Read, create, and update files on remote systems
3. Communicate between applications across the network

SMB is primarily used in Windows environments for:
- Network file sharing
- Printer sharing
- Remote administration
- Windows domain services

In a security context, SMB servers can be valuable targets because:
- They often contain sensitive organizational data
- Older versions have well-documented vulnerabilities (like EternalBlue)
- Misconfigured shares might allow unauthorized access
- They can provide lateral movement opportunities within networks

The presence of ports 139 (NetBIOS) and 445 (SMB) together is a classic signature of Windows file sharing services, making this target a good candidate for SMB-based enumeration and potential exploitation.

### Listing SMB Shares
To list the available SMB shares on the target:

```bash
smbclient -L <target-ip>
```

This command shows all available shares on the server. We should see 4 shares including:
- ADMIN$
- C$
- IPC$
- WorkShares

### Accessing the Share
We can try to connect to each share. The WorkShares share allows access with a blank password:

```bash
smbclient //<target-ip>/WorkShares
```

When prompted for a password, simply press Enter.

### Finding and Downloading the Flag
Once connected to the SMB share, we can navigate directories and look for the flag:

```
smb: \> ls
smb: \> cd Amy.J
smb: \Amy.J\> ls
smb: \Amy.J\> cd ..
smb: \> cd James.P
smb: \James.P\> ls
```

When we find the flag file, we can download it using the `get` command:

```
smb: \James.P\> get flag.txt
```

```bash
smbclient -L 10.129.213.214
Password for [WORKGROUP\ryan]:

        Sharename       Type      Comment
        ---------       ----      -------
        ADMIN$          Disk      Remote Admin
        C$              Disk      Default share
        IPC$            IPC       Remote IPC
        WorkShares      Disk
Reconnecting with SMB1 for workgroup listing.
do_connect: Connection to 10.129.213.214 failed (Error NT_STATUS_RESOURCE_NAME_NOT_FOUND)
Unable to connect with SMB1 -- no workgroup available
```
Line 1: Command executed - `smbclient -L 10.129.213.214` - This command lists (-L) all available SMB shares on the target IP without connecting to any specific share.

Line 2: Password prompt - The tool asks for authentication credentials for the WORKGROUP domain. Pressing Enter (blank password) is often sufficient for enumeration.

Lines 4-8: Share listing table with three columns:
   - Sharename: The name of the available network share
   - Type: The type of resource (Disk = file share, IPC = inter-process communication)
   - Comment: Additional information about the share's purpose

Line 5: ADMIN$ share - Administrative share used for remote management, typically maps to the Windows directory. Requires administrator access.

Line 6: C$ share - Default administrative share that maps to the C: drive. Requires administrator access.

Line 7: IPC$ share - Special share used for inter-process communication and remote administration. Not a regular file share.

Line 8: WorkShares share - A custom share with no comment. This is likely a user-created share and potentially accessible with limited privileges.

Lines 9-11: Additional information about workgroup enumeration:
   - The tool attempted to fall back to SMB1 protocol to list workgroups
   - The connection failed with NT_STATUS_RESOURCE_NAME_NOT_FOUND error
   - No workgroup information is available (this is normal and doesn't affect share access)

#### Key Point

The error message about "Unable to connect with SMB1" is actually not preventing you from accessing the shares. This is a common misunderstanding. Let me explain:

The error message "Connection to 10.129.213.214 failed (Error NT_STATUS_RESOURCE_NAME_NOT_FOUND)" and "Unable to connect with SMB1 -- no workgroup available" only refers to the workgroup listing functionality, not the share access itself.

Here's how to proceed despite seeing these messages:

1. The share listing was successful (you can see ADMIN$, C$, IPC$, and WorkShares)
2. The error only occurs when trying to list workgroups, which is not necessary for accessing shares

To connect to the WorkShares share:

```bash
smbclient //10.129.213.214/WorkShares
```

When prompted for a password, simply press Enter (use a blank password).

If you're still having connection issues, try these troubleshooting steps:

1. Verify your VPN connection is active (if using HTB)
2. Try specifying the SMB version:
   ```bash
   smbclient //10.129.213.214/WorkShares --option='client min protocol=SMB2'
   ```

3. Add username explicitly:
   ```bash
   smbclient //10.129.213.214/WorkShares -U 'guest%'
   ```
   (This uses 'guest' username with empty password)

The key point is that the error message about SMB1 is not preventing you from accessing the WorkShares share, which is what you need to find the flag.


### How to Navigate and Find the Flag:

1. First, connect to the WorkShares share (the only non-administrative share):
   ```bash
   smbclient //10.129.213.214/WorkShares
   ```
   When prompted for a password, press Enter (blank password).

2. Once connected, you'll be in the SMB shell. List the contents:
   ```
   smb: \> ls
   ```
   This will show directories and files in the root of the share.

3. Navigate through directories using `cd`:
   ```
   smb: \> cd DirectoryName
   ```

4. Move back up a directory:
   ```
   smb: \> cd ..
   ```

5. When you find the flag.txt file, download it:
   ```
   smb: \> get flag.txt
   ```
   This saves the file to your local machine.

6. Exit the SMB shell:
   ```
   smb: \> exit
   ```

7. View the downloaded flag:
   ```bash
   cat flag.txt


Exit the SMB shell:

```
smb: \James.P\> exit
```

View the flag:

```bash
cat flag.txt
```

Submit this flag to complete the challenge.


## Detailed Explination of Output

### Nmap Output Analysis

```bash
nmap -sV 10.129.213.214
Starting Nmap 7.95 ( https://nmap.org ) at 2025-05-26 13:27 MDT
Nmap scan report for 10.129.213.214
Host is up (0.072s latency).
Not shown: 996 closed tcp ports (reset)
PORT     STATE SERVICE       VERSION
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
445/tcp  open  microsoft-ds?
5985/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 14.00 seconds
```

Line 1: Command executed - `nmap -sV 10.129.213.214` - Running Nmap with service version detection (-sV flag) against the target IP address.

Line 2: Nmap version and timestamp - Shows Nmap version 7.95 and the exact date and time when the scan was initiated.

Line 3: Target identification - Confirms the scan is reporting results for the specified target IP address.

Line 4: Host status - Indicates the target is responsive with a latency of 0.072 seconds, meaning packets take about 72ms to reach the target and return.

Line 5: Port summary - Indicates that 996 out of 1000 commonly scanned TCP ports are closed and actively rejected connections (reset).

Line 6: Table header - Column labels for the detailed port information that follows:
   - PORT: Port number and protocol
   - STATE: Whether the port is open, closed, or filtered
   - SERVICE: The identified service running on the port
   - VERSION: The specific version of the service detected

Line 7: Port 135 details:
   - PORT: 135/tcp - TCP port 135
   - STATE: open - The port is accepting connections
   - SERVICE: msrpc - Microsoft Remote Procedure Call service
   - VERSION: Microsoft Windows RPC - Specific implementation identified

Line 8: Port 139 details:
   - PORT: 139/tcp - TCP port 139
   - STATE: open - The port is accepting connections
   - SERVICE: netbios-ssn - NetBIOS Session Service
   - VERSION: Microsoft Windows netbios-ssn - Windows implementation of NetBIOS

Line 9: Port 445 details:
   - PORT: 445/tcp - TCP port 445
   - STATE: open - The port is accepting connections
   - SERVICE: microsoft-ds - Microsoft Directory Services
   - VERSION: ? - Version could not be determined (question mark indicates uncertainty)

Line 10: Port 5985 details:
   - PORT: 5985/tcp - TCP port 5985
   - STATE: open - The port is accepting connections
   - SERVICE: http - HTTP service
   - VERSION: Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP) - Microsoft HTTP API web server version 2.0 with SSDP/UPnP capabilities

Line 11: Operating system information - Nmap has determined the target is running Windows based on service fingerprinting, with the Common Platform Enumeration (CPE) identifier for Microsoft Windows.

Line 13: Standard footer message - Encourages users to report any incorrect results to improve Nmap's accuracy.

Line 14: Scan completion summary - Confirms the scan finished successfully, scanned 1 host that was responsive, and took 14 seconds to complete.

