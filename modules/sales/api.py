"""
MinimalERP - Sales API
Customer and Sales Order Management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import List, Optional
from datetime import datetime

from core.database import get_db
from modules.sales.models import Customer, SalesOrder, SalesOrderLine, SalesOrderState
from modules.sales import schemas

router = APIRouter()


# ==================== CUSTOMERS ====================

@router.post("/customers", response_model=schemas.Customer, status_code=201)
async def create_customer(
    customer: schemas.CustomerCreate,
    db: AsyncSession = Depends(get_db)
):
    """Yeni müşteri oluştur"""
    # Müşteri kodu oluştur
    result = await db.execute(
        select(func.count(Customer.id))
    )
    count = result.scalar() or 0
    customer_code = f"C{str(count + 1).zfill(6)}"

    db_customer = Customer(
        **customer.model_dump(),
        code=customer_code
    )

    db.add(db_customer)
    await db.commit()
    await db.refresh(db_customer)

    return db_customer


@router.get("/customers", response_model=List[schemas.Customer])
async def list_customers(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """Müşteri listesi"""
    query = select(Customer)

    # Arama
    if search:
        query = query.where(
            or_(
                Customer.name.ilike(f"%{search}%"),
                Customer.code.ilike(f"%{search}%"),
                Customer.email.ilike(f"%{search}%"),
                Customer.tax_number.ilike(f"%{search}%")
            )
        )

    # Aktiflik filtresi
    if is_active is not None:
        query = query.where(Customer.is_active == is_active)

    query = query.offset(skip).limit(limit).order_by(Customer.name)

    result = await db.execute(query)
    customers = result.scalars().all()

    return customers


@router.get("/customers/{customer_id}", response_model=schemas.Customer)
async def get_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Müşteri detayı"""
    result = await db.execute(
        select(Customer).where(Customer.id == customer_id)
    )
    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(status_code=404, detail="Müşteri bulunamadı")

    return customer


@router.put("/customers/{customer_id}", response_model=schemas.Customer)
async def update_customer(
    customer_id: int,
    customer_update: schemas.CustomerUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Müşteri güncelle"""
    result = await db.execute(
        select(Customer).where(Customer.id == customer_id)
    )
    db_customer = result.scalar_one_or_none()

    if not db_customer:
        raise HTTPException(status_code=404, detail="Müşteri bulunamadı")

    # Güncelleme
    update_data = customer_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_customer, field, value)

    await db.commit()
    await db.refresh(db_customer)

    return db_customer


@router.delete("/customers/{customer_id}", status_code=204)
async def delete_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Müşteri sil"""
    result = await db.execute(
        select(Customer).where(Customer.id == customer_id)
    )
    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(status_code=404, detail="Müşteri bulunamadı")

    await db.delete(customer)
    await db.commit()

    return None


# ==================== SALES ORDERS ====================

def generate_order_name(count: int) -> str:
    """Sipariş numarası oluştur: SO001, SO002..."""
    return f"SO{str(count + 1).zfill(5)}"


@router.post("/orders", response_model=schemas.SalesOrder, status_code=201)
async def create_sales_order(
    order: schemas.SalesOrderCreate,
    db: AsyncSession = Depends(get_db)
):
    """Yeni satış siparişi oluştur"""
    # Müşteri kontrolü
    result = await db.execute(
        select(Customer).where(Customer.id == order.customer_id)
    )
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Müşteri bulunamadı")

    # Sipariş numarası oluştur
    result = await db.execute(select(func.count(SalesOrder.id)))
    count = result.scalar() or 0
    order_name = generate_order_name(count)

    # Sipariş oluştur
    order_data = order.model_dump(exclude={'lines'})
    db_order = SalesOrder(**order_data, name=order_name)

    # Satırları ekle
    for idx, line_data in enumerate(order.lines, start=1):
        line = SalesOrderLine(**line_data.model_dump(), sequence=idx * 10)
        line.calculate_prices()
        db_order.lines.append(line)

    # Toplamları hesapla
    db_order.calculate_totals()

    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)

    return db_order


@router.get("/orders", response_model=List[schemas.SalesOrderSummary])
async def list_sales_orders(
    skip: int = 0,
    limit: int = 100,
    state: Optional[SalesOrderState] = None,
    customer_id: Optional[int] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Satış siparişi listesi"""
    query = select(
        SalesOrder.id,
        SalesOrder.name,
        SalesOrder.state,
        SalesOrder.customer_id,
        Customer.name.label("customer_name"),
        SalesOrder.order_date,
        SalesOrder.amount_total,
        SalesOrder.created_at
    ).join(Customer)

    # Filtreler
    if state:
        query = query.where(SalesOrder.state == state)

    if customer_id:
        query = query.where(SalesOrder.customer_id == customer_id)

    if search:
        query = query.where(
            or_(
                SalesOrder.name.ilike(f"%{search}%"),
                Customer.name.ilike(f"%{search}%"),
                SalesOrder.reference.ilike(f"%{search}%")
            )
        )

    query = query.offset(skip).limit(limit).order_by(SalesOrder.created_at.desc())

    result = await db.execute(query)
    orders = result.all()

    return [
        schemas.SalesOrderSummary(
            id=row.id,
            name=row.name,
            state=row.state,
            customer_id=row.customer_id,
            customer_name=row.customer_name,
            order_date=row.order_date,
            amount_total=row.amount_total,
            created_at=row.created_at
        )
        for row in orders
    ]


@router.get("/orders/{order_id}", response_model=schemas.SalesOrder)
async def get_sales_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Sipariş detayı"""
    result = await db.execute(
        select(SalesOrder).where(SalesOrder.id == order_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Sipariş bulunamadı")

    return order


@router.put("/orders/{order_id}", response_model=schemas.SalesOrder)
async def update_sales_order(
    order_id: int,
    order_update: schemas.SalesOrderUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Sipariş güncelle"""
    result = await db.execute(
        select(SalesOrder).where(SalesOrder.id == order_id)
    )
    db_order = result.scalar_one_or_none()

    if not db_order:
        raise HTTPException(status_code=404, detail="Sipariş bulunamadı")

    # Sadece draft veya quotation durumunda güncellenebilir
    if db_order.state not in [SalesOrderState.DRAFT, SalesOrderState.QUOTATION]:
        raise HTTPException(
            status_code=400,
            detail="Sadece taslak veya teklif durumundaki siparişler güncellenebilir"
        )

    # Güncelleme
    update_data = order_update.model_dump(exclude_unset=True, exclude={'lines'})
    for field, value in update_data.items():
        setattr(db_order, field, value)

    # Satırlar güncellenirse
    if order_update.lines is not None:
        # Eski satırları sil
        db_order.lines = []

        # Yeni satırları ekle
        for idx, line_data in enumerate(order_update.lines, start=1):
            line = SalesOrderLine(**line_data.model_dump(), sequence=idx * 10)
            line.calculate_prices()
            db_order.lines.append(line)

        # Toplamları yeniden hesapla
        db_order.calculate_totals()

    await db.commit()
    await db.refresh(db_order)

    return db_order


@router.post("/orders/{order_id}/confirm", response_model=schemas.SalesOrder)
async def confirm_sales_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Siparişi onayla"""
    result = await db.execute(
        select(SalesOrder).where(SalesOrder.id == order_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Sipariş bulunamadı")

    if order.state not in [SalesOrderState.DRAFT, SalesOrderState.QUOTATION]:
        raise HTTPException(
            status_code=400,
            detail="Sadece taslak veya teklif durumundaki siparişler onaylanabilir"
        )

    order.confirm_order()

    await db.commit()
    await db.refresh(order)

    return order


@router.post("/orders/{order_id}/cancel", response_model=schemas.SalesOrder)
async def cancel_sales_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Siparişi iptal et"""
    result = await db.execute(
        select(SalesOrder).where(SalesOrder.id == order_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Sipariş bulunamadı")

    if order.state == SalesOrderState.DELIVERED:
        raise HTTPException(
            status_code=400,
            detail="Teslim edilmiş siparişler iptal edilemez"
        )

    order.state = SalesOrderState.CANCELLED

    await db.commit()
    await db.refresh(order)

    return order


@router.delete("/orders/{order_id}", status_code=204)
async def delete_sales_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Sipariş sil (sadece draft)"""
    result = await db.execute(
        select(SalesOrder).where(SalesOrder.id == order_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Sipariş bulunamadı")

    if order.state != SalesOrderState.DRAFT:
        raise HTTPException(
            status_code=400,
            detail="Sadece taslak siparişler silinebilir"
        )

    await db.delete(order)
    await db.commit()

    return None


# ==================== STATISTICS ====================

@router.get("/stats/dashboard")
async def sales_dashboard(
    db: AsyncSession = Depends(get_db)
):
    """Satış dashboard istatistikleri"""
    # Toplam müşteri sayısı
    result = await db.execute(
        select(func.count(Customer.id)).where(Customer.is_active == True)
    )
    total_customers = result.scalar() or 0

    # Sipariş istatistikleri
    result = await db.execute(
        select(
            SalesOrder.state,
            func.count(SalesOrder.id).label("count"),
            func.sum(SalesOrder.amount_total).label("total")
        ).group_by(SalesOrder.state)
    )
    order_stats = result.all()

    stats_dict = {}
    for stat in order_stats:
        stats_dict[stat.state.value] = {
            "count": stat.count,
            "total": float(stat.total or 0)
        }

    return {
        "total_customers": total_customers,
        "orders_by_state": stats_dict,
        "generated_at": datetime.utcnow()
    }
