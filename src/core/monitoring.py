# src/core/monitoring.py

"""
Monitoring module for tracking model drift, performance metrics, and system health
in a Federated Learning Framework for Healthcare Data Sharing.

Features:
- Model drift detection
- Performance metrics tracking
- System health monitoring
- Advanced logging and alerting
- Thread-safe and memory-efficient implementation
- Fully configurable and production-ready

Author: Senior Software Engineer - Production Systems Specialist
"""

import os
import logging
import threading
import time
from typing import Dict, Any, Optional
from datetime import datetime
import psutil
import numpy as np
from sklearn.metrics import mean_squared_error

# Constants for monitoring thresholds
DEFAULT_DRIFT_THRESHOLD = 0.05
DEFAULT_HEALTH_CHECK_INTERVAL = 60  # seconds
DEFAULT_METRICS_LOG_INTERVAL = 300  # seconds

# Logging configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("MonitoringModule")

# Dependency injection for configuration
class MonitoringConfig:
    def __init__(self, drift_threshold: float = DEFAULT_DRIFT_THRESHOLD,
                 health_check_interval: int = DEFAULT_HEALTH_CHECK_INTERVAL,
                 metrics_log_interval: int = DEFAULT_METRICS_LOG_INTERVAL):
        self.drift_threshold = drift_threshold
        self.health_check_interval = health_check_interval
        self.metrics_log_interval = metrics_log_interval

# Thread-safe singleton pattern for monitoring
class MonitoringSingleton:
    _instance_lock = threading.Lock()
    _instance = None

    def __new__(cls, *args, **kwargs):
        with cls._instance_lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
        return cls._instance

# Monitoring class
class Monitoring(MonitoringSingleton):
    def __init__(self, config: MonitoringConfig):
        if not hasattr(self, "_initialized"):
            self.config = config
            self._initialized = True
            self._lock = threading.Lock()
            self._last_metrics = {}
            self._last_drift_check = None
            self._last_health_check = None

    def track_model_drift(self, baseline_predictions: np.ndarray, current_predictions: np.ndarray) -> bool:
        """
        Detects model drift by comparing baseline predictions with current predictions.
        Returns True if drift exceeds the configured threshold.
        """
        with self._lock:
            drift_score = mean_squared_error(baseline_predictions, current_predictions)
            logger.info(f"Model drift score: {drift_score}")
            if drift_score > self.config.drift_threshold:
                logger.warning(f"Model drift detected! Drift score: {drift_score}")
                return True
            return False

    def log_performance_metrics(self, metrics: Dict[str, Any]) -> None:
        """
        Logs performance metrics at regular intervals.
        """
        with self._lock:
            self._last_metrics = metrics
            logger.info(f"Performance metrics logged: {metrics}")

    def monitor_system_health(self) -> Dict[str, Any]:
        """
        Monitors system health metrics such as CPU, memory, and disk usage.
        Returns a dictionary of system health metrics.
        """
        with self._lock:
            health_metrics = {
                "cpu_usage": psutil.cpu_percent(interval=1),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "timestamp": datetime.now().isoformat()
            }
            logger.info(f"System health metrics: {health_metrics}")
            return health_metrics

    def start_monitoring(self) -> None:
        """
        Starts the monitoring process in a separate thread.
        """
        def monitor():
            while True:
                try:
                    # Perform health check
                    health_metrics = self.monitor_system_health()
                    self._last_health_check = health_metrics

                    # Log metrics periodically
                    if self._last_metrics:
                        self.log_performance_metrics(self._last_metrics)

                    time.sleep(self.config.health_check_interval)
                except Exception as e:
                    logger.error(f"Error during monitoring: {e}")

        monitoring_thread = threading.Thread(target=monitor, daemon=True)
        monitoring_thread.start()
        logger.info("Monitoring thread started.")

# Example usage
if __name__ == "__main__":
    # Load configuration
    config = MonitoringConfig(drift_threshold=0.1, health_check_interval=30, metrics_log_interval=120)

    # Initialize monitoring
    monitoring = Monitoring(config)

    # Simulate model drift detection
    baseline = np.array([0.1, 0.2, 0.3])
    current = np.array([0.15, 0.25, 0.35])
    drift_detected = monitoring.track_model_drift(baseline, current)
    logger.info(f"Drift detected: {drift_detected}")

    # Simulate performance metrics logging
    metrics = {"accuracy": 0.95, "loss": 0.05}
    monitoring.log_performance_metrics(metrics)

    # Start system health monitoring
    monitoring.start_monitoring()