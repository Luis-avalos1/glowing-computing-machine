import React, { useRef, useEffect } from 'react';
import * as THREE from 'three';
import './HolographicDisplay.css';

interface SystemMetrics {
  timestamp: number;
  cpu: {
    brand: string;
    cores: number;
    usage: number;
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
}

interface Props {
  metrics: SystemMetrics;
}

const HolographicDisplay: React.FC<Props> = ({ metrics }) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const animationRef = useRef<number | null>(null);

  useEffect(() => {
    if (!mountRef.current) return;

    // Scene setup
    const scene = new THREE.Scene();
    sceneRef.current = scene;

    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    rendererRef.current = renderer;
    
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setClearColor(0x000000, 0);
    mountRef.current.appendChild(renderer.domElement);

    // Create holographic grid
    const gridHelper = new THREE.GridHelper(20, 20, 0x00ffff, 0x004444);
    gridHelper.material.opacity = 0.3;
    gridHelper.material.transparent = true;
    scene.add(gridHelper);

    // Camera position
    camera.position.set(0, 10, 10);
    camera.lookAt(0, 0, 0);

    // Animation loop
    const animate = () => {
      animationRef.current = requestAnimationFrame(animate);
      
      // Rotate grid for holographic effect
      gridHelper.rotation.y += 0.002;
      
      renderer.render(scene, camera);
    };

    animate();

    // Handle resize
    const handleResize = () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      if (mountRef.current && renderer.domElement) {
        mountRef.current.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, []);

  const formatBytes = (bytes: number) => {
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    if (bytes === 0) return '0 B';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatSpeed = (bytesPerSec: number) => {
    return formatBytes(bytesPerSec) + '/s';
  };

  return (
    <div className="holographic-display">
      <div ref={mountRef} className="three-canvas" />
      
      <div className="metrics-overlay">
        <div className="metrics-grid">
          {/* CPU Section */}
          <div className="metric-card cpu-card">
            <div className="metric-header">
              <h3 className="metric-title">NEURAL PROCESSOR</h3>
              <div className="metric-brand">{metrics.cpu.brand}</div>
            </div>
            <div className="metric-content">
              <div className="circular-progress">
                <svg className="progress-ring" width="120" height="120">
                  <circle
                    className="progress-ring-circle background"
                    stroke="rgba(0, 255, 255, 0.2)"
                    strokeWidth="8"
                    fill="transparent"
                    r="52"
                    cx="60"
                    cy="60"
                  />
                  <circle
                    className="progress-ring-circle"
                    stroke="url(#cpuGradient)"
                    strokeWidth="8"
                    fill="transparent"
                    r="52"
                    cx="60"
                    cy="60"
                    strokeDasharray={`${2 * Math.PI * 52}`}
                    strokeDashoffset={`${2 * Math.PI * 52 * (1 - metrics.cpu.usage / 100)}`}
                    transform="rotate(-90 60 60)"
                  />
                  <defs>
                    <linearGradient id="cpuGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stopColor="#00ffff" />
                      <stop offset="100%" stopColor="#ff0080" />
                    </linearGradient>
                  </defs>
                </svg>
                <div className="progress-text">
                  <span className="progress-value">{metrics.cpu.usage.toFixed(1)}%</span>
                  <span className="progress-label">LOAD</span>
                </div>
              </div>
              <div className="metric-details">
                <div className="detail-item">
                  <span className="detail-label">CORES:</span>
                  <span className="detail-value">{metrics.cpu.cores}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Memory Section */}
          <div className="metric-card memory-card">
            <div className="metric-header">
              <h3 className="metric-title">MEMORY BANKS</h3>
            </div>
            <div className="metric-content">
              <div className="circular-progress">
                <svg className="progress-ring" width="120" height="120">
                  <circle
                    className="progress-ring-circle background"
                    stroke="rgba(0, 255, 0, 0.2)"
                    strokeWidth="8"
                    fill="transparent"
                    r="52"
                    cx="60"
                    cy="60"
                  />
                  <circle
                    className="progress-ring-circle"
                    stroke="url(#memoryGradient)"
                    strokeWidth="8"
                    fill="transparent"
                    r="52"
                    cx="60"
                    cy="60"
                    strokeDasharray={`${2 * Math.PI * 52}`}
                    strokeDashoffset={`${2 * Math.PI * 52 * (1 - metrics.memory.percentage / 100)}`}
                    transform="rotate(-90 60 60)"
                  />
                  <defs>
                    <linearGradient id="memoryGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stopColor="#00ff00" />
                      <stop offset="100%" stopColor="#ffff00" />
                    </linearGradient>
                  </defs>
                </svg>
                <div className="progress-text">
                  <span className="progress-value">{metrics.memory.percentage.toFixed(1)}%</span>
                  <span className="progress-label">USED</span>
                </div>
              </div>
              <div className="metric-details">
                <div className="detail-item">
                  <span className="detail-label">TOTAL:</span>
                  <span className="detail-value">{formatBytes(metrics.memory.total)}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">USED:</span>
                  <span className="detail-value">{formatBytes(metrics.memory.used)}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Network Section */}
          <div className="metric-card network-card">
            <div className="metric-header">
              <h3 className="metric-title">DATA STREAMS</h3>
            </div>
            <div className="metric-content">
              {metrics.network.slice(0, 2).map((net, index) => (
                <div key={net.iface} className="network-interface">
                  <div className="interface-name">{net.iface}</div>
                  <div className="network-speeds">
                    <div className="speed-item download">
                      <span className="speed-label">↓ RX:</span>
                      <span className="speed-value">{formatSpeed(net.rx_sec)}</span>
                    </div>
                    <div className="speed-item upload">
                      <span className="speed-label">↑ TX:</span>
                      <span className="speed-value">{formatSpeed(net.tx_sec)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Disk Section */}
          <div className="metric-card disk-card">
            <div className="metric-header">
              <h3 className="metric-title">STORAGE UNITS</h3>
            </div>
            <div className="metric-content">
              {metrics.disk.slice(0, 3).map((disk, index) => (
                <div key={disk.fs} className="disk-item">
                  <div className="disk-name">{disk.fs}</div>
                  <div className="disk-bar">
                    <div 
                      className="disk-usage"
                      style={{ width: `${disk.percentage}%` }}
                    ></div>
                  </div>
                  <div className="disk-details">
                    <span>{formatBytes(disk.used)} / {formatBytes(disk.size)}</span>
                    <span>{disk.percentage.toFixed(1)}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HolographicDisplay;