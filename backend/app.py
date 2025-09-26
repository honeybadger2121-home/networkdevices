#!/usr/bin/env python3
"""
Aruba AP 500 & 3Com Switch Manager
Main Flask Application

This application provides a web-based interface for managing:
- Aruba AP 500 access points
- 3Com switches

Author: Network Administrator
Date: September 2025
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import os
import sys
import logging
from datetime import datetime

# Add modules directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from device_manager import DeviceManager
from monitoring import NetworkMonitor

app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
CORS(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('network_manager.log'),
        logging.StreamHandler()
    ]
)

# Initialize components
device_manager = DeviceManager()
network_monitor = NetworkMonitor()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/devices')
def get_devices():
    """Get all discovered devices"""
    try:
        devices = device_manager.get_all_devices()
        return jsonify({
            'success': True,
            'devices': devices,
            'count': len(devices)
        })
    except Exception as e:
        logging.error(f"Error getting devices: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/devices/discover', methods=['POST'])
def discover_devices():
    """Discover devices on the network"""
    try:
        data = request.get_json()
        network_range = data.get('network_range', '192.168.1.0/24')
        
        discovered = device_manager.discover_devices(network_range)
        return jsonify({
            'success': True,
            'discovered': discovered,
            'count': len(discovered)
        })
    except Exception as e:
        logging.error(f"Error during device discovery: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/devices/<device_id>/status')
def get_device_status(device_id):
    """Get status of a specific device"""
    try:
        status = network_monitor.get_device_status(device_id)
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        logging.error(f"Error getting device status: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/devices/<device_id>/config', methods=['GET'])
def get_device_config(device_id):
    """Get configuration of a specific device"""
    try:
        config = device_manager.get_device_config(device_id)
        return jsonify({
            'success': True,
            'config': config
        })
    except Exception as e:
        logging.error(f"Error getting device config: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/devices/<device_id>/config', methods=['POST'])
def update_device_config(device_id):
    """Update configuration of a specific device"""
    try:
        config_data = request.get_json()
        result = device_manager.update_device_config(device_id, config_data)
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        logging.error(f"Error updating device config: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/devices/<device_id>/backup', methods=['POST'])
def backup_device_config(device_id):
    """Backup device configuration"""
    try:
        backup_result = device_manager.backup_device_config(device_id)
        return jsonify({
            'success': True,
            'backup': backup_result
        })
    except Exception as e:
        logging.error(f"Error backing up device config: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/devices/<device_id>/restore', methods=['POST'])
def restore_device_config(device_id):
    """Restore device configuration from backup"""
    try:
        data = request.get_json()
        backup_id = data.get('backup_id')
        restore_result = device_manager.restore_device_config(device_id, backup_id)
        return jsonify({
            'success': True,
            'result': restore_result
        })
    except Exception as e:
        logging.error(f"Error restoring device config: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/monitoring/dashboard')
def get_monitoring_dashboard():
    """Get monitoring dashboard data"""
    try:
        dashboard_data = network_monitor.get_dashboard_data()
        return jsonify({
            'success': True,
            'data': dashboard_data
        })
    except Exception as e:
        logging.error(f"Error getting dashboard data: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/alerts')
def get_alerts():
    """Get current system alerts"""
    try:
        alerts = network_monitor.get_alerts()
        return jsonify({
            'success': True,
            'alerts': alerts
        })
    except Exception as e:
        logging.error(f"Error getting alerts: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """System health check endpoint"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("Starting Aruba AP 500 & 3Com Switch Manager...")
    print("Web interface will be available at: http://localhost:5000")
    
    # Initialize device manager
    device_manager.initialize()
    
    # Start monitoring
    network_monitor.start()
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )