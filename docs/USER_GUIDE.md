# User Guide - Aruba AP 500 & 3Com Switch Manager

## Getting Started

### Accessing the Web Interface

1. Start the application by running:
   ```bash
   cd backend
   python app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

3. The dashboard will load showing your network overview.

## Dashboard Overview

The main dashboard provides a comprehensive view of your network infrastructure:

### Status Cards
- **Online Devices**: Number of reachable devices
- **Offline Devices**: Number of unreachable devices  
- **Active Alerts**: Current system alerts requiring attention
- **Wireless Clients**: Total connected wireless clients across all APs

### Navigation Tabs
- **Devices**: View and manage individual devices
- **Monitoring**: Real-time performance monitoring
- **Alerts**: System alerts and notifications
- **Configuration**: Device configuration management

## Managing Devices

### Viewing Devices

The Devices tab shows all configured network devices with:
- **Device Name**: Friendly name and type
- **Status**: Online/Offline/Error status
- **IP Address**: Network address
- **Device Type**: Aruba AP 500 or 3Com Switch
- **Key Metrics**: Clients (APs) or Ports (Switches)
- **Action Buttons**: Status and Config options

### Device Filtering

Use the filter dropdown to view specific device types:
- **All Devices**: Show all configured devices
- **Aruba AP 500**: Show only access points
- **3Com Switches**: Show only switches
- **Online Only**: Show only reachable devices
- **Offline Only**: Show only unreachable devices

### Device Actions

Each device card provides action buttons:

1. **Status Button**: View detailed device status including:
   - Current operational state
   - Performance metrics
   - Connected clients (APs) or port status (switches)
   - System information

2. **Config Button**: Access device configuration management
   - View current configuration
   - Backup configuration
   - Restore from backup

## Device Discovery

### Automatic Discovery

To discover new devices on your network:

1. Click the **"Discover Devices"** button in the header
2. Enter the network range to scan (e.g., 192.168.1.0/24)
3. Click **"Start Discovery"**
4. Wait for the scan to complete
5. Review discovered devices
6. New devices will be automatically added to your device list

### Supported Discovery Methods
- **Network Ping**: Tests basic connectivity
- **SNMP Detection**: Identifies device types via SNMP
- **Port Scanning**: Tests common management ports (SSH, HTTP, HTTPS)

## Monitoring and Performance

### Real-time Monitoring

The Monitoring tab provides:

#### Performance Charts
- **CPU Usage**: Average CPU utilization across devices
- **Memory Usage**: Average memory utilization
- Real-time updates every 30 seconds

#### Metrics Table
Detailed performance data for each device:
- **Device Name**: Device identifier
- **Type**: Device category (AP/Switch)
- **Status**: Current operational state
- **CPU %**: Processor utilization
- **Memory %**: Memory usage
- **Temperature**: Operating temperature in Celsius
- **Clients/Ports**: Active connections
- **Last Seen**: Last successful communication

### Setting Up Monitoring

Monitoring is automatically enabled for all configured devices. The system:
- Polls devices every 30 seconds
- Stores performance history
- Generates alerts based on thresholds
- Provides trend analysis

## Alert Management

### Understanding Alerts

The Alerts tab displays system notifications with:
- **Severity Levels**: Critical, Warning, Info
- **Device Information**: Which device triggered the alert
- **Alert Message**: Description of the issue
- **Timestamp**: When the alert occurred

### Alert Types

1. **Device Offline**: Device becomes unreachable
2. **High CPU Usage**: CPU utilization above 80%
3. **High Memory Usage**: Memory usage above 85%
4. **High Temperature**: Device temperature above 60°C
5. **Port Down**: Network port becomes unavailable (switches)
6. **Low Client Count**: No wireless clients connected (APs)

### Managing Alerts

- **View All Alerts**: All current and historical alerts
- **Clear All**: Remove all alerts from the display
- **Auto-Resolution**: Alerts automatically resolve when conditions improve

## Configuration Management

### Device Configuration

1. **Select Device**: Choose a device from the dropdown
2. **View Config**: Current configuration displays in JSON format
3. **Backup Config**: Create a backup of current settings
4. **Restore Config**: Restore from a previous backup
5. **Edit Config**: Modify device settings (advanced users)

### Configuration Features

#### Aruba AP 500 Configuration
- **Wireless Settings**: SSID configuration, security settings
- **Radio Settings**: Channel, power, band configuration
- **Network Settings**: VLAN, IP addressing
- **Security Policies**: Access control, authentication

#### 3Com Switch Configuration  
- **Port Settings**: Speed, duplex, VLAN assignments
- **VLAN Configuration**: VLAN creation and management
- **Spanning Tree**: STP/RSTP settings
- **Management**: SNMP, SSH access configuration

### Backup and Restore

#### Creating Backups
1. Select the device to backup
2. Click **"Backup Config"**
3. Backup is saved with timestamp
4. Confirmation message appears

#### Restoring Configurations
1. Select the device to restore
2. Click **"Restore Config"**
3. Choose from available backups
4. Confirm the restore operation

**⚠️ Warning**: Restoring configuration may cause temporary device unavailability.

## Aruba AP 500 Specific Features

### Wireless Management
- **SSID Monitoring**: View all configured wireless networks
- **Client Tracking**: Monitor connected wireless devices
- **RF Performance**: Channel utilization and signal strength
- **Band Management**: 2.4GHz and 5GHz radio settings

### Access Point Health
- **System Resources**: CPU, memory, temperature monitoring
- **Wireless Statistics**: Throughput, error rates, associations
- **Network Connectivity**: Uplink status and performance
- **Firmware Status**: Current version and update availability

## 3Com Switch Specific Features

### Port Management
- **Port Status**: Up/down status for all switch ports
- **Link Statistics**: Speed, duplex, utilization
- **VLAN Assignments**: Port-to-VLAN mappings
- **Port Descriptions**: Custom port labeling

### Switch Health
- **System Performance**: CPU, memory monitoring
- **Environmental**: Temperature and power status
- **Network Topology**: Spanning tree and link aggregation
- **Management Access**: SNMP, SSH connectivity

## Best Practices

### Regular Monitoring
- Check the dashboard daily for device status
- Review alerts regularly
- Monitor performance trends

### Configuration Management
- Create regular configuration backups
- Document configuration changes
- Test changes in maintenance windows

### Security
- Change default passwords
- Use strong SNMP community strings
- Regularly update device firmware
- Monitor for unauthorized access

### Network Planning
- Document device locations
- Maintain inventory of all devices
- Plan for growth and redundancy

## Troubleshooting

### Device Shows as Offline
1. Verify network connectivity to the device
2. Check device power status
3. Verify SNMP community string
4. Check firewall rules

### High CPU/Memory Alerts
1. Check device workload
2. Review connected clients/traffic
3. Consider firmware updates
4. Monitor trends over time

### Configuration Issues
1. Verify credentials are correct
2. Check device management interface status
3. Ensure proper access privileges
4. Review device logs

### Discovery Problems
1. Verify network ranges are correct
2. Check SNMP settings on devices
3. Ensure devices are powered and reachable
4. Review firewall configurations

For additional support, check the installation guide and API documentation.