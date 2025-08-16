# 🚀 AgisFL Enterprise - Quick Start Guide

## Overview
AgisFL Enterprise is a Federated Learning Intrusion Detection System designed for enterprise cybersecurity. This guide gets you running in under 5 minutes.

## ⚡ Instant Setup

### Prerequisites
- Python 3.8+ installed
- Windows environment
- 4GB RAM minimum

### One-Command Start
```bash
START_AGISFL.bat
```

Choose option **1** for Quick Start (fastest demo mode)

## 🎯 Access Points

Once started, access these URLs:

| Service | URL | Purpose |
|---------|-----|---------|
| **Main Dashboard** | http://127.0.0.1:8001/app | Complete FL-IDS interface |
| **API Documentation** | http://127.0.0.1:8001/docs | Interactive API explorer |
| **Health Check** | http://127.0.0.1:8001/api/health | System status |

## 🔍 Key Features Demo

### 1. Dashboard Overview
- Real-time FL training metrics
- Network security monitoring  
- Threat detection alerts
- System performance stats

### 2. Federated Learning Engine
- Multi-client FL simulation
- Privacy-preserving algorithms
- Model aggregation visualization

### 3. Security Monitoring
- Network packet analysis
- Anomaly detection
- Threat intelligence integration

## 🎓 College Project Mode

The system automatically runs in **College Project Mode** with:
- Enhanced real-time monitoring
- Detailed FL training progress
- Comprehensive security metrics
- Optimized for presentations

## 🛠️ Startup Modes

| Mode | Command | Use Case |
|------|---------|----------|
| Quick Start | `1` | Fast demo (2 minutes) |
| Production | `2` | Full features |
| Development | `3` | Hot reload enabled |
| Desktop App | `5` | Native application |

## 📊 Demo Scenarios

### Scenario 1: FL Training Demo
1. Navigate to Dashboard
2. View "FL Training Progress" 
3. Show distributed client metrics
4. Demonstrate privacy preservation

### Scenario 2: Security Monitoring
1. Access "Security Center"
2. View real-time threat detection
3. Show network analysis
4. Demonstrate anomaly detection

### Scenario 3: API Integration
1. Open http://127.0.0.1:8001/docs
2. Test `/api/dashboard` endpoint
3. Show real-time data APIs
4. Demonstrate WebSocket updates

## 🔧 Troubleshooting

### Common Issues
- **Port 8001 busy**: Kill existing processes or restart
- **Python not found**: Ensure Python 3.8+ in PATH
- **Dependencies fail**: Run mode 2 for full installation

### Quick Fixes
```bash
# Kill existing processes
taskkill /f /im python.exe
taskkill /f /im uvicorn.exe

# Restart
START_AGISFL.bat
```

## 📱 Desktop Application

For native desktop experience:
```bash
START_AGISFL.bat
# Choose option 5
```

Features:
- Offline capability
- Native Windows integration
- Professional presentation mode

## 🎯 Evaluation Points

### Technical Excellence
- ✅ Full-stack implementation (React + FastAPI)
- ✅ Real-time WebSocket communication
- ✅ Federated Learning algorithms
- ✅ Security monitoring engine
- ✅ Desktop application (Electron)

### Innovation
- ✅ Privacy-preserving ML
- ✅ Distributed threat detection
- ✅ Real-time FL visualization
- ✅ Enterprise-grade architecture

### Practical Application
- ✅ Cybersecurity focus
- ✅ Scalable FL framework
- ✅ Production-ready code
- ✅ Comprehensive testing

## 📞 Support

- **Logs**: `backend/logs/agisfl_enterprise.log`
- **Configuration**: Environment variables in startup script
- **API Reference**: http://127.0.0.1:8001/docs (when running)

---

**Ready to impress? Run `START_AGISFL.bat` and choose option 1!** 🚀