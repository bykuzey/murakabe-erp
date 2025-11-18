from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from core.database import Base


# Enums
class ProductType(str, enum.Enum):
    STORABLE = "storable"      # Stoklanabilir
    CONSUMABLE = "consumable"  # Sarf Malzeme
    SERVICE = "service"        # Hizmet


class StockMoveType(str, enum.Enum):
    IN = "in"           # Giriş
    OUT = "out"         # Çıkış
    INTERNAL = "internal"  # İç Transfer


class StockMoveState(str, enum.Enum):
    DRAFT = "draft"        # Taslak
    CONFIRMED = "confirmed"  # Onaylandı
    DONE = "done"          # Tamamlandı
    CANCELLED = "cancelled"  # İptal


# Models
class Product(Base):
    """Ürün Modeli - Merkezi ürün yönetimi"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    # Temel Bilgiler
    name = Column(String(200), nullable=False, index=True)
    code = Column(String(50), unique=True, index=True)  # Ürün Kodu
    barcode = Column(String(50), unique=True, index=True)
    description = Column(Text)

    # Kategori
    category_id = Column(Integer, ForeignKey("product_categories.id"), index=True)
    category = relationship("ProductCategory", back_populates="products")

    # Tip ve Durum
    product_type = Column(SQLEnum(ProductType), default=ProductType.STORABLE)
    is_active = Column(Boolean, default=True)
    can_be_sold = Column(Boolean, default=True)
    can_be_purchased = Column(Boolean, default=True)

    # Fiyatlar
    list_price = Column(Float, default=0.0)  # Satış Fiyatı
    cost_price = Column(Float, default=0.0)  # Maliyet

    # Stok Bilgileri
    qty_available = Column(Float, default=0.0)  # Mevcut Stok
    qty_reserved = Column(Float, default=0.0)   # Rezerve Stok
    virtual_available = Column(Float, default=0.0)  # Kullanılabilir (available - reserved)

    # Stok Limitleri
    min_qty = Column(Float, default=0.0)  # Minimum Stok
    max_qty = Column(Float, default=0.0)  # Maximum Stok
    reorder_point = Column(Float, default=0.0)  # Yeniden Sipariş Noktası

    # Birim
    uom = Column(String(50), default="Adet")  # Birim (Adet, Kg, Litre, vb.)

    # Tedarikçi
    supplier_id = Column(Integer)  # Foreign key to Customer/Supplier (gelecekte)
    supplier_code = Column(String(50))  # Tedarikçi Ürün Kodu

    # Vergi
    tax_rate = Column(Float, default=20.0)  # KDV oranı

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer)

    # İlişkiler
    stock_moves = relationship("StockMove", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product {self.name} ({self.code})>"

    def update_virtual_available(self):
        """Kullanılabilir stok hesaplama"""
        qty_reserved = self.qty_reserved or 0.0
        self.virtual_available = self.qty_available - qty_reserved

    def is_below_reorder_point(self) -> bool:
        """Yeniden sipariş noktasının altında mı?"""
        return self.virtual_available <= self.reorder_point if self.reorder_point > 0 else False


class ProductCategory(Base):
    """Ürün Kategorisi"""
    __tablename__ = "product_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    code = Column(String(50), unique=True)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey("product_categories.id"))  # Alt kategori desteği

    # İlişkiler
    products = relationship("Product", back_populates="category")
    parent = relationship("ProductCategory", remote_side=[id], backref="children")

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ProductCategory {self.name}>"


class StockLocation(Base):
    """Depo/Lokasyon Modeli"""
    __tablename__ = "stock_locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    code = Column(String(50), unique=True, index=True)
    location_type = Column(String(50), default="internal")  # internal, customer, supplier, transit
    is_active = Column(Boolean, default=True)

    # Adres
    address = Column(Text)

    # İlişkiler
    moves_from = relationship("StockMove", foreign_keys="StockMove.location_from_id", back_populates="location_from")
    moves_to = relationship("StockMove", foreign_keys="StockMove.location_to_id", back_populates="location_to")

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<StockLocation {self.name}>"


class StockMove(Base):
    """Stok Hareketi - Giriş/Çıkış/Transfer"""
    __tablename__ = "stock_moves"

    id = Column(Integer, primary_key=True, index=True)

    # Referans
    name = Column(String(100), unique=True, index=True)  # SM001, SM002
    reference = Column(String(100))  # Dış referans (Sipariş no, vb.)

    # Ürün
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    product = relationship("Product", back_populates="stock_moves")

    # Hareket Bilgileri
    move_type = Column(SQLEnum(StockMoveType), nullable=False, index=True)
    state = Column(SQLEnum(StockMoveState), default=StockMoveState.DRAFT, index=True)

    # Lokasyonlar
    location_from_id = Column(Integer, ForeignKey("stock_locations.id"), nullable=False, index=True)
    location_to_id = Column(Integer, ForeignKey("stock_locations.id"), nullable=False, index=True)
    location_from = relationship("StockLocation", foreign_keys=[location_from_id], back_populates="moves_from")
    location_to = relationship("StockLocation", foreign_keys=[location_to_id], back_populates="moves_to")

    # Miktar
    quantity = Column(Float, nullable=False)
    uom = Column(String(50), default="Adet")

    # Fiyat
    unit_price = Column(Float, default=0.0)
    total_value = Column(Float, default=0.0)

    # Tarihler
    scheduled_date = Column(DateTime)  # Planlanan Tarih
    done_date = Column(DateTime)  # Gerçekleşme Tarihi

    # Notlar
    note = Column(Text)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer)
    confirmed_by = Column(Integer)

    def __repr__(self):
        return f"<StockMove {self.name} - {self.move_type}>"

    def calculate_total(self):
        """Toplam değeri hesapla"""
        self.total_value = self.quantity * self.unit_price

    def confirm(self):
        """Hareketi onayla"""
        if self.state == StockMoveState.DRAFT:
            self.state = StockMoveState.CONFIRMED

    def execute(self):
        """Hareketi gerçekleştir - stok güncelle"""
        if self.state != StockMoveState.CONFIRMED:
            raise ValueError("Sadece onaylanmış hareketler gerçekleştirilebilir")

        # Stok güncellemesi (basitleştirilmiş - gerçek uygulamada daha karmaşık olabilir)
        if self.move_type == StockMoveType.IN:
            # Giriş - stoğu artır
            self.product.qty_available += self.quantity
        elif self.move_type == StockMoveType.OUT:
            # Çıkış - stoğu azalt
            self.product.qty_available -= self.quantity

        self.product.update_virtual_available()
        self.state = StockMoveState.DONE
        self.done_date = datetime.utcnow()


class StockQuant(Base):
    """Stok Miktarları - Lokasyon bazlı stok takibi"""
    __tablename__ = "stock_quants"

    id = Column(Integer, primary_key=True, index=True)

    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    location_id = Column(Integer, ForeignKey("stock_locations.id"), nullable=False, index=True)

    quantity = Column(Float, default=0.0)
    reserved_quantity = Column(Float, default=0.0)

    # İlişkiler
    product = relationship("Product")
    location = relationship("StockLocation")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<StockQuant Product:{self.product_id} Location:{self.location_id} Qty:{self.quantity}>"
