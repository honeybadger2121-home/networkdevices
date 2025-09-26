# Production Deployment Guide

## Overview
This guide covers deploying the Network Device Management System in a production environment.

## Prerequisites
- Python 3.7 or higher
- SSL certificates for HTTPS
- Access to network devices (Aruba AP 500s and 3Com switch)
- Email server for alerts (optional)

## Configuration

### 1. Production Configuration
The system uses `config/production.json` for production settings:

```bash
cp config/production.json config/active_config.json
```

### 2. SSL Certificate Setup
```bash
# Create SSL certificate directory
mkdir -p /etc/ssl/certs /etc/ssl/private

# Copy your SSL certificates
cp your-server.crt /etc/ssl/certs/server.crt
cp your-server.key /etc/ssl/private/server.key

# Set proper permissions
chmod 644 /etc/ssl/certs/server.crt
chmod 600 /etc/ssl/private/server.key
```

### 3. Database Setup
```bash
# Create data directory
mkdir -p data logs

# Initialize database
python -c "from backend.app import init_database; init_database()"
```

## Deployment Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Device Settings
Edit `config/devices.json` with your actual device information:
```json
{
    "aruba_ap_1": {
        "type": "aruba_ap500",
        "ip": "192.168.1.10",
        "community": "your-snmp-community"
    },
    "aruba_ap_2": {
        "type": "aruba_ap500", 
        "ip": "192.168.1.11",
        "community": "your-snmp-community"
    },
    "switch_3com": {
        "type": "3com_switch",
        "ip": "192.168.1.1",
        "community": "your-snmp-community"
    }
}
```

### 3. Start the Application
```bash
# Production mode
python start.py --config production

# Or with systemd service
sudo systemctl start network-manager
```

## Security Considerations

### Firewall Configuration
```bash
# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 5000/tcp
```

### SNMP Security
- Use SNMPv3 when possible
- Configure read-only community strings
- Restrict SNMP access by IP

## Monitoring and Alerts

### Log Files
- Application logs: `logs/production.log`
- Error logs: `logs/error.log`
- Access logs: `logs/access.log`

### Health Checks
The system provides health check endpoints:
- `/health` - Basic health status
- `/api/devices/status` - Device connectivity status
- `/api/system/metrics` - System performance metrics

## Backup and Recovery

### Database Backup
```bash
# Manual backup
cp data/production.db backups/production_$(date +%Y%m%d_%H%M%S).db

# Automated backup (add to cron)
0 2 * * * /path/to/backup_script.sh
```

### Configuration Backup
```bash
# Backup all configuration files
tar -czf config_backup_$(date +%Y%m%d).tar.gz config/
```

## Troubleshooting

### Common Issues

1. **SSL Certificate Errors**
   - Verify certificate paths in production.json
   - Check file permissions
   - Ensure certificates are valid and not expired

2. **Device Connection Issues**
   - Verify IP addresses and SNMP communities
   - Check network connectivity
   - Review firewall rules

3. **Performance Issues**
   - Monitor system resources
   - Check database size and performance
   - Review log files for errors

### Support
For technical support, check the documentation in the `docs/` directory or review the system logs.

---
*Production deployment guide for Network Device Management System*