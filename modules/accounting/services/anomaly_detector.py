"""
MinimalERP - Anomaly Detector

AI-powered anomaly detection for financial transactions.
"""

import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pickle

from core.services.ai_base import AIServiceBase
from core.config import settings

logger = logging.getLogger(__name__)


class AnomalyDetector(AIServiceBase):
    """
    Anomaly Detection Service using Isolation Forest.

    Detects:
    - Duplicate entries
    - Unusual amounts
    - Suspicious patterns
    - Outlier transactions
    - Frequency anomalies
    """

    def __init__(self):
        super().__init__(model_name="anomaly_detector")
        self.model = None
        self.scaler = StandardScaler()
        self.contamination = 0.1  # Expected proportion of outliers (10%)

    async def train(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """
        Train Isolation Forest model with normal transaction data.

        Args:
            data: DataFrame with transaction features
            **kwargs: Additional model parameters

        Returns:
            Training metrics
        """
        try:
            # Prepare features
            features = self._prepare_features(data)

            if features is None or len(features) == 0:
                return {"success": False, "error": "No valid features extracted"}

            # Scale features
            X_scaled = self.scaler.fit_transform(features)

            # Initialize and train Isolation Forest
            self.model = IsolationForest(
                contamination=kwargs.get('contamination', self.contamination),
                random_state=42,
                n_estimators=100,
                max_samples='auto',
                **{k: v for k, v in kwargs.items() if k != 'contamination'}
            )

            logger.info(f"Training Isolation Forest with {len(X_scaled)} samples")
            self.model.fit(X_scaled)

            # Calculate anomaly scores for training data
            scores = self.model.score_samples(X_scaled)
            predictions = self.model.predict(X_scaled)

            anomalies_count = np.sum(predictions == -1)
            anomaly_percentage = (anomalies_count / len(predictions)) * 100

            self.is_trained = True
            await self.save_model()

            logger.info(f"✅ Anomaly detector trained. Found {anomalies_count} anomalies ({anomaly_percentage:.1f}%)")

            return {
                "success": True,
                "training_samples": len(X_scaled),
                "anomalies_detected": int(anomalies_count),
                "anomaly_percentage": float(anomaly_percentage),
                "feature_count": features.shape[1]
            }

        except Exception as e:
            logger.error(f"Training failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def predict(self, data: Any, **kwargs) -> Dict[str, Any]:
        """
        Detect anomalies in transactions.

        Args:
            data: DataFrame with transactions or single transaction dict
            **kwargs: Additional parameters

        Returns:
            Anomaly detection results
        """
        try:
            if not self.is_trained or self.model is None:
                return {
                    "success": False,
                    "error": "Model not trained. Please train the model first."
                }

            # Convert single transaction to DataFrame
            if isinstance(data, dict):
                data = pd.DataFrame([data])

            # Prepare features
            features = self._prepare_features(data)

            if features is None or len(features) == 0:
                return {"success": False, "error": "No valid features"}

            # Scale features
            X_scaled = self.scaler.transform(features)

            # Predict anomalies
            predictions = self.model.predict(X_scaled)
            scores = self.model.score_samples(X_scaled)

            # Normalize scores to 0-1 range (higher = more anomalous)
            anomaly_scores = 1 - ((scores - scores.min()) / (scores.max() - scores.min() + 1e-10))

            # Prepare results
            results = []
            for idx, (pred, score) in enumerate(zip(predictions, anomaly_scores)):
                is_anomaly = pred == -1

                result = {
                    "index": int(idx),
                    "is_anomaly": bool(is_anomaly),
                    "anomaly_score": float(score),
                    "severity": self._get_severity(score),
                    "reasons": self._identify_anomaly_reasons(data.iloc[idx], score) if is_anomaly else []
                }

                results.append(result)

            anomalies_count = sum(1 for r in results if r['is_anomaly'])

            return {
                "success": True,
                "total_checked": len(results),
                "anomalies_found": anomalies_count,
                "results": results
            }

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _prepare_features(self, data: pd.DataFrame) -> Optional[np.ndarray]:
        """
        Prepare features for anomaly detection.

        Features:
        - Transaction amount
        - Transaction frequency (daily)
        - Amount deviation from mean
        - Time features (day of week, hour)
        - Partner frequency
        """
        try:
            features = []

            # Amount features
            if 'amount' in data.columns or 'total_amount' in data.columns:
                amount_col = 'amount' if 'amount' in data.columns else 'total_amount'
                features.append(data[amount_col].values.reshape(-1, 1))

            # Date features
            if 'date' in data.columns or 'invoice_date' in data.columns:
                date_col = 'date' if 'date' in data.columns else 'invoice_date'
                dates = pd.to_datetime(data[date_col])

                # Day of week
                features.append(dates.dt.dayofweek.values.reshape(-1, 1))

                # Day of month
                features.append(dates.dt.day.values.reshape(-1, 1))

                # Month
                features.append(dates.dt.month.values.reshape(-1, 1))

            # Partner ID (if available)
            if 'partner_id' in data.columns:
                features.append(data['partner_id'].values.reshape(-1, 1))

            # VAT rate (if available)
            if 'vat_rate' in data.columns:
                features.append(data['vat_rate'].fillna(20).values.reshape(-1, 1))

            if len(features) == 0:
                return None

            return np.hstack(features)

        except Exception as e:
            logger.error(f"Feature preparation failed: {e}")
            return None

    def _get_severity(self, score: float) -> str:
        """Classify anomaly severity based on score"""
        if score > 0.8:
            return "critical"
        elif score > 0.6:
            return "high"
        elif score > 0.4:
            return "medium"
        else:
            return "low"

    def _identify_anomaly_reasons(self, transaction: pd.Series, score: float) -> List[str]:
        """
        Identify reasons why transaction is anomalous.

        Returns list of human-readable reasons.
        """
        reasons = []

        # Check amount
        amount = transaction.get('amount') or transaction.get('total_amount')
        if amount and amount > 100000:
            reasons.append(f"Çok yüksek tutar: {amount:,.2f} TL")
        elif amount and amount < 0:
            reasons.append("Negatif tutar")

        # Check date patterns
        if 'date' in transaction or 'invoice_date' in transaction:
            date_col = 'date' if 'date' in transaction else 'invoice_date'
            date = pd.to_datetime(transaction[date_col])

            # Weekend transaction
            if date.dayofweek >= 5:
                reasons.append("Hafta sonu işlemi")

            # Month end/start
            if date.day >= 28 or date.day <= 2:
                reasons.append("Ay başı/sonu işlemi")

        # Check VAT
        if 'vat_rate' in transaction:
            vat_rate = transaction['vat_rate']
            if vat_rate not in [0, 1, 10, 20]:
                reasons.append(f"Olağandışı KDV oranı: %{vat_rate}")

        # Generic high score
        if score > 0.7 and not reasons:
            reasons.append("Genel işlem paterni olağandışı")

        return reasons if reasons else ["Anomali tespiti"]

    async def detect_duplicates(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Detect potential duplicate transactions.

        Args:
            data: DataFrame with transactions

        Returns:
            List of potential duplicates
        """
        try:
            duplicates = []

            # Check for exact duplicates
            duplicate_cols = ['invoice_number', 'invoice_date', 'total_amount', 'partner_id']
            available_cols = [col for col in duplicate_cols if col in data.columns]

            if not available_cols:
                return []

            # Find duplicates
            dup_mask = data.duplicated(subset=available_cols, keep=False)
            dup_groups = data[dup_mask].groupby(available_cols)

            for name, group in dup_groups:
                if len(group) > 1:
                    duplicates.append({
                        "type": "exact_duplicate",
                        "count": len(group),
                        "transactions": group.index.tolist(),
                        "details": dict(zip(available_cols, name)),
                        "severity": "high"
                    })

            # Check for near-duplicates (same day, similar amount)
            if 'invoice_date' in data.columns and 'total_amount' in data.columns:
                for date in data['invoice_date'].unique():
                    day_data = data[data['invoice_date'] == date]

                    for i, row1 in day_data.iterrows():
                        for j, row2 in day_data.iterrows():
                            if i >= j:
                                continue

                            # Similar amount (within 1%)
                            amt1 = row1['total_amount']
                            amt2 = row2['total_amount']
                            diff_percent = abs(amt1 - amt2) / max(amt1, amt2) * 100

                            if diff_percent < 1:
                                duplicates.append({
                                    "type": "near_duplicate",
                                    "transactions": [i, j],
                                    "details": {
                                        "date": str(date),
                                        "amount_1": float(amt1),
                                        "amount_2": float(amt2),
                                        "difference_percent": float(diff_percent)
                                    },
                                    "severity": "medium"
                                })

            logger.info(f"Found {len(duplicates)} potential duplicates")
            return duplicates

        except Exception as e:
            logger.error(f"Duplicate detection failed: {e}")
            return []

    async def save_model(self) -> bool:
        """Save model and scaler"""
        try:
            model_file = f"{self.model_path}/isolation_forest.pkl"
            scaler_file = f"{self.model_path}/scaler.pkl"

            with open(model_file, 'wb') as f:
                pickle.dump(self.model, f)

            with open(scaler_file, 'wb') as f:
                pickle.dump(self.scaler, f)

            logger.info("Model and scaler saved")
            return True
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            return False

    async def load_model(self) -> bool:
        """Load model and scaler"""
        try:
            model_file = f"{self.model_path}/isolation_forest.pkl"
            scaler_file = f"{self.model_path}/scaler.pkl"

            with open(model_file, 'rb') as f:
                self.model = pickle.load(f)

            with open(scaler_file, 'rb') as f:
                self.scaler = pickle.load(f)

            self.is_trained = True
            logger.info("Model and scaler loaded")
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
