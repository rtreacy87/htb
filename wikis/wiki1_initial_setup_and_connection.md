# Initial Setup and Connection

## Objective
Establish connection to HTB network and prepare for the lab

## Topics to Cover

### HTB Account Setup
- Creating HTB account and accessing Starting Point
- Understanding the Starting Point Tier system
- Navigating to Tier 0 - Meow machine

### Connection Methods

#### Method A: Using Pwnbox (Recommended for beginners)
- Browser-based virtual machine
- Automatic VPN connection
- No additional software required

#### Method B: OpenVPN Configuration
- Using local VM (Kali Linux/Parrot Security)
- Downloading VPN configuration files
- Manual VPN setup

### VPN Setup Process
- Downloading `.ovpn` configuration file
- Running `sudo openvpn filename.ovpn` command
- Verifying successful VPN connection
- Understanding tunnel interface creation

### Target Machine Setup
- Spawning the Meow machine
- Obtaining target IP address
- Understanding lab environment

## Prerequisites
- Basic understanding of Linux terminal
- Virtual machine software (if using Method B)
- HTB account registration

## Expected Outcomes
- Successfully connected to HTB network
- Target machine spawned and accessible
- Ready to begin enumeration phase

## Detailed Instructions

### Creating an HTB Account
1. Navigate to [Hack The Box](https://www.hackthebox.com/) website
2. Click on "Join" or "Sign Up" button
3. Complete the registration process
4. Verify your email address
5. Log in to your new account

### Accessing Starting Point
1. From the HTB dashboard, locate the "Starting Point" section
2. Click on "Starting Point" to access the beginner-friendly labs
3. Review the tier system explanation
4. Navigate to Tier 0 machines
5. Locate the "Meow" machine card

### Connection Setup

#### Using Pwnbox (Method A)
1. From the Meow machine page, click "Start Machine"
2. Wait for the machine to spawn (usually takes 1-2 minutes)
3. Click "Start Pwnbox" to launch the browser-based VM
4. The Pwnbox will automatically connect to the HTB VPN
5. Note the target IP address displayed on the machine information panel

#### Using Local VM (Method B)
1. Ensure you have a penetration testing VM ready (Kali Linux or Parrot Security OS)
2. From the Meow machine page, click "Start Machine"
3. Click on "Connection Pack" to download the OpenVPN configuration
4. Select the appropriate region for your location
5. Download the .ovpn file to your local VM
6. Open a terminal in your VM
7. Navigate to the directory containing the .ovpn file
8. Run the following command:
   ```bash
   sudo openvpn filename.ovpn
   ```
9. Enter your password when prompted
10. Wait for the "Initialization Sequence Completed" message
11. Keep this terminal window open to maintain the VPN connection
12. Note the target IP address displayed on the machine information panel

### Verifying Connection
1. Open a new terminal window
2. Ping the target IP address to verify connectivity:
   ```bash
   ping <target_IP>
   ```
3. You should see successful ping responses
4. Press Ctrl+C to stop the ping
5. If ping is unsuccessful, verify your VPN connection is active

### Understanding the Lab Environment
1. The Meow machine is a Linux-based server
2. It has intentional security vulnerabilities for learning purposes
3. Your goal will be to gain access and find the "flag" file
4. The lab is isolated and safe for ethical hacking practice
5. All actions are logged for educational purposes

Now that you have successfully set up your connection to the HTB network and spawned the Meow machine, you are ready to proceed to the reconnaissance phase.
