import React from 'react';
import './SystemMonitor.css';

interface SystemMetrics {
  timestamp: number;
  cpu: {
    brand: string;
    cores: number;
    physicalCores: number;
    usage: number;
    speed: number;
    temperature: number;
  };
  memory: {
    total: number;
    used: number;
    available: number;
    percentage: number;
  };
  disk: Array<{
    fs: string;
    size: number;
    used: number;
    available: number;
    percentage: number;
  }>;
  network: Array<{
    iface: string;
    rx_sec: number;
    tx_sec: number;
  }>;
  device: {
    hostname: string;
    platform: string;
    arch: string;
    kernel: string;
    uptime: number;
    manufacturer: string;
    model: string;
    version: string;
    serial: string;
  };
  processes: {
    all: number;
    running: number;
    sleeping: number;
    list: Array<{
      pid: number;
      name: string;
      cpu: number;
      mem: number;
    }>;
  };
  graphics: Array<{
    vendor: string;
    model: string;
    vram: number;
  }>;
}

interface Props {
  metrics: SystemMetrics;
}

const SystemMonitor: React.FC<Props> = ({ metrics }) => {
  const formatBytes = (bytes: number): string => {
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    if (bytes === 0) return '0 B';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatSpeed = (bytesPerSec: number): string => {
    return formatBytes(bytesPerSec) + '/s';
  };

  const getUsageColor = (percentage: number): string => {
    if (percentage < 30) return '#22c55e';
    if (percentage < 60) return '#3b82f6';
    if (percentage < 80) return '#fbbf24';
    return '#ef4444';
  };

  const getCPUColor = (percentage: number): string => {
    if (percentage < 30) return 'linear-gradient(90deg, #22c55e, #34d399)';
    if (percentage < 60) return 'linear-gradient(90deg, #3b82f6, #60a5fa)';
    if (percentage < 80) return 'linear-gradient(90deg, #fbbf24, #fcd34d)';
    return 'linear-gradient(90deg, #ef4444, #f87171)';
  };

  const getMemoryColor = (percentage: number): string => {
    if (percentage < 30) return 'linear-gradient(90deg, #22c55e, #34d399)';
    if (percentage < 60) return 'linear-gradient(90deg, #06b6d4, #22d3ee)';
    if (percentage < 80) return 'linear-gradient(90deg, #fbbf24, #fcd34d)';
    return 'linear-gradient(90deg, #ef4444, #f87171)';
  };

  const formatUptime = (seconds: number): string => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${days}d ${hours}h ${minutes}m`;
  };

  return (
    <div className="system-monitor">
      <div className="monitor-container">
        {/* Top Row - Device Info */}
        <div className="top-section">
          <div className="metric-panel device-panel">
            <div className="panel-header">
              <h3>DEVICE INFORMATION</h3>
            </div>
            <div className="device-grid">
              <div className="device-item">
                <span className="device-label">Hostname:</span>
                <span className="device-value">{metrics.device.hostname}</span>
              </div>
              <div className="device-item">
                <span className="device-label">System:</span>
                <span className="device-value">{metrics.device.platform} {metrics.device.arch}</span>
              </div>
              <div className="device-item">
                <span className="device-label">Manufacturer:</span>
                <span className="device-value">{metrics.device.manufacturer || 'Unknown'}</span>
              </div>
              <div className="device-item">
                <span className="device-label">Model:</span>
                <span className="device-value">{metrics.device.model || 'Unknown'}</span>
              </div>
              <div className="device-item">
                <span className="device-label">Kernel:</span>
                <span className="device-value">{metrics.device.kernel}</span>
              </div>
              <div className="device-item">
                <span className="device-label">Uptime:</span>
                <span className="device-value">{formatUptime(metrics.device.uptime)}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Main Grid */}
        <div className="main-grid">
          {/* CPU Panel */}
          <div className="metric-panel cpu-panel">
            <div className="panel-header">
              <h3>PROCESSOR</h3>
              <span className="metric-value">{metrics.cpu.usage.toFixed(1)}%</span>
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill cpu-progress"
                style={{ 
                  width: `${metrics.cpu.usage}%`,
                  background: getCPUColor(metrics.cpu.usage),
                  boxShadow: `0 0 20px ${getUsageColor(metrics.cpu.usage)}40`
                }}
              />
            </div>
            <div className="panel-details">
              <div className="detail-row">
                <span>Brand:</span>
                <span>{metrics.cpu.brand}</span>
              </div>
              <div className="detail-row">
                <span>Cores:</span>
                <span>{metrics.cpu.cores} ({metrics.cpu.physicalCores} physical)</span>
              </div>
              <div className="detail-row">
                <span>Speed:</span>
                <span>{metrics.cpu.speed} GHz</span>
              </div>
            </div>
          </div>

          {/* Memory Panel */}
          <div className="metric-panel memory-panel">
            <div className="panel-header">
              <h3>MEMORY</h3>
              <span className="metric-value">{metrics.memory.percentage.toFixed(1)}%</span>
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill memory-progress"
                style={{ 
                  width: `${metrics.memory.percentage}%`,
                  background: getMemoryColor(metrics.memory.percentage),
                  boxShadow: `0 0 20px ${getUsageColor(metrics.memory.percentage)}40`
                }}
              />
            </div>
            <div className="panel-details">
              <div className="detail-row">
                <span>Used:</span>
                <span>{formatBytes(metrics.memory.used)}</span>
              </div>
              <div className="detail-row">
                <span>Available:</span>
                <span>{formatBytes(metrics.memory.available)}</span>
              </div>
              <div className="detail-row">
                <span>Total:</span>
                <span>{formatBytes(metrics.memory.total)}</span>
              </div>
            </div>
          </div>

          {/* Storage Panel */}
          <div className="metric-panel storage-panel">
            <div className="panel-header">
              <h3>STORAGE</h3>
            </div>
            <div className="storage-list">
              {metrics.disk.slice(0, 4).map((disk, index) => (
                <div key={disk.fs} className="storage-item">
                  <div className="storage-header">
                    <span className="storage-name">{disk.fs}</span>
                    <span className="storage-percentage">{disk.percentage.toFixed(1)}%</span>
                  </div>
                  <div className="storage-bar">
                    <div 
                      className="storage-fill"
                      style={{ 
                        width: `${disk.percentage}%`,
                        background: `linear-gradient(90deg, ${getUsageColor(disk.percentage)}, ${getUsageColor(disk.percentage)}aa)`,
                        boxShadow: `0 0 15px ${getUsageColor(disk.percentage)}30`
                      }}
                    />
                  </div>
                  <div className="storage-info">
                    <span>{formatBytes(disk.used)} / {formatBytes(disk.size)}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Network Panel */}
          <div className="metric-panel network-panel">
            <div className="panel-header">
              <h3>NETWORK</h3>
            </div>
            <div className="network-list">
              {metrics.network.slice(0, 3).map((net, index) => (
                <div key={net.iface} className="network-item">
                  <div className="network-header">
                    <span className="network-name">{net.iface}</span>
                  </div>
                  <div className="network-stats">
                    <div className="network-stat">
                      <span className="network-label">↓ RX:</span>
                      <span className="network-value">{formatSpeed(net.rx_sec)}</span>
                    </div>
                    <div className="network-stat">
                      <span className="network-label">↑ TX:</span>
                      <span className="network-value">{formatSpeed(net.tx_sec)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Processes Panel */}
          <div className="metric-panel processes-panel">
            <div className="panel-header">
              <h3>PROCESSES</h3>
              <span className="metric-value">{metrics.processes.all}</span>
            </div>
            <div className="process-summary">
              <div className="process-stat">
                <span>Running: {metrics.processes.running}</span>
                <span>Sleeping: {metrics.processes.sleeping}</span>
              </div>
            </div>
            <div className="process-list">
              {metrics.processes.list.slice(0, 8).map((process, index) => (
                <div key={process.pid} className="process-item">
                  <div className="process-info">
                    <span className="process-name">{process.name}</span>
                    <span className="process-pid">PID: {process.pid}</span>
                  </div>
                  <div className="process-usage">
                    <span className="process-cpu">{process.cpu.toFixed(1)}%</span>
                    <span className="process-mem">{process.mem.toFixed(1)}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Graphics Panel */}
          {metrics.graphics.length > 0 && (
            <div className="metric-panel graphics-panel">
              <div className="panel-header">
                <h3>GRAPHICS</h3>
              </div>
              <div className="graphics-list">
                {metrics.graphics.map((gpu, index) => (
                  <div key={index} className="graphics-item">
                    <div className="graphics-info">
                      <div className="detail-row">
                        <span>Vendor:</span>
                        <span>{gpu.vendor}</span>
                      </div>
                      <div className="detail-row">
                        <span>Model:</span>
                        <span>{gpu.model}</span>
                      </div>
                      <div className="detail-row">
                        <span>VRAM:</span>
                        <span>{formatBytes(gpu.vram * 1024 * 1024)}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SystemMonitor;