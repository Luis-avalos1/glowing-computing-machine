import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import SystemMonitor from './components/SystemMonitor';
import './App.css';

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

const socket = io('http://localhost:3001');

function App() {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    socket.on('connect', () => {
      setIsConnected(true);
      console.log('🔗 Connected to Glowing Computing Machine');
    });

    socket.on('disconnect', () => {
      setIsConnected(false);
      console.log('💔 Disconnected from server');
    });

    socket.on('systemMetrics', (data: SystemMetrics) => {
      setMetrics(data);
    });

    return () => {
      socket.off('connect');
      socket.off('disconnect');
      socket.off('systemMetrics');
    };
  }, []);

  return (
    <div className="App">
      {metrics ? (
        <SystemMonitor metrics={metrics} />
      ) : (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading system metrics...</p>
        </div>
      )}
    </div>
  );
}

export default App;
