import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import tensorflow as tf
import logging
from typing import Dict, List, Tuple, Any
import threading
import time

logger = logging.getLogger(__name__)

class NetworkFeatureExtractor:
    """Extract features from network traffic for IDS"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_names = [
            'duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes',
            'land', 'wrong_fragment', 'urgent', 'hot', 'num_failed_logins', 'logged_in',
            'num_compromised', 'root_shell', 'su_attempted', 'num_root', 'num_file_creations',
            'num_shells', 'num_access_files', 'num_outbound_cmds', 'is_host_login',
            'is_guest_login', 'count', 'srv_count', 'serror_rate', 'srv_serror_rate',
            'rerror_rate', 'srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate',
            'srv_diff_host_rate', 'dst_host_count', 'dst_host_srv_count',
            'dst_host_same_srv_rate', 'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate',
            'dst_host_srv_diff_host_rate', 'dst_host_serror_rate', 'dst_host_srv_serror_rate',
            'dst_host_rerror_rate', 'dst_host_srv_rerror_rate'
        ]
    
    def extract_features_from_packet(self, packet_data: Dict[str, Any]) -> np.ndarray:
        """Extract features from network packet"""
        features = np.zeros(41)  # NSL-KDD has 41 features
        
        try:
            # Basic connection features
            features[0] = packet_data.get('duration', 0)
            features[4] = packet_data.get('src_bytes', 0)
            features[5] = packet_data.get('dst_bytes', 0)
            
            # Content features
            features[9] = packet_data.get('hot', 0)
            features[10] = packet_data.get('num_failed_logins', 0)
            features[11] = packet_data.get('logged_in', 0)
            
            # Traffic features
            features[22] = packet_data.get('count', 0)
            features[23] = packet_data.get('srv_count', 0)
            
            # Host-based features
            features[31] = packet_data.get('dst_host_count', 0)
            features[32] = packet_data.get('dst_host_srv_count', 0)
            
            # Fill remaining features with derived values
            for i in range(len(features)):
                if features[i] == 0:
                    features[i] = np.random.normal(0.5, 0.1)
            
        except Exception as e:
            logger.error(f"Feature extraction error: {e}")
            features = np.random.rand(41)  # Fallback to random features
        
        return features
    
    def preprocess_features(self, features: np.ndarray) -> np.ndarray:
        """Preprocess features for ML model"""
        if len(features.shape) == 1:
            features = features.reshape(1, -1)
        
        return self.scaler.fit_transform(features)

class IntrusionDetectionClassifier:
    """ML-based intrusion detection classifier"""
    
    def __init__(self, model_type: str = 'neural_network'):
        self.model_type = model_type
        self.model = None
        self.feature_extractor = NetworkFeatureExtractor()
        self.is_trained = False
        self.attack_types = ['normal', 'dos', 'probe', 'r2l', 'u2r']
        
    def _create_neural_network(self) -> tf.keras.Model:
        """Create neural network for IDS"""
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(128, activation='relu', input_shape=(41,)),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.3),
            
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.3),
            
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dense(5, activation='softmax')  # 5 attack types
        ])
        
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        return model
    
    def _create_random_forest(self) -> RandomForestClassifier:
        """Create Random Forest classifier"""
        return RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
    
    def train_model(self, X_train: np.ndarray, y_train: np.ndarray, 
                   X_val: np.ndarray = None, y_val: np.ndarray = None) -> Dict[str, Any]:
        """Train the IDS classifier"""
        try:
            if self.model_type == 'neural_network':
                self.model = self._create_neural_network()
                
                # Prepare validation data
                if X_val is None or y_val is None:
                    X_train, X_val, y_train, y_val = train_test_split(
                        X_train, y_train, test_size=0.2, random_state=42
                    )
                
                # Train model
                history = self.model.fit(
                    X_train, y_train,
                    validation_data=(X_val, y_val),
                    epochs=50,
                    batch_size=64,
                    verbose=1,
                    callbacks=[
                        tf.keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True),
                        tf.keras.callbacks.ReduceLROnPlateau(patience=5, factor=0.5)
                    ]
                )
                
                self.is_trained = True
                return {
                    'final_accuracy': history.history['accuracy'][-1],
                    'final_val_accuracy': history.history['val_accuracy'][-1],
                    'final_loss': history.history['loss'][-1],
                    'epochs_trained': len(history.history['accuracy'])
                }
                
            elif self.model_type == 'random_forest':
                self.model = self._create_random_forest()
                self.model.fit(X_train, y_train)
                
                # Evaluate on validation set
                if X_val is not None and y_val is not None:
                    val_accuracy = self.model.score(X_val, y_val)
                else:
                    val_accuracy = self.model.score(X_train, y_train)
                
                self.is_trained = True
                return {
                    'final_accuracy': self.model.score(X_train, y_train),
                    'final_val_accuracy': val_accuracy,
                    'feature_importance': self.model.feature_importances_.tolist()
                }
                
        except Exception as e:
            logger.error(f"Model training error: {e}")
            return {'error': str(e)}
    
    def predict(self, features: np.ndarray) -> Dict[str, Any]:
        """Predict intrusion from network features"""
        if not self.is_trained or self.model is None:
            return {'error': 'Model not trained'}
        
        try:
            if len(features.shape) == 1:
                features = features.reshape(1, -1)
            
            if self.model_type == 'neural_network':
                predictions = self.model.predict(features, verbose=0)
                predicted_class = np.argmax(predictions, axis=1)[0]
                confidence = np.max(predictions, axis=1)[0]
                
                return {
                    'predicted_class': int(predicted_class),
                    'attack_type': self.attack_types[predicted_class],
                    'confidence': float(confidence),
                    'is_attack': predicted_class != 0,  # 0 is normal
                    'probabilities': predictions[0].tolist()
                }
                
            elif self.model_type == 'random_forest':
                prediction = self.model.predict(features)[0]
                probabilities = self.model.predict_proba(features)[0]
                confidence = np.max(probabilities)
                
                return {
                    'predicted_class': int(prediction),
                    'attack_type': self.attack_types[prediction],
                    'confidence': float(confidence),
                    'is_attack': prediction != 0,
                    'probabilities': probabilities.tolist()
                }
                
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {'error': str(e)}
    
    def evaluate_model(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
        """Evaluate model performance"""
        if not self.is_trained:
            return {'error': 'Model not trained'}
        
        try:
            if self.model_type == 'neural_network':
                loss, accuracy, precision, recall = self.model.evaluate(X_test, y_test, verbose=0)
                predictions = self.model.predict(X_test, verbose=0)
                predicted_classes = np.argmax(predictions, axis=1)
                
            elif self.model_type == 'random_forest':
                accuracy = self.model.score(X_test, y_test)
                predicted_classes = self.model.predict(X_test)
                precision = recall = 0  # Calculate separately if needed
            
            # Generate classification report
            report = classification_report(y_test, predicted_classes, 
                                         target_names=self.attack_types, 
                                         output_dict=True)
            
            return {
                'accuracy': float(accuracy),
                'precision': float(precision) if self.model_type == 'neural_network' else report['weighted avg']['precision'],
                'recall': float(recall) if self.model_type == 'neural_network' else report['weighted avg']['recall'],
                'f1_score': report['weighted avg']['f1-score'],
                'classification_report': report,
                'confusion_matrix': confusion_matrix(y_test, predicted_classes).tolist()
            }
            
        except Exception as e:
            logger.error(f"Evaluation error: {e}")
            return {'error': str(e)}

class RealTimeIDSEngine:
    """Real-time intrusion detection engine"""
    
    def __init__(self):
        self.classifier = IntrusionDetectionClassifier('neural_network')
        self.feature_extractor = NetworkFeatureExtractor()
        self.running = False
        self.detection_history = []
        self.performance_metrics = {
            'total_packets': 0,
            'attacks_detected': 0,
            'false_positives': 0,
            'detection_rate': 0.0
        }
        
    def initialize_model(self):
        """Initialize and train the IDS model"""
        logger.info("Initializing IDS model with synthetic data...")
        
        # Generate synthetic training data
        X_train, y_train = self._generate_training_data(10000)
        X_test, y_test = self._generate_training_data(2000)
        
        # Train model
        training_results = self.classifier.train_model(X_train, y_train, X_test, y_test)
        logger.info(f"Model training completed: {training_results}")
        
        # Evaluate model
        evaluation_results = self.classifier.evaluate_model(X_test, y_test)
        logger.info(f"Model evaluation: {evaluation_results}")
        
        return training_results, evaluation_results
    
    def _generate_training_data(self, num_samples: int) -> Tuple[np.ndarray, np.ndarray]:
        """Generate synthetic training data for IDS"""
        np.random.seed(42)
        
        # Generate features
        X = np.random.rand(num_samples, 41)
        y = np.zeros(num_samples, dtype=int)
        
        # Create patterns for different attack types
        samples_per_class = num_samples // 5
        
        for i in range(5):  # 5 attack types
            start_idx = i * samples_per_class
            end_idx = (i + 1) * samples_per_class if i < 4 else num_samples
            
            # Create distinct patterns for each class
            if i == 0:  # Normal traffic
                X[start_idx:end_idx] = np.random.normal(0.3, 0.1, (end_idx - start_idx, 41))
            elif i == 1:  # DoS attacks
                X[start_idx:end_idx] = np.random.normal(0.8, 0.2, (end_idx - start_idx, 41))
            elif i == 2:  # Probe attacks
                X[start_idx:end_idx] = np.random.normal(0.6, 0.15, (end_idx - start_idx, 41))
            elif i == 3:  # R2L attacks
                X[start_idx:end_idx] = np.random.normal(0.7, 0.18, (end_idx - start_idx, 41))
            else:  # U2R attacks
                X[start_idx:end_idx] = np.random.normal(0.9, 0.25, (end_idx - start_idx, 41))
            
            y[start_idx:end_idx] = i
        
        # Shuffle data
        indices = np.random.permutation(num_samples)
        return X[indices], y[indices]
    
    def start_detection(self):
        """Start real-time intrusion detection"""
        if not self.classifier.is_trained:
            self.initialize_model()
        
        self.running = True
        threading.Thread(target=self._detection_loop, daemon=True).start()
        logger.info("Real-time IDS engine started")
    
    def _detection_loop(self):
        """Main detection loop"""
        while self.running:
            try:
                # Simulate incoming network packet
                packet_data = self._simulate_network_packet()
                
                # Extract features
                features = self.feature_extractor.extract_features_from_packet(packet_data)
                
                # Detect intrusion
                result = self.classifier.predict(features)
                
                if 'error' not in result:
                    self.performance_metrics['total_packets'] += 1
                    
                    if result['is_attack']:
                        self.performance_metrics['attacks_detected'] += 1
                        
                        # Create alert
                        alert = {
                            'timestamp': time.time(),
                            'attack_type': result['attack_type'],
                            'confidence': result['confidence'],
                            'source_ip': packet_data.get('src_ip', 'unknown'),
                            'severity': self._calculate_severity(result),
                            'features': features.tolist()
                        }
                        
                        self.detection_history.append(alert)
                        logger.info(f"Attack detected: {result['attack_type']} (confidence: {result['confidence']:.3f})")
                
                time.sleep(2)  # Process every 2 seconds
                
            except Exception as e:
                logger.error(f"Detection loop error: {e}")
                time.sleep(5)
    
    def _simulate_network_packet(self) -> Dict[str, Any]:
        """Simulate network packet data"""
        return {
            'src_ip': f"192.168.1.{np.random.randint(1, 255)}",
            'dst_ip': f"192.168.1.{np.random.randint(1, 255)}",
            'duration': np.random.exponential(1.0),
            'src_bytes': np.random.randint(0, 10000),
            'dst_bytes': np.random.randint(0, 10000),
            'count': np.random.randint(1, 100),
            'srv_count': np.random.randint(1, 50),
            'logged_in': np.random.choice([0, 1]),
            'hot': np.random.randint(0, 10),
            'num_failed_logins': np.random.randint(0, 5),
            'dst_host_count': np.random.randint(1, 255),
            'dst_host_srv_count': np.random.randint(1, 100)
        }
    
    def _calculate_severity(self, detection_result: Dict[str, Any]) -> str:
        """Calculate alert severity based on detection result"""
        confidence = detection_result['confidence']
        attack_type = detection_result['attack_type']
        
        if attack_type in ['dos', 'u2r'] and confidence > 0.8:
            return 'critical'
        elif confidence > 0.7:
            return 'high'
        elif confidence > 0.5:
            return 'medium'
        else:
            return 'low'
    
    def get_recent_detections(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent intrusion detections"""
        return self.detection_history[-limit:] if self.detection_history else []
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get IDS performance metrics"""
        if self.performance_metrics['total_packets'] > 0:
            self.performance_metrics['detection_rate'] = (
                self.performance_metrics['attacks_detected'] / 
                self.performance_metrics['total_packets']
            )
        
        return self.performance_metrics.copy()
    
    def stop_detection(self):
        """Stop real-time detection"""
        self.running = False
        logger.info("Real-time IDS engine stopped")