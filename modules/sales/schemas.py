from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional, List
from modules.sales.models import CustomerType, SalesOrderState, PaymentTerms


# Customer Schemas
class CustomerBase(BaseModel):
    name: str
    customer_type: CustomerType = CustomerType.INDIVIDUAL
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    website: Optional[str] = None
    street: Optional[str] = None
    street2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: str = "Türkiye"
    tax_office: Optional[str] = None
    tax_number: Optional[str] = None
    payment_term: PaymentTerms = PaymentTerms.IMMEDIATE
    credit_limit: float = 0.0
    is_active: bool = True
    note: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    customer_type: Optional[CustomerType] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    website: Optional[str] = None
    street: Optional[str] = None
    street2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    tax_office: Optional[str] = None
    tax_number: Optional[str] = None
    payment_term: Optional[PaymentTerms] = None
    credit_limit: Optional[float] = None
    is_active: Optional[bool] = None
    note: Optional[str] = None


class Customer(CustomerBase):
    id: int
    code: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Sales Order Line Schemas
class SalesOrderLineBase(BaseModel):
    product_name: str
    product_code: Optional[str] = None
    description: Optional[str] = None
    quantity: float = 1.0
    unit_price: float = 0.0
    discount: float = 0.0
    tax_rate: float = 20.0

    @validator('quantity')
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Miktar 0\'dan büyük olmalıdır')
        return v


class SalesOrderLineCreate(SalesOrderLineBase):
    pass


class SalesOrderLine(SalesOrderLineBase):
    id: int
    order_id: int
    price_subtotal: float
    price_tax: float
    price_total: float
    sequence: int
    created_at: datetime

    class Config:
        from_attributes = True


# Sales Order Schemas
class SalesOrderBase(BaseModel):
    customer_id: int
    order_date: Optional[datetime] = None
    validity_date: Optional[datetime] = None
    expected_delivery: Optional[datetime] = None
    delivery_address: Optional[str] = None
    invoice_address: Optional[str] = None
    payment_term: PaymentTerms = PaymentTerms.IMMEDIATE
    amount_discount: float = 0.0
    note: Optional[str] = None
    internal_note: Optional[str] = None
    reference: Optional[str] = None


class SalesOrderCreate(SalesOrderBase):
    lines: List[SalesOrderLineCreate] = []


class SalesOrderUpdate(BaseModel):
    customer_id: Optional[int] = None
    state: Optional[SalesOrderState] = None
    validity_date: Optional[datetime] = None
    expected_delivery: Optional[datetime] = None
    delivery_address: Optional[str] = None
    invoice_address: Optional[str] = None
    payment_term: Optional[PaymentTerms] = None
    amount_discount: Optional[float] = None
    note: Optional[str] = None
    internal_note: Optional[str] = None
    reference: Optional[str] = None
    lines: Optional[List[SalesOrderLineCreate]] = None


class SalesOrder(SalesOrderBase):
    id: int
    name: str
    state: SalesOrderState
    amount_untaxed: float
    amount_tax: float
    amount_total: float
    confirmation_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    lines: List[SalesOrderLine] = []

    class Config:
        from_attributes = True


class SalesOrderSummary(BaseModel):
    """Liste görünümü için özet"""
    id: int
    name: str
    state: SalesOrderState
    customer_id: int
    customer_name: str
    order_date: datetime
    amount_total: float
    created_at: datetime

    class Config:
        from_attributes = True
