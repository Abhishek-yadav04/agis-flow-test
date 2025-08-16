"""
Research Laboratory API
Advanced FL-IDS Research and Experimentation Platform
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime, timezone
import uuid
import random
import asyncio
from typing import Dict, List, Any, Optional
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/research", tags=["Research Lab"])

# In-memory storage (replace with database in production)
research_projects = {}
experiment_results = {}
active_experiments = {}

class ResearchProject:
    def __init__(self, name: str, description: str, datasets: List[str], algorithms: List[str]):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.status = "active"
        self.progress = 0
        self.datasets = datasets
        self.algorithms = algorithms
        self.results = []
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.updated_at = datetime.now(timezone.utc).isoformat()

class ExperimentResult:
    def __init__(self, project_id: str, experiment_name: str, algorithm: str, dataset: str):
        self.id = str(uuid.uuid4())
        self.project_id = project_id
        self.experiment_name = experiment_name
        self.algorithm = algorithm
        self.dataset = dataset
        self.accuracy = round(random.uniform(0.75, 0.95), 4)
        self.precision = round(random.uniform(0.70, 0.92), 4)
        self.recall = round(random.uniform(0.72, 0.90), 4)
        self.f1_score = round(2 * (self.precision * self.recall) / (self.precision + self.recall), 4)
        self.training_time = random.randint(120, 3600)
        self.dataset_size = random.randint(10000, 100000)
        self.parameters = {
            "learning_rate": round(random.uniform(0.001, 0.1), 4),
            "batch_size": random.choice([16, 32, 64, 128]),
            "epochs": random.randint(10, 100),
            "clients": random.randint(3, 20)
        }
        self.timestamp = datetime.now(timezone.utc).isoformat()

@router.get("/projects")
async def get_research_projects():
    """Get all research projects"""
    return list(research_projects.values())

@router.post("/projects")
async def create_research_project(project_data: Dict[str, Any]):
    """Create a new research project"""
    try:
        project = ResearchProject(
            name=project_data["name"],
            description=project_data["description"],
            datasets=project_data.get("datasets", []),
            algorithms=project_data.get("algorithms", ["FedAvg"])
        )
        
        research_projects[project.id] = project.__dict__
        logger.info(f"Created research project: {project.name}")
        
        return project.__dict__
    except Exception as e:
        logger.error(f"Failed to create research project: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/projects/{project_id}")
async def get_research_project(project_id: str):
    """Get a specific research project"""
    if project_id not in research_projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = research_projects[project_id]
    # Add latest results
    project_results = [r for r in experiment_results.values() if r["project_id"] == project_id]
    project["results"] = sorted(project_results, key=lambda x: x["timestamp"], reverse=True)
    
    return project

@router.put("/projects/{project_id}")
async def update_research_project(project_id: str, updates: Dict[str, Any]):
    """Update a research project"""
    if project_id not in research_projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = research_projects[project_id]
    project.update(updates)
    project["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    return project

@router.delete("/projects/{project_id}")
async def delete_research_project(project_id: str):
    """Delete a research project"""
    if project_id not in research_projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Delete associated results
    results_to_delete = [r_id for r_id, r in experiment_results.items() if r["project_id"] == project_id]
    for r_id in results_to_delete:
        del experiment_results[r_id]
    
    del research_projects[project_id]
    return {"message": "Project deleted successfully"}

@router.post("/projects/{project_id}/experiments")
async def run_experiment(project_id: str, config: Dict[str, Any], background_tasks: BackgroundTasks):
    """Run a new experiment"""
    if project_id not in research_projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = research_projects[project_id]
    experiment_name = f"Experiment_{len(project.get('results', [])) + 1}"
    
    # Start experiment in background
    background_tasks.add_task(
        simulate_experiment,
        project_id,
        experiment_name,
        config.get("algorithm", "FedAvg"),
        config.get("dataset", project["datasets"][0] if project["datasets"] else "CICIDS2017")
    )
    
    return {
        "message": "Experiment started",
        "experiment_name": experiment_name,
        "estimated_duration": "5-10 minutes"
    }

async def simulate_experiment(project_id: str, experiment_name: str, algorithm: str, dataset: str):
    """Simulate running an FL experiment"""
    try:
        # Mark experiment as active
        active_experiments[f"{project_id}_{experiment_name}"] = {
            "status": "running",
            "progress": 0,
            "started_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Simulate training progress
        for progress in range(0, 101, 10):
            active_experiments[f"{project_id}_{experiment_name}"]["progress"] = progress
            research_projects[project_id]["progress"] = progress
            await asyncio.sleep(2)  # Simulate training time
        
        # Generate results
        result = ExperimentResult(project_id, experiment_name, algorithm, dataset)
        experiment_results[result.id] = result.__dict__
        
        # Update project
        if "results" not in research_projects[project_id]:
            research_projects[project_id]["results"] = []
        research_projects[project_id]["results"].append(result.__dict__)
        research_projects[project_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        # Mark as completed
        del active_experiments[f"{project_id}_{experiment_name}"]
        
        logger.info(f"Completed experiment {experiment_name} for project {project_id}")
        
    except Exception as e:
        logger.error(f"Experiment simulation failed: {e}")
        if f"{project_id}_{experiment_name}" in active_experiments:
            active_experiments[f"{project_id}_{experiment_name}"]["status"] = "failed"

@router.get("/projects/{project_id}/experiments/{experiment_id}/results")
async def get_experiment_results(project_id: str, experiment_id: str):
    """Get detailed results for a specific experiment"""
    if experiment_id not in experiment_results:
        raise HTTPException(status_code=404, detail="Experiment results not found")
    
    result = experiment_results[experiment_id]
    if result["project_id"] != project_id:
        raise HTTPException(status_code=404, detail="Experiment not found in this project")
    
    return result

@router.get("/algorithms")
async def get_fl_algorithms():
    """Get available FL algorithms with their configurations"""
    algorithms = [
        {
            "name": "FedAvg",
            "description": "Federated Averaging - Standard FL algorithm",
            "type": "aggregation",
            "parameters": {
                "learning_rate": {"type": "float", "default": 0.01, "range": [0.001, 0.1]},
                "local_epochs": {"type": "int", "default": 5, "range": [1, 20]},
                "batch_size": {"type": "int", "default": 32, "options": [16, 32, 64, 128]}
            },
            "performance_metrics": {
                "convergence_speed": 0.7,
                "communication_efficiency": 0.8,
                "privacy_level": 0.6,
                "accuracy": 0.85
            },
            "supported_models": ["CNN", "MLP", "LSTM", "Transformer"],
            "implementation_status": "implemented"
        },
        {
            "name": "FedProx",
            "description": "Federated Proximal - Handles heterogeneous data",
            "type": "optimization",
            "parameters": {
                "learning_rate": {"type": "float", "default": 0.01, "range": [0.001, 0.1]},
                "mu": {"type": "float", "default": 0.1, "range": [0.01, 1.0]},
                "local_epochs": {"type": "int", "default": 5, "range": [1, 20]}
            },
            "performance_metrics": {
                "convergence_speed": 0.8,
                "communication_efficiency": 0.7,
                "privacy_level": 0.6,
                "accuracy": 0.87
            },
            "supported_models": ["CNN", "MLP", "LSTM"],
            "implementation_status": "implemented"
        },
        {
            "name": "SCAFFOLD",
            "description": "Stochastic Controlled Averaging for Federated Learning",
            "type": "optimization",
            "parameters": {
                "learning_rate": {"type": "float", "default": 0.01, "range": [0.001, 0.1]},
                "local_epochs": {"type": "int", "default": 5, "range": [1, 20]}
            },
            "performance_metrics": {
                "convergence_speed": 0.9,
                "communication_efficiency": 0.8,
                "privacy_level": 0.7,
                "accuracy": 0.89
            },
            "supported_models": ["CNN", "MLP"],
            "implementation_status": "implemented"
        },
        {
            "name": "FedNova",
            "description": "Normalized Averaging for Heterogeneous FL",
            "type": "aggregation",
            "parameters": {
                "learning_rate": {"type": "float", "default": 0.01, "range": [0.001, 0.1]},
                "local_epochs": {"type": "int", "default": 5, "range": [1, 20]}
            },
            "performance_metrics": {
                "convergence_speed": 0.8,
                "communication_efficiency": 0.9,
                "privacy_level": 0.6,
                "accuracy": 0.86
            },
            "supported_models": ["CNN", "MLP", "LSTM"],
            "implementation_status": "implemented"
        },
        {
            "name": "Personalized FL",
            "description": "Personalized Federated Learning for client-specific models",
            "type": "personalization",
            "parameters": {
                "learning_rate": {"type": "float", "default": 0.01, "range": [0.001, 0.1]},
                "personalization_layers": {"type": "int", "default": 2, "range": [1, 5]},
                "alpha": {"type": "float", "default": 0.5, "range": [0.1, 0.9]}
            },
            "performance_metrics": {
                "convergence_speed": 0.7,
                "communication_efficiency": 0.6,
                "privacy_level": 0.8,
                "accuracy": 0.91
            },
            "supported_models": ["CNN", "MLP"],
            "implementation_status": "in_progress"
        },
        {
            "name": "Differential Privacy FL",
            "description": "Privacy-preserving FL with differential privacy",
            "type": "privacy",
            "parameters": {
                "epsilon": {"type": "float", "default": 1.0, "range": [0.1, 10.0]},
                "delta": {"type": "float", "default": 1e-5, "range": [1e-6, 1e-3]},
                "noise_multiplier": {"type": "float", "default": 1.1, "range": [0.5, 2.0]}
            },
            "performance_metrics": {
                "convergence_speed": 0.6,
                "communication_efficiency": 0.7,
                "privacy_level": 0.95,
                "accuracy": 0.82
            },
            "supported_models": ["CNN", "MLP"],
            "implementation_status": "planned"
        }
    ]
    
    return algorithms

@router.get("/datasets/recommended")
async def get_recommended_datasets():
    """Get recommended datasets for FL-IDS research"""
    datasets = [
        {
            "name": "CICIDS2017",
            "description": "Canadian Institute for Cybersecurity Intrusion Detection System Dataset",
            "type": "intrusion_detection",
            "size_mb": 2800,
            "samples": 2830743,
            "features": 78,
            "labels": ["BENIGN", "DoS", "PortScan", "Bot", "Infiltration", "Web Attack", "Brute Force"],
            "source": "University of New Brunswick",
            "license": "Academic Use",
            "download_url": "https://www.unb.ca/cic/datasets/ids-2017.html",
            "preprocessing_required": True,
            "quality_score": 95,
            "last_updated": "2017-07-01",
            "fl_suitability": 0.9,
            "privacy_level": "Medium"
        },
        {
            "name": "NSL-KDD",
            "description": "Improved version of KDD Cup 1999 dataset",
            "type": "intrusion_detection",
            "size_mb": 45,
            "samples": 148517,
            "features": 41,
            "labels": ["normal", "dos", "probe", "r2l", "u2r"],
            "source": "University of New Brunswick",
            "license": "Public Domain",
            "download_url": "https://www.unb.ca/cic/datasets/nsl.html",
            "preprocessing_required": False,
            "quality_score": 85,
            "last_updated": "2009-03-11",
            "fl_suitability": 0.8,
            "privacy_level": "Low"
        },
        {
            "name": "UNSW-NB15",
            "description": "University of New South Wales Network-based Dataset",
            "type": "network_traffic",
            "size_mb": 850,
            "samples": 2540044,
            "features": 49,
            "labels": ["Normal", "Analysis", "Backdoor", "DoS", "Exploits", "Fuzzers", "Generic", "Reconnaissance", "Shellcode", "Worms"],
            "source": "UNSW Canberra",
            "license": "Academic Use",
            "download_url": "https://research.unsw.edu.au/projects/unsw-nb15-dataset",
            "preprocessing_required": True,
            "quality_score": 90,
            "last_updated": "2015-02-22",
            "fl_suitability": 0.85,
            "privacy_level": "Medium"
        },
        {
            "name": "DARPA 1998",
            "description": "DARPA Intrusion Detection Evaluation Dataset",
            "type": "intrusion_detection",
            "size_mb": 4200,
            "samples": 4900000,
            "features": 41,
            "labels": ["normal", "attack"],
            "source": "MIT Lincoln Laboratory",
            "license": "Public Domain",
            "download_url": "https://www.ll.mit.edu/r-d/datasets/1998-darpa-intrusion-detection-evaluation-dataset",
            "preprocessing_required": True,
            "quality_score": 80,
            "last_updated": "1998-12-31",
            "fl_suitability": 0.75,
            "privacy_level": "Low"
        },
        {
            "name": "CTU-13",
            "description": "CTU University Malware Capture Facility Dataset",
            "type": "malware",
            "size_mb": 1200,
            "samples": 1048575,
            "features": 13,
            "labels": ["Normal", "Botnet"],
            "source": "Czech Technical University",
            "license": "Academic Use",
            "download_url": "https://www.stratosphereips.org/datasets-ctu13",
            "preprocessing_required": True,
            "quality_score": 88,
            "last_updated": "2013-06-19",
            "fl_suitability": 0.82,
            "privacy_level": "High"
        },
        {
            "name": "ISCX2012",
            "description": "Information Security Centre of Excellence Dataset",
            "type": "intrusion_detection",
            "size_mb": 1800,
            "samples": 1690000,
            "features": 20,
            "labels": ["Normal", "HTTP DoS", "DDoS", "Brute Force SSH", "Brute Force FTP", "Infiltrating"],
            "source": "University of New Brunswick",
            "license": "Academic Use",
            "download_url": "https://www.unb.ca/cic/datasets/ids.html",
            "preprocessing_required": True,
            "quality_score": 87,
            "last_updated": "2012-06-11",
            "fl_suitability": 0.83,
            "privacy_level": "Medium"
        }
    ]
    
    return datasets

@router.get("/experiments/active")
async def get_active_experiments():
    """Get currently running experiments"""
    return active_experiments

@router.get("/statistics")
async def get_research_statistics():
    """Get research lab statistics"""
    total_projects = len(research_projects)
    active_projects = len([p for p in research_projects.values() if p["status"] == "active"])
    total_experiments = len(experiment_results)
    running_experiments = len(active_experiments)
    
    # Calculate average accuracy across all experiments
    if experiment_results:
        avg_accuracy = sum(r["accuracy"] for r in experiment_results.values()) / len(experiment_results)
    else:
        avg_accuracy = 0
    
    return {
        "total_projects": total_projects,
        "active_projects": active_projects,
        "completed_projects": len([p for p in research_projects.values() if p["status"] == "completed"]),
        "total_experiments": total_experiments,
        "running_experiments": running_experiments,
        "average_accuracy": round(avg_accuracy, 4),
        "algorithms_available": 6,
        "datasets_available": 6,
        "last_updated": datetime.now(timezone.utc).isoformat()
    }