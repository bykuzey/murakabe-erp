"""
MinimalERP - Cash Flow Predictor

AI-powered cash flow forecasting using Prophet.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from prophet import Prophet
import pickle

from core.services.ai_base import TimeSeriesAIService
from core.config import settings

logger = logging.getLogger(__name__)


class CashFlowPredictor(TimeSeriesAIService):
    """
    Cash Flow Forecasting Service using Facebook Prophet.

    Features:
    - Historical data analysis
    - Trend detection
    - Seasonality modeling
    - Future predictions (30/60/90 days)
    - Confidence intervals
    - Critical date alerts
    """

    def __init__(self):
        super().__init__(model_name="cashflow_predictor")
        self.model = None
        self.last_training_date = None
        self.forecast_data = None

    async def train(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """
        Train Prophet model with historical cash flow data.

        Args:
            data: DataFrame with columns ['date', 'inflow', 'outflow']
            **kwargs: Additional Prophet parameters

        Returns:
            Training metrics and model info
        """
        try:
            # Validate data
            required_columns = ['date', 'inflow', 'outflow']
            if not self.validate_data(data, required_columns):
                return {"success": False, "error": "Invalid data format"}

            # Prepare data
            data = self.preprocess_data(data)

            # Calculate net cash flow
            data['net_flow'] = data['inflow'] - data['outflow']

            # Prepare for Prophet (requires 'ds' and 'y' columns)
            prophet_data = pd.DataFrame({
                'ds': pd.to_datetime(data['date']),
                'y': data['net_flow']
            })

            # Initialize and fit Prophet model
            self.model = Prophet(
                daily_seasonality=True,
                weekly_seasonality=True,
                yearly_seasonality=True,
                changepoint_prior_scale=0.05,  # Flexibility of trend
                seasonality_prior_scale=10.0,  # Flexibility of seasonality
                interval_width=0.95,  # 95% confidence interval
                **kwargs
            )

            logger.info(f"Training Prophet model with {len(prophet_data)} data points")
            self.model.fit(prophet_data)

            # Calculate training metrics
            predictions = self.model.predict(prophet_data)
            y_true = prophet_data['y'].values
            y_pred = predictions['yhat'].values

            metrics = self.calculate_metrics(y_true, y_pred)

            # Save model
            self.is_trained = True
            self.last_training_date = datetime.now()
            await self.save_model()

            logger.info(f"✅ Cash flow model trained successfully. RMSE: {metrics['rmse']:.2f}")

            return {
                "success": True,
                "metrics": metrics,
                "training_samples": len(prophet_data),
                "trained_at": self.last_training_date.isoformat()
            }

        except Exception as e:
            logger.error(f"Training failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def predict(self, data: Any = None, days_ahead: int = 30, **kwargs) -> Dict[str, Any]:
        """
        Predict future cash flow.

        Args:
            data: Not used (model uses historical data)
            days_ahead: Number of days to forecast
            **kwargs: Additional parameters

        Returns:
            Forecast with predictions and confidence intervals
        """
        try:
            if not self.is_trained or self.model is None:
                return {
                    "success": False,
                    "error": "Model not trained. Please train the model first."
                }

            # Create future dataframe
            future = self.model.make_future_dataframe(periods=days_ahead, freq='D')

            # Make predictions
            forecast = self.model.predict(future)

            # Get only future predictions
            future_forecast = forecast.tail(days_ahead)

            # Extract predictions
            predictions = []
            critical_dates = []

            for idx, row in future_forecast.iterrows():
                date = row['ds'].date()
                predicted_net = row['yhat']
                lower_bound = row['yhat_lower']
                upper_bound = row['yhat_upper']

                prediction = {
                    "date": date.isoformat(),
                    "predicted_net_flow": float(predicted_net),
                    "confidence_lower": float(lower_bound),
                    "confidence_upper": float(upper_bound),
                    "confidence_interval": float(upper_bound - lower_bound)
                }

                predictions.append(prediction)

                # Detect critical dates (negative cash flow)
                if predicted_net < 0:
                    critical_dates.append({
                        "date": date.isoformat(),
                        "predicted_deficit": abs(float(predicted_net)),
                        "severity": "high" if predicted_net < -10000 else "medium"
                    })

            # Calculate statistics
            mean_flow = float(future_forecast['yhat'].mean())
            std_flow = float(future_forecast['yhat'].std())

            # Detect seasonality
            seasonality_info = self.detect_seasonality(future_forecast['yhat'])

            self.forecast_data = predictions

            return {
                "success": True,
                "forecast_period": days_ahead,
                "predictions": predictions,
                "critical_dates": critical_dates,
                "statistics": {
                    "mean_daily_flow": mean_flow,
                    "std_daily_flow": std_flow,
                    "total_predicted_flow": float(future_forecast['yhat'].sum())
                },
                "seasonality": seasonality_info,
                "model_info": {
                    "trained_at": self.last_training_date.isoformat() if self.last_training_date else None,
                    "model_type": "Prophet"
                }
            }

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def save_model(self) -> bool:
        """Save trained Prophet model to disk"""
        try:
            model_file = f"{self.model_path}/prophet_model.pkl"
            with open(model_file, 'wb') as f:
                pickle.dump(self.model, f)

            logger.info(f"Model saved to {model_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            return False

    async def load_model(self) -> bool:
        """Load trained Prophet model from disk"""
        try:
            model_file = f"{self.model_path}/prophet_model.pkl"
            with open(model_file, 'rb') as f:
                self.model = pickle.load(f)

            self.is_trained = True
            logger.info(f"Model loaded from {model_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False

    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """Get component importance from Prophet model"""
        if not self.is_trained or self.model is None:
            return None

        try:
            # Prophet doesn't have traditional feature importance
            # but we can check component strengths
            components = {}

            if hasattr(self.model, 'seasonalities'):
                for name, params in self.model.seasonalities.items():
                    components[f"seasonality_{name}"] = float(params.get('prior_scale', 0))

            return components
        except Exception:
            return None

    async def get_alerts(self, threshold: float = 0.0) -> List[Dict[str, Any]]:
        """
        Get cash flow alerts based on predictions.

        Args:
            threshold: Negative flow threshold for alerts

        Returns:
            List of alerts
        """
        if not self.forecast_data:
            return []

        alerts = []

        for prediction in self.forecast_data:
            net_flow = prediction['predicted_net_flow']

            if net_flow < threshold:
                severity = "critical" if net_flow < -50000 else "high" if net_flow < -10000 else "medium"

                alerts.append({
                    "date": prediction['date'],
                    "type": "negative_cash_flow",
                    "severity": severity,
                    "predicted_deficit": abs(net_flow),
                    "message": f"{prediction['date']} tarihinde {abs(net_flow):.2f} TL nakit açığı öngörülüyor",
                    "recommendation": self._get_recommendation(net_flow)
                })

        return alerts

    def _get_recommendation(self, net_flow: float) -> str:
        """Generate recommendation based on predicted cash flow"""
        if net_flow < -50000:
            return "ACİL: Büyük nakit açığı riski. Tahsilatları hızlandırın veya kredi hattı açın."
        elif net_flow < -10000:
            return "UYARI: Müşteri tahsilatlarını öne alın ve gereksiz harcamaları erteleyin."
        elif net_flow < 0:
            return "DİKKAT: Küçük nakit açığı olabilir. Giderlerinizi gözden geçirin."
        else:
            return "Normal nakit akışı bekleniyor."

    async def analyze_trend(self) -> Dict[str, Any]:
        """Analyze cash flow trend"""
        if not self.is_trained or self.model is None:
            return {"success": False, "error": "Model not trained"}

        try:
            # Extract trend component
            if hasattr(self.model, 'params') and 'trend' in self.model.params:
                trend = self.model.params['trend']

                return {
                    "success": True,
                    "trend_direction": "increasing" if trend > 0 else "decreasing",
                    "trend_strength": abs(float(trend)),
                    "interpretation": self._interpret_trend(trend)
                }

            return {"success": False, "error": "Trend data not available"}

        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            return {"success": False, "error": str(e)}

    def _interpret_trend(self, trend: float) -> str:
        """Interpret trend value"""
        if trend > 100:
            return "Güçlü pozitif trend: Nakit akışınız sürekli artıyor. 📈"
        elif trend > 0:
            return "Hafif pozitif trend: Nakit akışınız iyileşiyor. ✅"
        elif trend > -100:
            return "Hafif negatif trend: Nakit akışınız azalıyor. ⚠️"
        else:
            return "Güçlü negatif trend: Nakit akışınız ciddi şekilde azalıyor. 🚨"
