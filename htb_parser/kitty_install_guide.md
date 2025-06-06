# Kitty Terminal Installation Guide for Ubuntu

## Installation Methods

### Method 1: Official Installer (Recommended)
```bash
curl -L https://sw.kovidgoyal.net/kitty/installer.sh | sh /dev/stdin
```

### Method 2: System Package
```bash
sudo apt update
sudo apt install kitty
```

### Method 3: Snap Package
```bash
sudo snap install kitty
```

## Post-Installation Setup (for Official Installer)

### 1. Find Kitty Installation Location
```bash
find ~ -name "kitty" -type f 2>/dev/null
```

Typically installs to: `~/.local/kitty.app/bin/kitty`

### 2. Set as Default Terminal
```bash
sudo update-alternatives --install /usr/bin/x-terminal-emulator x-terminal-emulator ~/.local/kitty.app/bin/kitty 50
sudo update-alternatives --config x-terminal-emulator
```

### 3. Add to PATH
Add this line to your `~/.bashrc`:
```bash
export PATH="$HOME/.local/kitty.app/bin:$PATH"
```

Then reload your shell:
```bash
source ~/.bashrc
```

### 4. Create Desktop Entry (Optional)
```bash
mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/kitty.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=kitty
GenericName=Terminal emulator
Comment=Fast, feature-rich, cross-platform, GPU-based terminal
TryExec=kitty
Exec=kitty
Icon=kitty
StartupNotify=true
StartupWMClass=kitty
Categories=System;TerminalEmulator;
Keywords=console;terminal;shell;
EOF

# Update to use full path
sed -i "s|Exec=kitty|Exec=$HOME/.local/kitty.app/bin/kitty|" ~/.local/share/applications/kitty.desktop
sed -i "s|TryExec=kitty|TryExec=$HOME/.local/kitty.app/bin/kitty|" ~/.local/share/applications/kitty.desktop

# Update desktop database
update-desktop-database ~/.local/share/applications/
```

### 5. Verify Installation
```bash
kitty --version
```

## Configuration

- Configuration file location: `~/.config/kitty/kitty.conf`
- Launch Kitty with: `kitty` command or from applications menu

## Troubleshooting

If the official installer doesn't work as expected, use the system package method:
```bash
sudo apt update
sudo apt install kitty
```

This installs to `/usr/bin/kitty` and integrates automatically with the system.

## Notes

- The official installer creates a self-contained `.app` directory with all dependencies
- System packages may have older versions but integrate better with the system
- Kitty supports extensive customization through its configuration file