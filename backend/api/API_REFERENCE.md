# 📡 AgisFL Enterprise - API Reference

## Base URL
```
http://127.0.0.1:8001
```

## Authentication
- JWT-based authentication
- College Project Mode: Simplified auth
- Production Mode: Full RBAC

## Core Endpoints

### 🏠 Dashboard & System

#### Get Dashboard Data
```http
GET /api/dashboard
```
**Response**: Complete dashboard with FL metrics, security stats, and system health

#### Health Check
```http
GET /api/health
```
**Response**: System status and uptime

#### System Metrics
```http
GET /api/system/metrics
```
**Response**: CPU, memory, disk usage, and performance stats

### 🤖 Federated Learning

#### FL Strategies
```http
GET /api/fl/strategies
```
**Response**: Available FL algorithms (FedAvg, FedProx, FedNova)

#### Experiments
```http
GET /api/experiments
```
**Response**: ML experiments, results, and training progress

#### Research Algorithms
```http
GET /api/research/enterprise/research-algorithms
```
**Response**: Advanced FL research algorithms and methodologies

### 🛡️ Security & Threats

#### Security Metrics
```http
GET /api/security/metrics
```
**Response**: Security performance, detection rates, false positives

#### Threat Detection
```http
GET /api/threats
GET /api/security/threats
```
**Response**: Real-time threats, alerts, and security incidents

### 🌐 Network Monitoring

#### Network Statistics
```http
GET /api/network/stats
```
**Response**: Bandwidth, latency, packet loss, connection stats

#### Packet Analysis
```http
GET /api/network/packets
```
**Response**: Network packet analysis and traffic patterns

### 📊 Dataset Management

#### List Datasets
```http
GET /api/datasets
```
**Response**: Available datasets for FL training

#### Upload Dataset
```http
POST /api/datasets/upload
Content-Type: multipart/form-data

{
  "file": <dataset_file>,
  "name": "dataset_name",
  "description": "Dataset description"
}
```

#### Delete Dataset
```http
DELETE /api/datasets/{dataset_id}
```

### 🔧 Settings & Configuration

#### Get Settings
```http
GET /api/settings
```
**Response**: Application configuration and preferences

#### Update Settings
```http
POST /api/settings
Content-Type: application/json

{
  "theme": "dark",
  "notifications": true,
  "auto_refresh": 5000
}
```

### 🔗 Integrations

#### Integration Overview
```http
GET /api/integrations/overview
```
**Response**: Status of external integrations (CrowdStrike, FireEye, etc.)

## WebSocket Endpoints

### Real-time Updates
```javascript
ws://127.0.0.1:8001/ws/dashboard
```
**Events**: Live dashboard updates, FL progress, security alerts

### FL Training Progress
```javascript
ws://127.0.0.1:8001/ws/fl-training
```
**Events**: Real-time federated learning training updates

## Response Formats

### Standard Success Response
```json
{
  "status": "success",
  "data": { ... },
  "timestamp": "2025-01-27T10:30:00Z"
}
```

### Error Response
```json
{
  "status": "error",
  "message": "Error description",
  "code": "ERROR_CODE",
  "timestamp": "2025-01-27T10:30:00Z"
}
```

## College Project Mode Features

When `COLLEGE_PROJECT=true`:

- Enhanced real-time monitoring
- Detailed FL training visualization
- Comprehensive security metrics
- Optimized response times for demos

## Example Usage

### JavaScript/Fetch
```javascript
// Get dashboard data
const response = await fetch('http://127.0.0.1:8001/api/dashboard');
const data = await response.json();

// WebSocket connection
const ws = new WebSocket('ws://127.0.0.1:8001/ws/dashboard');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Real-time update:', data);
};
```

### Python/Requests
```python
import requests

# Get system metrics
response = requests.get('http://127.0.0.1:8001/api/system/metrics')
metrics = response.json()

# Upload dataset
files = {'file': open('dataset.csv', 'rb')}
data = {'name': 'Test Dataset', 'description': 'Sample data'}
response = requests.post('http://127.0.0.1:8001/api/datasets/upload', 
                        files=files, data=data)
```

### cURL
```bash
# Health check
curl http://127.0.0.1:8001/api/health

# Get FL strategies
curl http://127.0.0.1:8001/api/fl/strategies

# Upload dataset
curl -X POST http://127.0.0.1:8001/api/datasets/upload \
  -F "file=@dataset.csv" \
  -F "name=Sample Dataset"
```

## Rate Limits

- **Development**: No limits
- **Production**: 1000 requests/hour per IP
- **WebSocket**: 100 connections per IP

## Interactive Documentation

Visit http://127.0.0.1:8001/docs for:
- Interactive API testing
- Request/response schemas
- Authentication testing
- Real-time API exploration

---

**Pro Tip**: Use the interactive docs at `/docs` for live API testing during demonstrations!