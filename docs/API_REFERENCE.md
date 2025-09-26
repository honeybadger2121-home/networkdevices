# API Reference

## Overview

The Network Device Manager provides a RESTful API for programmatic access to device management functionality. All API endpoints return JSON responses and use standard HTTP status codes.

**Base URL**: `http://localhost:5000/api`

## Authentication

Currently, the API does not require authentication. In production environments, consider implementing:
- API keys
- OAuth 2.0
- JWT tokens
- Basic authentication

## Response Format

All API responses follow this standard format:

```json
{
  "success": true|false,
  "data": {...},
  "error": "Error message (if success=false)",
  "timestamp": "2025-09-26T10:30:00Z"
}
```

## Endpoints

### Health Check

#### GET /api/health

Returns the system health status.

**Response**:
```json
{
  "success": true,
  "status": "healthy",
  "timestamp": "2025-09-26T10:30:00Z",
  "version": "1.0.0"
}
```

---

### Devices

#### GET /api/devices

Retrieve all configured devices with their current status.

**Response**:
```json
{
  "success": true,
  "devices": [
    {
      "id": "aruba_ap_1",
      "name": "Aruba AP 500 - Office",
      "type": "aruba_ap500",
      "ip": "192.168.1.10",
      "status": "online",
      "location": "Main Office",
      "clients_connected": 15,
      "cpu_usage": 25,
      "memory_usage": 40,
      "temperature": 42,
      "last_seen": "2025-09-26T10:29:45Z"
    }
  ],
  "count": 1
}
```

#### POST /api/devices/discover

Discover devices on the network.

**Request Body**:
```json
{
  "network_range": "192.168.1.0/24"
}
```

**Response**:
```json
{
  "success": true,
  "discovered": [
    {
      "ip": "192.168.1.10",
      "type": "aruba_ap500",
      "name": "Auto-discovered aruba_ap500",
      "status": "online",
      "discovered_at": "2025-09-26T10:30:00Z"
    }
  ],
  "count": 1
}
```

#### GET /api/devices/{device_id}/status

Get detailed status information for a specific device.

**Parameters**:
- `device_id` (string): Device identifier

**Response**:
```json
{
  "success": true,
  "status": {
    "status": "online",
    "clients_connected": 15,
    "ssids": [
      {
        "name": "Corporate-WiFi",
        "enabled": true,
        "clients": 12,
        "band": "2.4GHz/5GHz"
      }
    ],
    "radio_status": {
      "2.4GHz": {
        "enabled": true,
        "channel": 6,
        "power": 20,
        "utilization": 45
      }
    },
    "cpu_usage": 25,
    "memory_usage": 40
  }
}
```

#### GET /api/devices/{device_id}/config

Retrieve the configuration of a specific device.

**Parameters**:
- `device_id` (string): Device identifier

**Response**:
```json
{
  "success": true,
  "config": {
    "device_info": {
      "name": "Aruba AP 500 - Office",
      "ip": "192.168.1.10",
      "model": "Aruba AP 500",
      "serial": "AP500-12345",
      "firmware": "8.10.0.4"
    },
    "wireless": {
      "ssids": [...],
      "radio_settings": {...},
      "security": {...}
    },
    "network": {
      "vlan": 1,
      "ip_assignment": "dhcp"
    }
  }
}
```

#### POST /api/devices/{device_id}/config

Update the configuration of a specific device.

**Parameters**:
- `device_id` (string): Device identifier

**Request Body**:
```json
{
  "wireless": {
    "ssids": [
      {
        "name": "NewSSID",
        "enabled": true,
        "security": "WPA2"
      }
    ]
  }
}
```

**Response**:
```json
{
  "success": true,
  "result": {
    "message": "Configuration updated successfully",
    "changes_applied": 3,
    "restart_required": false
  }
}
```

#### POST /api/devices/{device_id}/backup

Create a backup of the device configuration.

**Parameters**:
- `device_id` (string): Device identifier

**Response**:
```json
{
  "success": true,
  "backup": {
    "backup_id": "backup_20250926_103000",
    "timestamp": "2025-09-26T10:30:00Z",
    "size": 2048,
    "description": "Automatic backup"
  }
}
```

#### POST /api/devices/{device_id}/restore

Restore device configuration from a backup.

**Parameters**:
- `device_id` (string): Device identifier

**Request Body**:
```json
{
  "backup_id": "backup_20250926_103000"
}
```

**Response**:
```json
{
  "success": true,
  "result": {
    "message": "Configuration restored successfully",
    "backup_id": "backup_20250926_103000",
    "restore_time": "2025-09-26T10:35:00Z"
  }
}
```

---

### Monitoring

#### GET /api/monitoring/dashboard

Get aggregated dashboard data for monitoring overview.

**Response**:
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_devices": 3,
      "online_devices": 2,
      "offline_devices": 1,
      "total_alerts": 5,
      "unresolved_alerts": 2
    },
    "metrics": {
      "average_cpu_usage": 23.5,
      "average_memory_usage": 42.3,
      "total_wireless_clients": 28
    },
    "device_types": {
      "Aruba AP": 2,
      "3Com Switch": 1
    },
    "recent_alerts": [...],
    "last_updated": "2025-09-26T10:30:00Z"
  }
}
```

---

### Alerts

#### GET /api/alerts

Retrieve all system alerts.

**Response**:
```json
{
  "success": true,
  "alerts": [
    {
      "id": "aruba_ap_1_high_cpu_1727349000",
      "device_id": "aruba_ap_1",
      "rule_name": "high_cpu_usage",
      "severity": "warning",
      "message": "CPU usage is 85% (threshold: 80%)",
      "description": "CPU usage is above threshold",
      "timestamp": "2025-09-26T10:30:00Z",
      "acknowledged": false,
      "resolved": false
    }
  ]
}
```

#### POST /api/alerts/{alert_id}/acknowledge

Acknowledge an alert.

**Parameters**:
- `alert_id` (string): Alert identifier

**Response**:
```json
{
  "success": true,
  "message": "Alert acknowledged successfully"
}
```

#### POST /api/alerts/{alert_id}/resolve

Mark an alert as resolved.

**Parameters**:
- `alert_id` (string): Alert identifier

**Response**:
```json
{
  "success": true,
  "message": "Alert resolved successfully"
}
```

---

## Error Codes

The API uses standard HTTP status codes:

- **200 OK**: Request successful
- **400 Bad Request**: Invalid request parameters
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

### Common Error Responses

#### 400 Bad Request
```json
{
  "success": false,
  "error": "Invalid network range format. Use CIDR notation (e.g., 192.168.1.0/24)"
}
```

#### 404 Not Found
```json
{
  "success": false,
  "error": "Device 'invalid_device' not found"
}
```

#### 500 Internal Server Error
```json
{
  "success": false,
  "error": "Failed to connect to device. Check network connectivity."
}
```

---

## Rate Limiting

Currently, no rate limiting is implemented. In production environments, consider:
- Request rate limits per IP
- API key-based quotas
- Throttling for expensive operations

---

## Examples

### Python Example

```python
import requests
import json

# Base API URL
api_base = "http://localhost:5000/api"

# Get all devices
response = requests.get(f"{api_base}/devices")
if response.status_code == 200:
    data = response.json()
    if data['success']:
        devices = data['devices']
        print(f"Found {len(devices)} devices")
        for device in devices:
            print(f"- {device['name']} ({device['ip']}) - {device['status']}")

# Discover new devices
discovery_data = {"network_range": "192.168.1.0/24"}
response = requests.post(
    f"{api_base}/devices/discover", 
    json=discovery_data
)
if response.status_code == 200:
    data = response.json()
    print(f"Discovered {data['count']} devices")

# Get device status
device_id = "aruba_ap_1"
response = requests.get(f"{api_base}/devices/{device_id}/status")
if response.status_code == 200:
    status = response.json()['status']
    print(f"Device status: {status['status']}")
    print(f"Connected clients: {status.get('clients_connected', 0)}")
```

### JavaScript Example

```javascript
const apiBase = 'http://localhost:5000/api';

// Get all devices
async function getDevices() {
    try {
        const response = await fetch(`${apiBase}/devices`);
        const data = await response.json();
        
        if (data.success) {
            console.log(`Found ${data.devices.length} devices`);
            data.devices.forEach(device => {
                console.log(`- ${device.name} (${device.ip}) - ${device.status}`);
            });
        }
    } catch (error) {
        console.error('Error fetching devices:', error);
    }
}

// Create device backup
async function backupDevice(deviceId) {
    try {
        const response = await fetch(`${apiBase}/devices/${deviceId}/backup`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            console.log('Backup created:', data.backup.backup_id);
        }
    } catch (error) {
        console.error('Error creating backup:', error);
    }
}
```

### cURL Examples

```bash
# Get all devices
curl -X GET http://localhost:5000/api/devices

# Discover devices
curl -X POST http://localhost:5000/api/devices/discover \
     -H "Content-Type: application/json" \
     -d '{"network_range": "192.168.1.0/24"}'

# Get device status
curl -X GET http://localhost:5000/api/devices/aruba_ap_1/status

# Create device backup
curl -X POST http://localhost:5000/api/devices/aruba_ap_1/backup

# Get monitoring dashboard
curl -X GET http://localhost:5000/api/monitoring/dashboard

# Get alerts
curl -X GET http://localhost:5000/api/alerts
```

---

## Webhooks (Future Enhancement)

Future versions may include webhook support for:
- Device status changes
- Alert notifications
- Configuration changes
- Discovery events

Example webhook payload:
```json
{
  "event": "device.status.changed",
  "device_id": "aruba_ap_1",
  "old_status": "online",
  "new_status": "offline",
  "timestamp": "2025-09-26T10:30:00Z"
}
```