"""
POS Module - Database Models

Models for Point of Sale operations.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base


class POSSession(Base):
    """POS Session - Kasa açma/kapama seansları"""
    __tablename__ = "pos_sessions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # Otomatik: "POS/2024/11/0001"
    user_id = Column(Integer, nullable=False)  # Kullanıcı ID (authentication sistemi eklenince ForeignKey olacak)
    user_name = Column(String(100), nullable=False)

    # Session durumu
    state = Column(String(20), default="opening_control")  # opening_control, opened, closing_control, closed

    # Tarih bilgileri
    start_at = Column(DateTime, default=datetime.utcnow)
    stop_at = Column(DateTime, nullable=True)

    # Kasa bilgileri
    opening_cash = Column(Float, default=0.0)  # Açılış kasası
    closing_cash = Column(Float, nullable=True)  # Kapanış kasası
    cash_register_difference = Column(Float, default=0.0)  # Fark

    # Satış özeti
    total_sales = Column(Float, default=0.0)
    total_payments = Column(Float, default=0.0)
    order_count = Column(Integer, default=0)

    # İlişkiler
    orders = relationship("POSOrder", back_populates="session", cascade="all, delete-orphan")

    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class POSOrder(Base):
    """POS Order - Satış siparişleri"""
    __tablename__ = "pos_orders"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)  # ORD/2024/11/0001

    # Session bağlantısı
    session_id = Column(Integer, ForeignKey("pos_sessions.id"), nullable=False)
    session = relationship("POSSession", back_populates="orders")

    # Müşteri bilgileri (opsiyonel)
    customer_id = Column(Integer, nullable=True)  # İleride customer modülü eklenecek
    customer_name = Column(String(200), nullable=True)
    customer_phone = Column(String(20), nullable=True)
    customer_tax_id = Column(String(20), nullable=True)  # VKN/TCKN

    # Sipariş durumu
    state = Column(String(20), default="draft")  # draft, paid, done, invoiced, cancelled

    # Tarih bilgileri
    date_order = Column(DateTime, default=datetime.utcnow)

    # Tutar bilgileri
    amount_tax = Column(Float, default=0.0)
    amount_total = Column(Float, default=0.0)
    amount_paid = Column(Float, default=0.0)
    amount_return = Column(Float, default=0.0)

    # Satır detayları
    lines = relationship("POSOrderLine", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("POSPayment", back_populates="order", cascade="all, delete-orphan")

    # Fiş/Fatura bilgileri
    receipt_number = Column(String(50), nullable=True)
    invoice_id = Column(Integer, nullable=True)  # E-fatura entegrasyonu için

    # Notlar
    note = Column(Text, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class POSOrderLine(Base):
    """POS Order Line - Sipariş satırları"""
    __tablename__ = "pos_order_lines"

    id = Column(Integer, primary_key=True, index=True)

    # Sipariş bağlantısı
    order_id = Column(Integer, ForeignKey("pos_orders.id"), nullable=False)
    order = relationship("POSOrder", back_populates="lines")

    # Ürün bilgileri
    product_id = Column(Integer, nullable=False)  # İleride product modülüne bağlanacak
    product_name = Column(String(200), nullable=False)
    product_barcode = Column(String(50), nullable=True)

    # Miktar ve fiyat
    qty = Column(Float, default=1.0)
    price_unit = Column(Float, nullable=False)
    discount = Column(Float, default=0.0)  # İndirim yüzdesi

    # KDV bilgileri
    tax_rate = Column(Float, default=20.0)  # KDV oranı (%)
    price_subtotal = Column(Float, nullable=False)  # KDV hariç
    price_subtotal_incl = Column(Float, nullable=False)  # KDV dahil

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)


class POSPayment(Base):
    """POS Payment - Ödeme kayıtları"""
    __tablename__ = "pos_payments"

    id = Column(Integer, primary_key=True, index=True)

    # Sipariş bağlantısı
    order_id = Column(Integer, ForeignKey("pos_orders.id"), nullable=False)
    order = relationship("POSOrder", back_populates="payments")

    # Ödeme bilgileri
    payment_method = Column(String(50), nullable=False)  # cash, card, bank_transfer, check
    payment_method_name = Column(String(100), nullable=False)  # "Nakit", "Kredi Kartı" vb.
    amount = Column(Float, nullable=False)

    # Kart bilgileri (opsiyonel)
    card_type = Column(String(20), nullable=True)  # visa, mastercard, amex
    card_number_masked = Column(String(20), nullable=True)  # **** **** **** 1234

    # Metadata
    payment_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)


class POSCategory(Base):
    """POS Category - Hızlı erişim için ürün kategorileri"""
    __tablename__ = "pos_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    parent_id = Column(Integer, ForeignKey("pos_categories.id"), nullable=True)

    # Görsel
    color = Column(String(7), default="#6366f1")  # Hex color
    icon = Column(String(50), nullable=True)  # Icon name
    image_url = Column(String(500), nullable=True)

    # Sıralama
    sequence = Column(Integer, default=10)

    # Durum
    active = Column(Boolean, default=True)

    # İlişkiler
    children = relationship("POSCategory", backref="parent", remote_side=[id])

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class POSProduct(Base):
    """POS Product - POS için optimize edilmiş ürün bilgileri"""
    __tablename__ = "pos_products"

    id = Column(Integer, primary_key=True, index=True)

    # Temel bilgiler
    name = Column(String(200), nullable=False)
    internal_reference = Column(String(100), nullable=True)  # Ürün kodu
    barcode = Column(String(100), unique=True, nullable=True, index=True)

    # Kategori
    category_id = Column(Integer, ForeignKey("pos_categories.id"), nullable=True)
    category = relationship("POSCategory")

    # Fiyat bilgileri
    list_price = Column(Float, nullable=False)  # Satış fiyatı
    cost_price = Column(Float, default=0.0)  # Maliyet fiyatı

    # KDV
    tax_rate = Column(Float, default=20.0)

    # Stok bilgileri
    qty_available = Column(Float, default=0.0)
    track_inventory = Column(Boolean, default=True)

    # Görsel
    image_url = Column(String(500), nullable=True)
    color = Column(String(7), default="#3b82f6")

    # POS özellikleri
    available_in_pos = Column(Boolean, default=True)
    to_weight = Column(Boolean, default=False)  # Tartılı ürün mü?

    # Hızlı butonlar
    is_favorite = Column(Boolean, default=False)
    sequence = Column(Integer, default=10)

    # Durum
    active = Column(Boolean, default=True)

    # Metadata
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class POSConfig(Base):
    """POS Configuration - POS ayarları"""
    __tablename__ = "pos_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

    # Temel ayarlar
    company_name = Column(String(200), nullable=False)
    company_vat = Column(String(20), nullable=True)
    company_address = Column(Text, nullable=True)
    company_phone = Column(String(20), nullable=True)

    # POS ayarları
    receipt_header = Column(Text, nullable=True)
    receipt_footer = Column(Text, nullable=True)
    auto_print_receipt = Column(Boolean, default=True)

    # Ödeme yöntemleri
    payment_methods = Column(JSON, default=list)  # [{"id": 1, "name": "Nakit", "type": "cash"}, ...]

    # Özellikler
    allow_discount = Column(Boolean, default=True)
    max_discount = Column(Float, default=50.0)
    require_customer = Column(Boolean, default=False)
    allow_invoice = Column(Boolean, default=True)

    # Fiş numaralandırma
    receipt_prefix = Column(String(20), default="FIS")
    receipt_sequence = Column(Integer, default=1)

    # Durum
    active = Column(Boolean, default=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
