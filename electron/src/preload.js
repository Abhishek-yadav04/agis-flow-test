const { contextBridge, ipcRenderer } = require('electron');

// Secure API bridge between frontend and backend
contextBridge.exposeInMainWorld('electronAPI', {
  // Project management
  getProjects: () => ipcRenderer.invoke('get-projects'),
  createProject: (data) => ipcRenderer.invoke('create-project', data),
  
  // Experiment management
  getExperiments: (projectId) => ipcRenderer.invoke('get-experiments', projectId),
  createExperiment: (data) => ipcRenderer.invoke('create-experiment', data),
  
  // Adversarial FL
  startAdversarialExperiment: (config) => ipcRenderer.invoke('start-adversarial-experiment', config),
  getAdversarialResults: (experimentId) => ipcRenderer.invoke('get-adversarial-results', experimentId),
  
  // Data management
  loadDataset: (path) => ipcRenderer.invoke('load-dataset', path),
  getDatasetInfo: (datasetId) => ipcRenderer.invoke('get-dataset-info', datasetId),
  
  // Reproducibility
  exportResults: (experimentId) => ipcRenderer.invoke('export-results', experimentId),
  generateLatexReport: (experimentId) => ipcRenderer.invoke('generate-latex-report', experimentId),
  
  // Real-time updates
  onExperimentUpdate: (callback) => {
    ipcRenderer.on('experiment-update', callback);
  },
  
  onAttackDetected: (callback) => {
    ipcRenderer.on('attack-detected', callback);
  },
  
  // Cleanup
  removeAllListeners: (channel) => {
    ipcRenderer.removeAllListeners(channel);
  }
});