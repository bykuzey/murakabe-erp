"""
MinimalERP - Accounting Service Layer

Business logic for accounting module.
"""

from __future__ import annotations

from typing import List, Optional
from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from core.database import get_istanbul_time
from modules.accounting.models import (
    Invoice,
    InvoiceLine,
    Partner,
    Company,
    Transaction,
    Account,
    CashFlowForecast,
    AnomalyDetection,
    AccountType,
    TransactionType,
    DocumentStatus,
)
from modules.accounting import schemas


async def ensure_default_company(db: AsyncSession) -> Company:
  """Create a minimal default company if none exists."""
  result = await db.execute(select(Company).limit(1))
  company = result.scalar_one_or_none()
  if company:
      return company

  company = Company(
      name="Örnek Şirket A.Ş.",
      trade_name="Örnek Şirket",
      tax_office="MERKEZ",
      tax_number="1111111111",
      email="info@example.com",
      phone="+90 212 000 00 00",
      address="İstanbul",
      city="İstanbul",
  )
  db.add(company)
  await db.flush()
  await db.refresh(company)
  return company


async def create_invoice(
    db: AsyncSession,
    invoice_data: schemas.InvoiceCreate,
) -> Invoice:
    """Create invoice and its lines, calculate totals."""
    result = await db.execute(
        select(Company).where(Company.id == invoice_data.company_id)
    )
    company = result.scalar_one_or_none()
    if not company:
        if invoice_data.company_id == 1:
            company = await ensure_default_company(db)
            invoice_data.company_id = company.id
        else:
            raise ValueError("Şirket bulunamadı")

    result = await db.execute(
        select(Partner).where(Partner.id == invoice_data.partner_id)
    )
    partner = result.scalar_one_or_none()
    if not partner:
        raise ValueError("Cari hesap (partner) bulunamadı")

    subtotal = 0.0
    total_vat = 0.0
    total_withholding = 0.0

    invoice = Invoice(
        invoice_number=invoice_data.invoice_number,
        invoice_date=invoice_data.invoice_date,
        invoice_type=invoice_data.invoice_type,
        company_id=invoice_data.company_id,
        partner_id=invoice_data.partner_id,
        subtotal=0.0,
        vat_amount=0.0,
        total_amount=0.0,
        currency="TRY",
        status=DocumentStatus.DRAFT,
    )

    for line_data in invoice_data.lines:
        line_subtotal = line_data.quantity * line_data.unit_price
        line_vat = line_subtotal * (line_data.vat_rate / 100.0)
        line_withholding = line_subtotal * (line_data.withholding_rate / 100.0)
        line_total = line_subtotal + line_vat - line_withholding

        line = InvoiceLine(
            description=line_data.description,
            quantity=line_data.quantity,
            unit_price=line_data.unit_price,
            vat_rate=line_data.vat_rate,
            vat_amount=line_vat,
            withholding_rate=line_data.withholding_rate,
            withholding_amount=line_withholding,
            line_total=line_total,
        )

        invoice.lines.append(line)

        subtotal += line_subtotal
        total_vat += line_vat
        total_withholding += line_withholding

    if not invoice_data.lines:
        subtotal = invoice_data.subtotal
        total_vat = invoice_data.vat_amount
        total_withholding = 0.0

    total_amount = subtotal + total_vat - total_withholding

    invoice.subtotal = subtotal
    invoice.vat_amount = total_vat
    invoice.total_amount = total_amount

    db.add(invoice)
    await db.flush()
    await db.refresh(invoice)

    return invoice


async def list_invoices(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    partner_id: Optional[int] = None,
) -> List[Invoice]:
    """List invoices with optional filters."""
    query = select(Invoice)

    if start_date:
        query = query.where(Invoice.invoice_date >= start_date)
    if end_date:
        query = query.where(Invoice.invoice_date <= end_date)
    if partner_id:
        query = query.where(Invoice.partner_id == partner_id)

    query = query.order_by(Invoice.invoice_date.desc(), Invoice.id.desc())
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


async def get_invoice(
    db: AsyncSession,
    invoice_id: int,
) -> Optional[Invoice]:
    """Get single invoice by id."""
    result = await db.execute(
        select(Invoice).where(Invoice.id == invoice_id)
    )
    return result.scalar_one_or_none()


async def create_partner(
    db: AsyncSession,
    partner_data: schemas.PartnerCreate,
) -> Partner:
    """Create partner (cari hesap)."""
    partner = Partner(
        name=partner_data.name,
        tax_office=partner_data.tax_office,
        tax_number=partner_data.tax_number,
        is_customer=partner_data.is_customer,
        is_supplier=partner_data.is_supplier,
        email=partner_data.email,
        phone=partner_data.phone,
    )

    db.add(partner)
    await db.flush()
    await db.refresh(partner)
    return partner


async def list_partners(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    is_customer: Optional[bool] = None,
    is_supplier: Optional[bool] = None,
) -> List[Partner]:
    """List partners with filters."""
    query = select(Partner).where(Partner.is_deleted == False)  # noqa: E712

    if is_customer is not None:
        query = query.where(Partner.is_customer == is_customer)
    if is_supplier is not None:
        query = query.where(Partner.is_supplier == is_supplier)

    query = query.order_by(Partner.name).offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()

async def calculate_cashflow_forecast(
    db: AsyncSession,
    days_ahead: int,
) -> CashFlowForecast:
    """Simple average-based cashflow forecast."""
    end_date = date.today()
    start_date = end_date - timedelta(days=90)

    result = await db.execute(
        select(
            func.sum(Transaction.debit).label("total_debit"),
            func.sum(Transaction.credit).label("total_credit"),
        ).where(
            and_(
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date,
            )
        )
    )
    row = result.one_or_none()
    total_debit = float(row.total_debit or 0.0)
    total_credit = float(row.total_credit or 0.0)

    days = max((end_date - start_date).days, 1)
    avg_inflow = total_debit / days
    avg_outflow = total_credit / days
    avg_balance_change = avg_inflow - avg_outflow

    forecast_date = end_date + timedelta(days=days_ahead)
    predicted_inflow = avg_inflow * days_ahead
    predicted_outflow = avg_outflow * days_ahead
    predicted_balance = avg_balance_change * days_ahead

    forecast = CashFlowForecast(
        forecast_date=forecast_date,
        predicted_inflow=predicted_inflow,
        predicted_outflow=predicted_outflow,
        predicted_balance=predicted_balance,
        confidence_score=None,
    )
    db.add(forecast)
    await db.flush()
    await db.refresh(forecast)
    return forecast


async def detect_transaction_anomalies(
    db: AsyncSession,
) -> int:
    """Rule-based anomaly detection over transactions."""
    result = await db.execute(select(Transaction))
    transactions = result.scalars().all()

    created = 0
    for tx in transactions:
        amount = abs((tx.debit or 0.0) - (tx.credit or 0.0))
        is_suspicious = amount > 1_000_000 or amount < 0
        if not is_suspicious:
            continue

        anomaly = AnomalyDetection(
            detection_date=get_istanbul_time(),
            anomaly_type="SUSPICIOUS_AMOUNT",
            severity="HIGH" if amount > 5_000_000 else "MEDIUM",
            anomaly_score=min(amount / 1_000_000, 10.0),
            entity_type="TRANSACTION",
            entity_id=tx.id,
            description=f"Şüpheli tutar: {amount}",
            ai_analysis=None,
        )
        db.add(anomaly)
        created += 1

    return created


async def resolve_anomaly(
    db: AsyncSession,
    anomaly_id: int,
    resolution: schemas.AnomalyResolution,
) -> AnomalyDetection:
    """Mark anomaly as resolved."""
    result = await db.execute(
        select(AnomalyDetection).where(AnomalyDetection.id == anomaly_id)
    )
    anomaly = result.scalar_one_or_none()
    if not anomaly:
        raise ValueError("Anomali kaydı bulunamadı")

    anomaly.is_resolved = True
    anomaly.resolution_notes = resolution.resolution_notes
    anomaly.resolved_at = get_istanbul_time()

    await db.flush()
    await db.refresh(anomaly)
    return anomaly


async def get_balance_sheet_data(
    db: AsyncSession,
    report_date: Optional[date] = None,
):
    """Return balance sheet structure grouped by account type."""
    if report_date is None:
        report_date = date.today()

    result = await db.execute(
        select(
            Account.id,
            Account.code,
            Account.name,
            Account.account_type,
            func.sum(Transaction.debit - Transaction.credit).label("balance"),
        )
        .join(Transaction, Transaction.account_id == Account.id, isouter=True)
        .where(
            or_(
                Transaction.transaction_date <= report_date,
                Transaction.id.is_(None),
            )
        )
        .group_by(Account.id, Account.code, Account.name, Account.account_type)
    )
    rows = result.all()

    assets = []
    liabilities = []
    equity = []

    for row in rows:
        account_info = {
            "code": row.code,
            "name": row.name,
            "balance": float(row.balance or 0.0),
        }
        if row.account_type == AccountType.ASSET:
            assets.append(account_info)
        elif row.account_type == AccountType.LIABILITY:
            liabilities.append(account_info)
        elif row.account_type == AccountType.EQUITY:
            equity.append(account_info)

    return {
        "report_date": report_date,
        "assets": {
            "total": sum(a["balance"] for a in assets),
            "accounts": assets,
        },
        "liabilities": {
            "total": sum(l["balance"] for l in liabilities),
            "accounts": liabilities,
        },
        "equity": {
            "total": sum(e["balance"] for e in equity),
            "accounts": equity,
        },
    }


async def get_income_statement_data(
    db: AsyncSession,
    start_date: date,
    end_date: date,
):
    """Return income statement summary."""
    result = await db.execute(
        select(
            Account.account_type,
            func.sum(Transaction.debit - Transaction.credit).label("balance"),
        )
        .join(Transaction, Transaction.account_id == Account.id)
        .where(
            and_(
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date,
                Account.account_type.in_([AccountType.REVENUE, AccountType.EXPENSE]),
            )
        )
        .group_by(Account.account_type)
    )
    rows = result.all()

    total_revenue = 0.0
    total_expense = 0.0
    for row in rows:
        if row.account_type == AccountType.REVENUE:
            total_revenue += float(row.balance or 0.0)
        elif row.account_type == AccountType.EXPENSE:
            total_expense += float(row.balance or 0.0)

    net_profit = total_revenue - total_expense

    return {
        "start_date": start_date,
        "end_date": end_date,
        "total_revenue": total_revenue,
        "total_expense": total_expense,
        "net_profit": net_profit,
    }


async def get_vat_declaration_data(
    db: AsyncSession,
    year: int,
    month: int,
):
    """Return monthly VAT declaration draft."""
    period_start = date(year, month, 1)
    if month == 12:
        period_end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        period_end = date(year, month + 1, 1) - timedelta(days=1)

    result = await db.execute(
        select(func.sum(InvoiceLine.vat_amount).label("vat_sales"))
        .join(Invoice, InvoiceLine.invoice_id == Invoice.id)
        .where(
            and_(
                Invoice.invoice_date >= period_start,
                Invoice.invoice_date <= period_end,
                Invoice.invoice_type == "SATIS",
            )
        )
    )
    vat_sales = float(result.scalar() or 0.0)

    result = await db.execute(
        select(func.sum(InvoiceLine.vat_amount).label("vat_purchases"))
        .join(Invoice, InvoiceLine.invoice_id == Invoice.id)
        .where(
            and_(
                Invoice.invoice_date >= period_start,
                Invoice.invoice_date <= period_end,
                Invoice.invoice_type == "ALIS",
            )
        )
    )
    vat_purchases = float(result.scalar() or 0.0)

    vat_payable = vat_sales - vat_purchases

    return {
        "year": year,
        "month": month,
        "period_start": period_start,
        "period_end": period_end,
        "vat_sales": vat_sales,
        "vat_purchases": vat_purchases,
        "vat_payable": vat_payable,
    }
