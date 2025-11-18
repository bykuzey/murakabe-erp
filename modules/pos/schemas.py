"""
POS Module - API Schemas

Pydantic models for request/response validation.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SessionState(str, Enum):
    OPENING_CONTROL = "opening_control"
    OPENED = "opened"
    CLOSING_CONTROL = "closing_control"
    CLOSED = "closed"


class OrderState(str, Enum):
    DRAFT = "draft"
    PAID = "paid"
    DONE = "done"
    INVOICED = "invoiced"
    CANCELLED = "cancelled"


class PaymentMethod(str, Enum):
    CASH = "cash"
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    CHECK = "check"


# ============= SESSION SCHEMAS =============

class POSSessionCreate(BaseModel):
    user_id: int
    user_name: str
    opening_cash: float = 0.0
    notes: Optional[str] = None


class POSSessionUpdate(BaseModel):
    state: Optional[SessionState] = None
    closing_cash: Optional[float] = None
    notes: Optional[str] = None


class POSSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    user_id: int
    user_name: str
    state: str
    start_at: datetime
    stop_at: Optional[datetime] = None
    opening_cash: float
    closing_cash: Optional[float] = None
    cash_register_difference: float
    total_sales: float
    total_payments: float
    order_count: int
    notes: Optional[str] = None
    created_at: datetime


# ============= ORDER LINE SCHEMAS =============

class POSOrderLineCreate(BaseModel):
    product_id: int
    product_name: str
    product_barcode: Optional[str] = None
    qty: float = 1.0
    price_unit: float
    discount: float = 0.0
    tax_rate: float = 20.0


class POSOrderLineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    product_name: str
    product_barcode: Optional[str] = None
    qty: float
    price_unit: float
    discount: float
    tax_rate: float
    price_subtotal: float
    price_subtotal_incl: float


# ============= PAYMENT SCHEMAS =============

class POSPaymentCreate(BaseModel):
    payment_method: PaymentMethod
    payment_method_name: str
    amount: float
    card_type: Optional[str] = None
    card_number_masked: Optional[str] = None


class POSPaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    payment_method: str
    payment_method_name: str
    amount: float
    card_type: Optional[str] = None
    card_number_masked: Optional[str] = None
    payment_date: datetime


# ============= ORDER SCHEMAS =============

class POSOrderCreate(BaseModel):
    session_id: int
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_tax_id: Optional[str] = None
    lines: List[POSOrderLineCreate]
    payments: List[POSPaymentCreate]
    note: Optional[str] = None


class POSOrderUpdate(BaseModel):
    state: Optional[OrderState] = None
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_tax_id: Optional[str] = None
    note: Optional[str] = None


class POSOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    session_id: int
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_tax_id: Optional[str] = None
    state: str
    date_order: datetime
    amount_tax: float
    amount_total: float
    amount_paid: float
    amount_return: float
    receipt_number: Optional[str] = None
    invoice_id: Optional[int] = None
    note: Optional[str] = None
    lines: List[POSOrderLineResponse] = []
    payments: List[POSPaymentResponse] = []
    created_at: datetime


# ============= PRODUCT SCHEMAS =============

class POSProductCreate(BaseModel):
    name: str
    internal_reference: Optional[str] = None
    barcode: Optional[str] = None
    category_id: Optional[int] = None
    list_price: float
    cost_price: float = 0.0
    tax_rate: float = 20.0
    qty_available: float = 0.0
    track_inventory: bool = True
    image_url: Optional[str] = None
    color: str = "#3b82f6"
    available_in_pos: bool = True
    to_weight: bool = False
    is_favorite: bool = False
    sequence: int = 10
    description: Optional[str] = None


class POSProductUpdate(BaseModel):
    name: Optional[str] = None
    internal_reference: Optional[str] = None
    barcode: Optional[str] = None
    category_id: Optional[int] = None
    list_price: Optional[float] = None
    cost_price: Optional[float] = None
    tax_rate: Optional[float] = None
    qty_available: Optional[float] = None
    track_inventory: Optional[bool] = None
    image_url: Optional[str] = None
    color: Optional[str] = None
    available_in_pos: Optional[bool] = None
    to_weight: Optional[bool] = None
    is_favorite: Optional[bool] = None
    sequence: Optional[int] = None
    active: Optional[bool] = None
    description: Optional[str] = None


class POSProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    internal_reference: Optional[str] = None
    barcode: Optional[str] = None
    category_id: Optional[int] = None
    list_price: float
    cost_price: float
    tax_rate: float
    qty_available: float
    track_inventory: bool
    image_url: Optional[str] = None
    color: str
    available_in_pos: bool
    to_weight: bool
    is_favorite: bool
    sequence: int
    active: bool
    description: Optional[str] = None
    created_at: datetime


# ============= CATEGORY SCHEMAS =============

class POSCategoryCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None
    color: str = "#6366f1"
    icon: Optional[str] = None
    image_url: Optional[str] = None
    sequence: int = 10


class POSCategoryUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    image_url: Optional[str] = None
    sequence: Optional[int] = None
    active: Optional[bool] = None


class POSCategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    parent_id: Optional[int] = None
    color: str
    icon: Optional[str] = None
    image_url: Optional[str] = None
    sequence: int
    active: bool
    created_at: datetime


# ============= CONFIG SCHEMAS =============

class POSConfigCreate(BaseModel):
    name: str
    company_name: str
    company_vat: Optional[str] = None
    company_address: Optional[str] = None
    company_phone: Optional[str] = None
    receipt_header: Optional[str] = None
    receipt_footer: Optional[str] = None
    auto_print_receipt: bool = True
    payment_methods: List[dict] = Field(default_factory=list)
    allow_discount: bool = True
    max_discount: float = 50.0
    require_customer: bool = False
    allow_invoice: bool = True
    receipt_prefix: str = "FIS"


class POSConfigResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    company_name: str
    company_vat: Optional[str] = None
    company_address: Optional[str] = None
    company_phone: Optional[str] = None
    receipt_header: Optional[str] = None
    receipt_footer: Optional[str] = None
    auto_print_receipt: bool
    payment_methods: List[dict]
    allow_discount: bool
    max_discount: float
    require_customer: bool
    allow_invoice: bool
    receipt_prefix: str
    receipt_sequence: int
    active: bool
    created_at: datetime
