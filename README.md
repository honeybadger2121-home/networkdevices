# Aruba AP 500 & 3Com Switch Manager

A comprehensive network management solution for managing Aruba AP 500 access points and 3Com switches through a unified web interface.

## Features

- **Device Discovery**: Automatic discovery of Aruba AP 500s and 3Com switches on your network
- **Real-time Monitoring**: Live status monitoring, performance metrics, and health checks
- **Configuration Management**: Backup, restore, and push configurations to devices
- **Web Interface**: Clean, responsive web interface for easy management
- **Multi-Protocol Support**: SNMP, SSH, and vendor-specific protocols
- **Alert System**: Notifications for device status changes and issues

## Supported Devices

### Aruba AP 500 Access Points
- Wireless client management
- SSID configuration
- RF performance monitoring
- Firmware management
- Security settings

### 3Com Switches
- Port status and configuration
- VLAN management
- Link monitoring
- Switch configuration backup

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure your devices in `config/devices.json`

3. Start the application:
   ```bash
   python app.py
   ```

4. Open your browser to `http://localhost:5000`

## Project Structure

```
aruba-3com-manager/
├── backend/                 # Python Flask backend
│   ├── modules/            # Device-specific modules
│   ├── app.py              # Main application
│   └── api.py              # REST API endpoints
├── frontend/               # Web interface
│   ├── static/            # CSS, JS, images
│   └── templates/         # HTML templates
├── config/                 # Configuration files
└── docs/                  # Documentation
```

## Requirements

- Python 3.7+
- Network access to managed devices
- SNMP enabled on devices
- SSH access for advanced management

## License

MIT License - see LICENSE file for details