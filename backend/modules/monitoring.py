#!/usr/bin/env python3
"""
Network Monitoring Module

Provides real-time monitoring capabilities for network devices:
- Status monitoring
- Performance metrics collection
- Alert generation
- Dashboard data aggregation

Supports both polling and event-based monitoring
"""

import time
import logging
import threading
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import deque
import schedule

class NetworkMonitor:
    """Network monitoring service"""
    
    def __init__(self):
        self.monitoring_thread = None
        self.running = False
        self.devices_status = {}
        self.alerts = deque(maxlen=100)  # Keep last 100 alerts
        self.metrics_history = {}
        self.alert_rules = self._load_alert_rules()
        self.lock = threading.Lock()
        
    def start(self):
        """Start the monitoring service"""
        if not self.running:
            self.running = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
            
            # Schedule periodic tasks
            schedule.every(30).seconds.do(self._collect_metrics)
            schedule.every(1).minute.do(self._check_alerts)
            schedule.every(5).minutes.do(self._cleanup_old_data)
            
            logging.info("Network monitoring service started")
    
    def stop(self):
        """Stop the monitoring service"""
        self.running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logging.info("Network monitoring service stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logging.error(f"Error in monitoring loop: {e}")
                time.sleep(5)
    
    def _load_alert_rules(self) -> Dict:
        """Load alert rules configuration"""
        return {
            'device_offline': {
                'enabled': True,
                'severity': 'critical',
                'description': 'Device is offline or unreachable'
            },
            'high_cpu_usage': {
                'enabled': True,
                'threshold': 80,
                'severity': 'warning',
                'description': 'CPU usage is above threshold'
            },
            'high_memory_usage': {
                'enabled': True,
                'threshold': 85,
                'severity': 'warning',
                'description': 'Memory usage is above threshold'
            },
            'port_down': {
                'enabled': True,
                'severity': 'warning',
                'description': 'Network port is down'
            },
            'high_temperature': {
                'enabled': True,
                'threshold': 60,
                'severity': 'warning',
                'description': 'Device temperature is above threshold'
            },
            'low_client_count': {
                'enabled': True,
                'threshold': 0,
                'severity': 'info',
                'description': 'No wireless clients connected to AP'
            }
        }
    
    def _collect_metrics(self):
        """Collect metrics from all devices"""
        try:
            # This would typically interface with DeviceManager
            # For now, we'll simulate data collection
            
            devices = self._get_devices_list()
            
            with self.lock:
                current_time = datetime.now()
                
                for device in devices:
                    device_id = device['id']
                    
                    # Initialize metrics history for new devices
                    if device_id not in self.metrics_history:
                        self.metrics_history[device_id] = {
                            'cpu_usage': deque(maxlen=60),  # Last 60 measurements
                            'memory_usage': deque(maxlen=60),
                            'temperature': deque(maxlen=60),
                            'client_count': deque(maxlen=60),
                            'timestamps': deque(maxlen=60)
                        }
                    
                    # Collect current metrics (simulated)
                    metrics = self._get_device_metrics(device_id)
                    
                    # Store metrics
                    history = self.metrics_history[device_id]
                    history['cpu_usage'].append(metrics.get('cpu_usage', 0))
                    history['memory_usage'].append(metrics.get('memory_usage', 0))
                    history['temperature'].append(metrics.get('temperature', 0))
                    history['client_count'].append(metrics.get('client_count', 0))
                    history['timestamps'].append(current_time.isoformat())
                    
                    # Update device status
                    self.devices_status[device_id] = {
                        'last_seen': current_time.isoformat(),
                        'status': metrics.get('status', 'unknown'),
                        'metrics': metrics
                    }
                    
        except Exception as e:
            logging.error(f"Error collecting metrics: {e}")
    
    def _get_devices_list(self) -> List[Dict]:
        """Get list of devices to monitor (simulated)"""
        # This would typically come from DeviceManager
        return [
            {'id': 'aruba_ap_1', 'type': 'aruba_ap500'},
            {'id': 'aruba_ap_2', 'type': 'aruba_ap500'},
            {'id': '3com_switch_1', 'type': '3com_switch'}
        ]
    
    def _get_device_metrics(self, device_id: str) -> Dict:
        """Get current metrics for a device (simulated)"""
        import random
        
        # Simulate different metrics based on device type
        if 'aruba_ap' in device_id:
            return {
                'status': 'online',
                'cpu_usage': random.randint(10, 40),
                'memory_usage': random.randint(30, 60),
                'temperature': random.randint(35, 50),
                'client_count': random.randint(5, 25),
                'signal_strength': random.randint(-70, -30)
            }
        elif '3com_switch' in device_id:
            return {
                'status': 'online',
                'cpu_usage': random.randint(5, 25),
                'memory_usage': random.randint(20, 45),
                'temperature': random.randint(30, 45),
                'port_count': 24,
                'ports_up': random.randint(15, 24)
            }
        
        return {'status': 'unknown'}
    
    def _check_alerts(self):
        """Check for alert conditions and generate alerts"""
        try:
            with self.lock:
                for device_id, status in self.devices_status.items():
                    metrics = status.get('metrics', {})
                    
                    # Check each alert rule
                    for rule_name, rule_config in self.alert_rules.items():
                        if not rule_config.get('enabled', False):
                            continue
                            
                        alert = None
                        
                        # Device offline check
                        if rule_name == 'device_offline':
                            last_seen = datetime.fromisoformat(status['last_seen'])
                            if datetime.now() - last_seen > timedelta(minutes=2):
                                alert = self._create_alert(
                                    device_id, rule_name, rule_config,
                                    f"Device {device_id} has been offline for more than 2 minutes"
                                )
                        
                        # High CPU usage
                        elif rule_name == 'high_cpu_usage':
                            cpu_usage = metrics.get('cpu_usage', 0)
                            if cpu_usage > rule_config.get('threshold', 80):
                                alert = self._create_alert(
                                    device_id, rule_name, rule_config,
                                    f"CPU usage is {cpu_usage}% (threshold: {rule_config['threshold']}%)"
                                )
                        
                        # High memory usage
                        elif rule_name == 'high_memory_usage':
                            memory_usage = metrics.get('memory_usage', 0)
                            if memory_usage > rule_config.get('threshold', 85):
                                alert = self._create_alert(
                                    device_id, rule_name, rule_config,
                                    f"Memory usage is {memory_usage}% (threshold: {rule_config['threshold']}%)"
                                )
                        
                        # High temperature
                        elif rule_name == 'high_temperature':
                            temperature = metrics.get('temperature', 0)
                            if temperature > rule_config.get('threshold', 60):
                                alert = self._create_alert(
                                    device_id, rule_name, rule_config,
                                    f"Temperature is {temperature}°C (threshold: {rule_config['threshold']}°C)"
                                )
                        
                        if alert:
                            self.alerts.appendleft(alert)
                            logging.warning(f"Alert generated: {alert['message']}")
                            
        except Exception as e:
            logging.error(f"Error checking alerts: {e}")
    
    def _create_alert(self, device_id: str, rule_name: str, rule_config: Dict, message: str) -> Dict:
        """Create an alert"""
        return {
            'id': f"{device_id}_{rule_name}_{int(time.time())}",
            'device_id': device_id,
            'rule_name': rule_name,
            'severity': rule_config.get('severity', 'info'),
            'message': message,
            'description': rule_config.get('description', ''),
            'timestamp': datetime.now().isoformat(),
            'acknowledged': False,
            'resolved': False
        }
    
    def _cleanup_old_data(self):
        """Clean up old monitoring data"""
        try:
            # Remove device status older than 1 hour
            cutoff_time = datetime.now() - timedelta(hours=1)
            
            with self.lock:
                devices_to_remove = []
                for device_id, status in self.devices_status.items():
                    last_seen = datetime.fromisoformat(status['last_seen'])
                    if last_seen < cutoff_time:
                        devices_to_remove.append(device_id)
                
                for device_id in devices_to_remove:
                    del self.devices_status[device_id]
                    if device_id in self.metrics_history:
                        del self.metrics_history[device_id]
                
            logging.info(f"Cleaned up data for {len(devices_to_remove)} inactive devices")
            
        except Exception as e:
            logging.error(f"Error cleaning up old data: {e}")
    
    def get_device_status(self, device_id: str) -> Dict:
        """Get current status for a specific device"""
        with self.lock:
            if device_id in self.devices_status:
                status = self.devices_status[device_id].copy()
                
                # Add metrics history
                if device_id in self.metrics_history:
                    history = self.metrics_history[device_id]
                    status['history'] = {
                        'cpu_usage': list(history['cpu_usage'])[-10:],  # Last 10 points
                        'memory_usage': list(history['memory_usage'])[-10:],
                        'temperature': list(history['temperature'])[-10:],
                        'timestamps': list(history['timestamps'])[-10:]
                    }
                
                return status
            
        return {'status': 'unknown', 'message': 'Device not found'}
    
    def get_dashboard_data(self) -> Dict:
        """Get aggregated dashboard data"""
        with self.lock:
            total_devices = len(self.devices_status)
            online_devices = sum(1 for status in self.devices_status.values() 
                               if status.get('metrics', {}).get('status') == 'online')
            offline_devices = total_devices - online_devices
            
            # Get recent alerts
            recent_alerts = [alert for alert in list(self.alerts)[:10]]
            
            # Calculate average metrics
            avg_cpu = 0
            avg_memory = 0
            total_clients = 0
            
            if self.devices_status:
                cpu_values = [status.get('metrics', {}).get('cpu_usage', 0) 
                             for status in self.devices_status.values()]
                memory_values = [status.get('metrics', {}).get('memory_usage', 0) 
                               for status in self.devices_status.values()]
                client_values = [status.get('metrics', {}).get('client_count', 0) 
                               for status in self.devices_status.values()]
                
                avg_cpu = sum(cpu_values) / len(cpu_values) if cpu_values else 0
                avg_memory = sum(memory_values) / len(memory_values) if memory_values else 0
                total_clients = sum(client_values)
            
            # Device breakdown by type
            device_types = {}
            for device_id in self.devices_status.keys():
                if 'aruba_ap' in device_id:
                    device_types['Aruba AP'] = device_types.get('Aruba AP', 0) + 1
                elif '3com_switch' in device_id:
                    device_types['3Com Switch'] = device_types.get('3Com Switch', 0) + 1
                else:
                    device_types['Other'] = device_types.get('Other', 0) + 1
            
            return {
                'summary': {
                    'total_devices': total_devices,
                    'online_devices': online_devices,
                    'offline_devices': offline_devices,
                    'total_alerts': len(self.alerts),
                    'unresolved_alerts': sum(1 for alert in self.alerts if not alert.get('resolved', False))
                },
                'metrics': {
                    'average_cpu_usage': round(avg_cpu, 1),
                    'average_memory_usage': round(avg_memory, 1),
                    'total_wireless_clients': total_clients
                },
                'device_types': device_types,
                'recent_alerts': recent_alerts,
                'last_updated': datetime.now().isoformat()
            }
    
    def get_alerts(self) -> List[Dict]:
        """Get all alerts"""
        with self.lock:
            return list(self.alerts)
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        with self.lock:
            for alert in self.alerts:
                if alert['id'] == alert_id:
                    alert['acknowledged'] = True
                    alert['acknowledged_at'] = datetime.now().isoformat()
                    return True
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        with self.lock:
            for alert in self.alerts:
                if alert['id'] == alert_id:
                    alert['resolved'] = True
                    alert['resolved_at'] = datetime.now().isoformat()
                    return True
        return False