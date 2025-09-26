#!/usr/bin/env python3
"""
Aruba AP 500 & 3Com Switch Manager
Startup Script

This script provides an easy way to start the network device manager
with proper initialization and error handling.
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("ERROR: Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'flask',
        'requests', 
        'pysnmp',
        'paramiko',
        'netmiko',
        'flask_cors',
        'schedule',
        'psutil',
        'jsonschema',
        'pyyaml'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("ERROR: Missing required packages:")
        for pkg in missing_packages:
            print(f"  - {pkg}")
        print("\nPlease install missing packages:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def create_directories():
    """Create necessary directories"""
    directories = [
        'config',
        'logs',
        'backups'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def check_configuration():
    """Check if configuration file exists"""
    config_file = Path('config/devices.json')
    
    if not config_file.exists():
        print("WARNING: Configuration file not found")
        print("Creating default configuration...")
        
        # Import and run the device manager to create default config
        try:
            sys.path.append('backend/modules')
            from device_manager import DeviceManager
            dm = DeviceManager()
            dm.initialize()
            print("✓ Default configuration created")
        except Exception as e:
            print(f"ERROR: Failed to create configuration: {e}")
            return False
    
    return True

def start_application():
    """Start the Flask application"""
    print("Starting Network Device Manager...")
    print("=" * 50)
    
    # Change to backend directory
    backend_dir = Path('backend')
    if not backend_dir.exists():
        print("ERROR: Backend directory not found")
        return False
    
    os.chdir(backend_dir)
    
    try:
        # Start the Flask app
        import app
        print("✓ Application started successfully")
        print()
        print("Web Interface: http://localhost:5000")
        print("API Endpoint:  http://localhost:5000/api")
        print()
        print("Press Ctrl+C to stop the application")
        print("=" * 50)
        
        # Optional: Open browser automatically
        try:
            time.sleep(2)  # Give the server time to start
            webbrowser.open('http://localhost:5000')
        except:
            pass  # Ignore browser opening errors
        
    except KeyboardInterrupt:
        print("\nShutting down...")
        return True
    except Exception as e:
        print(f"ERROR: Failed to start application: {e}")
        return False

def main():
    """Main startup function"""
    print("Aruba AP 500 & 3Com Switch Manager")
    print("Initializing...")
    print()
    
    # Check system requirements
    if not check_python_version():
        return 1
    
    print("✓ Python version compatible")
    
    if not check_dependencies():
        return 1
    
    print("✓ Dependencies installed")
    
    # Create directories
    create_directories()
    print("✓ Directories created")
    
    # Check configuration
    if not check_configuration():
        return 1
    
    print("✓ Configuration ready")
    print()
    
    # Start application
    if start_application():
        return 0
    else:
        return 1

if __name__ == '__main__':
    sys.exit(main())