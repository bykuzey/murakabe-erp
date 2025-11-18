"""
MinimalERP - AI Service Base

Base class for all AI services with common functionality.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import logging
from datetime import datetime
import numpy as np
import pandas as pd
from core.config import settings

logger = logging.getLogger(__name__)


class AIServiceBase(ABC):
    """
    Base class for AI services.

    Provides common functionality for all AI models:
    - Model loading/saving
    - Prediction caching
    - Error handling
    - Logging
    """

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = None
        self.is_trained = False
        self.last_trained_at = None
        self.model_path = f"{settings.AI_MODELS_PATH}/{model_name}"

        logger.info(f"Initializing AI service: {model_name}")

    @abstractmethod
    async def train(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """
        Train the model with provided data.

        Args:
            data: Training data
            **kwargs: Additional training parameters

        Returns:
            Training metrics and results
        """
        pass

    @abstractmethod
    async def predict(self, data: Any, **kwargs) -> Any:
        """
        Make predictions using the trained model.

        Args:
            data: Input data for prediction
            **kwargs: Additional prediction parameters

        Returns:
            Predictions
        """
        pass

    async def load_model(self) -> bool:
        """
        Load trained model from disk.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Subclasses should implement model loading
            logger.info(f"Loading model: {self.model_name}")
            return True
        except Exception as e:
            logger.error(f"Error loading model {self.model_name}: {e}")
            return False

    async def save_model(self) -> bool:
        """
        Save trained model to disk.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Subclasses should implement model saving
            logger.info(f"Saving model: {self.model_name}")
            self.last_trained_at = datetime.now()
            return True
        except Exception as e:
            logger.error(f"Error saving model {self.model_name}: {e}")
            return False

    def validate_data(self, data: pd.DataFrame, required_columns: List[str]) -> bool:
        """
        Validate input data.

        Args:
            data: DataFrame to validate
            required_columns: List of required column names

        Returns:
            True if valid, False otherwise
        """
        if data is None or data.empty:
            logger.error("Data is empty")
            return False

        missing_columns = set(required_columns) - set(data.columns)
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            return False

        return True

    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess data before training/prediction.

        Args:
            data: Raw data

        Returns:
            Preprocessed data
        """
        # Remove duplicates
        data = data.drop_duplicates()

        # Handle missing values
        data = data.fillna(method='ffill').fillna(method='bfill')

        return data

    def calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """
        Calculate common evaluation metrics.

        Args:
            y_true: Actual values
            y_pred: Predicted values

        Returns:
            Dictionary of metrics
        """
        from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

        mae = mean_absolute_error(y_true, y_pred)
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_true, y_pred)

        return {
            "mae": float(mae),
            "mse": float(mse),
            "rmse": float(rmse),
            "r2": float(r2)
        }

    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """
        Get feature importance from the model.

        Returns:
            Dictionary of feature names and their importance scores
        """
        # Subclasses should implement this if applicable
        return None

    async def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the model.

        Returns:
            Model metadata
        """
        return {
            "name": self.model_name,
            "is_trained": self.is_trained,
            "last_trained_at": self.last_trained_at.isoformat() if self.last_trained_at else None,
            "model_path": self.model_path
        }


class TimeSeriesAIService(AIServiceBase):
    """
    Base class for time series forecasting AI services.
    """

    def prepare_time_series_data(
        self,
        data: pd.DataFrame,
        date_column: str,
        value_column: str,
        frequency: str = 'D'
    ) -> pd.DataFrame:
        """
        Prepare time series data for forecasting.

        Args:
            data: Raw data
            date_column: Name of date column
            value_column: Name of value column
            frequency: Time series frequency (D=daily, W=weekly, M=monthly)

        Returns:
            Prepared time series data
        """
        # Convert date column to datetime
        data[date_column] = pd.to_datetime(data[date_column])

        # Set date as index
        data = data.set_index(date_column)

        # Resample to specified frequency
        data = data.resample(frequency)[value_column].sum()

        # Fill missing values
        data = data.fillna(method='ffill')

        return pd.DataFrame({value_column: data})

    def detect_seasonality(self, data: pd.Series) -> Dict[str, Any]:
        """
        Detect seasonality in time series data.

        Args:
            data: Time series data

        Returns:
            Seasonality information
        """
        from statsmodels.tsa.seasonal import seasonal_decompose

        try:
            # Perform seasonal decomposition
            decomposition = seasonal_decompose(data, model='additive', period=7)

            return {
                "has_trend": decomposition.trend.notna().sum() > 0,
                "has_seasonality": decomposition.seasonal.notna().sum() > 0,
                "seasonal_strength": float(decomposition.seasonal.std() / data.std())
            }
        except Exception as e:
            logger.warning(f"Could not detect seasonality: {e}")
            return {
                "has_trend": False,
                "has_seasonality": False,
                "seasonal_strength": 0.0
            }


class ClassificationAIService(AIServiceBase):
    """
    Base class for classification AI services.
    """

    def calculate_classification_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_prob: Optional[np.ndarray] = None
    ) -> Dict[str, float]:
        """
        Calculate classification metrics.

        Args:
            y_true: Actual labels
            y_pred: Predicted labels
            y_prob: Prediction probabilities (optional)

        Returns:
            Dictionary of metrics
        """
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

        metrics = {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "precision": float(precision_score(y_true, y_pred, average='weighted', zero_division=0)),
            "recall": float(recall_score(y_true, y_pred, average='weighted', zero_division=0)),
            "f1": float(f1_score(y_true, y_pred, average='weighted', zero_division=0))
        }

        if y_prob is not None:
            from sklearn.metrics import roc_auc_score
            try:
                metrics["auc"] = float(roc_auc_score(y_true, y_prob, average='weighted', multi_class='ovr'))
            except Exception:
                pass

        return metrics
