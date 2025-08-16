import numpy as np
try:
    import tensorflow as tf
    from tensorflow import keras
    import os
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TF warnings
    # Enable deterministic operations
    tf.config.experimental.enable_op_determinism()
    tf.random.set_seed(42)
    # Configure GPU if available
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
        except RuntimeError as e:
            pass
    TF_AVAILABLE = True
except (ImportError, AttributeError) as e:
    tf = None
    keras = None
    TF_AVAILABLE = False
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class PersonalizedFL:
    """Personalized Federated Learning (Per-FedAvg)"""
    
    def __init__(self, alpha: float = 0.01):
        self.alpha = alpha  # Personalization rate
        self.client_models = {}
        
    def personalized_update(self, client_id: int, global_weights: List, local_weights: List, local_data_size: int):
        """Apply personalized model update"""
        if client_id not in self.client_models:
            self.client_models[client_id] = global_weights
            
        # Interpolate between global and local models
        personalized_weights = []
        for g_w, l_w in zip(global_weights, local_weights):
            p_w = self.alpha * l_w + (1 - self.alpha) * g_w
            personalized_weights.append(p_w)
            
        self.client_models[client_id] = personalized_weights
        return personalized_weights

class ClusteredFL:
    """Clustered Federated Learning"""
    
    def __init__(self, num_clusters: int = 3):
        self.num_clusters = num_clusters
        self.clusters = {}
        self.cluster_models = {}
        
    def assign_to_cluster(self, client_id: int, client_weights: List) -> int:
        """Assign client to cluster based on model similarity"""
        if not self.cluster_models:
            cluster_id = len(self.clusters) % self.num_clusters
            if cluster_id not in self.clusters:
                self.clusters[cluster_id] = []
            self.clusters[cluster_id].append(client_id)
            return cluster_id
            
        # Find most similar cluster
        min_distance = float('inf')
        best_cluster = 0
        
        for cluster_id, model_weights in self.cluster_models.items():
            distance = self._calculate_model_distance(client_weights, model_weights)
            if distance < min_distance:
                min_distance = distance
                best_cluster = cluster_id
                
        if best_cluster not in self.clusters:
            self.clusters[best_cluster] = []
        self.clusters[best_cluster].append(client_id)
        return best_cluster
    
    def _calculate_model_distance(self, weights1: List, weights2: List) -> float:
        """Calculate Euclidean distance between model weights"""
        total_distance = 0.0
        for w1, w2 in zip(weights1, weights2):
            total_distance += np.sum((w1 - w2) ** 2)
        return np.sqrt(total_distance)

class FederatedTransferLearning:
    """Federated Transfer Learning with pre-trained models"""
    
    def __init__(self, base_model_path: Optional[str] = None):
        self.base_model = self._load_pretrained_model(base_model_path)
        
    def _load_pretrained_model(self, model_path: Optional[str]):
        """Load pre-trained model for transfer learning"""
        if model_path:
            return tf.keras.models.load_model(model_path)
        else:
            # Use a simple pre-trained base
            base_model = tf.keras.Sequential([
                tf.keras.layers.Dense(128, activation='relu', input_shape=(41,)),
                tf.keras.layers.Dense(64, activation='relu'),
                tf.keras.layers.Dense(32, activation='relu')
            ])
            return base_model
    
    def create_task_specific_model(self, num_classes: int):
        """Create task-specific model with frozen base layers"""
        # Freeze base layers
        for layer in self.base_model.layers[:-1]:
            layer.trainable = False
            
        # Add task-specific head
        model = tf.keras.Sequential([
            self.base_model,
            tf.keras.layers.Dense(num_classes, activation='softmax')
        ])
        
        return model

class MultiTaskFL:
    """Federated Multi-Task Learning"""
    
    def __init__(self, shared_layers: int = 2):
        self.shared_layers = shared_layers
        self.task_models = {}
        
    def create_multitask_model(self, task_id: str, num_classes: int):
        """Create multi-task model with shared representation"""
        # Shared layers
        shared_base = tf.keras.Sequential([
            tf.keras.layers.Dense(128, activation='relu', input_shape=(41,)),
            tf.keras.layers.Dense(64, activation='relu')
        ])
        
        # Task-specific head
        task_head = tf.keras.Sequential([
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(num_classes, activation='softmax')
        ])
        
        # Combined model
        inputs = tf.keras.Input(shape=(41,))
        shared_features = shared_base(inputs)
        outputs = task_head(shared_features)
        
        model = tf.keras.Model(inputs=inputs, outputs=outputs)
        self.task_models[task_id] = model
        return model

class AdvancedFLEngine:
    """Advanced Federated Learning Engine with multiple strategies"""
    
    def __init__(self):
        self.strategies = {
            'personalized': PersonalizedFL(),
            'clustered': ClusteredFL(),
            'transfer': FederatedTransferLearning(),
            'multitask': MultiTaskFL()
        }
        self.current_strategy = 'fedavg'
        self.strategy_history = []
        
    def set_strategy(self, strategy_name: str, **kwargs):
        """Set FL strategy"""
        if strategy_name in self.strategies:
            self.current_strategy = strategy_name
            self.strategy_history.append({
                'strategy': strategy_name,
                'params': kwargs,
                'timestamp': np.datetime64('now')
            })
            logger.info(f"FL strategy set to: {strategy_name}")
        else:
            logger.error(f"Unknown strategy: {strategy_name}")
    
    def dynamic_strategy_selection(self, round_num: int, performance_metrics: Dict):
        """Dynamically select FL strategy based on performance"""
        accuracy = performance_metrics.get('accuracy', 0.0)
        
        if round_num < 10:
            return 'fedavg'  # Start with standard FedAvg
        elif accuracy < 0.7:
            return 'clustered'  # Use clustering for poor performance
        elif round_num > 30:
            return 'personalized'  # Switch to personalization later
        else:
            return 'fedavg'
    
    def execute_fl_round(self, client_updates: List[Dict], strategy: str = None) -> Dict:
        """Execute FL round with specified strategy"""
        if strategy is None:
            strategy = self.current_strategy
            
        if strategy == 'personalized':
            return self._execute_personalized_round(client_updates)
        elif strategy == 'clustered':
            return self._execute_clustered_round(client_updates)
        elif strategy == 'transfer':
            return self._execute_transfer_round(client_updates)
        elif strategy == 'multitask':
            return self._execute_multitask_round(client_updates)
        else:
            return self._execute_fedavg_round(client_updates)
    
    def _execute_personalized_round(self, client_updates: List[Dict]) -> Dict:
        """Execute personalized FL round"""
        pfl = self.strategies['personalized']
        results = []
        
        for update in client_updates:
            client_id = update['client_id']
            personalized_weights = pfl.personalized_update(
                client_id, 
                update.get('global_weights', []),
                update['weights'],
                update['data_size']
            )
            results.append({
                'client_id': client_id,
                'personalized_weights': personalized_weights
            })
        
        return {
            'strategy': 'personalized',
            'results': results,
            'global_update': None  # No single global model
        }
    
    def _execute_clustered_round(self, client_updates: List[Dict]) -> Dict:
        """Execute clustered FL round"""
        clustered_fl = self.strategies['clustered']
        cluster_updates = {}
        
        # Assign clients to clusters
        for update in client_updates:
            client_id = update['client_id']
            cluster_id = clustered_fl.assign_to_cluster(client_id, update['weights'])
            
            if cluster_id not in cluster_updates:
                cluster_updates[cluster_id] = []
            cluster_updates[cluster_id].append(update)
        
        # Aggregate within clusters
        cluster_models = {}
        for cluster_id, updates in cluster_updates.items():
            cluster_models[cluster_id] = self._fedavg_aggregation(updates)
        
        clustered_fl.cluster_models = cluster_models
        
        return {
            'strategy': 'clustered',
            'cluster_models': cluster_models,
            'cluster_assignments': clustered_fl.clusters
        }
    
    def _execute_transfer_round(self, client_updates: List[Dict]) -> Dict:
        """Execute transfer learning FL round"""
        # Fine-tune only the task-specific layers
        aggregated_weights = self._fedavg_aggregation(client_updates)
        
        return {
            'strategy': 'transfer',
            'aggregated_weights': aggregated_weights,
            'frozen_layers': 'base_model'
        }
    
    def _execute_multitask_round(self, client_updates: List[Dict]) -> Dict:
        """Execute multi-task FL round"""
        # Separate shared and task-specific updates
        shared_updates = []
        task_updates = {}
        
        for update in client_updates:
            task_id = update.get('task_id', 'default')
            if task_id not in task_updates:
                task_updates[task_id] = []
            task_updates[task_id].append(update)
            shared_updates.append(update)
        
        # Aggregate shared layers
        shared_weights = self._fedavg_aggregation(shared_updates)
        
        # Aggregate task-specific layers
        task_weights = {}
        for task_id, updates in task_updates.items():
            task_weights[task_id] = self._fedavg_aggregation(updates)
        
        return {
            'strategy': 'multitask',
            'shared_weights': shared_weights,
            'task_weights': task_weights
        }
    
    def _execute_fedavg_round(self, client_updates: List[Dict]) -> Dict:
        """Execute standard FedAvg round"""
        aggregated_weights = self._fedavg_aggregation(client_updates)
        
        return {
            'strategy': 'fedavg',
            'aggregated_weights': aggregated_weights
        }
    
    def _fedavg_aggregation(self, client_updates: List[Dict]) -> List:
        """Standard FedAvg aggregation"""
        if not client_updates:
            return []
            
        total_samples = sum(update['data_size'] for update in client_updates)
        aggregated_weights = None
        
        for update in client_updates:
            weight = update['data_size'] / total_samples
            weights = update['weights']
            
            if aggregated_weights is None:
                aggregated_weights = [w * weight for w in weights]
            else:
                for i in range(len(weights)):
                    aggregated_weights[i] += weights[i] * weight
        
        return aggregated_weights
    
    def get_strategy_performance(self) -> Dict:
        """Get performance metrics for different strategies"""
        return {
            'current_strategy': self.current_strategy,
            'strategy_history': self.strategy_history,
            'available_strategies': list(self.strategies.keys())
        }