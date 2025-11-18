"""
MinimalERP - Accounting Schemas

Pydantic models for request/response validation.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


class InvoiceLineCreate(BaseModel):
    """Invoice line creation schema"""
    description: str
    quantity: float = 1.0
    unit_price: float
    vat_rate: float = 0.0
    withholding_rate: float = 0.0

    @validator("quantity")
    def quantity_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Miktar 0'dan büyük olmalıdır")
        return v


class InvoiceCreate(BaseModel):
    """Invoice creation schema"""
    invoice_number: str
    invoice_date: date
    invoice_type: str  # SATIS, ALIS, IADE
    company_id: int
    partner_id: int
    subtotal: float = 0.0
    vat_amount: float = 0.0
    total_amount: float = 0.0
    lines: List[InvoiceLineCreate] = []


class InvoiceResponse(BaseModel):
    """Invoice response schema"""
    id: int
    invoice_number: str
    invoice_date: date
    invoice_type: str
    company_id: int
    partner_id: int
    subtotal: float
    vat_amount: float
    total_amount: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class CashFlowForecastResponse(BaseModel):
    """Cash flow forecast response"""
    forecast_date: date
    predicted_inflow: float
    predicted_outflow: float
    predicted_balance: float
    confidence_score: Optional[float] = None


class AnomalyResponse(BaseModel):
    """Anomaly detection response"""
    id: int
    detection_date: datetime
    anomaly_type: str
    severity: str
    anomaly_score: float
    description: str
    is_resolved: bool

    class Config:
        from_attributes = True


class AnomalyResolution(BaseModel):
    """Anomaly resolution schema"""
    resolution_notes: str


class PartnerCreate(BaseModel):
    """Partner creation schema"""
    name: str
    tax_office: Optional[str] = None
    tax_number: Optional[str] = None
    is_customer: bool = True
    is_supplier: bool = False
    email: Optional[str] = None
    phone: Optional[str] = None


class PartnerResponse(BaseModel):
    """Partner response schema"""
    id: int
    name: str
    tax_office: Optional[str]
    tax_number: Optional[str]
    is_customer: bool
    is_supplier: bool
    current_balance: float
    created_at: datetime

    class Config:
        from_attributes = True
