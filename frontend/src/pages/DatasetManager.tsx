import React, { useState, useEffect } from 'react';
import { Upload, Database, BarChart3, Download, Trash2, Eye, Settings, Plus } from 'lucide-react';

interface Dataset {
  id: string;
  name: string;
  description: string;
  size_mb: number;
  samples: number;
  features: number;
  quality_score: number;
  fl_suitability: number;
  privacy_level: string;
  upload_date: string;
  status: string;
}

const DatasetManager: React.FC = () => {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [selectedDataset, setSelectedDataset] = useState<Dataset | null>(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  useEffect(() => {
    fetchDatasets();
  }, []);

  const fetchDatasets = async () => {
    try {
      const response = await fetch('/api/datasets');
      if (response.ok) {
        const data = await response.json();
        setDatasets(data);
      }
    } catch (error) {
      console.error('Failed to fetch datasets:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setUploadFile(file);
      setShowUploadModal(true);
    }
  };

  const uploadDataset = async () => {
    if (!uploadFile) return;

    setUploading(true);
    setUploadProgress(0);

    const formData = new FormData();
    formData.append('file', uploadFile);

    try {
      const response = await fetch('/api/datasets/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Upload successful:', result);
        setShowUploadModal(false);
        setUploadFile(null);
        fetchDatasets(); // Refresh the list
      }
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const downloadDataset = async (datasetId: string) => {
    try {
      const response = await fetch(`/api/datasets/${datasetId}/download`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `dataset_${datasetId}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Download failed:', error);
    }
  };

  const deleteDataset = async (datasetId: string) => {
    if (window.confirm('Are you sure you want to delete this dataset?')) {
      try {
        const response = await fetch(`/api/datasets/${datasetId}`, {
          method: 'DELETE',
        });
        if (response.ok) {
          fetchDatasets(); // Refresh the list
        }
      } catch (error) {
        console.error('Delete failed:', error);
      }
    }
  };

  const getQualityColor = (score: number) => {
    if (score >= 90) return 'text-green-500';
    if (score >= 75) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getPrivacyColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'low': return 'text-green-500';
      case 'medium': return 'text-yellow-500';
      case 'high': return 'text-red-500';
      default: return 'text-gray-500';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Dataset Management</h1>
          <p className="text-gray-400 mt-2">Manage and analyze datasets for federated learning</p>
        </div>
        <button
          onClick={() => setShowUploadModal(true)}
          className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
        >
          <Plus className="w-5 h-5" />
          <span>Upload Dataset</span>
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center space-x-3">
            <Database className="w-8 h-8 text-blue-400" />
            <div>
              <p className="text-gray-400 text-sm">Total Datasets</p>
              <p className="text-2xl font-bold text-white">{datasets.length}</p>
            </div>
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center space-x-3">
            <BarChart3 className="w-8 h-8 text-green-400" />
            <div>
              <p className="text-gray-400 text-sm">Total Samples</p>
              <p className="text-2xl font-bold text-white">
                {datasets.reduce((sum, ds) => sum + ds.samples, 0).toLocaleString()}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center space-x-3">
            <Settings className="w-8 h-8 text-purple-400" />
            <div>
              <p className="text-gray-400 text-sm">Avg Quality</p>
              <p className="text-2xl font-bold text-white">
                {datasets.length > 0 
                  ? Math.round(datasets.reduce((sum, ds) => sum + ds.quality_score, 0) / datasets.length)
                  : 0}%
              </p>
            </div>
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center space-x-3">
            <Upload className="w-8 h-8 text-orange-400" />
            <div>
              <p className="text-gray-400 text-sm">Total Size</p>
              <p className="text-2xl font-bold text-white">
                {Math.round(datasets.reduce((sum, ds) => sum + ds.size_mb, 0))} MB
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Datasets Table */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-700">
          <h3 className="text-lg font-semibold text-white">Available Datasets</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-700/50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Dataset
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Size
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Samples
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Quality
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  FL Suitability
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Privacy
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {datasets.map((dataset) => (
                <tr key={dataset.id} className="hover:bg-gray-700/30">
                  <td className="px-6 py-4">
                    <div>
                      <p className="text-sm font-medium text-white">{dataset.name}</p>
                      <p className="text-sm text-gray-400">{dataset.description}</p>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-300">
                    {dataset.size_mb} MB
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-300">
                    {dataset.samples.toLocaleString()}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`text-sm font-medium ${getQualityColor(dataset.quality_score)}`}>
                      {dataset.quality_score}%
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-sm font-medium text-blue-400">
                      {(dataset.fl_suitability * 100).toFixed(1)}%
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`text-sm font-medium ${getPrivacyColor(dataset.privacy_level)}`}>
                      {dataset.privacy_level}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => setSelectedDataset(dataset)}
                        className="p-1 text-blue-400 hover:text-blue-300"
                        title="View Details"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => downloadDataset(dataset.id)}
                        className="p-1 text-green-400 hover:text-green-300"
                        title="Download"
                      >
                        <Download className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => deleteDataset(dataset.id)}
                        className="p-1 text-red-400 hover:text-red-300"
                        title="Delete"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-white mb-4">Upload Dataset</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Select File</label>
                <input
                  type="file"
                  accept=".csv,.json,.parquet"
                  onChange={handleFileUpload}
                  className="w-full text-sm text-gray-300 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
              </div>
              {uploadFile && (
                <div className="text-sm text-gray-400">
                  Selected: {uploadFile.name} ({(uploadFile.size / 1024 / 1024).toFixed(2)} MB)
                </div>
              )}
              {uploading && (
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  ></div>
                </div>
              )}
              <div className="flex space-x-3">
                <button
                  onClick={uploadDataset}
                  disabled={!uploadFile || uploading}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors"
                >
                  {uploading ? 'Uploading...' : 'Upload'}
                </button>
                <button
                  onClick={() => setShowUploadModal(false)}
                  className="flex-1 bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Dataset Details Modal */}
      {selectedDataset && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Dataset Details</h3>
              <button
                onClick={() => setSelectedDataset(null)}
                className="text-gray-400 hover:text-gray-300"
              >
                ✕
              </button>
            </div>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300">Name</label>
                  <p className="text-white">{selectedDataset.name}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300">Size</label>
                  <p className="text-white">{selectedDataset.size_mb} MB</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300">Samples</label>
                  <p className="text-white">{selectedDataset.samples.toLocaleString()}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300">Features</label>
                  <p className="text-white">{selectedDataset.features}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300">Quality Score</label>
                  <p className={`${getQualityColor(selectedDataset.quality_score)}`}>
                    {selectedDataset.quality_score}%
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300">FL Suitability</label>
                  <p className="text-blue-400">
                    {(selectedDataset.fl_suitability * 100).toFixed(1)}%
                  </p>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300">Description</label>
                <p className="text-white">{selectedDataset.description}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300">Privacy Level</label>
                <p className={`${getPrivacyColor(selectedDataset.privacy_level)}`}>
                  {selectedDataset.privacy_level}
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300">Upload Date</label>
                <p className="text-white">{new Date(selectedDataset.upload_date).toLocaleDateString()}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DatasetManager;
