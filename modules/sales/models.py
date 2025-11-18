from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from core.database import Base


# Enums
class CustomerType(str, enum.Enum):
    INDIVIDUAL = "individual"  # Bireysel
    CORPORATE = "corporate"    # Kurumsal


class SalesOrderState(str, enum.Enum):
    DRAFT = "draft"           # Taslak
    QUOTATION = "quotation"   # Teklif
    CONFIRMED = "confirmed"   # Onaylandı
    DELIVERED = "delivered"   # Teslim Edildi
    CANCELLED = "cancelled"   # İptal


class PaymentTerms(str, enum.Enum):
    IMMEDIATE = "immediate"   # Peşin
    NET15 = "net15"          # 15 Gün
    NET30 = "net30"          # 30 Gün
    NET60 = "net60"          # 60 Gün
    NET90 = "net90"          # 90 Gün


# Models
class Customer(Base):
    """Müşteri Modeli - Bireysel ve Kurumsal Müşteriler"""
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)

    # Temel Bilgiler
    name = Column(String(200), nullable=False, index=True)
    customer_type = Column(SQLEnum(CustomerType), default=CustomerType.INDIVIDUAL)
    code = Column(String(50), unique=True, index=True)  # Müşteri Kodu

    # İletişim
    email = Column(String(100), index=True)
    phone = Column(String(20))
    mobile = Column(String(20))
    website = Column(String(100))

    # Adres
    street = Column(String(200))
    street2 = Column(String(200))
    city = Column(String(100))
    state = Column(String(100))  # İl
    zip_code = Column(String(10))
    country = Column(String(100), default="Türkiye")

    # Vergi Bilgileri
    tax_office = Column(String(100))  # Vergi Dairesi
    tax_number = Column(String(20), index=True)  # VKN/TCKN

    # Ticari Bilgiler
    payment_term = Column(SQLEnum(PaymentTerms), default=PaymentTerms.IMMEDIATE)
    credit_limit = Column(Float, default=0.0)  # Kredi Limiti
    is_active = Column(Boolean, default=True)

    # Notlar
    note = Column(Text)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer)  # Foreign key to User (gelecekte)

    # İlişkiler
    sales_orders = relationship("SalesOrder", back_populates="customer", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Customer {self.name} ({self.code})>"

    @property
    def full_address(self):
        """Tam adres string"""
        parts = [self.street, self.street2, self.city, self.state, self.zip_code, self.country]
        return ", ".join([p for p in parts if p])


class SalesOrder(Base):
    """Satış Siparişi - Teklif ve Sipariş"""
    __tablename__ = "sales_orders"

    id = Column(Integer, primary_key=True, index=True)

    # Sipariş Bilgileri
    name = Column(String(100), unique=True, index=True)  # SO001, SO002
    state = Column(SQLEnum(SalesOrderState), default=SalesOrderState.DRAFT, index=True)

    # Müşteri
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    customer = relationship("Customer", back_populates="sales_orders")

    # Tarihler
    order_date = Column(DateTime, default=datetime.utcnow)  # Sipariş Tarihi
    validity_date = Column(DateTime)  # Geçerlilik Tarihi (teklif için)
    expected_delivery = Column(DateTime)  # Tahmini Teslimat
    confirmation_date = Column(DateTime)  # Onay Tarihi

    # Adres Bilgileri
    delivery_address = Column(Text)
    invoice_address = Column(Text)

    # Ödeme
    payment_term = Column(SQLEnum(PaymentTerms), default=PaymentTerms.IMMEDIATE)

    # Tutarlar
    amount_untaxed = Column(Float, default=0.0)  # KDV Hariç
    amount_tax = Column(Float, default=0.0)      # KDV
    amount_total = Column(Float, default=0.0)    # Toplam
    amount_discount = Column(Float, default=0.0) # İndirim

    # Diğer
    note = Column(Text)  # Sipariş Notu
    internal_note = Column(Text)  # İç Not
    reference = Column(String(100))  # Müşteri Referansı

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer)  # Foreign key to User
    confirmed_by = Column(Integer)  # Onaylayan kullanıcı

    # İlişkiler
    lines = relationship("SalesOrderLine", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<SalesOrder {self.name} - {self.state}>"

    def calculate_totals(self):
        """Toplam tutarları hesapla"""
        self.amount_untaxed = sum(line.price_subtotal for line in self.lines)
        self.amount_tax = sum(line.price_tax for line in self.lines)
        discount = self.amount_discount or 0.0  # None ise 0 kullan
        self.amount_total = self.amount_untaxed + self.amount_tax - discount

    def confirm_order(self):
        """Siparişi onayla"""
        if self.state in [SalesOrderState.DRAFT, SalesOrderState.QUOTATION]:
            self.state = SalesOrderState.CONFIRMED
            self.confirmation_date = datetime.utcnow()


class SalesOrderLine(Base):
    """Satış Sipariş Satırı"""
    __tablename__ = "sales_order_lines"

    id = Column(Integer, primary_key=True, index=True)

    # Sipariş İlişkisi
    order_id = Column(Integer, ForeignKey("sales_orders.id"), nullable=False, index=True)
    order = relationship("SalesOrder", back_populates="lines")

    # Ürün Bilgileri
    product_name = Column(String(200), nullable=False)
    product_code = Column(String(50))
    description = Column(Text)

    # Miktar ve Fiyat
    quantity = Column(Float, nullable=False, default=1.0)
    unit_price = Column(Float, nullable=False, default=0.0)
    discount = Column(Float, default=0.0)  # İndirim yüzdesi
    tax_rate = Column(Float, default=20.0)  # KDV oranı

    # Hesaplanan Tutarlar
    price_subtotal = Column(Float, default=0.0)  # İndirim sonrası, KDV öncesi
    price_tax = Column(Float, default=0.0)       # KDV tutarı
    price_total = Column(Float, default=0.0)     # KDV dahil toplam

    # Metadata
    sequence = Column(Integer, default=10)  # Sıralama
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<SalesOrderLine {self.product_name} x{self.quantity}>"

    def calculate_prices(self):
        """Fiyatları hesapla"""
        # Brüt tutar
        gross = self.quantity * self.unit_price

        # İndirim uygula
        discount_amount = gross * (self.discount / 100)
        self.price_subtotal = gross - discount_amount

        # KDV hesapla
        self.price_tax = self.price_subtotal * (self.tax_rate / 100)

        # Toplam
        self.price_total = self.price_subtotal + self.price_tax
