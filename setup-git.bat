@echo off
REM Git Configuration and Repository Setup Script
REM Run this after installing Git for Windows

echo Configuring Git with your credentials...
echo.

REM Configure Git user settings
git config --global user.name "honeybadger2121-home"
git config --global user.email "brs8519@gmail.com"

echo Git configuration completed:
git config --global user.name
git config --global user.email
echo.

echo Initializing Git repository...
git init

echo Adding files to repository...
git add .

echo Creating initial commit...
git commit -m "Initial commit: Aruba AP 500 & 3Com Switch Manager

- Complete network device management solution
- Support for Aruba AP 500 access points  
- Support for 3Com switches
- Web-based dashboard with real-time monitoring
- Device discovery via SNMP
- Configuration backup and restore
- Alert management system
- REST API for programmatic access
- Comprehensive documentation"

echo Adding remote repository...
git remote add origin https://github.com/honeybadger2121-home/networkdevices.git

echo Setting main branch...
git branch -M main

echo Pushing to GitHub...
git push -u origin main

echo.
echo Repository setup complete!
echo Your project is now available at:
echo https://github.com/honeybadger2121-home/networkdevices
echo.
pause