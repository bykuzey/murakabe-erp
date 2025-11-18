"""
MinimalERP - Accounting Models

Database models for accounting module.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    DateTime,
    ForeignKey,
    Text,
    Enum,
    JSON,
    Boolean,
)
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from core.database import BaseModel


class AccountType(str, PyEnum):
    """Account types based on Turkish Uniform Chart of Accounts"""
    ASSET = "VARLIK"  # Varlık (100-299)
    LIABILITY = "BORC"  # Borç (300-499)
    EQUITY = "OZKAYNAKLAR"  # Özkaynaklar (500-599)
    REVENUE = "GELIR"  # Gelir (600-799)
    EXPENSE = "GIDER"  # Gider (700-899)


class TransactionType(str, PyEnum):
    """Transaction types"""
    INVOICE = "FATURA"
    RECEIPT = "MAKBUZ"
    EXPENSE = "GIDER"
    PAYMENT = "ODEME"
    BANK_TRANSFER = "HAVALE"
    CASH = "NAKIT"


class DocumentStatus(str, PyEnum):
    """Document status for e-Invoice integration"""
    DRAFT = "TASLAK"
    PENDING = "BEKLEMEDE"
    SENT = "GONDERILDI"
    APPROVED = "ONAYLANDI"
    REJECTED = "REDDEDILDI"
    CANCELLED = "IPTAL"


class Account(BaseModel):
    """Chart of Accounts (Hesap Planı)"""
    __tablename__ = "accounts"

    code = Column(String(20), unique=True, nullable=False, index=True)  # Hesap kodu (örn: 100.01.001)
    name = Column(String(200), nullable=False)  # Hesap adı
    account_type = Column(Enum(AccountType), nullable=False)
    parent_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    currency = Column(String(3), default="TRY")
    balance = Column(Float, default=0.0)

    # Turkish-specific
    is_vat_account = Column(Boolean, default=False)  # KDV hesabı mı?
    vat_rate = Column(Float, nullable=True)  # KDV oranı

    # Relationships
    parent = relationship("Account", remote_side="Account.id", backref="children")
    transactions = relationship("Transaction", back_populates="account")


class Company(BaseModel):
    """Company information"""
    __tablename__ = "companies"

    # Basic Info
    name = Column(String(200), nullable=False)
    trade_name = Column(String(200), nullable=True)
    tax_office = Column(String(100), nullable=False)  # Vergi dairesi
    tax_number = Column(String(20), unique=True, nullable=False)  # Vergi numarası

    # Contact
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    website = Column(String(100), nullable=True)

    # Address
    address = Column(Text, nullable=True)
    city = Column(String(50), nullable=True)
    district = Column(String(50), nullable=True)
    postal_code = Column(String(10), nullable=True)

    # GİB Integration
    gib_username = Column(String(100), nullable=True)
    gib_alias = Column(String(50), nullable=True)  # e-Fatura alias
    gib_registered = Column(Boolean, default=False)

    # Relationships
    invoices = relationship("Invoice", back_populates="company")


class Partner(BaseModel):
    """Business partners (customers and suppliers)"""
    __tablename__ = "partners"

    # Basic Info
    name = Column(String(200), nullable=False)
    tax_office = Column(String(100), nullable=True)
    tax_number = Column(String(20), nullable=True)

    # Type
    is_customer = Column(Boolean, default=True)
    is_supplier = Column(Boolean, default=False)

    # Contact
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    mobile = Column(String(20), nullable=True)

    # Address
    address = Column(Text, nullable=True)
    city = Column(String(50), nullable=True)
    district = Column(String(50), nullable=True)
    postal_code = Column(String(10), nullable=True)

    # Financial
    credit_limit = Column(Float, default=0.0)
    current_balance = Column(Float, default=0.0)

    # GİB
    gib_alias = Column(String(50), nullable=True)

    # AI Scoring
    credit_score = Column(Float, nullable=True)  # AI-calculated credit score
    payment_behavior_score = Column(Float, nullable=True)  # Ödeme davranışı skoru

    # Relationships
    invoices = relationship("Invoice", back_populates="partner")


class Invoice(BaseModel):
    """Invoices (Faturalar)"""
    __tablename__ = "invoices"

    # Basic Info
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    invoice_date = Column(Date, nullable=False, index=True)
    invoice_type = Column(String(20), nullable=False)  # SATIS, ALIS, IADE

    # Parties
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    partner_id = Column(Integer, ForeignKey("partners.id"), nullable=False)

    # Amounts
    subtotal = Column(Float, nullable=False)
    vat_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    currency = Column(String(3), default="TRY")

    # Payment
    payment_term = Column(String(50), nullable=True)
    due_date = Column(Date, nullable=True)
    paid_amount = Column(Float, default=0.0)

    # Status
    status = Column(Enum(DocumentStatus), default=DocumentStatus.DRAFT)

    # e-Invoice
    is_einvoice = Column(Boolean, default=False)
    einvoice_uuid = Column(String(100), nullable=True, unique=True)
    einvoice_sent_date = Column(DateTime, nullable=True)
    gib_envelope_id = Column(String(100), nullable=True)

    # AI Analysis
    ai_extracted = Column(Boolean, default=False)  # OCR ile mi oluşturuldu?
    anomaly_score = Column(Float, nullable=True)  # Anomali skoru (0-1)
    is_anomaly = Column(Boolean, default=False)
    ai_metadata = Column(JSON, nullable=True)  # AI ile ilgili ek bilgiler

    # Relationships
    company = relationship("Company", back_populates="invoices")
    partner = relationship("Partner", back_populates="invoices")
    lines = relationship("InvoiceLine", back_populates="invoice", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="invoice")


class InvoiceLine(BaseModel):
    """Invoice line items"""
    __tablename__ = "invoice_lines"

    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)

    # Product/Service
    description = Column(String(500), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)

    # Tax
    vat_rate = Column(Float, default=0.0)
    vat_amount = Column(Float, default=0.0)

    # Withholding (Tevkifat)
    withholding_rate = Column(Float, default=0.0)
    withholding_amount = Column(Float, default=0.0)

    # Total
    line_total = Column(Float, nullable=False)

    # Relationship
    invoice = relationship("Invoice", back_populates="lines")


class Transaction(BaseModel):
    """Financial transactions (Muhasebe Fişleri)"""
    __tablename__ = "transactions"

    # Basic Info
    transaction_date = Column(Date, nullable=False, index=True)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    description = Column(String(500), nullable=False)

    # Accounting
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    debit = Column(Float, default=0.0)
    credit = Column(Float, default=0.0)
    currency = Column(String(3), default="TRY")

    # Reference
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)
    reference_number = Column(String(100), nullable=True)

    # Bank/Cash
    bank_account = Column(String(50), nullable=True)

    # Relationships
    account = relationship("Account", back_populates="transactions")
    invoice = relationship("Invoice", back_populates="transactions")


class CashFlowForecast(BaseModel):
    """AI-generated cash flow forecasts"""
    __tablename__ = "cashflow_forecasts"

    forecast_date = Column(Date, nullable=False, index=True)
    predicted_inflow = Column(Float, nullable=False)
    predicted_outflow = Column(Float, nullable=False)
    predicted_balance = Column(Float, nullable=False)

    # Confidence
    confidence_score = Column(Float, nullable=True)  # 0-1

    # Actual (for comparison)
    actual_inflow = Column(Float, nullable=True)
    actual_outflow = Column(Float, nullable=True)
    actual_balance = Column(Float, nullable=True)

    # Model info
    model_version = Column(String(20), nullable=True)
    created_by_model = Column(String(50), nullable=True)


class AnomalyDetection(BaseModel):
    """AI-detected anomalies"""
    __tablename__ = "anomaly_detections"

    # Detection info
    detection_date = Column(DateTime, nullable=False)
    anomaly_type = Column(String(50), nullable=False)  # SUSPICIOUS_AMOUNT, DUPLICATE, UNUSUAL_PATTERN
    severity = Column(String(20), nullable=False)  # LOW, MEDIUM, HIGH
    anomaly_score = Column(Float, nullable=False)

    # Related entity
    entity_type = Column(String(50), nullable=True)  # INVOICE, TRANSACTION
    entity_id = Column(Integer, nullable=True)

    # Description
    description = Column(Text, nullable=False)
    ai_analysis = Column(JSON, nullable=True)

    # Status
    is_resolved = Column(Boolean, default=False)
    resolution_notes = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(Integer, nullable=True)
