#!/usr/bin/env python3
"""
Git Configuration and Setup Script
Configures Git and pushes project to GitHub
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✓ {description} completed")
        if result.stdout.strip():
            print(result.stdout.strip())
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False

def check_git_installed():
    """Check if Git is installed"""
    try:
        result = subprocess.run(['git', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✓ Git found: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Git is not installed or not in PATH")
        print("\nPlease install Git first:")
        print("1. Download from: https://git-scm.com/download/win")
        print("2. Install with default settings")
        print("3. Restart your command prompt")
        print("4. Run this script again")
        return False

def main():
    """Main setup function"""
    print("Git Configuration and Repository Setup")
    print("=" * 50)
    
    # Check if Git is installed
    if not check_git_installed():
        return 1
    
    # Configure Git user settings
    user_name = "honeybadger2121-home"
    user_email = "brs8519@gmail.com"
    
    print(f"\nConfiguring Git with:")
    print(f"Username: {user_name}")
    print(f"Email: {user_email}")
    
    commands = [
        (f'git config --global user.name "{user_name}"', 
         "Setting Git username"),
        (f'git config --global user.email "{user_email}"', 
         "Setting Git email"),
        ("git config --global user.name", 
         "Verifying username"),
        ("git config --global user.email", 
         "Verifying email"),
        ("git init", 
         "Initializing Git repository"),
        ("git add .", 
         "Adding all files to repository"),
        ('git commit -m "Initial commit: Aruba AP 500 & 3Com Switch Manager\n\n- Complete network device management solution\n- Support for Aruba AP 500 access points\n- Support for 3Com switches\n- Web-based dashboard with real-time monitoring\n- Device discovery via SNMP\n- Configuration backup and restore\n- Alert management system\n- REST API for programmatic access\n- Comprehensive documentation"', 
         "Creating initial commit"),
        ("git remote add origin https://github.com/honeybadger2121-home/networkdevices.git", 
         "Adding remote repository"),
        ("git branch -M main", 
         "Setting main branch"),
        ("git push -u origin main", 
         "Pushing to GitHub")
    ]
    
    # Execute commands
    for command, description in commands:
        if not run_command(command, description):
            print(f"\n✗ Setup failed at: {description}")
            return 1
    
    print("\n" + "=" * 50)
    print("✓ Repository setup completed successfully!")
    print("\nYour project is now available at:")
    print("https://github.com/honeybadger2121-home/networkdevices")
    print("\nNext steps:")
    print("1. Configure your devices in config/devices.json")
    print("2. Install Python dependencies: pip install -r requirements.txt")
    print("3. Start the application: python start.py")
    print("4. Access the web interface: http://localhost:5000")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())