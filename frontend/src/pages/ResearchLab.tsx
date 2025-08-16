import { useEffect, useState } from 'react';
import { researchAPI } from '../services/api';
import { 
  FlaskConical, 
  Plus, 
  Play, 
  BarChart3, 
  Settings
} from 'lucide-react';
import { clsx } from 'clsx';

export const ResearchLab: React.FC = () => {
  const [researchProjects, setResearchProjects] = useState<any[]>([]);
  const [activeProject, setActiveProject] = useState<any>(null);

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newProject, setNewProject] = useState({
    name: '',
    description: '',
    datasets: [] as string[],
    algorithms: ['FedAvg'],
    status: 'active'
  });

  useEffect(() => {
    loadResearchProjects();
  }, []);

  const loadResearchProjects = async () => {
    try {
      const projects = await researchAPI.getAlgorithms();
      setResearchProjects(projects.data || []);
    } catch (error) {
      console.error('Failed to load research projects:', error);
    }
  };

  const createProject = async () => {
    try {
      const project = {
        ...newProject,
        id: `project_${Date.now()}`,
        progress: 0,
        results: [],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      setResearchProjects(prev => [...prev, project]);
      setShowCreateModal(false);
      setNewProject({
        name: '',
        description: '',
        datasets: [],
        algorithms: ['FedAvg'],
        status: 'active'
      });
    } catch (error) {
      console.error('Failed to create project:', error);
    }
  };

  const runExperiment = async (projectId: string) => {
    try {
      await researchAPI.getAlgorithms();
      console.log('Running experiment for project:', projectId);
    } catch (error) {
      console.error('Failed to run experiment:', error);
    }
  };

  const availableDatasets = [
    'CICIDS2017', 'NSL-KDD', 'UNSW-NB15', 'KDDCup99', 
    'DARPA', 'ISCX2012', 'CTU-13', 'MAWI'
  ];

  const availableAlgorithms = [
    'FedAvg', 'FedProx', 'FedNova', 'SCAFFOLD', 
    'FedOpt', 'FedBN', 'Personalized FL', 'Clustered FL'
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center">
            <FlaskConical className="w-8 h-8 mr-3 text-blue-500" />
            Research Laboratory
          </h1>
          <p className="text-gray-400">Advanced FL-IDS Research & Experimentation</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4 mr-2" />
          New Project
        </button>
      </div>

      {/* Projects Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {researchProjects.map((project) => (
          <div
            key={project.id}
            className={clsx(
              'bg-gray-800 rounded-lg p-6 border-2 transition-all cursor-pointer',
              activeProject?.id === project.id 
                ? 'border-blue-500 bg-gray-750' 
                : 'border-gray-700 hover:border-gray-600'
            )}
            onClick={() => setActiveProject(project)}
          >
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-white">{project.name}</h3>
                <p className="text-sm text-gray-400 mt-1">{project.description}</p>
              </div>
              <div className={clsx(
                'px-2 py-1 rounded text-xs font-medium',
                project.status === 'active' ? 'bg-green-100 text-green-800' :
                project.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                'bg-yellow-100 text-yellow-800'
              )}>
                {project.status}
              </div>
            </div>

            {/* Progress */}
            <div className="mb-4">
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-400">Progress</span>
                <span className="text-white">{project.progress}%</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all"
                  style={{ width: `${project.progress}%` }}
                />
              </div>
            </div>

            {/* Datasets & Algorithms */}
            <div className="space-y-2 mb-4">
              <div>
                <span className="text-xs text-gray-400">Datasets: </span>
                <span className="text-xs text-white">{project.datasets.join(', ')}</span>
              </div>
              <div>
                <span className="text-xs text-gray-400">Algorithms: </span>
                <span className="text-xs text-white">{project.algorithms.join(', ')}</span>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center justify-between">
              <div className="flex space-x-2">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    runExperiment(project.id);
                  }}
                  className="p-1.5 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                >
                  <Play className="w-3 h-3" />
                </button>
                <button className="p-1.5 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors">
                  <BarChart3 className="w-3 h-3" />
                </button>
                <button className="p-1.5 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors">
                  <Settings className="w-3 h-3" />
                </button>
              </div>
              <div className="text-xs text-gray-400">
                {project.results.length} experiments
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Active Project Details */}
      {activeProject && (
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-white mb-4">
            {activeProject.name} - Experiment Results
          </h2>
          
          {activeProject.results.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-700">
                    <th className="text-left py-2 text-gray-400">Experiment</th>
                    <th className="text-left py-2 text-gray-400">Algorithm</th>
                    <th className="text-left py-2 text-gray-400">Accuracy</th>
                    <th className="text-left py-2 text-gray-400">Precision</th>
                    <th className="text-left py-2 text-gray-400">Recall</th>
                    <th className="text-left py-2 text-gray-400">F1-Score</th>
                    <th className="text-left py-2 text-gray-400">Training Time</th>
                    <th className="text-left py-2 text-gray-400">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {activeProject.results.map((result: any) => (
                    <tr key={result.id} className="border-b border-gray-700">
                      <td className="py-2 text-white">{result.experiment_name}</td>
                      <td className="py-2 text-white">{result.algorithm}</td>
                      <td className="py-2 text-green-400">{(result.accuracy * 100).toFixed(2)}%</td>
                      <td className="py-2 text-blue-400">{(result.precision * 100).toFixed(2)}%</td>
                      <td className="py-2 text-purple-400">{(result.recall * 100).toFixed(2)}%</td>
                      <td className="py-2 text-yellow-400">{(result.f1_score * 100).toFixed(2)}%</td>
                      <td className="py-2 text-gray-300">{result.training_time}s</td>
                      <td className="py-2 text-gray-400">
                        {new Date(result.timestamp).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-8">
              <FlaskConical className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400">No experiments run yet</p>
              <button
                onClick={() => runExperiment(activeProject.id)}
                className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Run First Experiment
              </button>
            </div>
          )}
        </div>
      )}

      {/* Create Project Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-semibold text-white mb-4">Create New Research Project</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Project Name
                </label>
                <input
                  type="text"
                  value={newProject.name}
                  onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter project name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Description
                </label>
                <textarea
                  value={newProject.description}
                  onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={3}
                  placeholder="Project description"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Datasets
                </label>
                <select
                  multiple
                  value={newProject.datasets}
                  onChange={(e) => setNewProject({ 
                    ...newProject, 
                    datasets: Array.from(e.target.selectedOptions, option => option.value)
                  })}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  size={4}
                >
                  {availableDatasets.map(dataset => (
                    <option key={dataset} value={dataset}>{dataset}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Algorithms
                </label>
                <select
                  multiple
                  value={newProject.algorithms}
                  onChange={(e) => setNewProject({ 
                    ...newProject, 
                    algorithms: Array.from(e.target.selectedOptions, option => option.value)
                  })}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  size={4}
                >
                  {availableAlgorithms.map(algorithm => (
                    <option key={algorithm} value={algorithm}>{algorithm}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={createProject}
                disabled={!newProject.name || !newProject.description}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Create Project
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};