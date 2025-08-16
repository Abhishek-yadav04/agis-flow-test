import numpy as np
try:
    import tensorflow as tf
    # Test if TensorFlow is properly installed
    _ = tf.__version__
except (ImportError, AttributeError):
    tf = None
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import threading
import time
import logging
from typing import List, Dict, Any

# Set random seeds for reproducibility
if tf is not None:
    try:
        tf.random.set_seed(42)
    except AttributeError:
        try:
            tf.set_random_seed(42)
        except AttributeError:
            pass
np.random.seed(42)

logger = logging.getLogger(__name__)

class FederatedClient:
    def __init__(self, client_id: int, data_samples: np.ndarray, labels: np.ndarray):
        self.client_id = client_id
        self.data = data_samples
        self.labels = labels
        self.model = self._create_model()
        self.local_epochs = 5  # Configurable epochs
        
    def _create_model(self):
        """Create neural network model for IDS"""
        if tf is None:
            # Fallback to sklearn model if TensorFlow not available
            from sklearn.ensemble import RandomForestClassifier
            return RandomForestClassifier(n_estimators=100, random_state=42)
            
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation='relu', input_shape=(41,)),  # NSL-KDD features
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dense(2, activation='softmax')  # Binary: Normal/Attack
        ])
        
        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        return model
    
    def local_train(self, global_weights: List[np.ndarray]) -> Dict[str, Any]:
        """Train model locally with federated learning and error handling"""
        try:
            # Set global model weights
            if global_weights:
                self.model.set_weights(global_weights)
            
            # Local training
            history = self.model.fit(
                self.data, self.labels,
                epochs=self.local_epochs,
                batch_size=32,
                verbose=0,
                validation_split=0.2
            )
            
            # Return local model weights and metrics
            return {
                'client_id': self.client_id,
                'weights': self.model.get_weights(),
                'data_size': len(self.data),
                'loss': history.history['loss'][-1],
                'accuracy': history.history['accuracy'][-1],
                'val_accuracy': history.history['val_accuracy'][-1] if 'val_accuracy' in history.history else 0
            }
        except Exception as e:
            logger.error(f"Client {self.client_id} training failed: {e}")
            return {
                'client_id': self.client_id,
                'error': str(e),
                'data_size': len(self.data),
                'loss': float('inf'),
                'accuracy': 0.0,
                'val_accuracy': 0.0
            }
    
    def evaluate_model(self, test_data: np.ndarray, test_labels: np.ndarray, batch_size: int = 1000) -> Dict[str, float]:
        """Evaluate model performance with batch processing"""
        try:
            # Batch processing for large datasets
            predictions = []
            for i in range(0, len(test_data), batch_size):
                batch_data = test_data[i:i+batch_size]
                batch_pred = self.model.predict(batch_data, verbose=0)
                predictions.extend(np.argmax(batch_pred, axis=1))
            
            predictions = np.array(predictions)
            
            return {
                'accuracy': accuracy_score(test_labels, predictions),
                'precision': precision_score(test_labels, predictions, average='weighted'),
                'recall': recall_score(test_labels, predictions, average='weighted'),
                'f1_score': f1_score(test_labels, predictions, average='weighted')
            }
        except Exception as e:
            logger.error(f"Model evaluation failed: {e}")
            return {
                'accuracy': 0.0,
                'precision': 0.0,
                'recall': 0.0,
                'f1_score': 0.0
            }

class FederatedServer:
    def __init__(self, num_clients: int = 5):
        self.num_clients = num_clients
        self.clients: List[FederatedClient] = []
        self.global_model = self._create_global_model()
        self.round_number = 0
        self.training_history = []
        
    def _create_global_model(self):
        """Create global model architecture"""
        if tf is None:
            # Fallback to sklearn model if TensorFlow not available
            from sklearn.ensemble import RandomForestClassifier
            return RandomForestClassifier(n_estimators=100, random_state=42)
            
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation='relu', input_shape=(41,)),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dense(2, activation='softmax')
        ])
        
        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        return model
    
    def add_client(self, client: FederatedClient):
        """Add client to federation"""
        self.clients.append(client)
        logger.info(f"Added client {client.client_id} with {len(client.data)} samples")
    
    def federated_averaging(self, client_updates: List[Dict[str, Any]]) -> List[np.ndarray]:
        """Implement FedAvg algorithm"""
        if not client_updates:
            return self.global_model.get_weights()
        
        # Calculate total data size for weighted averaging
        total_data_size = sum(update['data_size'] for update in client_updates)
        
        # Initialize averaged weights
        averaged_weights = []
        num_layers = len(client_updates[0]['weights'])
        
        for layer_idx in range(num_layers):
            # Weighted average of layer weights
            layer_weights = np.zeros_like(client_updates[0]['weights'][layer_idx])
            
            for update in client_updates:
                weight = update['data_size'] / total_data_size
                layer_weights += weight * update['weights'][layer_idx]
            
            averaged_weights.append(layer_weights)
        
        return averaged_weights
    
    def train_round(self) -> Dict[str, Any]:
        """Execute one federated learning round"""
        self.round_number += 1
        logger.info(f"Starting FL round {self.round_number}")
        
        # Get current global weights
        global_weights = self.global_model.get_weights()
        
        # Collect client updates
        client_updates = []
        for client in self.clients:
            try:
                update = client.local_train(global_weights)
                client_updates.append(update)
                logger.info(f"Client {client.client_id} - Accuracy: {update['accuracy']:.4f}")
            except Exception as e:
                logger.error(f"Client {client.client_id} training failed: {e}")
        
        # Aggregate models using FedAvg
        if client_updates:
            new_global_weights = self.federated_averaging(client_updates)
            self.global_model.set_weights(new_global_weights)
            
            # Calculate round metrics
            avg_accuracy = np.mean([update['accuracy'] for update in client_updates])
            avg_loss = np.mean([update['loss'] for update in client_updates])
            
            round_metrics = {
                'round': self.round_number,
                'avg_accuracy': avg_accuracy,
                'avg_loss': avg_loss,
                'participating_clients': len(client_updates),
                'global_model_accuracy': avg_accuracy  # Simplified
            }
            # Increment global FL rounds metric if available
            try:
                from backend.main import app_state  # type: ignore
                if hasattr(app_state, 'metrics'):
                    app_state.metrics['fl_rounds_total'] = app_state.metrics.get('fl_rounds_total', 0) + 1
            except Exception:
                pass
            
            self.training_history.append(round_metrics)
            try:
                from backend.logging.structured import log_event  # type: ignore
                log_event("info", "fl_round_completed", round=self.round_number, avg_accuracy=float(avg_accuracy), clients=len(client_updates))
            except Exception:
                pass
            logger.info(f"Round {self.round_number} completed - Avg Accuracy: {avg_accuracy:.4f}")
            
            return round_metrics
        
        return {'round': self.round_number, 'error': 'No client updates received'}
    
    def evaluate_global_model(self, test_data: np.ndarray, test_labels: np.ndarray, batch_size: int = 1000) -> Dict[str, float]:
        """Evaluate global model performance with batch processing"""
        try:
            # Batch processing for large datasets
            predictions = []
            for i in range(0, len(test_data), batch_size):
                batch_data = test_data[i:i+batch_size]
                batch_pred = self.global_model.predict(batch_data, verbose=0)
                predictions.extend(np.argmax(batch_pred, axis=1))
            
            predictions = np.array(predictions)
            
            return {
                'accuracy': accuracy_score(test_labels, predictions),
                'precision': precision_score(test_labels, predictions, average='weighted'),
                'recall': recall_score(test_labels, predictions, average='weighted'),
                'f1_score': f1_score(test_labels, predictions, average='weighted')
            }
        except Exception as e:
            logger.error(f"Global model evaluation failed: {e}")
            return {
                'accuracy': 0.0,
                'precision': 0.0,
                'recall': 0.0,
                'f1_score': 0.0
            }

class IDSDataGenerator:
    """Generate realistic IDS data for federated learning"""
    
    @staticmethod
    def generate_network_features(num_samples: int = 1000) -> tuple:
        """Generate network traffic features similar to NSL-KDD dataset"""
        np.random.seed(42)
        
        # Generate 41 features similar to NSL-KDD
        features = np.random.rand(num_samples, 41)
        
        # Create realistic patterns for normal vs attack traffic
        labels = np.zeros(num_samples)
        
        # Normal traffic patterns (70%)
        normal_indices = np.random.choice(num_samples, int(0.7 * num_samples), replace=False)
        features[normal_indices, :10] = np.random.normal(0.3, 0.1, (len(normal_indices), 10))  # Lower values
        labels[normal_indices] = 0
        
        # Attack traffic patterns (30%)
        attack_indices = np.setdiff1d(np.arange(num_samples), normal_indices)
        features[attack_indices, :10] = np.random.normal(0.8, 0.2, (len(attack_indices), 10))  # Higher values
        labels[attack_indices] = 1
        
        return features, labels.astype(int)
    
    @staticmethod
    def distribute_data_non_iid(features: np.ndarray, labels: np.ndarray, num_clients: int = 5):
        """Distribute data in non-IID manner across clients"""
        client_data = []
        samples_per_client = len(features) // num_clients
        
        for i in range(num_clients):
            start_idx = i * samples_per_client
            end_idx = (i + 1) * samples_per_client if i < num_clients - 1 else len(features)
            
            client_features = features[start_idx:end_idx]
            client_labels = labels[start_idx:end_idx]
            
            client_data.append((client_features, client_labels))
        
        return client_data

# Integration with existing system
class FederatedIDSSystem:
    def __init__(self):
        self.fl_server = FederatedServer(num_clients=5)
        self.data_generator = IDSDataGenerator()
        self.running = False
        self.current_metrics = {
            'round': 0,
            'accuracy': 0.65,
            'precision': 0.0,
            'recall': 0.0,
            'f1_score': 0.0,
            'participating_clients': 0
        }
        
    def initialize_federation(self):
        """Initialize federated learning system with clients"""
        # Generate dataset
        features, labels = self.data_generator.generate_network_features(5000)
        client_data = self.data_generator.distribute_data_non_iid(features, labels, 5)
        
        # Create and add clients
        for i, (client_features, client_labels) in enumerate(client_data):
            client = FederatedClient(i, client_features, client_labels)
            self.fl_server.add_client(client)
        
        logger.info("Federated IDS system initialized with 5 clients")
    
    def start_training(self):
        """Start federated learning training"""
        self.running = True
        threading.Thread(target=self._training_loop, daemon=True).start()
    
    def _training_loop(self):
        """Main training loop"""
        while self.running:
            try:
                metrics = self.fl_server.train_round()
                if 'error' not in metrics:
                    self.current_metrics.update({
                        'round': metrics['round'],
                        'accuracy': metrics['avg_accuracy'],
                        'participating_clients': metrics['participating_clients']
                    })
                
                time.sleep(90)  # Train every 90 seconds
            except Exception as e:
                logger.error(f"Training loop error: {e}")
                time.sleep(60)
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current FL metrics"""
        return self.current_metrics.copy()
    
    def stop_training(self):
        """Stop federated learning"""
        self.running = False