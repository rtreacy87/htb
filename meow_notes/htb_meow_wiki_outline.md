# HTB Meow Lab Wiki Series Outline

## Overview
This outline provides a comprehensive guide for completing the Hack The Box (HTB) Meow lab, designed for beginners entering the world of ethical hacking and penetration testing.

---

## Wiki 1: Initial Setup and Connection

### Objective
Establish connection to HTB network and prepare for the lab

### Topics to Cover
- **HTB Account Setup**
  - Creating HTB account and accessing Starting Point
  - Understanding the Starting Point Tier system
  - Navigating to Tier 0 - Meow machine

- **Connection Methods**
  - **Method A: Using Pwnbox (Recommended for beginners)**
    - Browser-based virtual machine
    - Automatic VPN connection
    - No additional software required
  - **Method B: OpenVPN Configuration**
    - Using local VM (Kali Linux/Parrot Security)
    - Downloading VPN configuration files
    - Manual VPN setup

- **VPN Setup Process**
  - Downloading `.ovpn` configuration file
  - Running `sudo openvpn filename.ovpn` command
  - Verifying successful VPN connection
  - Understanding tunnel interface creation

- **Target Machine Setup**
  - Spawning the Meow machine
  - Obtaining target IP address
  - Understanding lab environment

### Prerequisites
- Basic understanding of Linux terminal
- Virtual machine software (if using Method B)
- HTB account registration

### Expected Outcomes
- Successfully connected to HTB network
- Target machine spawned and accessible
- Ready to begin enumeration phase

---

## Wiki 2: Basic Reconnaissance and Question Answers

### Objective
Answer initial knowledge-based questions and understand fundamental concepts

### Key Questions to Address

#### Question 1: VM Terminology
- **Question**: What does the acronym VM stand for?
- **Answer**: Virtual Machine
- **Concept**: Understanding virtualization technology

#### Question 2: Command Line Interface
- **Question**: What tool do we use to interact with the operating system via command line?
- **Answer**: Terminal (also known as console or shell)
- **Concept**: Command-line interface fundamentals

#### Question 3: VPN Service
- **Question**: What service do we use to form our VPN connection into HTB labs?
- **Answer**: OpenVPN
- **Concept**: Virtual Private Network protocols

#### Question 4: Tunnel Interface
- **Question**: What is the abbreviated name for a 'tunnel interface' in the VPN output?
- **Answer**: tun
- **Concept**: Network tunneling and interface naming

### Skills Learned
- Basic cybersecurity terminology
- Network interface concepts
- VPN technology understanding
- Command-line tool identification

### Practice Exercises
- Research additional VPN protocols
- Explore terminal commands
- Investigate network interface types

---

## Wiki 3: Network Enumeration with Nmap

### Objective
Discover open services and ports on the target machine

### Enumeration Process

#### Step 1: Connectivity Test
```bash
ping [target_IP]
```
- Test network connectivity
- Verify packets reach destination
- Confirm stable connection
- Use Ctrl+C to stop ping

#### Step 2: Port Scanning with Nmap
```bash
nmap [target_IP]
```
- Scan top 1000 common ports
- Identify open services
- Analyze service versions
- Document findings

#### Step 3: Result Analysis
- **Expected Results**:
  - Port 23/tcp open (Telnet)
  - Other ports closed
- **Service Identification**:
  - Telnet protocol analysis
  - Security implications
  - Attack vectors

### Key Concepts
- **Port Scanning Fundamentals**
  - TCP vs UDP protocols
  - Common port numbers
  - Service enumeration techniques

- **Nmap Usage**
  - Basic scanning syntax
  - Output interpretation
  - Advanced scanning options

### Troubleshooting Common Issues
- Connection timeouts
- Firewall blocking
- VPN connectivity problems
- Target machine not responding

### Security Implications
- Why port scanning is important
- Information disclosure risks
- Defense mechanisms

---

## Wiki 4: Service Exploitation - Telnet Attack

### Objective
Connect to and exploit the Telnet service vulnerability

### Attack Methodology

#### Step 1: Understanding Telnet
- **Protocol Overview**:
  - Unencrypted communication
  - Default port 23
  - Legacy remote access protocol
  - Security vulnerabilities

#### Step 2: Connection Attempt
```bash
telnet [target_IP] 23
```
- Establish Telnet connection
- Observe login prompt
- Note system banner information

#### Step 3: Credential Testing
- **Common Default Credentials**:
  - admin/admin
  - root/root
  - user/user
  - admin/password

- **Attack Process**:
  ```
  Meow login: user
  Password: [try common passwords]
  Login incorrect
  
  Meow login: root
  Password: [press Enter - no password]  
  Welcome to Ubuntu 20.04.2 LTS
  ```

#### Step 4: Successful Authentication
- Login with username: `root`
- No password required
- Access granted to system

### Key Security Concepts
- **Default Credential Vulnerability**
  - Why default passwords are dangerous
  - Password policy importance
  - Authentication best practices

- **Telnet Security Issues**
  - Unencrypted transmission
  - Man-in-the-middle attacks
  - Modern alternatives (SSH)

### Ethical Considerations
- Authorized testing only
- Responsible disclosure
- Legal implications
- Professional conduct

---

## Wiki 5: Post-Exploitation and Flag Capture

### Objective
Navigate the compromised system and locate the target flag

### System Exploration

#### Step 1: Initial Reconnaissance
```bash
whoami          # Confirm user privileges
pwd             # Check current directory
ls -la          # List directory contents
```

#### Step 2: Directory Navigation
```bash
ls -la
# Expected output shows:
# - .bash_history
# - .bashrc
# - flag.txt  <-- Target file
# - .profile
# - Other system files
```

#### Step 3: Flag Capture
```bash
cat flag.txt
```
- Read flag contents
- Copy the hash value
- Format: 32-character hash

#### Step 4: Flag Submission
- Navigate to HTB Starting Point page
- Locate flag submission field
- Paste captured flag
- Submit for verification
- Confirm successful completion

### Post-Exploitation Concepts
- **Privilege Escalation**
  - Current user privileges
  - System access levels
  - Potential escalation paths

- **Data Exfiltration**
  - File system exploration
  - Sensitive data identification
  - Information gathering techniques

### Best Practices
- Document all findings
- Maintain detailed logs
- Screenshot important steps
- Verify flag accuracy before submission

---

## Wiki 6: Lessons Learned and Security Concepts

### Objective
Consolidate learning and understand broader security implications

### Key Takeaways

#### Vulnerability Analysis
- **Root Cause**: Default credentials enabled
- **Impact**: Complete system compromise
- **Severity**: Critical
- **CVSS Factors**: High availability, integrity, and confidentiality impact

#### Attack Chain Summary
1. **Reconnaissance**: Network scanning identified open Telnet
2. **Enumeration**: Service version and configuration discovery
3. **Exploitation**: Default credential authentication bypass
4. **Post-Exploitation**: System access and flag capture

#### Security Recommendations
- **Immediate Actions**:
  - Disable unnecessary services
  - Change default credentials
  - Implement strong password policies
  - Enable account lockout mechanisms

- **Long-term Security**:
  - Replace Telnet with SSH
  - Implement network segmentation
  - Deploy monitoring solutions
  - Regular security assessments

### Penetration Testing Methodology
- **Information Gathering**
- **Vulnerability Assessment**
- **Exploitation**
- **Post-Exploitation**
- **Reporting**

### Industry Standards
- **OWASP Top 10** relevance
- **NIST Cybersecurity Framework**
- **Common Vulnerability Scoring System (CVSS)**
- **Penetration Testing Execution Standard (PTES)**

---

## Wiki 7: Clean-up and Next Steps

### Objective
Properly terminate the lab session and plan continued learning

### Lab Termination Process

#### Step 1: System Clean-up
```bash
exit            # Logout from Telnet session
```
- Close Telnet connection
- Clear command history (if required)
- Documen