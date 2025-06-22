To install Burp Suite Community Edition on Linux:

1. Download the latest Burp Suite Community Edition from the [official PortSwigger website](https://portswigger.net/burp/communitydownload).
2. Make the downloaded file executable:
   ```sh
   chmod +x burpsuite_community_linux_v*.sh
   ```
3. Run the installer:
   ```sh
   ./burpsuite_community_linux_v*.sh
   ```
4. Follow the on-screen installation instructions.

You can then launch Burp Suite from your applications menu or by running:
```sh
burpsuite
```
in your terminal (if added to PATH).

To find where Burp Suite Community Edition is installed, try these steps:

1. **Check Common Directories:**  
   Look in typical install locations, such as:
   - `/opt/BurpSuiteCommunity`
   - `~/BurpSuiteCommunity`
   - `~/burpsuite_community`

2. **Use `find` to Search:**  
   Run this command to search your home directory:
   ```sh
   find ~ -type d -iname '*burp*'
   ```

3. **Check Desktop Entry:**  
   If you launch Burp Suite from your applications menu, check the `.desktop` file:
   ```sh
   grep -iR burp ~/.local/share/applications/
   ```

Once you find the directory containing the `BurpSuiteCommunity` executable, add it to your PATH by editing your `~/.bashrc` or `~/.zshrc`:

```sh
export PATH="$PATH:/path/to/BurpSuiteCommunity"
```

Replace `/path/to/BurpSuiteCommunity` with the actual directory path. Then reload your shell:

```sh
source ~/.bashrc
```
or
```sh
source ~/.zshrc

```
creat an alias for easier access:

```sh
alias burp='java -jar /path/to/BurpSuiteCommunity/BurpSuiteCommunity'
```
here's what each represents:

**Burp Suite Versions/Components:**

1. **BurpSuiteCommunity** - The main executable for Burp Suite Community Edition (free version)
2. **burpsuite_community.jar** - The Java JAR file that contains the actual application
3. **burpbrowser** - Burp's built-in Chromium browser for easier testing workflow

**Supporting Files:**
- **BurpSuiteCommunity.vmoptions** - JVM configuration options (memory settings, etc.)
- **jre/** - Bundled Java Runtime Environment 
- **uninstall** - Uninstaller script
- **'Burp Suite Community Edition.desktop'** - Desktop entry file for GUI launchers

**Burp Suite Editions:**
- **Community Edition** (what you have) - Free version with basic features
- **Professional Edition** - Paid version with advanced scanning, extensions, and automation
- **Enterprise Edition** - For large organizations with collaborative features

For your alias, you can use any of these:
```sh
alias burp='BurpSuiteCommunity'                    # Main executable
alias burp='burpbrowser'                           # Built-in browser
alias burp='java -jar burpsuite_community.jar'    # Direct JAR execution
```

The main executable (`BurpSuiteCommunity`) is usually the best choice for an alias.

Here are the terminal commands to set up Burp Suite and configure Firefox for proxy:

**1. Launch Burp Suite:**
```sh
BurpSuiteCommunity &
```

**2. Configure Firefox Proxy via Command Line:**
```sh
# Launch Firefox with proxy settings
firefox --proxy-type=manual --proxy-http=127.0.0.1:8080 --proxy-https=127.0.0.1:8080 --proxy-ftp=127.0.0.1:8080 &
```
This Firefox command launches the browser with manual proxy configuration. Here's each part explained:

**`firefox`** - The Firefox browser executable

**`--proxy-type=manual`** - Sets the proxy configuration type to manual (as opposed to automatic detection or system settings)

**`--proxy-http=127.0.0.1:8080`** - Routes HTTP traffic through a proxy server running on:
- `127.0.0.1` (localhost/local machine)
- Port `8080`

**`--proxy-https=127.0.0.1:8080`** - Routes HTTPS traffic through the same proxy server (localhost:8080)

**`--proxy-ftp=127.0.0.1:8080`** - Routes FTP traffic through the same proxy server (localhost:8080)

**`&`** - Runs the command in the background, returning control to the terminal immediately
**Alternative - Set Firefox proxy via about:config:**

This setup is commonly used for:
- Web development testing through a local proxy
- Traffic analysis/debugging with tools like Burp Suite or OWASP ZAP
- Security testing or penetration testing scenarios
- Routing traffic through a local development proxy server

All web traffic (HTTP, HTTPS, FTP) will be intercepted and routed through whatever service is running on localhost port 8080.

```sh
# Launch Firefox and navigate to proxy settings
firefox about:preferences#general &
```
This Firefox command opens the browser directly to a specific preferences page. Here's each part explained:

**`firefox`** - The Firefox browser executable

**`about:preferences#general`** - A special Firefox URL that:
- `about:preferences` - Opens Firefox's Settings/Preferences page
- `#general` - Jumps directly to the "General" section within preferences

**`&`** - Runs the command in the background, returning control to the terminal immediately

This is a convenient way to quickly access Firefox's general settings without having to:
1. Launch Firefox normally
2. Navigate to the hamburger menu
3. Click "Settings" 
4. Scroll to find the General section

The `about:` protocol in Firefox provides access to various internal pages. Other common examples include:
- `about:config` - Advanced configuration editor
- `about:addons` - Extensions and themes manager
- `about:downloads` - Download history
- `about:support` - Troubleshooting information

This command is useful for automation scripts or when you need to quickly modify Firefox's general settings like startup behavior, downloads, or language preferences.


**3. For persistent proxy configuration, create a Firefox profile:**
```sh
# Create new Firefox profile with proxy
firefox -CreateProfile "burp-proxy"
firefox -P "burp-proxy" --proxy-type=manual --proxy-http=127.0.0.1:8080 &
```
Here are the details for both commands:

**Command 1:** `firefox -CreateProfile "burp-proxy"`

**`firefox`** - The Firefox browser executable

**`-CreateProfile "burp-proxy"`** - Creates a new Firefox profile named "burp-proxy". Profiles allow you to have separate settings, bookmarks, extensions, history, and configurations. This command only creates the profile but doesn't launch Firefox.

**Command 2:** `firefox -P "burp-proxy" --proxy-type=manual --proxy-http=127.0.0.1:8080 &`

**`firefox`** - The Firefox browser executable

**`-P "burp-proxy"`** - Launches Firefox using the specified profile named "burp-proxy". The `-P` option allows you to specify which profile to use when starting Firefox.

**`--proxy-type=manual`** - Sets the proxy configuration type to manual (rather than automatic detection or system proxy settings)

**`--proxy-http=127.0.0.1:8080`** - Routes HTTP traffic through a proxy server running on:
- `127.0.0.1` (localhost/local machine)  
- Port `8080`

**`&`** - Runs the command in the background, returning control to the terminal immediately

**Missing details:**
- The first command creates the profile but doesn't launch Firefox
- The second command only configures HTTP proxy - HTTPS traffic may not be proxied unless explicitly configured
- For complete proxy coverage, you'd typically also need `--proxy-https=127.0.0.1:8080`
- Profile data is stored in `~/.mozilla/firefox/` directory
- You can list existing profiles with `firefox -ProfileManager`
overall, this setup allows you to easily switch between different Firefox profiles with specific proxy configurations, which is useful for testing web applications or performing security assessments with Burp Suite.

**4. Disable Burp Suite Interception:**
To disable interception in Burp Suite, you can use the following command to set the proxy listener to "off" via the command line. However, this typically requires manual interaction in the GUI:

**Note:** The Burp Suite proxy listener defaults to 127.0.0.1:8080, and you'll need to manually disable interception in the Burp Suite GUI (Proxy tab → Intercept → "Intercept is off").

For a complete automated setup, you'd need to use Burp's REST API or command-line options, but the GUI interaction for disabling interception is typically done manually.

Here's how to access the Burp Suite GUI and disable interception:

**1. Launch Burp Suite GUI:**
```sh
BurpSuiteCommunity
```
or
```sh
java -jar /path/to/burpsuite_community.jar
```

**2. Initial Startup Process:**
- Burp Suite will open with a startup screen
- Choose "Temporary project" (for Community Edition)
- Click "Next"
- Select "Use Burp defaults" for configuration
- Click "Start Burp"

**3. Navigate to Proxy Settings:**
- Once Burp Suite loads, you'll see the main interface
- Click on the **"Proxy"** tab at the top of the window
- You'll see sub-tabs: "Intercept", "HTTP history", "WebSockets history", etc.

**4. Disable Interception:**
- Click on the **"Intercept"** sub-tab
- Look for the button that says **"Intercept is on"**
- Click this button to toggle it to **"Intercept is off"**
- The button color will change (typically from orange/red to gray)

**5. Verify Proxy Listener:**
- Click on the **"Options"** sub-tab within Proxy
- Check that the proxy listener is running on `127.0.0.1:8080`
- The "Running" checkbox should be checked

**Visual Guide:**
```
Burp Suite Interface:
[Target] [Proxy] [Intruder] [Repeater] [Sequencer] [Decoder] [Comparer] [Extender]
            ↓
    [Intercept] [HTTP history] [WebSockets history] [Options]
         ↓
[Intercept is off] ← Click this button to toggle
```

With interception disabled, web traffic will flow through Burp Suite for logging and analysis without being stopped for manual review.

**Comparison of GUI vs Command Line Methods for Burp Suite Proxy Setup**:

## **GUI Method**

**Advantages:**
- **Visual feedback** - Clear interface showing proxy status, intercept toggle, and traffic
- **Complete control** - Access to all Burp Suite features and settings
- **User-friendly** - No need to remember complex commands or API endpoints
- **Real-time monitoring** - Can see HTTP requests/responses as they happen
- **Full feature set** - Access to all tabs (Target, Intruder, Repeater, etc.)
- **Troubleshooting** - Easy to diagnose proxy issues visually

**Disadvantages:**
- **Manual interaction required** - Must click through startup process and toggle settings
- **Not scriptable** - Cannot automate the setup process
- **Resource intensive** - Full GUI consumes more memory and CPU
- **Remote access issues** - Difficult to use on headless servers
- **Slower setup** - Multiple clicks and navigation required

## **Command Line Method**

**Advantages:**
- **Automation friendly** - Can be scripted and integrated into workflows
- **Faster setup** - Single commands to launch with specific configurations
- **Resource efficient** - Less overhead than full GUI
- **Remote compatible** - Works on headless systems via SSH
- **Consistent** - Same setup every time through scripts
- **CI/CD integration** - Can be part of automated testing pipelines

**Disadvantages:**
- **Limited functionality** - Command line options don't cover all features
- **No visual feedback** - Can't easily see if proxy is working correctly
- **Complex syntax** - Need to remember proxy parameters and options
- **Incomplete automation** - As noted in your file: "GUI interaction for disabling interception is typically done manually"
- **Debugging difficulty** - Harder to troubleshoot issues without visual interface
- **Feature limitations** - Cannot access advanced features like Intruder, Repeater, etc.

## **Hybrid Approach (Recommended)**

The notes suggest the most practical approach is:
1. **Use command line** for initial Firefox proxy configuration
2. **Use GUI** for Burp Suite control and monitoring
3. **Script what you can** (browser launch, proxy settings)
4. **Manual GUI steps** for features that require it (intercept toggle, advanced analysis)

This gives you the automation benefits where possible while maintaining full functionality through the GUI.


**comparison table of proxy configuration types:**

| **Aspect**           | **Manual Proxy**                                  | **Automatic Detection (WPAD)**            | **System Settings**                       |
|----------------------|---------------------------------------------------|-------------------------------------------|-------------------------------------------|
| **Configuration**    | Manually specify proxy server IP/port             | Browser auto-discovers proxy via DHCP/DNS | Uses OS-level proxy settings              |
| **Command Example**  | `--proxy-type=manual --proxy-http=127.0.0.1:8080` | `--proxy-type=auto`                       | `--proxy-type=system`                     |
| **Setup Complexity** | Medium - requires knowing proxy details           | Low - automatic discovery                 | Low - inherits from OS                    |
| **Control Level**    | High - precise control over settings              | Low - relies on network configuration     | Medium - controlled via OS settings       |
| **Reliability**      | High - direct configuration                       | Medium - depends on network setup         | High - consistent with system             |
| **Security**         | High - you control the proxy                      | Low - vulnerable to WPAD hijacking        | Medium - depends on system security       |
| **Portability**      | Low - settings tied to specific proxy             | High - works across different networks    | Medium - works where system is configured |

## **When to Use Each:**

### **Manual Proxy (`--proxy-type=manual`)**
**Use when:**
- Security testing with Burp Suite/OWASP ZAP
- Development with local proxy servers
- Penetration testing scenarios
- You need specific proxy configurations
- Working with localhost proxies (127.0.0.1)

**Don't use when:**
- Moving between different networks frequently
- You don't know proxy server details
- Network administrators handle proxy setup

### **Automatic Detection (`--proxy-type=auto`)**
**Use when:**
- Corporate environments with WPAD configured
- Frequently switching between networks
- Network administrators manage proxy settings
- You want zero-configuration setup

**Don't use when:**
- Security-sensitive environments (WPAD vulnerabilities)
- Local development/testing
- Network doesn't support WPAD
- You need specific proxy configurations

### **System Settings (`--proxy-type=system`)**
**Use when:**
- Want browser to match OS proxy configuration
- Centrally managed systems
- Consistent proxy needs across all applications
- Corporate environments with group policies

**Don't use when:**
- Need browser-specific proxy settings
- Testing scenarios requiring different proxies
- OS proxy settings are incorrect/unavailable

For Burp Suite testing, **manual** is preferred because you need precise control over the proxy endpoint (127.0.0.1:8080).

Here are several commands to check what's using 127.0.0.1:8080 on your Linux system:

## **Check Active Network Connections:**

**1. Using `netstat`:**
```sh
netstat -tulpn | grep :8080
```
- Shows all processes listening on port 8080
- `-t` = TCP, `-u` = UDP, `-l` = listening, `-p` = process, `-n` = numerical

**2. Using `ss` (modern replacement for netstat):**
```sh
ss -tulpn | grep :8080
```
- Same functionality as netstat but faster and more detailed

**3. Using `lsof` (list open files):**
```sh
lsof -i :8080
```
- Shows which processes have port 8080 open
- More detailed process information

## **Specific to localhost:**

**4. Check only localhost connections:**
```sh
ss -tulpn | grep 127.0.0.1:8080
```

**5. Check if Burp Suite is running:**
```sh
ps aux | grep -i burp
```

**6. Find Java processes (since Burp Suite is Java-based):**
```sh
ps aux | grep java | grep 8080
```

## **Kill Process Using Port 8080:**

**If you need to free up the port:**
```sh
# Find the process ID (PID)
lsof -ti :8080

# Kill the process
kill $(lsof -ti :8080)

# Force kill if needed
kill -9 $(lsof -ti :8080)
```

## **One-liner to see everything on port 8080:**
```sh
echo "=== netstat ===" && netstat -tulpn | grep :8080 && echo "=== lsof ===" && lsof -i :8080 && echo "=== processes ===" && ps aux | grep -E "(burp|8080)" | grep -v grep
```

Based on your setup, you should see Burp Suite (`BurpSuiteCommunity` or `java`) listening on 127.0.0.1:8080 when it's running properly.

# Find and kill the process
sudo fuser -k 8080/tcp

# Or if you can identify the PID
sudo kill -9 <PID>

# For systemd services (if it's a service)
sudo systemctl stop <service-name>

2. **Browser Configuration:** 
   - Access Chromium settings (three dots menu → Settings)
   - Navigate to Advanced → System
   - Click "Open your computer's proxy settings"
   - Configure manual proxy: HTTP Proxy 127.0.0.1, Port 8080
   - Enable "Use this proxy server for all protocols"
```

Alternatively, if you want to launch Chromium directly with proxy settings from the command line:

```bash
chromium --proxy-server=127.0.0.1:8080
```

This bypasses the need for manual browser configuration and directly connects Chromium to your Burp Suite proxy.

## Finding User IDs in Burp Suite:

### Method 1: Sitemap Analysis
1. **Browse the application** while Burp is running (with intercept off)
2. **Check Burp's Sitemap** (Target tab > Site map)
3. **Look for URLs containing ID parameters** like:
   - `/account.php?id=2233`
   - `/profile.php?id=2233` 
   - `/user.php?id=2233`
   - Any URL with `id=` parameter

### Method 2: HTTP History Analysis
1. **Go to Proxy tab > HTTP History** in Burp
2. **Review all requests** made while browsing
3. **Look for GET/POST requests** with ID parameters
4. **Note any URLs** that reference user IDs

### Method 3: Manual Discovery
1. **After guest login**, look for links like:
   - "My Account"
   - "Profile" 
   - "User Settings"
2. **Check the URL bar** when clicking these links
3. **Note the ID parameter** (likely `id=2233` for guest)

### Method 4: Active Enumeration
1. **Find any URL with an ID parameter**
2. **Send it to Burp Repeater** (right-click > Send to Repeater)
3. **Modify the ID value systematically**:
   - Try `id=1` (often admin)
   - Try `id=0`
   - Try sequential numbers: `id=2`, `id=3`, etc.
4. **Look for different responses** indicating different users
5. **When you find admin user**, note their actual ID (34322)

The key is that somewhere in the application (likely an account/profile page), there will be a URL that reveals your current user ID, which you can then manipulate to discover other users.

Here's how to modify it in Burp Suite to enumerate users:

## Method 1: Using Burp Repeater (Recommended)

1. **Send to Repeater:**
   - Right-click on that request in Site map
   - Select "Send to Repeater"

2. **Go to Repeater tab** and you'll see the full request

3. **Modify the URL parameter:**
   - Look for the line: `GET /cdn-cgi/login/admin.php?content=uploads&orgId=2`
   - Change `orgId=2` to `orgId=1` (or try other numbers)

4. **Click "Send"** to see the response

5. **Look for user information** in the response that reveals different user IDs

## Method 2: Browser URL Bar

1. **Copy the URL:** `http://10.129.242.196/cdn-cgi/login/admin.php?content=uploads&orgId=2`

2. **Modify in browser:** Change `orgId=2` to `orgId=1`:
   ```
   http://10.129.242.196/cdn-cgi/login/admin.php?content=uploads&orgId=1
   ```

3. **Navigate to the modified URL** and see what user information is displayed

## What to Look For:

In the response, look for:
- User names
- User IDs  
- Email addresses
- Role information
- Any data that shows you're viewing a different user's information

The goal is to find an admin user (likely at `orgId=1`) and note their actual user ID (which should be 34322 according to your writeup).

Try starting with `orgId=1` since that's often the admin/first user in many systems.

To install gobuster on Linux, you have several options:

## Method 1: Using Package Manager (Recommended)

### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install gobuster
```

### Arch Linux:
```bash
sudo pacman -S gobuster
```

### CentOS/RHEL/Fedora:
```bash
sudo dnf install gobuster
# or for older versions:
sudo yum install gobuster
```

## Method 2: Using Go (if not in repositories)

```bash
# Install Go first if not installed
sudo apt install golang-go

# Install gobuster via Go
go install github.com/OJ/gobuster/v3@latest

# Add Go bin to PATH if needed
echo 'export PATH=$PATH:$(go env GOPATH)/bin' >> ~/.bashrc
source ~/.bashrc
```

## Method 3: Download Pre-compiled Binary

```bash
# Download latest release
wget https://github.com/OJ/gobuster/releases/download/v3.6.0/gobuster_Linux_x86_64.tar.gz

# Extract
tar -xzf gobuster_Linux_x86_64.tar.gz

# Move to PATH
sudo mv gobuster /usr/local/bin/
```

## Verify Installation:

```bash
gobuster version
```

After installation, you can run the command from your writeup:
```bash
gobuster dir --url http://{TARGET_IP}/ --wordlist /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt -x php
```

**Note:** Make sure you have the wordlist installed too. If `/usr/share/wordlists/dirbuster/` doesn't exist, install it with:
```bash
sudo apt install dirbuster


A **wordlist** in this context is simply a text file containing a list of common directory and file names that web applications typically use. It's used for **directory enumeration** - basically guessing what folders and files might exist on the web server.

## What Does Gobuster Do?

Gobuster takes each word from the wordlist and tries to access it on the target website:

```
http://10.129.242.196/admin       (tries "admin" from wordlist)
http://10.129.242.196/uploads     (tries "uploads" from wordlist)  
http://10.129.242.196/config      (tries "config" from wordlist)
http://10.129.242.196/backup      (tries "backup" from wordlist)
```

## Example Wordlist Content:

A wordlist file looks like this:
```
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
```

## Why Use `-x php`?

The `-x php` flag also tries each word with `.php` extension:
```
http://10.129.242.196/admin.php
http://10.129.242.196/config.php
http://10.129.242.196/login.php
```

## Simple Example:

You can create a basic wordlist right now:

```bash
echo -e "admin\nuploads\nlogin\nconfig\nbackup\ntest" > /tmp/basic-wordlist.txt

gobuster dir --url http://10.129.242.196/ --wordlist /tmp/basic-wordlist.txt -x php
```

## What You're Looking For:

- **Status 200** = Found (directory/file exists)
- **Status 403** = Forbidden (exists but access denied)
- **Status 301/302** = Redirect (exists, redirects somewhere)

The goal is to discover hidden directories like `/uploads` or files like `admin.php` that aren't linked on the main website but exist on the server.

The command `nc -lvnp 1234` sets up a **netcat listener** for receiving a reverse shell connection. Let me break down each flag:

## Command Breakdown:

```bash
nc -lvnp 1234
```

- **`nc`** = netcat (network utility for TCP/UDP connections)
- **`-l`** = **Listen mode** (wait for incoming connections)
- **`-v`** = **Verbose** (show detailed output/connection info)
- **`-n`** = **No DNS resolution** (use IP addresses only, faster)
- **`-p 1234`** = **Port** (listen on port 1234)

## What It Does:

1. **Opens port 1234** on your machine
2. **Waits for incoming connections** from the target
3. **Provides a shell interface** when connection is received
4. **Shows verbose output** about the connection

## Context in HTB Oopsie:

This is typically used for:
- **Receiving reverse shells** after uploading a PHP webshell
- **Getting command execution** on the target system
- **Establishing persistent access** to the compromised machine

## Usage Flow:

1. **Start listener:** `nc -lvnp 1234` (on your attacking machine)
2. **Upload/execute payload** that connects back to your IP:1234
3. **Receive shell** when payload executes on target

## Example Output:
```bash
$ nc -lvnp 1234
listening on [any] 1234 ...
connect to [10.10.14.15] from (UNKNOWN) [10.129.242.196] 45678
$ whoami
www-data
```

This is a crucial step for gaining shell access after exploiting the file upload vulnerability in the Oopsie challenge.

