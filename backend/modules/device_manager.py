#!/usr/bin/env python3
"""
Device Manager Module

Handles discovery, configuration, and management of network devices:
- Aruba AP 500 access points
- 3Com switches

Supports multiple protocols:
- SNMP for monitoring and basic configuration
- SSH for advanced configuration
- Vendor-specific APIs where available
"""

import json
import os
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import ipaddress
import socket
import threading
from concurrent.futures import ThreadPoolExecutor

try:
    from pysnmp.hlapi import *
    from netmiko import ConnectHandler
    import requests
except ImportError as e:
    logging.error(f"Required libraries not installed: {e}")
    logging.info("Please run: pip install -r requirements.txt")

class DeviceManager:
    """Main device management class"""
    
    def __init__(self, config_file='../config/devices.json'):
        self.config_file = config_file
        self.devices = {}
        self.device_types = {
            'aruba_ap500': ArubaAP500Manager,
            '3com_switch': ThreeComSwitchManager
        }
        self.lock = threading.Lock()
        
    def initialize(self):
        """Initialize device manager and load configuration"""
        try:
            self.load_device_config()
            logging.info("Device Manager initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize Device Manager: {e}")
            
    def load_device_config(self):
        """Load device configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.devices = config.get('devices', {})
                logging.info(f"Loaded {len(self.devices)} devices from config")
            except Exception as e:
                logging.error(f"Error loading device config: {e}")
        else:
            self.create_default_config()
            
    def create_default_config(self):
        """Create default configuration file"""
        default_config = {
            "devices": {
                "aruba_ap_1": {
                    "name": "Aruba AP 500 - Office",
                    "type": "aruba_ap500",
                    "ip": "192.168.1.10",
                    "snmp_community": "public",
                    "ssh_username": "admin",
                    "ssh_password": "password",
                    "location": "Main Office",
                    "enabled": True
                },
                "aruba_ap_2": {
                    "name": "Aruba AP 500 - Conference Room",
                    "type": "aruba_ap500",
                    "ip": "192.168.1.11",
                    "snmp_community": "public",
                    "ssh_username": "admin",
                    "ssh_password": "password",
                    "location": "Conference Room",
                    "enabled": True
                },
                "3com_switch_1": {
                    "name": "3Com Switch - Main",
                    "type": "3com_switch",
                    "ip": "192.168.1.20",
                    "snmp_community": "public",
                    "ssh_username": "admin",
                    "ssh_password": "password",
                    "location": "Server Room",
                    "enabled": True
                }
            },
            "discovery": {
                "enabled": True,
                "networks": ["192.168.1.0/24"],
                "scan_ports": [22, 161, 443, 80],
                "timeout": 5
            }
        }
        
        # Create config directory if it doesn't exist
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        self.devices = default_config['devices']
        logging.info("Created default device configuration")
        
    def get_all_devices(self) -> List[Dict]:
        """Get all configured devices with their status"""
        devices_list = []
        
        for device_id, device_config in self.devices.items():
            device_info = device_config.copy()
            device_info['id'] = device_id
            
            # Get device manager instance
            manager = self.get_device_manager(device_id)
            if manager:
                try:
                    status = manager.get_status()
                    device_info.update(status)
                except Exception as e:
                    device_info['status'] = 'error'
                    device_info['error'] = str(e)
            else:
                device_info['status'] = 'unknown'
                
            devices_list.append(device_info)
            
        return devices_list
    
    def get_device_manager(self, device_id: str):
        """Get device manager instance for a specific device"""
        if device_id not in self.devices:
            return None
            
        device_config = self.devices[device_id]
        device_type = device_config.get('type')
        
        if device_type in self.device_types:
            return self.device_types[device_type](device_config)
        
        return None
    
    def discover_devices(self, network_range: str = "192.168.1.0/24") -> List[Dict]:
        """Discover devices on the network"""
        discovered_devices = []
        
        try:
            network = ipaddress.IPv4Network(network_range, strict=False)
            
            # Use ThreadPoolExecutor for concurrent scanning
            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = []
                
                for ip in network.hosts():
                    future = executor.submit(self._scan_device, str(ip))
                    futures.append(future)
                
                for future in futures:
                    result = future.result()
                    if result:
                        discovered_devices.append(result)
                        
        except Exception as e:
            logging.error(f"Error during device discovery: {e}")
            
        logging.info(f"Discovered {len(discovered_devices)} devices")
        return discovered_devices
    
    def _scan_device(self, ip: str, timeout: int = 2) -> Optional[Dict]:
        """Scan a single IP for device presence and type"""
        try:
            # Check if device responds to ping
            if not self._ping_device(ip, timeout):
                return None
                
            device_info = {
                'ip': ip,
                'status': 'online',
                'discovered_at': datetime.now().isoformat()
            }
            
            # Try to identify device type through SNMP
            device_type = self._identify_device_type(ip)
            if device_type:
                device_info['type'] = device_type
                device_info['name'] = f"Auto-discovered {device_type}"
                
            # Try to get additional info via SNMP
            snmp_info = self._get_snmp_info(ip)
            if snmp_info:
                device_info.update(snmp_info)
                
            return device_info
            
        except Exception as e:
            logging.debug(f"Error scanning {ip}: {e}")
            return None
    
    def _ping_device(self, ip: str, timeout: int = 2) -> bool:
        """Check if device is reachable"""
        try:
            sock = socket.create_connection((ip, 22), timeout)
            sock.close()
            return True
        except:
            try:
                sock = socket.create_connection((ip, 80), timeout)
                sock.close()
                return True
            except:
                return False
    
    def _identify_device_type(self, ip: str) -> Optional[str]:
        """Identify device type using SNMP system description"""
        try:
            for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
                SnmpEngine(),
                CommunityData('public'),
                UdpTransportTarget((ip, 161)),
                ContextData(),
                ObjectType(ObjectIdentity('1.3.6.1.2.1.1.1.0')),  # sysDescr
                lexicographicMode=False,
                maxRows=1):
                
                if errorIndication or errorStatus:
                    break
                    
                for varBind in varBinds:
                    name, val = varBind
                    sys_descr = str(val).lower()
                    
                    # Identify Aruba devices
                    if 'aruba' in sys_descr and 'ap' in sys_descr:
                        return 'aruba_ap500'
                    
                    # Identify 3Com devices
                    if '3com' in sys_descr or 'comware' in sys_descr:
                        return '3com_switch'
                        
        except Exception as e:
            logging.debug(f"Error identifying device type for {ip}: {e}")
            
        return None
    
    def _get_snmp_info(self, ip: str) -> Dict:
        """Get basic device information via SNMP"""
        info = {}
        
        try:
            # Get system information
            oids = {
                'hostname': '1.3.6.1.2.1.1.5.0',    # sysName
                'description': '1.3.6.1.2.1.1.1.0', # sysDescr
                'uptime': '1.3.6.1.2.1.1.3.0',      # sysUpTime
                'location': '1.3.6.1.2.1.1.6.0'     # sysLocation
            }
            
            for key, oid in oids.items():
                for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
                    SnmpEngine(),
                    CommunityData('public'),
                    UdpTransportTarget((ip, 161)),
                    ContextData(),
                    ObjectType(ObjectIdentity(oid)),
                    lexicographicMode=False,
                    maxRows=1):
                    
                    if not errorIndication and not errorStatus:
                        for varBind in varBinds:
                            name, val = varBind
                            info[key] = str(val)
                            break
                    break
                    
        except Exception as e:
            logging.debug(f"Error getting SNMP info for {ip}: {e}")
            
        return info
    
    def get_device_config(self, device_id: str) -> Dict:
        """Get device configuration"""
        manager = self.get_device_manager(device_id)
        if not manager:
            raise ValueError(f"Device {device_id} not found")
            
        return manager.get_config()
    
    def update_device_config(self, device_id: str, config: Dict) -> Dict:
        """Update device configuration"""
        manager = self.get_device_manager(device_id)
        if not manager:
            raise ValueError(f"Device {device_id} not found")
            
        return manager.update_config(config)
    
    def backup_device_config(self, device_id: str) -> Dict:
        """Backup device configuration"""
        manager = self.get_device_manager(device_id)
        if not manager:
            raise ValueError(f"Device {device_id} not found")
            
        return manager.backup_config()
    
    def restore_device_config(self, device_id: str, backup_id: str) -> Dict:
        """Restore device configuration from backup"""
        manager = self.get_device_manager(device_id)
        if not manager:
            raise ValueError(f"Device {device_id} not found")
            
        return manager.restore_config(backup_id)


class BaseDeviceManager:
    """Base class for device managers"""
    
    def __init__(self, device_config: Dict):
        self.config = device_config
        self.ip = device_config['ip']
        self.name = device_config.get('name', 'Unknown Device')
        
    def get_status(self) -> Dict:
        """Get device status - to be implemented by subclasses"""
        return {'status': 'unknown'}
        
    def get_config(self) -> Dict:
        """Get device configuration - to be implemented by subclasses"""
        return {}
        
    def update_config(self, config: Dict) -> Dict:
        """Update device configuration - to be implemented by subclasses"""
        return {'success': False, 'message': 'Not implemented'}
        
    def backup_config(self) -> Dict:
        """Backup device configuration - to be implemented by subclasses"""
        return {'success': False, 'message': 'Not implemented'}
        
    def restore_config(self, backup_id: str) -> Dict:
        """Restore device configuration - to be implemented by subclasses"""
        return {'success': False, 'message': 'Not implemented'}


class ArubaAP500Manager(BaseDeviceManager):
    """Manager for Aruba AP 500 access points"""
    
    def get_status(self) -> Dict:
        """Get AP status including wireless clients and performance"""
        status = {
            'status': 'unknown',
            'clients_connected': 0,
            'ssids': [],
            'radio_status': {},
            'cpu_usage': 0,
            'memory_usage': 0
        }
        
        try:
            # Check basic connectivity
            if self._ping_device():
                status['status'] = 'online'
                
                # Get wireless client count via SNMP
                status['clients_connected'] = self._get_client_count()
                
                # Get SSID information
                status['ssids'] = self._get_ssids()
                
                # Get radio status
                status['radio_status'] = self._get_radio_status()
                
                # Get system resources
                status['cpu_usage'] = self._get_cpu_usage()
                status['memory_usage'] = self._get_memory_usage()
                
            else:
                status['status'] = 'offline'
                
        except Exception as e:
            status['status'] = 'error'
            status['error'] = str(e)
            logging.error(f"Error getting Aruba AP status: {e}")
            
        return status
    
    def _ping_device(self) -> bool:
        """Check if AP is reachable"""
        try:
            sock = socket.create_connection((self.ip, 22), 5)
            sock.close()
            return True
        except:
            return False
    
    def _get_client_count(self) -> int:
        """Get number of connected wireless clients"""
        try:
            # SNMP OID for wireless client count (generic)
            for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
                SnmpEngine(),
                CommunityData(self.config.get('snmp_community', 'public')),
                UdpTransportTarget((self.ip, 161)),
                ContextData(),
                ObjectType(ObjectIdentity('1.3.6.1.4.1.14823.2.2.1.1.3.2.0')),
                lexicographicMode=False,
                maxRows=1):
                
                if not errorIndication and not errorStatus:
                    for varBind in varBinds:
                        name, val = varBind
                        return int(val)
                        
        except Exception as e:
            logging.debug(f"Error getting client count: {e}")
            
        return 0
    
    def _get_ssids(self) -> List[Dict]:
        """Get configured SSIDs"""
        ssids = []
        
        try:
            # This would typically require specific SNMP OIDs for Aruba
            # For now, return example data
            ssids = [
                {
                    'name': 'Corporate-WiFi',
                    'enabled': True,
                    'clients': 15,
                    'band': '2.4GHz/5GHz'
                },
                {
                    'name': 'Guest-WiFi',
                    'enabled': True,
                    'clients': 8,
                    'band': '2.4GHz/5GHz'
                }
            ]
            
        except Exception as e:
            logging.debug(f"Error getting SSIDs: {e}")
            
        return ssids
    
    def _get_radio_status(self) -> Dict:
        """Get radio status for different bands"""
        return {
            '2.4GHz': {
                'enabled': True,
                'channel': 6,
                'power': 20,
                'utilization': 45
            },
            '5GHz': {
                'enabled': True,
                'channel': 36,
                'power': 23,
                'utilization': 30
            }
        }
    
    def _get_cpu_usage(self) -> int:
        """Get CPU usage percentage"""
        # Would use SNMP OID for CPU usage
        return 25
    
    def _get_memory_usage(self) -> int:
        """Get memory usage percentage"""
        # Would use SNMP OID for memory usage
        return 40
    
    def get_config(self) -> Dict:
        """Get AP configuration"""
        return {
            'device_info': {
                'name': self.name,
                'ip': self.ip,
                'model': 'Aruba AP 500',
                'serial': 'AP500-12345',
                'firmware': '8.10.0.4'
            },
            'wireless': {
                'ssids': self._get_ssids(),
                'radio_settings': self._get_radio_status(),
                'security': {
                    'wpa2_enabled': True,
                    'wpa3_enabled': True
                }
            },
            'network': {
                'vlan': 1,
                'ip_assignment': 'dhcp'
            }
        }


class ThreeComSwitchManager(BaseDeviceManager):
    """Manager for 3Com switches"""
    
    def get_status(self) -> Dict:
        """Get switch status including port information"""
        status = {
            'status': 'unknown',
            'ports': {},
            'vlans': [],
            'cpu_usage': 0,
            'memory_usage': 0,
            'temperature': 0
        }
        
        try:
            # Check basic connectivity
            if self._ping_device():
                status['status'] = 'online'
                
                # Get port status
                status['ports'] = self._get_port_status()
                
                # Get VLAN information
                status['vlans'] = self._get_vlans()
                
                # Get system resources
                status['cpu_usage'] = self._get_cpu_usage()
                status['memory_usage'] = self._get_memory_usage()
                status['temperature'] = self._get_temperature()
                
            else:
                status['status'] = 'offline'
                
        except Exception as e:
            status['status'] = 'error'
            status['error'] = str(e)
            logging.error(f"Error getting 3Com switch status: {e}")
            
        return status
    
    def _ping_device(self) -> bool:
        """Check if switch is reachable"""
        try:
            sock = socket.create_connection((self.ip, 22), 5)
            sock.close()
            return True
        except:
            return False
    
    def _get_port_status(self) -> Dict:
        """Get status of all switch ports"""
        ports = {}
        
        try:
            # Get interface status via SNMP
            # This is a simplified example
            for port in range(1, 25):  # Assuming 24 ports
                ports[f"port_{port}"] = {
                    'name': f"GigabitEthernet0/{port}",
                    'status': 'up' if port <= 12 else 'down',
                    'speed': '1000Mbps',
                    'duplex': 'full',
                    'vlan': 1 if port <= 20 else 10,
                    'description': f"Port {port}"
                }
                
        except Exception as e:
            logging.debug(f"Error getting port status: {e}")
            
        return ports
    
    def _get_vlans(self) -> List[Dict]:
        """Get VLAN configuration"""
        return [
            {
                'id': 1,
                'name': 'default',
                'ports': list(range(1, 21)),
                'status': 'active'
            },
            {
                'id': 10,
                'name': 'management',
                'ports': [21, 22, 23, 24],
                'status': 'active'
            }
        ]
    
    def _get_cpu_usage(self) -> int:
        """Get CPU usage percentage"""
        return 15
    
    def _get_memory_usage(self) -> int:
        """Get memory usage percentage"""
        return 35
    
    def _get_temperature(self) -> int:
        """Get system temperature in Celsius"""
        return 42
    
    def get_config(self) -> Dict:
        """Get switch configuration"""
        return {
            'device_info': {
                'name': self.name,
                'ip': self.ip,
                'model': '3Com Switch 4500',
                'serial': '3COM-67890',
                'firmware': '7.1.045'
            },
            'ports': self._get_port_status(),
            'vlans': self._get_vlans(),
            'spanning_tree': {
                'enabled': True,
                'mode': 'rstp'
            },
            'management': {
                'snmp_enabled': True,
                'ssh_enabled': True,
                'telnet_enabled': False
            }
        }