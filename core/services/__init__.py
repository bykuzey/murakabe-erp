"""
MinimalERP - Core Services Module
"""

from .ai_base import AIServiceBase, TimeSeriesAIService, ClassificationAIService

__all__ = [
    "AIServiceBase",
    "TimeSeriesAIService",
    "ClassificationAIService",
]
