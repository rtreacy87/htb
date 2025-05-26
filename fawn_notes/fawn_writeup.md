# Fawn Box Writeup

Here's a step-by-step guide to solving the Fawn box on Hack The Box:

## Task 1: What does the 3-letter acronym FTP stand for?
FTP stands for File Transfer Protocol.

## Task 2: Which port does the FTP service listen on usually?
FTP typically listens on port 21.

## Task 3: What acronym is used for a secure FTP protocol as an SSH extension?
SFTP (Secure File Transfer Protocol) is the secure alternative to FTP, built as an extension of SSH.

## Task 4: What is the command to test connection to the target?
Use `ping` to send ICMP echo requests:
```bash
ping <target-ip>
```

## Task 5-6: Scanning the target
Run an Nmap scan to identify services and OS:
```bash
nmap -sV <target-ip>
```

```bash
Starting Nmap 7.95 ( https://nmap.org ) at 2025-05-26 11:50 MDT
Nmap scan report for 10.129.251.17
Host is up (0.074s latency).
Not shown: 999 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
Service Info: OS: Unix

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 2.57 seconds
From the scan results:
- FTP version: vsftpd 3.0.3
- OS type: Unix
```
1. **Starting Nmap 7.95**: Shows the Nmap version (7.95) being used, along with the date and time the scan started.

2. **Nmap scan report for 10.129.251.17**: Identifies the target IP address being scanned.

3. **Host is up (0.074s latency)**: Confirms the target is online and responsive, with a response time of 0.074 seconds.

4. **Not shown: 999 closed tcp ports (reset)**: Indicates that 999 ports were scanned but found closed. These closed ports are not displayed in the output to keep it concise.

5. **PORT   STATE SERVICE VERSION**: Column headers for the detailed port information that follows.

6. **21/tcp open  ftp     vsftpd 3.0.3**: The key finding:
   - Port 21 is open
   - It's using TCP protocol
   - The service running is FTP
   - The specific FTP server software is vsftpd version 3.0.3

7. **Service Info: OS: Unix**: Nmap has determined that the target is likely running a Unix-based operating system.

8. **Service detection performed...**: Standard message about reporting incorrect results to Nmap.

9. **Nmap done: 1 IP address (1 host up) scanned in 2.57 seconds**: Summary showing the scan completed in 2.57 seconds, confirming one host was successfully scanned.

This output tells us everything we need for tasks 5 and 6 - the FTP version (vsftpd 3.0.3) and the OS type (Unix). It also confirms that port 21 is open, which is the standard FTP port mentioned in task 2.

## Task 5: FTP version
From the scan results, the FTP version is vsftpd 3.0.3.

## Task 6: OS type
From the scan results, the OS type is Unix.

## Tasks 7-11: Accessing and Retrieving the Flag

### Step 1: Check the FTP help menu
To view available FTP client commands:
```bash
ftp -h
```

### Step 2: Connect to the FTP server
Connect to the target FTP server:
```bash
ftp 10.129.251.17
```

You'll see the connection established:
```
Connected to 10.129.251.17.
220 (vsFTPd 3.0.3)
```
This confirms:
- Connection successful
- Server is running vsFTPd version 3.0.3

### Step 3: Log in anonymously
When prompted for a username:
```
Name (10.129.251.17:ryan): anonymous
```
Enter `anonymous` - this is the standard username for logging in without an account.

For the password prompt:
```
331 Please specify the password.
Password:
```
Simply press Enter (empty password). Anonymous FTP typically doesn't require a password.

### Step 4: Verify successful login
After login, you'll see:
```
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
```
This tells you:
- Code 230 confirms successful authentication
- The server is running UNIX
- Files will transfer in binary mode (exact byte-for-byte copies)

### Step 5: List and download files
List available files:
```bash
ls
```
or
```bash
dir
```

Download the flag file:
```bash
get flag.txt
```

You'll see the transfer progress:
```
local: flag.txt remote: flag.txt
229 Entering Extended Passive Mode (|||15923|)
150 Opening BINARY mode data connection for flag.txt (32 bytes).
100% |*********************************************************|    32      664.89 KiB/s    00:00 ETA
226 Transfer complete.
```
This shows:
- The file transfer is in progress
- The file size is 32 bytes
- Transfer completed successfully (code 226)

### Step 6: Exit and view the flag
Exit the FTP session:
```bash
bye
```

View the flag contents:
```bash
cat flag.txt
```

Submit this flag to complete the challenge.

# FTP Connection Analysis

Let's break down each line of the FTP connection output:

```bash
ftp 10.129.251.17
Connected to 10.129.251.17.
220 (vsFTPd 3.0.3)
Name (10.129.251.17:ryan): anonymous
331 Please specify the password.
Password:
```
1. **`ftp 10.129.251.17`**: Command to connect to the FTP server at IP address 10.129.251.17.

2. **`Connected to 10.129.251.17.`**: Confirmation that a TCP connection has been established with the server.

3. **`220 (vsFTPd 3.0.3)`**: Server response code 220 indicating service is ready for a new user. The server identifies itself as vsFTPd version 3.0.3.

4. **`Name (10.129.251.17:ryan): anonymous`**: Prompt for username, where:
   - 10.129.251.17 is the server address
   - ryan is your local username
   - anonymous is what you entered as the username

5. **`331 Please specify the password.`**: Server response code 331 indicating it requires a password for the anonymous user.

6. **`Password:`**: Prompt for the password.

## Getting Past the Password Prompt

For anonymous FTP access:
1. When you see the password prompt, simply press Enter (empty password)
2. Anonymous FTP typically doesn't require an actual password

After pressing Enter, you should see a response code 230 "Login successful" and gain access to the FTP server. Then you can use commands like `ls` or `dir` to list files, and `get filename` to download files.

If the empty password doesn't work (which would be unusual for anonymous FTP), you could try:
- Your email address (a common convention)
- The word "anonymous"
- The word "guest"
When prompted for username, enter `anonymous` and press Enter for the password (empty password).

You should see response code 230 for "Login successful".

```bash 
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> get flag.txt
local: flag.txt remote: flag.txt
229 Entering Extended Passive Mode (|||15923|)
150 Opening BINARY mode data connection for flag.txt (32 bytes).
100% |****************************************************************************************************************************|    32      664.89 KiB/s    00:00 ETA
226 Transfer complete.
```

Let's break down each line of the FTP session output:


1. **`230 Login successful.`**: Server response code 230 confirming that your login attempt with anonymous credentials was successful. You now have access to the FTP server.

2. **`Remote system type is UNIX.`**: The FTP server is running on a UNIX-based operating system, which affects file naming conventions and path separators.

3. **`Using binary mode to transfer files.`**: The FTP client is set to binary transfer mode (as opposed to ASCII mode), which is appropriate for transferring non-text files or when you want exact byte-for-byte copies.

4. **`ftp> get flag.txt`**: The command you entered to download a file named "flag.txt" from the server to your local machine.

5. **`local: flag.txt remote: flag.txt`**: Confirms the file names for the transfer - the remote file "flag.txt" will be saved as "flag.txt" on your local system.

6. **`229 Entering Extended Passive Mode (|||15923|)`**: Server response code 229 indicating it's using Extended Passive Mode (EPSV) for the data connection, with port 15923 for the transfer.

7. **`150 Opening BINARY mode data connection for flag.txt (32 bytes).`**: Server response code 150 indicating it's opening a data connection for the file transfer. The file size is 32 bytes, and it will be transferred in binary mode.

8. **`100% |*****...*****| 32 664.89 KiB/s 00:00 ETA`**: Progress bar showing:
   - 100% of the file has been transferred
   - Visual representation of progress (the asterisks)
   - 32 bytes transferred
   - Transfer speed of 664.89 KiB/s
   - Estimated Time of Arrival (ETA) of 0 seconds (already complete)

9. **`226 Transfer complete.`**: Server response code 226 confirming that the file transfer has completed successfully.

This output shows a successful anonymous login to the FTP server and the complete download of the flag.txt file, which contains the flag needed to complete the challenge.

Submit the flag to complete the challenge.

