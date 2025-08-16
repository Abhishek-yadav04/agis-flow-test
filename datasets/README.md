# AgisFL Enterprise Datasets

This folder contains datasets for Federated Learning Intrusion Detection System training and testing.

## 📊 **Available Datasets**

### 1. Network Traffic Dataset
- **File**: `network_traffic_dataset.csv`
- **Size**: ~150MB
- **Samples**: 50,000 network packets
- **Features**: 25 features including packet size, protocol, flags, etc.
- **Use Case**: Network intrusion detection training

### 2. Malware Detection Dataset
- **File**: `malware_detection_dataset.csv`
- **Size**: ~89MB
- **Samples**: 30,000 files (benign and malicious)
- **Features**: 30 features including entropy, strings, imports, etc.
- **Use Case**: Malware classification training

### 3. Behavioral Analysis Dataset
- **File**: `behavioral_analysis_dataset.csv`
- **Size**: ~200MB
- **Samples**: 75,000 user sessions
- **Features**: 40 features including timing, patterns, anomalies
- **Use Case**: Behavioral threat detection

## 🚀 **Adding Your Own Datasets**

### Supported Formats
- **CSV**: Comma-separated values (recommended)
- **JSON**: JavaScript Object Notation
- **Parquet**: Columnar storage format
- **HDF5**: Hierarchical Data Format

### Dataset Requirements
1. **Data Quality**: Clean, well-structured data
2. **Feature Engineering**: Relevant features for FL-IDS
3. **Privacy**: No personally identifiable information
4. **Documentation**: Clear description and metadata

### Upload Process
1. Place your dataset file in this folder
2. Update the metadata in `datasets_metadata.json`
3. The system will automatically detect and index it
4. Use the Dataset Manager in the frontend to manage

## 🔒 **Privacy & Security**

### Data Protection
- All datasets are encrypted at rest
- Access is controlled via role-based permissions
- No raw data is shared during federated learning
- Only model updates are transmitted

### Compliance
- GDPR compliant data handling
- HIPAA compatible for healthcare data
- SOX compliant for financial data
- PCI-DSS compliant for payment data

## 📈 **Performance Metrics**

### Dataset Quality Scoring
- **Completeness**: Percentage of non-null values
- **Consistency**: Data format and type consistency
- **Accuracy**: Ground truth validation
- **Relevance**: Feature importance for FL-IDS

### FL Suitability Score
- **Data Distribution**: Balance across classes
- **Feature Diversity**: Variety of patterns
- **Privacy Level**: Anonymization quality
- **Update Frequency**: Real-time capability

## 🧪 **Research & Development**

### Academic Use
- Perfect for research projects
- Supports reproducible experiments
- Enables algorithm comparison
- Facilitates collaboration

### Industry Applications
- Production-ready datasets
- Scalable to enterprise needs
- Supports real-time updates
- Enables continuous learning

## 📚 **Documentation**

### Dataset Schemas
- Detailed feature descriptions
- Data type specifications
- Value ranges and constraints
- Example records

### Usage Examples
- Training scripts
- Evaluation procedures
- Performance benchmarks
- Best practices

---

**Note**: This folder is designed to work seamlessly with the AgisFL Enterprise platform. Datasets added here will automatically be available for federated learning training and evaluation.
