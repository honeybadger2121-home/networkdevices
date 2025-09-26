/**
 * Network Device Manager JavaScript Application
 * 
 * Handles frontend functionality for managing Aruba AP 500s and 3Com switches
 * including device discovery, monitoring, alerts, and configuration management.
 */

class NetworkDeviceManager {
    constructor() {
        this.apiBase = window.location.origin + '/api';
        this.refreshInterval = null;
        this.currentTab = 'devices';
        this.devices = [];
        this.alerts = [];
        this.dashboardData = {};
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.initializeTabs();
        this.startAutoRefresh();
        this.loadInitialData();
        
        console.log('Network Device Manager initialized');
    }
    
    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });
        
        // Refresh button
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.refreshData();
        });
        
        // Discovery button
        document.getElementById('discoverBtn').addEventListener('click', () => {
            this.showDiscoveryModal();
        });
        
        // Discovery modal
        document.getElementById('startDiscoveryBtn').addEventListener('click', () => {
            this.startDeviceDiscovery();
        });
        
        // Modal close buttons
        document.querySelectorAll('.close-btn, [data-modal]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modalId = btn.dataset.modal || btn.closest('.modal').id;
                this.closeModal(modalId);
            });
        });
        
        // Device filter
        document.getElementById('deviceFilter').addEventListener('change', (e) => {
            this.filterDevices(e.target.value);
        });
        
        // Configuration device select
        document.getElementById('configDeviceSelect').addEventListener('change', (e) => {
            this.loadDeviceConfig(e.target.value);
        });
        
        // Configuration buttons
        document.getElementById('backupConfigBtn').addEventListener('click', () => {
            this.backupDeviceConfig();
        });
        
        document.getElementById('restoreConfigBtn').addEventListener('click', () => {
            this.restoreDeviceConfig();
        });
        
        document.getElementById('saveConfigBtn').addEventListener('click', () => {
            this.saveDeviceConfig();
        });
        
        document.getElementById('resetConfigBtn').addEventListener('click', () => {
            this.resetConfigEditor();
        });
        
        // Alert actions
        document.getElementById('clearAlertsBtn').addEventListener('click', () => {
            this.clearAllAlerts();
        });
        
        // Close modals when clicking outside
        window.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeModal(e.target.id);
            }
        });
    }
    
    initializeTabs() {
        // Set default active tab
        this.switchTab('devices');
    }
    
    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        // Update tab contents
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(tabName).classList.add('active');
        
        this.currentTab = tabName;
        
        // Load tab-specific data
        if (tabName === 'monitoring') {
            this.loadMonitoringData();
        } else if (tabName === 'alerts') {
            this.loadAlerts();
        } else if (tabName === 'config') {
            this.loadConfigurationTab();
        }
    }
    
    startAutoRefresh() {
        // Refresh data every 30 seconds
        this.refreshInterval = setInterval(() => {
            this.refreshData();
        }, 30000);
    }
    
    async loadInitialData() {
        this.showLoading(true);
        
        try {
            await Promise.all([
                this.loadDevices(),
                this.loadDashboardData(),
                this.loadAlerts()
            ]);
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showNotification('Error loading data. Please refresh the page.', 'error');
        }
        
        this.showLoading(false);
        this.updateLastUpdated();
    }
    
    async refreshData() {
        try {
            const refreshBtn = document.getElementById('refreshBtn');
            refreshBtn.querySelector('i').classList.add('fa-spin');
            
            await this.loadInitialData();
            
            refreshBtn.querySelector('i').classList.remove('fa-spin');
            this.showNotification('Data refreshed successfully', 'success');
        } catch (error) {
            console.error('Error refreshing data:', error);
            this.showNotification('Error refreshing data', 'error');
        }
    }
    
    async loadDevices() {
        try {
            const response = await fetch(`${this.apiBase}/devices`);
            const data = await response.json();
            
            if (data.success) {
                this.devices = data.devices;
                this.renderDevices();
                this.updateOverviewCards();
            } else {
                throw new Error(data.error || 'Failed to load devices');
            }
        } catch (error) {
            console.error('Error loading devices:', error);
            this.showNotification('Error loading devices', 'error');
        }
    }
    
    renderDevices() {
        const container = document.getElementById('devicesContainer');
        
        if (!this.devices || this.devices.length === 0) {
            container.innerHTML = `
                <div class="no-devices">
                    <i class="fas fa-server" style="font-size: 48px; color: #ccc; margin-bottom: 20px;"></i>
                    <h3>No devices found</h3>
                    <p>Click "Discover Devices" to scan your network for Aruba APs and 3Com switches.</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.devices.map(device => this.createDeviceCard(device)).join('');
        
        // Add event listeners to device action buttons
        container.querySelectorAll('.device-action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.target.dataset.action;
                const deviceId = e.target.dataset.device;
                this.handleDeviceAction(action, deviceId);
            });
        });
    }
    
    createDeviceCard(device) {
        const statusClass = device.status || 'unknown';
        const statusText = statusClass.charAt(0).toUpperCase() + statusClass.slice(1);
        
        const deviceInfo = this.getDeviceInfo(device);
        
        return `
            <div class="device-card ${statusClass}">
                <div class="device-header">
                    <div class="device-name">
                        <i class="${this.getDeviceIcon(device.type)}"></i>
                        ${device.name || device.id}
                    </div>
                    <span class="device-status ${statusClass}">${statusText}</span>
                </div>
                
                <div class="device-info">
                    <div class="info-item">
                        <span class="info-label">IP Address</span>
                        <span class="info-value">${device.ip || 'Unknown'}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Type</span>
                        <span class="info-value">${this.formatDeviceType(device.type)}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">${deviceInfo.label1}</span>
                        <span class="info-value">${deviceInfo.value1}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">${deviceInfo.label2}</span>
                        <span class="info-value">${deviceInfo.value2}</span>
                    </div>
                </div>
                
                <div class="device-actions">
                    <button class="btn btn-primary device-action-btn" 
                            data-action="status" data-device="${device.id}">
                        <i class="fas fa-info-circle"></i> Status
                    </button>
                    <button class="btn btn-secondary device-action-btn" 
                            data-action="config" data-device="${device.id}">
                        <i class="fas fa-cog"></i> Config
                    </button>
                </div>
            </div>
        `;
    }
    
    getDeviceIcon(type) {
        const icons = {
            'aruba_ap500': 'fas fa-wifi',
            '3com_switch': 'fas fa-network-wired',
            'default': 'fas fa-server'
        };
        return icons[type] || icons.default;
    }
    
    formatDeviceType(type) {
        const types = {
            'aruba_ap500': 'Aruba AP 500',
            '3com_switch': '3Com Switch',
            'default': 'Unknown'
        };
        return types[type] || types.default;
    }
    
    getDeviceInfo(device) {
        if (device.type === 'aruba_ap500') {
            return {
                label1: 'Connected Clients',
                value1: device.clients_connected || 0,
                label2: 'SSIDs',
                value2: device.ssids ? device.ssids.length : 0
            };
        } else if (device.type === '3com_switch') {
            return {
                label1: 'Active Ports',
                value1: device.ports ? Object.keys(device.ports).length : 0,
                label2: 'VLANs',
                value2: device.vlans ? device.vlans.length : 0
            };
        }
        
        return {
            label1: 'Location',
            value1: device.location || 'Unknown',
            label2: 'Status',
            value2: device.status || 'Unknown'
        };
    }
    
    filterDevices(filter) {
        const cards = document.querySelectorAll('.device-card');
        
        cards.forEach(card => {
            let show = true;
            
            if (filter !== 'all') {
                if (filter === 'online' || filter === 'offline') {
                    show = card.classList.contains(filter);
                } else {
                    // Filter by device type
                    const deviceType = card.querySelector('.info-value').textContent;
                    show = deviceType.toLowerCase().includes(filter.replace('_', ' '));
                }
            }
            
            card.style.display = show ? 'block' : 'none';
        });
    }
    
    async handleDeviceAction(action, deviceId) {
        if (action === 'status') {
            await this.showDeviceStatus(deviceId);
        } else if (action === 'config') {
            this.switchTab('config');
            document.getElementById('configDeviceSelect').value = deviceId;
            await this.loadDeviceConfig(deviceId);
        }
    }
    
    async showDeviceStatus(deviceId) {
        try {
            this.showLoading(true);
            
            const response = await fetch(`${this.apiBase}/devices/${deviceId}/status`);
            const data = await response.json();
            
            if (data.success) {
                this.showDeviceStatusModal(deviceId, data.status);
            } else {
                throw new Error(data.error || 'Failed to get device status');
            }
        } catch (error) {
            console.error('Error getting device status:', error);
            this.showNotification('Error getting device status', 'error');
        } finally {
            this.showLoading(false);
        }
    }
    
    showDeviceStatusModal(deviceId, status) {
        // Create and show device status modal
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.id = 'deviceStatusModal';
        
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Device Status: ${deviceId}</h3>
                    <button class="close-btn" onclick="document.getElementById('deviceStatusModal').remove()">&times;</button>
                </div>
                <div class="modal-body">
                    <pre>${JSON.stringify(status, null, 2)}</pre>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="document.getElementById('deviceStatusModal').remove()">Close</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        modal.style.display = 'block';
    }
    
    updateOverviewCards() {
        const onlineDevices = this.devices.filter(d => d.status === 'online').length;
        const offlineDevices = this.devices.filter(d => d.status === 'offline' || d.status === 'error').length;
        const totalClients = this.devices
            .filter(d => d.type === 'aruba_ap500')
            .reduce((sum, d) => sum + (d.clients_connected || 0), 0);
        
        document.getElementById('onlineDevices').textContent = onlineDevices;
        document.getElementById('offlineDevices').textContent = offlineDevices;
        document.getElementById('clientCount').textContent = totalClients;
        document.getElementById('alertCount').textContent = this.alerts.length;
    }
    
    async loadDashboardData() {
        try {
            const response = await fetch(`${this.apiBase}/monitoring/dashboard`);
            const data = await response.json();
            
            if (data.success) {
                this.dashboardData = data.data;
            } else {
                console.warn('Failed to load dashboard data:', data.error);
            }
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }
    
    async loadAlerts() {
        try {
            const response = await fetch(`${this.apiBase}/alerts`);
            const data = await response.json();
            
            if (data.success) {
                this.alerts = data.alerts;
                this.renderAlerts();
            } else {
                console.warn('Failed to load alerts:', data.error);
            }
        } catch (error) {
            console.error('Error loading alerts:', error);
        }
    }
    
    renderAlerts() {
        const container = document.getElementById('alertsContainer');
        
        if (!this.alerts || this.alerts.length === 0) {
            container.innerHTML = `
                <div class="no-alerts">
                    <i class="fas fa-check-circle" style="font-size: 48px; color: #28a745; margin-bottom: 20px;"></i>
                    <h3>No active alerts</h3>
                    <p>All systems are running normally.</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.alerts.map(alert => this.createAlertItem(alert)).join('');
    }
    
    createAlertItem(alert) {
        const timeAgo = this.formatTimeAgo(alert.timestamp);
        
        return `
            <div class="alert-item ${alert.severity}">
                <div class="alert-header">
                    <span class="alert-severity ${alert.severity}">${alert.severity}</span>
                    <span class="alert-time">${timeAgo}</span>
                </div>
                <div class="alert-message">${alert.message}</div>
                <div class="alert-device">Device: ${alert.device_id}</div>
            </div>
        `;
    }
    
    formatTimeAgo(timestamp) {
        const now = new Date();
        const alertTime = new Date(timestamp);
        const diffMs = now - alertTime;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMins / 60);
        
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        return alertTime.toLocaleDateString();
    }
    
    loadMonitoringData() {
        // Initialize charts if not already done
        this.initializeCharts();
        
        // Update charts with current data
        this.updateCharts();
        
        // Update metrics table
        this.updateMetricsTable();
    }
    
    initializeCharts() {
        // Simple chart implementation using canvas
        const cpuCanvas = document.getElementById('cpuChart');
        const memoryCanvas = document.getElementById('memoryChart');
        
        if (cpuCanvas && !cpuCanvas.chartInitialized) {
            this.drawChart(cpuCanvas, 'CPU Usage', this.generateSampleData(), '#007bff');
            cpuCanvas.chartInitialized = true;
        }
        
        if (memoryCanvas && !memoryCanvas.chartInitialized) {
            this.drawChart(memoryCanvas, 'Memory Usage', this.generateSampleData(), '#28a745');
            memoryCanvas.chartInitialized = true;
        }
    }
    
    drawChart(canvas, title, data, color) {
        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;
        
        // Clear canvas
        ctx.clearRect(0, 0, width, height);
        
        // Draw background
        ctx.fillStyle = '#f8f9fa';
        ctx.fillRect(0, 0, width, height);
        
        // Draw grid lines
        ctx.strokeStyle = '#e9ecef';
        ctx.lineWidth = 1;
        
        for (let i = 0; i <= 10; i++) {
            const y = (height / 10) * i;
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(width, y);
            ctx.stroke();
        }
        
        // Draw data line
        if (data && data.length > 1) {
            ctx.strokeStyle = color;
            ctx.lineWidth = 2;
            ctx.beginPath();
            
            const stepX = width / (data.length - 1);
            const maxValue = Math.max(...data);
            
            data.forEach((value, index) => {
                const x = index * stepX;
                const y = height - (value / maxValue) * height;
                
                if (index === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            });
            
            ctx.stroke();
        }
    }
    
    generateSampleData() {
        // Generate sample data for demonstration
        const data = [];
        for (let i = 0; i < 20; i++) {
            data.push(Math.random() * 100);
        }
        return data;
    }
    
    updateCharts() {
        // This would update charts with real data
        // For now, just refresh with sample data
        this.initializeCharts();
    }
    
    updateMetricsTable() {
        const tbody = document.querySelector('#metricsTable tbody');
        
        if (!this.devices || this.devices.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align: center;">No devices available</td></tr>';
            return;
        }
        
        tbody.innerHTML = this.devices.map(device => {
            const type = this.formatDeviceType(device.type);
            const status = device.status || 'unknown';
            const cpu = device.cpu_usage || 0;
            const memory = device.memory_usage || 0;
            const temperature = device.temperature || 0;
            const clientsOrPorts = device.type === 'aruba_ap500' 
                ? (device.clients_connected || 0) 
                : (device.ports ? Object.keys(device.ports).length : 0);
            const lastSeen = device.last_seen ? new Date(device.last_seen).toLocaleString() : 'Never';
            
            return `
                <tr>
                    <td>${device.name || device.id}</td>
                    <td>${type}</td>
                    <td><span class="device-status ${status}">${status}</span></td>
                    <td>${cpu}%</td>
                    <td>${memory}%</td>
                    <td>${temperature}°C</td>
                    <td>${clientsOrPorts}</td>
                    <td>${lastSeen}</td>
                </tr>
            `;
        }).join('');
    }
    
    loadConfigurationTab() {
        // Populate device select dropdown
        const select = document.getElementById('configDeviceSelect');
        select.innerHTML = '<option value="">Select a device...</option>';
        
        this.devices.forEach(device => {
            const option = document.createElement('option');
            option.value = device.id;
            option.textContent = `${device.name || device.id} (${this.formatDeviceType(device.type)})`;
            select.appendChild(option);
        });
    }
    
    async loadDeviceConfig(deviceId) {
        if (!deviceId) {
            this.clearConfigEditor();
            return;
        }
        
        try {
            this.showLoading(true);
            
            const response = await fetch(`${this.apiBase}/devices/${deviceId}/config`);
            const data = await response.json();
            
            if (data.success) {
                this.displayDeviceConfig(data.config);
                this.showConfigActions(true);
            } else {
                throw new Error(data.error || 'Failed to load device configuration');
            }
        } catch (error) {
            console.error('Error loading device config:', error);
            this.showNotification('Error loading device configuration', 'error');
        } finally {
            this.showLoading(false);
        }
    }
    
    displayDeviceConfig(config) {
        const editor = document.getElementById('configEditor');
        editor.innerHTML = `<pre>${JSON.stringify(config, null, 2)}</pre>`;
    }
    
    clearConfigEditor() {
        const editor = document.getElementById('configEditor');
        editor.innerHTML = '<p class="placeholder-text">Select a device to view/edit configuration</p>';
        this.showConfigActions(false);
    }
    
    showConfigActions(show) {
        const actions = document.querySelectorAll('.editor-actions button');
        actions.forEach(btn => {
            btn.style.display = show ? 'inline-flex' : 'none';
        });
    }
    
    async backupDeviceConfig() {
        const deviceId = document.getElementById('configDeviceSelect').value;
        if (!deviceId) {
            this.showNotification('Please select a device first', 'warning');
            return;
        }
        
        try {
            const response = await fetch(`${this.apiBase}/devices/${deviceId}/backup`, {
                method: 'POST'
            });
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('Configuration backup created successfully', 'success');
            } else {
                throw new Error(data.error || 'Backup failed');
            }
        } catch (error) {
            console.error('Error backing up config:', error);
            this.showNotification('Error creating backup', 'error');
        }
    }
    
    async restoreDeviceConfig() {
        const deviceId = document.getElementById('configDeviceSelect').value;
        if (!deviceId) {
            this.showNotification('Please select a device first', 'warning');
            return;
        }
        
        // For now, just show a placeholder
        this.showNotification('Restore functionality not yet implemented', 'info');
    }
    
    saveDeviceConfig() {
        this.showNotification('Save functionality not yet implemented', 'info');
    }
    
    resetConfigEditor() {
        const deviceId = document.getElementById('configDeviceSelect').value;
        if (deviceId) {
            this.loadDeviceConfig(deviceId);
        }
    }
    
    clearAllAlerts() {
        this.alerts = [];
        this.renderAlerts();
        this.updateOverviewCards();
        this.showNotification('All alerts cleared', 'success');
    }
    
    showDiscoveryModal() {
        document.getElementById('discoveryModal').style.display = 'block';
    }
    
    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
        }
    }
    
    async startDeviceDiscovery() {
        const networkRange = document.getElementById('networkRange').value;
        
        if (!networkRange) {
            this.showNotification('Please enter a network range', 'warning');
            return;
        }
        
        try {
            // Show progress
            document.getElementById('discoveryProgress').style.display = 'block';
            document.getElementById('discoveryResults').style.display = 'none';
            document.getElementById('startDiscoveryBtn').disabled = true;
            
            const response = await fetch(`${this.apiBase}/devices/discover`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ network_range: networkRange })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showDiscoveryResults(data.discovered);
            } else {
                throw new Error(data.error || 'Discovery failed');
            }
        } catch (error) {
            console.error('Error during discovery:', error);
            this.showNotification('Error during device discovery', 'error');
        } finally {
            document.getElementById('discoveryProgress').style.display = 'none';
            document.getElementById('startDiscoveryBtn').disabled = false;
        }
    }
    
    showDiscoveryResults(discovered) {
        const container = document.getElementById('discoveryResults');
        
        if (discovered.length === 0) {
            container.innerHTML = '<p>No devices discovered in the specified range.</p>';
        } else {
            container.innerHTML = discovered.map(device => `
                <div class="discovery-item">
                    <div>
                        <strong>${device.ip}</strong>
                        ${device.name ? ` - ${device.name}` : ''}
                        ${device.type ? `<span class="device-type">${this.formatDeviceType(device.type)}</span>` : ''}
                    </div>
                    <div>${device.status || 'Unknown'}</div>
                </div>
            `).join('');
        }
        
        container.style.display = 'block';
        
        // Refresh devices list
        setTimeout(() => {
            this.loadDevices();
        }, 2000);
    }
    
    showLoading(show) {
        document.getElementById('loadingOverlay').style.display = show ? 'block' : 'none';
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas ${this.getNotificationIcon(type)}"></i>
            <span>${message}</span>
        `;
        
        // Style notification
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '15px 20px',
            borderRadius: '8px',
            backgroundColor: this.getNotificationColor(type),
            color: 'white',
            zIndex: '9999',
            boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            maxWidth: '400px',
            animation: 'slideInRight 0.3s ease'
        });
        
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'slideOutRight 0.3s ease';
                setTimeout(() => {
                    notification.remove();
                }, 300);
            }
        }, 5000);
    }
    
    getNotificationIcon(type) {
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        return icons[type] || icons.info;
    }
    
    getNotificationColor(type) {
        const colors = {
            success: '#28a745',
            error: '#dc3545',
            warning: '#ffc107',
            info: '#007bff'
        };
        return colors[type] || colors.info;
    }
    
    updateLastUpdated() {
        document.getElementById('lastUpdated').textContent = new Date().toLocaleTimeString();
    }
}

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(400px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(400px); opacity: 0; }
    }
    
    .no-devices, .no-alerts {
        text-align: center;
        padding: 60px 20px;
        color: #666;
        grid-column: 1 / -1;
    }
    
    .no-devices h3, .no-alerts h3 {
        margin-bottom: 10px;
        color: #333;
    }
`;
document.head.appendChild(style);

// Initialize the application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.networkManager = new NetworkDeviceManager();
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NetworkDeviceManager;
}