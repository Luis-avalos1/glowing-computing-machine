const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');
const si = require('systeminformation');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: "http://localhost:3000",
    methods: ["GET", "POST"]
  }
});

app.use(cors());
app.use(express.json());

// Store active connections
let connectedClients = 0;

io.on('connection', (socket) => {
  connectedClients++;
  console.log(`Client connected. Total: ${connectedClients}`);

  socket.on('disconnect', () => {
    connectedClients--;
    console.log(`Client disconnected. Total: ${connectedClients}`);
  });
});

// System metrics collection
async function getSystemMetrics() {
  try {
    const [cpu, memory, disk, network, currentLoad, osInfo, system, graphics, processes] = await Promise.all([
      si.cpu(),
      si.mem(),
      si.fsSize(),
      si.networkStats(),
      si.currentLoad(),
      si.osInfo(),
      si.system(),
      si.graphics(),
      si.processes()
    ]);

    return {
      timestamp: Date.now(),
      cpu: {
        brand: cpu.brand,
        cores: cpu.cores,
        physicalCores: cpu.physicalCores,
        usage: currentLoad.currentLoad,
        speed: cpu.speed,
        temperature: currentLoad.currentLoadUser || 0
      },
      memory: {
        total: memory.total,
        used: memory.used,
        available: memory.available,
        percentage: (memory.used / memory.total) * 100
      },
      disk: disk.map(d => ({
        fs: d.fs,
        size: d.size,
        used: d.used,
        available: d.available,
        percentage: (d.used / d.size) * 100
      })),
      network: network.map(n => ({
        iface: n.iface,
        rx_sec: n.rx_sec || 0,
        tx_sec: n.tx_sec || 0
      })),
      device: {
        hostname: osInfo.hostname,
        platform: osInfo.platform,
        arch: osInfo.arch,
        kernel: osInfo.kernel,
        uptime: osInfo.uptime,
        manufacturer: system.manufacturer,
        model: system.model,
        version: system.version,
        serial: system.serial
      },
      processes: {
        all: processes.all,
        running: processes.running,
        sleeping: processes.sleeping,
        list: processes.list.slice(0, 10).map(p => ({
          pid: p.pid,
          name: p.name,
          cpu: p.cpu,
          mem: p.mem
        }))
      },
      graphics: graphics.controllers.map(g => ({
        vendor: g.vendor,
        model: g.model,
        vram: g.vram
      }))
    };
  } catch (error) {
    console.error('Error getting system metrics:', error);
    return null;
  }
}

// Emit system metrics every second
setInterval(async () => {
  if (connectedClients > 0) {
    const metrics = await getSystemMetrics();
    if (metrics) {
      io.emit('systemMetrics', metrics);
    }
  }
}, 1000);

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'OK', connectedClients });
});

const PORT = process.env.PORT || 3001;
server.listen(PORT, () => {
  console.log(`🚀 Glowing Computing Machine server running on port ${PORT}`);
  console.log(`🔥 System monitoring active - prepare for holographic awesomeness!`);
});