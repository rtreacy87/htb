# Basic Reconnaissance and Question Answers

## Objective
Answer initial knowledge-based questions and understand fundamental concepts

## Key Questions to Address

### Question 1: VM Terminology
- **Question**: What does the acronym VM stand for?
- **Answer**: Virtual Machine
- **Concept**: Understanding virtualization technology

A Virtual Machine (VM) is a software emulation of a physical computer system. It allows you to run an operating system and applications in an isolated environment, separate from your host machine. In the context of penetration testing, VMs are essential as they provide a safe, controlled environment for testing security vulnerabilities without affecting your main system.

### Question 2: Command Line Interface
- **Question**: What tool do we use to interact with the operating system via command line?
- **Answer**: Terminal (also known as console or shell)
- **Concept**: Command-line interface fundamentals

The terminal (also called console or shell) is a text-based interface used to interact with your operating system through commands. Unlike graphical user interfaces (GUIs), terminals allow for precise control and automation through text commands. In cybersecurity, the terminal is an essential tool as many security tools and techniques require command-line operations.

### Question 3: VPN Service
- **Question**: What service do we use to form our VPN connection into HTB labs?
- **Answer**: OpenVPN
- **Concept**: Virtual Private Network protocols

OpenVPN is an open-source VPN protocol that creates secure point-to-point connections. Hack The Box uses OpenVPN to establish a secure connection between your machine and their lab environment. This connection ensures that all traffic between your system and the lab network is encrypted and isolated from the public internet, creating a safe environment for ethical hacking practice.

### Question 4: Network Connectivity Testing
- **Question**: What tool do we use to test our connection to the target with an ICMP echo request?
- **Answer**: Ping 
- **Concept**: Network connectivity verification


### Question 5: Port Scanning
- **Question**: What is the name of the most common tool for finding open ports on a target?
- **Answer**: Nmap
- **Concept**: Network port scanning and service discovery

Nmap (Network Mapper) is an open-source utility for network discovery and security auditing. It's used to scan networks to identify hosts, services, and open ports. In penetration testing, Nmap is an essential reconnaissance tool that helps identify potential entry points into target systems by revealing which ports are open and what services are running on them.
`
When you connect to a VPN using OpenVPN, it creates a virtual network interface called a "tunnel interface" or "tun" for short. This interface handles the encrypted traffic between your machine and the VPN server. In the OpenVPN connection output, you'll see references to "tun0" or similar, indicating that the tunnel interface has been successfully created.

### Question 6: Service Identification
- **Question**: What service do we identify on port 23/tcp during our scans?
- **Answer**: Telnet
- **Concept**: Service enumeration and port identification

### Question 7: Authentication Vulnerability
- **Question**: What service do we identify on port 23/tcp during our scans?
- **Answer**: root
- **Concept**: Default credential vulnerability

### Question 8: Flag Capture
Connect to the Meow machine using Telnet on port 23. Based on the information in the wiki files, here's how to get the root flag:

1. First, connect to the machine via Telnet:
   ```
   telnet <target_IP> 23
   ```

2. At the login prompt, enter `root` as the username:
   ```
   Meow login: root
   ```

3. When prompted for a password, just press Enter (no password required)

4. Once logged in, you'll have root access to the system

5. The flag is located in the root user's home directory. You can view it with:
   ```
   cat flag.txt
   ```

6. The flag will be a 32-character hash (like `b40abdfe23665f766f9c61ecba8a4c19`) which you can submit to complete the challenge

This exploits a critical security vulnerability where the root account has no password set, giving you immediate administrative access to the system.

#### Example Output

```bash
Meow login: root
Welcome to Ubuntu 20.04.2 LTS (GNU/Linux 5.4.0-77-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

  System information as of Mon 26 May 2025 04:03:31 PM UTC

  System load:           0.0
  Usage of /:            41.7% of 7.75GB
  Memory usage:          4%
  Swap usage:            0%
  Processes:             135
  Users logged in:       0
  IPv4 address for eth0: 10.129.106.247
  IPv6 address for eth0: dead:beef::250:56ff:feb0:35d3

 * Super-optimized for small spaces - read how we shrank the memory
   footprint of MicroK8s to make it the smallest full K8s around.

   https://ubuntu.com/blog/microk8s-memory-optimisation

75 updates can be applied immediately.
31 of these updates are standard security updates.
To see these additional updates run: apt list --upgradable


The list of available updates is more than a week old.
To check for new updates run: sudo apt update
Ubuntu comes with ABSOLUTELY NO WARRANTY, to the extent permitted by
applicable law.


Last login: Mon Sep  6 15:15:23 UTC 2021 from 10.10.14.18 on pts/0
root@Meow:~# cat flag.txt
b40abdfe23665f766f9c61ecba8a4c19
```
## Skills Learned
- Basic cybersecurity terminology
- Network interface concepts
- VPN technology understanding
- Command-line tool identification


#### Troubleshooting Common Issues

If you encountered errors like these:
```bash
ztelnet 10.129.106.247 23
Command 'ztelnet' not found, but can be installed with:
sudo apt install zssh

telnet 10.129.106.247 23
Command 'telnet' not found, did you mean:
  command 'telnetd' from deb inetutils-telnetd
  command 'ztelnet' from deb zssh
Try: sudo apt install <deb name>
```


Here's how to resolve them:

1. **Install Telnet client**:
   ```bash
   sudo apt update
   sudo apt install telnet
   ```

2. **Verify installation**:
   ```bash
   which telnet
   ```

3. **Try connecting again**:
   ```bash
   telnet <target_IP> 23
   ```

If you're still having issues:
- Ensure your VPN connection is active
- Verify the target machine is running
- Check if the IP address is correct
- Make sure port 23 is not blocked by any firewall

## Practice Exercises

### Exercise 1: Exploring Virtual Machines
1. Research different types of virtualization (Type 1 vs Type 2 hypervisors)
2. Compare popular VM software (VirtualBox, VMware, Hyper-V)
3. Identify the benefits of using VMs in cybersecurity testing
4. Compare and contrast these virtualization options:
   - GUI-based VMs (VirtualBox, VMware)
   - WSL with Kali Linux
   - Command-line only VMs (like Linux KVM/QEMU headless VMs)

   | Option            | Pros                                                | Cons                                                    |
   |-------------------|-----------------------------------------------------|---------------------------------------------------------|
   | VirtualBox/VMware | Full GUI, easy management, snapshots                | Higher resource usage, slower startup                   |
   | WSL with Kali     | Fast, integrated with Windows, lightweight          | Limited hardware access, potential compatibility issues |
   | Headless VMs      | Minimal resource usage, scriptable, server-friendly | Steeper learning curve, CLI-only interface              |

5. For WSL Kali specifically:
   - Advantages: Quick to start, shares Windows filesystem at `/mnt/c/`, minimal overhead
   - Disadvantages: Network configuration can be tricky for VPNs, some tools may have compatibility issues

### Exercise 2: Terminal Commands Exploration
1. Open a terminal on your system
2. Try the following basic commands:
   ```bash
   pwd         # Print working directory
   ls -la      # List all files with details
   whoami      # Display current username
   ifconfig    # Show network interfaces (or 'ip a' on newer systems)
   ```
3. Research and try 5 additional terminal commands

### Exercise 3: VPN Protocols Comparison
1. Research at least three different VPN protocols (OpenVPN, WireGuard, IPSec)
2. Create a comparison table of their features, security, and performance
3. Explain why OpenVPN is commonly used in penetration testing environments

### Exercise 4: Network Interfaces
1. On your system, run the appropriate command to list network interfaces:
   - Linux/Mac: `ifconfig` or `ip a`
   - Windows: `ipconfig /all`
2. Identify your physical network interfaces
3. If you connect to a VPN, observe the creation of the tun/tap interface
4. Document the differences between physical and virtual network interfaces

## Additional Resources

### Virtual Machines
- [Introduction to Virtualization](https://www.vmware.com/topics/glossary/content/virtualization)
- [VirtualBox Documentation](https://www.virtualbox.org/wiki/Documentation)
- [Kali Linux VM Setup Guide](https://www.kali.org/docs/virtualization/)
- [KVM/QEMU Headless VM Guide](https://www.linux-kvm.org/page/RunningKvm)
- [WSL Kali Linux Setup](https://www.kali.org/docs/wsl/wsl-preparations/)

### Command Line
- [Linux Command Line Basics](https://ubuntu.com/tutorials/command-line-for-beginners)
- [Windows Command Prompt Guide](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/windows-commands)
- [Bash Scripting Tutorial](https://linuxconfig.org/bash-scripting-tutorial-for-beginners)

### VPN Technology
- [OpenVPN Documentation](https://openvpn.net/community-resources/)
- [Understanding VPN Protocols](https://www.vpnmentor.com/blog/vpn-protocols-explained/)
- [Setting Up OpenVPN on Different Platforms](https://openvpn.net/vpn-server-resources/connecting-to-access-server-with-linux/)

### Network Interfaces
- [Understanding Network Interfaces](https://www.redhat.com/sysadmin/linux-network-interface)
- [TUN/TAP Interface Explanation](https://www.kernel.org/doc/Documentation/networking/tuntap.txt)
- [Virtual Networking Concepts](https://docs.vmware.com/en/VMware-vSphere/7.0/com.vmware.vsphere.networking.doc/GUID-35B40B1B-0C13-43B2-BC85-18C9C91BE2D4.html)

Now that you understand these fundamental concepts, you're ready to move on to the next phase: network enumeration with Nmap.
`
