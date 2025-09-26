# Installation Guide

## Prerequisites

Before installing the Aruba AP 500 & 3Com Switch Manager, ensure you have the following:

### System Requirements
- **Operating System**: Windows 10/11, macOS 10.14+, or Linux
- **Python**: Version 3.7 or higher
- **RAM**: Minimum 2GB, recommended 4GB
- **Disk Space**: At least 500MB free space
- **Network**: Access to managed devices via SNMP/SSH

### Network Requirements
- SNMP enabled on all devices you want to manage
- SSH access configured on devices (for advanced management)
- Network connectivity between the management server and devices
- Firewall rules allowing SNMP (port 161) and SSH (port 22) traffic

## Installation Steps

### Step 1: Clone or Download the Project

```bash
git clone https://github.com/your-repo/aruba-3com-manager.git
cd aruba-3com-manager
```

Or download and extract the ZIP file to your desired location.

### Step 2: Install Python Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

If you encounter permission issues on Windows, try:
```bash
pip install --user -r requirements.txt
```

### Step 3: Configure Your Devices

1. Edit the device configuration file:
   ```bash
   notepad config\devices.json  # Windows
   nano config/devices.json     # Linux/macOS
   ```

2. Update the device information:
   ```json
   {
     "devices": {
       "aruba_ap_1": {
         "name": "Your AP Name",
         "type": "aruba_ap500",
         "ip": "192.168.1.10",
         "snmp_community": "your_snmp_community",
         "ssh_username": "your_username",
         "ssh_password": "your_password",
         "location": "Location Description",
         "enabled": true
       }
     }
   }
   ```

3. Configure network discovery ranges:
   ```json
   {
     "discovery": {
       "networks": ["192.168.1.0/24", "10.0.0.0/24"]
     }
   }
   ```

### Step 4: Test the Installation

1. Start the application:
   ```bash
   cd backend
   python app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

3. You should see the Network Device Manager dashboard.

## Device Configuration

### Aruba AP 500 Setup

To manage Aruba AP 500 access points, ensure the following:

1. **SNMP Configuration**:
   ```
   # Connect to AP via SSH or web interface
   configure
   snmp-server community public
   snmp-server host <manager_ip> public
   ```

2. **SSH Access**:
   - Enable SSH on the access point
   - Create a user account with appropriate privileges
   - Ensure the AP is reachable via SSH on port 22

3. **Required Information**:
   - IP address of the access point
   - SNMP community string (default: public)
   - SSH username and password
   - Location/description (optional)

### 3Com Switch Setup

To manage 3Com switches, configure the following:

1. **SNMP Configuration**:
   ```
   # Via console or Telnet/SSH
   system-view
   snmp-agent community read public
   snmp-agent sys-info version all
   ```

2. **SSH Access** (if supported):
   ```
   ssh server enable
   local-user admin
   password simple admin123
   service-type ssh
   authorization-attribute level 3
   ```

3. **Required Information**:
   - Switch IP address
   - SNMP community string
   - SSH/Telnet credentials
   - Switch model and location

## Network Discovery

The application can automatically discover devices on your network:

1. **Configure Discovery Networks**:
   Edit `config/devices.json` and update the networks array:
   ```json
   "discovery": {
     "networks": ["192.168.1.0/24", "10.0.1.0/24"]
   }
   ```

2. **Run Discovery**:
   - Use the web interface: Click "Discover Devices"
   - Via API: POST to `/api/devices/discover`

3. **Discovery Process**:
   - Scans specified network ranges
   - Tests connectivity on common ports (22, 161, 80, 443)
   - Attempts SNMP identification
   - Adds discovered devices to the management list

## Troubleshooting

### Common Issues

1. **"No module named 'pysnmp'"**:
   ```bash
   pip install pysnmp
   ```

2. **Permission denied when accessing devices**:
   - Verify SNMP community string
   - Check SSH credentials
   - Ensure network connectivity

3. **Web interface not loading**:
   - Check if port 5000 is available
   - Verify Python Flask installation
   - Check firewall settings

4. **Device discovery finds no devices**:
   - Verify network ranges are correct
   - Check if devices have SNMP enabled
   - Ensure devices are powered on and reachable

### Log Files

Check the following log files for detailed error information:
- `backend/network_manager.log` - Application logs
- Console output when running `python app.py`

### Getting Help

If you encounter issues:
1. Check the troubleshooting section above
2. Review log files for error messages
3. Verify network connectivity to devices
4. Ensure all dependencies are installed correctly

## Security Considerations

### Default Passwords
- Change all default passwords on network devices
- Use strong, unique passwords for each device
- Consider using SSH keys instead of passwords

### SNMP Security
- Avoid using default community strings like "public"
- Consider using SNMPv3 with authentication and encryption
- Restrict SNMP access to management networks only

### Network Access
- Run the management server on a secure network
- Use firewall rules to restrict access
- Consider using VPN for remote management

### Configuration Files
- Protect configuration files containing credentials
- Consider encrypting sensitive configuration data
- Regularly backup and secure configuration files