from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional, List
from modules.inventory.models import ProductType, StockMoveType, StockMoveState


# Product Category Schemas
class ProductCategoryBase(BaseModel):
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None


class ProductCategoryCreate(ProductCategoryBase):
    pass


class ProductCategory(ProductCategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Product Schemas
class ProductBase(BaseModel):
    name: str
    barcode: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    product_type: ProductType = ProductType.STORABLE
    is_active: bool = True
    can_be_sold: bool = True
    can_be_purchased: bool = True
    list_price: float = 0.0
    cost_price: float = 0.0
    min_qty: float = 0.0
    max_qty: float = 0.0
    reorder_point: float = 0.0
    uom: str = "Adet"
    supplier_code: Optional[str] = None
    tax_rate: float = 20.0


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    barcode: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    product_type: Optional[ProductType] = None
    is_active: Optional[bool] = None
    can_be_sold: Optional[bool] = None
    can_be_purchased: Optional[bool] = None
    list_price: Optional[float] = None
    cost_price: Optional[float] = None
    min_qty: Optional[float] = None
    max_qty: Optional[float] = None
    reorder_point: Optional[float] = None
    uom: Optional[str] = None
    supplier_code: Optional[str] = None
    tax_rate: Optional[float] = None


class Product(ProductBase):
    id: int
    code: str
    qty_available: float
    qty_reserved: float
    virtual_available: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductSummary(BaseModel):
    """Liste görünümü için özet"""
    id: int
    code: str
    name: str
    barcode: Optional[str]
    category_id: Optional[int]
    list_price: float
    cost_price: float
    qty_available: float
    virtual_available: float
    is_active: bool

    class Config:
        from_attributes = True


# Stock Location Schemas
class StockLocationBase(BaseModel):
    name: str
    code: Optional[str] = None
    location_type: str = "internal"
    is_active: bool = True
    address: Optional[str] = None


class StockLocationCreate(StockLocationBase):
    pass


class StockLocation(StockLocationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Stock Move Schemas
class StockMoveBase(BaseModel):
    product_id: int
    move_type: StockMoveType
    location_from_id: int
    location_to_id: int
    quantity: float
    uom: str = "Adet"
    unit_price: float = 0.0
    scheduled_date: Optional[datetime] = None
    reference: Optional[str] = None
    note: Optional[str] = None

    @validator('quantity')
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Miktar 0\'dan büyük olmalıdır')
        return v


class StockMoveCreate(StockMoveBase):
    pass


class StockMoveUpdate(BaseModel):
    product_id: Optional[int] = None
    move_type: Optional[StockMoveType] = None
    location_from_id: Optional[int] = None
    location_to_id: Optional[int] = None
    quantity: Optional[float] = None
    uom: Optional[str] = None
    unit_price: Optional[float] = None
    scheduled_date: Optional[datetime] = None
    reference: Optional[str] = None
    note: Optional[str] = None
    state: Optional[StockMoveState] = None


class StockMove(StockMoveBase):
    id: int
    name: str
    state: StockMoveState
    total_value: float
    done_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StockMoveSummary(BaseModel):
    """Liste görünümü için özet"""
    id: int
    name: str
    product_id: int
    product_name: str
    move_type: StockMoveType
    state: StockMoveState
    quantity: float
    unit_price: float
    total_value: float
    scheduled_date: Optional[datetime]
    done_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# Stock Quant Schemas
class StockQuantBase(BaseModel):
    product_id: int
    location_id: int
    quantity: float = 0.0
    reserved_quantity: float = 0.0


class StockQuantCreate(StockQuantBase):
    pass


class StockQuant(StockQuantBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Dashboard Schemas
class LowStockAlert(BaseModel):
    """Düşük stok uyarısı"""
    product_id: int
    product_code: str
    product_name: str
    qty_available: float
    reorder_point: float
    min_qty: float

    class Config:
        from_attributes = True
