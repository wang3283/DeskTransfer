#!/usr/bin/env python3
"""
DeskTransfer Cross-Platform Build Script
Automated building of standalone desktop executables
Supports Windows, macOS, Linux
"""
import os
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path
from datetime import datetime

class DeskTransferBuilder:
    def __init__(self):
        self.root_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.dist_dir = self.root_dir / 'dist'
        self.build_dir = self.root_dir / 'build'
        self.output_dir = self.dist_dir / 'DeskTransfer'
        self.version = "1.0.0"

        # Detect platform
        import platform
        self.platform = platform.system().lower()
        self.arch = platform.machine().lower()

        # Set platform-specific file extensions
        if self.platform == 'windows':
            self.exe_suffix = '.exe'
            self.script_suffix = '.bat'
        else:
            self.exe_suffix = ''
            self.script_suffix = '.sh'

    def log(self, message, level="INFO"):
        """Print log message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

    def check_python(self):
        """Check Python environment"""
        self.log("Checking Python environment...")
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 6):
            self.log("Python 3.6 or higher is required!", "ERROR")
            return False
        self.log(f"Python version: {sys.version.split()[0]}")
        return True

    def install_dependencies(self):
        """Install build dependencies"""
        self.log("Installing build dependencies...")
        try:
            # Upgrade pip
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Install PyInstaller
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Install project dependencies
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            self.log("Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"Failed to install dependencies: {e}", "ERROR")
            return False

    def clean_build(self):
        """Clean previous build files"""
        self.log("Cleaning old build files...")
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
        self.log("Cleanup completed")

    def build_executables(self):
        """Build executable files"""
        self.log("Starting executable build...")

        # Build sender
        if not self._build_single_executable('sender.py', 'DeskTransfer-Sender'):
            return False

        # Build receiver
        if not self._build_single_executable('receiver.py', 'DeskTransfer-Receiver'):
            return False

        self.log("Executable build completed successfully")
        return True

    def _build_single_executable(self, script_file, exe_name):
        """Build single executable"""
        try:
            cmd = [
                sys.executable, '-m', 'PyInstaller',
                '--clean',
                '--noconfirm',
                '--onedir',
                '--name', exe_name,
                '--hidden-import', 'tkinterdnd2',
                '--hidden-import', 'tkinterdnd2.tkdnd',
                '--hidden-import', 'PIL',
                '--hidden-import', 'PIL._tkinter_finder',
                '--hidden-import', 'PIL.Image',
                '--hidden-import', 'PIL.ImageTk',
                '--hidden-import', 'psutil',
                '--hidden-import', 'socket',
                '--hidden-import', 'struct',
                '--hidden-import', 'threading',
                '--hidden-import', 'json',
                '--hidden-import', 'os',
                '--hidden-import', 'sys',
                '--hidden-import', 'time',
                '--hidden-import', 'datetime',
                '--hidden-import', 'hashlib',
                '--hidden-import', 'platform',
                '--hidden-import', 'subprocess',
                '--add-data', f'{self.root_dir}/data:data',
                '--exclude-module', 'matplotlib',
                '--exclude-module', 'numpy',
                '--exclude-module', 'scipy',
                '--exclude-module', 'pandas',
                '--exclude-module', 'pytest',
                '--exclude-module', 'setuptools',
                '--exclude-module', 'unittest',
                '--exclude-module', 'doctest',
                '--exclude-module', 'pydoc',
                '--noupx',
                '--noconsole',
                script_file
            ]

            # Add platform-specific options
            if self.platform == 'windows':
                if (self.root_dir / 'assets' / 'icon.ico').exists():
                    cmd.extend(['--icon', str(self.root_dir / 'assets' / 'icon.ico')])

            subprocess.check_call(cmd, cwd=str(self.root_dir))
            return True

        except subprocess.CalledProcessError as e:
            self.log(f"Failed to build {exe_name}: {e}", "ERROR")
            return False

    def create_distribution_package(self):
        """Create distribution package"""
        self.log("Creating distribution package...")

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Check new format output (COLLECT mode)
        sender_dir = self.dist_dir / 'DeskTransfer-Sender'
        receiver_dir = self.dist_dir / 'DeskTransfer-Receiver'

        # Copy sender files
        if sender_dir.exists():
            self.log("Copying sender files...")
            for item in sender_dir.iterdir():
                if item.is_file():
                    shutil.copy2(item, self.output_dir)
                    if item.suffix == '.exe':
                        self.log(f"Copied: {item.name}")
                elif item.is_dir():
                    shutil.copytree(item, self.output_dir / item.name, dirs_exist_ok=True)
        else:
            # Compatible with old format (single exe)
            sender_exe = self.dist_dir / 'DeskTransfer-Sender.exe'
            if sender_exe.exists():
                shutil.copy(sender_exe, self.output_dir)
                self.log(f"Copied: {sender_exe.name}")
            else:
                self.log("Warning: Sender executable not found", "WARNING")

        # Copy receiver files
        if receiver_dir.exists():
            self.log("Copying receiver files...")
            for item in receiver_dir.iterdir():
                if item.is_file():
                    dest_file = self.output_dir / item.name
                    if not dest_file.exists():  # Avoid overwriting
                        shutil.copy2(item, self.output_dir)
                    if item.suffix == '.exe':
                        self.log(f"Copied: {item.name}")
                elif item.is_dir():
                    shutil.copytree(item, self.output_dir / item.name, dirs_exist_ok=True)
        else:
            # Compatible with old format (single exe)
            receiver_exe = self.dist_dir / 'DeskTransfer-Receiver.exe'
            if receiver_exe.exists():
                shutil.copy(receiver_exe, self.output_dir)
                self.log(f"Copied: {receiver_exe.name}")
            else:
                self.log("Warning: Receiver executable not found", "WARNING")

        # Create data directory
        data_dir = self.output_dir / 'data'
        data_dir.mkdir(exist_ok=True)
        (data_dir / 'received').mkdir(exist_ok=True)
        (data_dir / 'temp').mkdir(exist_ok=True)

        # Create start script
        self.create_start_script()

        # Create README file
        self.create_readme()

        # Copy documentation
        self.copy_documentation()

        self.log("Distribution package created successfully")

    def create_start_script(self):
        """Create start script"""
        if self.platform == 'windows':
            start_content = self._create_windows_start_script()
        else:
            start_content = self._create_unix_start_script()

        start_script_path = self.output_dir / f'start{self.script_suffix}'
        with open(start_script_path, 'w', encoding='utf-8') as f:
            f.write(start_content)
        self.log(f"Created start script: start{self.script_suffix}")

    def _create_windows_start_script(self):
        """Create Windows batch start script"""
        return """@echo off
chcp 65001 >nul
title DeskTransfer - LAN Image Transfer Tool
color 0A

:menu
cls
echo ========================================
echo    DeskTransfer v1.0.0
echo    LAN Image Transfer Tool
echo ========================================
echo.
echo    1. Start Receiver
echo    2. Start Sender
echo    3. Open Received Folder
echo    4. View Instructions
echo    5. Exit
echo.
echo ========================================

set /p choice=Select option (1-5):

if "%choice%"=="1" (
    echo.
    echo Starting Receiver...
    start "" "DeskTransfer-Receiver.exe"
    timeout /t 2 >nul
    goto menu
) else if "%choice%"=="2" (
    echo.
    echo Starting Sender...
    start "" "DeskTransfer-Sender.exe"
    timeout /t 2 >nul
    goto menu
) else if "%choice%"=="3" (
    echo.
    echo Opening received folder...
    if exist "data\\received" (
        explorer "data\\received"
    ) else (
        echo Received folder does not exist, creating...
        mkdir "data\\received"
        explorer "data\\received"
    )
    timeout /t 2 >nul
    goto menu
) else if "%choice%"=="4" (
    if exist "README.txt" (
        notepad "README.txt"
    ) else if exist "Instructions.txt" (
        notepad "Instructions.txt"
    ) else (
        echo Instructions file not found
        pause
    )
    goto menu
) else if "%choice%"=="5" (
    echo.
    echo Thank you for using!
    timeout /t 1 >nul
    exit
) else (
    echo.
    echo Invalid choice, please try again!
    timeout /t 2 >nul
    goto menu
)
"""

    def _create_unix_start_script(self):
        """Create Unix shell start script"""
        return """#!/bin/bash

# DeskTransfer Startup Script
# Supports macOS and Linux

show_menu() {
    clear
    echo "========================================"
    echo "    DeskTransfer v1.0.0"
    echo "    LAN Image Transfer Tool"
    echo "========================================"
    echo ""
    echo "    1. Start Receiver"
    echo "    2. Start Sender"
    echo "    3. Open Received Folder"
    echo "    4. View Instructions"
    echo "    5. Exit"
    echo ""
    echo "========================================"
}

# Create received folder if it doesn't exist
ensure_received_dir() {
    if [ ! -d "data/received" ]; then
        mkdir -p "data/received"
        echo "Received folder created"
    fi
}

# Main menu loop
while true; do
    show_menu
    read -p "Select option (1-5): " choice

    case $choice in
        1)
            echo ""
            echo "Starting Receiver..."
            if [ -f "./DeskTransfer-Receiver" ]; then
                ./DeskTransfer-Receiver &
            else
                echo "Error: Receiver executable not found"
                read -p "Press Enter to continue..."
            fi
            ;;
        2)
            echo ""
            echo "Starting Sender..."
            if [ -f "./DeskTransfer-Sender" ]; then
                ./DeskTransfer-Sender &
            else
                echo "Error: Sender executable not found"
                read -p "Press Enter to continue..."
            fi
            ;;
        3)
            echo ""
            echo "Opening received folder..."
            ensure_received_dir
            if command -v open >/dev/null 2>&1; then
                # macOS
                open "data/received"
            elif command -v xdg-open >/dev/null 2>&1; then
                # Linux
                xdg-open "data/received"
            else
                echo "Cannot open folder automatically, please manually open data/received directory"
                read -p "Press Enter to continue..."
            fi
            ;;
        4)
            if [ -f "README.txt" ]; then
                if command -v open >/dev/null 2>&1; then
                    open "README.txt"
                elif command -v xdg-open >/dev/null 2>&1; then
                    xdg-open "README.txt"
                else
                    cat "README.txt" | less
                fi
            elif [ -f "Instructions.txt" ]; then
                if command -v open >/dev/null 2>&1; then
                    open "Instructions.txt"
                elif command -v xdg-open >/dev/null 2>&1; then
                    xdg-open "Instructions.txt"
                else
                    cat "Instructions.txt" | less
                fi
            else
                echo "Instructions file not found"
                read -p "Press Enter to continue..."
            fi
            ;;
        5)
            echo ""
            echo "Thank you for using!"
            exit 0
            ;;
        *)
            echo ""
            echo "Invalid choice, please try again!"
            read -p "Press Enter to continue..."
            ;;
    esac
done
"""

    def create_readme(self):
        """Create README file"""
        readme_content = """# DeskTransfer - LAN Image Transfer Tool

## Version Info
Version: v1.0.0
Release Date: """ + datetime.now().strftime("%Y-%m-%d") + """

## Quick Start

### Method 1: Using Start Script (Recommended)
1. Double-click `start.bat` to run
2. Select from menu:
   - Choose 1 to start Receiver
   - Choose 2 to start Sender
   - Choose 3 to open received folder
   - Choose 4 to view instructions

### Method 2: Direct Run
1. Double-click `DeskTransfer-Receiver.exe` to start receiver
2. Double-click `DeskTransfer-Sender.exe` to start sender

## Usage Steps

### 1. Start Receiver
- Run receiver program on receiving computer
- Click "Start Server" button
- Record displayed IP address and port (default: 12345)

### 2. Start Sender
- Run sender program on sending computer
- Enter receiver's IP address
- Port remains default (12345) or enter receiver's displayed port

### 3. Transfer Files
- Click "Select Files" in sender, choose images
- Supports multi-select for batch transfer
- Click "Connect" to connect to receiver
- After successful connection, click "Send Files" to start transfer
- Progress bar shows transfer status

### 4. View Received Files
- Received files are stored in `data/received` directory
- Click "Open Received Folder" button in receiver interface
- Or use start script menu option 3

## Features

- ✅ Fast LAN transfer of images
- ✅ Batch file selection and transfer
- ✅ Real-time transfer progress display
- ✅ Support for common image formats (JPG, PNG, GIF, BMP, TIFF, WebP)
- ✅ Simple and intuitive GUI
- ✅ No Python environment required

## System Requirements

- Operating System: Windows 7 or higher
- Network: Sender and receiver must be on same LAN
- Firewall: Allow TCP port 12345 communication

## Important Notes

1. **Network Connection**
   - Ensure both computers are on the same LAN
   - Test network connectivity using ping command

2. **Firewall Settings**
   - Windows Firewall may block connections
   - Allow program through firewall on first run
   - Default uses TCP port 12345

3. **File Paths**
   - Do not move or delete other files in exe directory
   - data directory stores received files

4. **Antivirus Software**
   - Some antivirus software may show false positives
   - Add program to whitelist if this occurs

## Troubleshooting

### Problem: Cannot connect to receiver
Solution:
1. Check both computers are on same LAN
2. Confirm receiver server is started
3. Verify IP address and port are correct
4. Check firewall settings

### Problem: Transfer interrupted
Solution:
1. Check network connection stability
2. Restart programs and try again
3. Ensure no other programs use port 12345

### Problem: Program won't start
Solution:
1. Confirm Windows version (Windows 7 or higher)
2. Run as administrator
3. Install Visual C++ Redistributable

## Technical Support

For issues or suggestions, please contact developer.

## Copyright

Copyright (c) 2024 DeskTransfer
This software is for learning and personal use only.
"""

        readme_path = self.output_dir / 'README.txt'
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        self.log("Created README file")

    def copy_documentation(self):
        """Copy documentation files"""
        docs = ['Instructions.md', 'USAGE.md']
        for doc in docs:
            doc_path = self.root_dir / doc
            if doc_path.exists():
                shutil.copy(doc_path, self.output_dir)
                self.log(f"Copied documentation: {doc}")

    def create_portable_zip(self):
        """Create portable ZIP package"""
        self.log("Creating portable ZIP package...")

        zip_name = f'DeskTransfer_v{self.version}_Portable.zip'
        zip_path = self.dist_dir / zip_name

        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(self.output_dir):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(self.output_dir.parent)
                        zipf.write(file_path, arcname)

            file_size = zip_path.stat().st_size / (1024 * 1024)  # MB
            self.log(f"ZIP package created: {zip_name} ({file_size:.2f} MB)")
            return True
        except Exception as e:
            self.log(f"Failed to create ZIP package: {e}", "ERROR")
            return False

    def create_installer_script(self):
        """Create Inno Setup installer script"""
        self.log("Creating installer script...")

        iss_content = f"""[Setup]
AppName=DeskTransfer
AppVersion={self.version}
AppPublisher=DeskTransfer
DefaultDirName={{autopf}}\\DeskTransfer
DefaultGroupName=DeskTransfer
OutputDir=..\\..
OutputBaseFilename=DeskTransfer_v{self.version}_Setup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={{app}}\\DeskTransfer-Sender.exe
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"

[Files]
Source: "DeskTransfer\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{{group}}\\DeskTransfer - Sender"; Filename: "{{app}}\\DeskTransfer-Sender.exe"
Name: "{{group}}\\DeskTransfer - Receiver"; Filename: "{{app}}\\DeskTransfer-Receiver.exe"
Name: "{{group}}\\Start Menu"; Filename: "{{app}}\\start.bat"
Name: "{{group}}\\Received Folder"; Filename: "{{app}}\\data\\received"
Name: "{{desktopicon}}\\DeskTransfer"; Filename: "{{app}}\\start.bat"; Tasks: desktopicon

[Run]
Filename: "{{app}}\\start.bat"; Description: "{{cm:LaunchProgram,DeskTransfer}}"; Flags: shellexec postinstall skipifsilent
"""

        iss_path = self.output_dir / 'installer.iss'
        with open(iss_path, 'w', encoding='utf-8') as f:
            f.write(iss_content)
        self.log("Installer script created: installer.iss")
        self.log("Note: Use Inno Setup to compile this script into an installer")

    def print_summary(self):
        """Print build summary"""
        print("\n" + "=" * 60)
        print("Build Summary".center(60))
        print("=" * 60)

        print(f"\nDistribution location: {self.output_dir}")
        print("\nIncluded files:")

        sender_name = f"DeskTransfer-Sender{self.exe_suffix}"
        receiver_name = f"DeskTransfer-Receiver{self.exe_suffix}"
        start_name = f"start{self.script_suffix}"

        files = [
            (sender_name, "Sender executable"),
            (receiver_name, "Receiver executable"),
            (start_name, "Start menu script"),
            ("README.txt", "Instructions"),
            ("data/", "Data directory"),
        ]

        for filename, description in files:
            file_path = self.output_dir / filename
            if file_path.exists():
                print(f"  [OK] {filename:<30} - {description}")
            else:
                print(f"  [MISSING] {filename:<30} - {description}")

        # Check ZIP package
        zip_name = f'DeskTransfer_v{self.version}_Portable.zip'
        zip_path = self.dist_dir / zip_name
        if zip_path.exists():
            file_size = zip_path.stat().st_size / (1024 * 1024)
            print(f"\nPortable ZIP: {zip_name} ({file_size:.2f} MB)")

        print("\n" + "=" * 60)
        print("\nNext steps:")
        print("  1. Test executables run properly")
        if self.platform == "windows":
            print("  2. Copy entire DeskTransfer directory to other Windows computers")
            print(f"  3. Or use portable ZIP package: {zip_name}")
            print("  4. Use Inno Setup to compile installer.iss into installer")
        else:
            platform_name = "macOS" if self.platform == "darwin" else self.platform.title()
            print(f"  2. Copy entire DeskTransfer directory to other {platform_name} computers")
            print(f"  3. Or use portable ZIP package: {zip_name}")
            print("  4. Rebuild on other platforms to get corresponding versions")
        print("=" * 60 + "\n")

    def build(self):
        """Execute complete build process"""
        print("\n" + "=" * 60)
        platform_name = "Windows" if self.platform == "windows" else ("macOS" if self.platform == "darwin" else self.platform.title())
        print(f"DeskTransfer {platform_name} Build Tool".center(60))
        print("=" * 60 + "\n")

        # Check Python environment
        if not self.check_python():
            return 1

        # Install dependencies
        if not self.install_dependencies():
            return 1

        # Clean old files
        self.clean_build()

        # Build executables
        if not self.build_executables():
            return 1

        # Create distribution package
        self.create_distribution_package()

        # Create ZIP package
        self.create_portable_zip()

        # Create installer script
        self.create_installer_script()

        # Print summary
        self.print_summary()

        return 0

def main():
    """Main function"""
    builder = DeskTransferBuilder()
    return builder.build()

if __name__ == "__main__":
    sys.exit(main())
