"""
POS Module - API Endpoints

RESTful API for Point of Sale operations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
from datetime import datetime

from core.database import get_db
from modules.pos import models, schemas

router = APIRouter(prefix="/api/pos", tags=["POS"])


# ============= HELPER FUNCTIONS =============

def calculate_line_totals(line: schemas.POSOrderLineCreate):
    """Satır tutarlarını hesapla"""
    subtotal = line.qty * line.price_unit
    if line.discount > 0:
        subtotal = subtotal * (1 - line.discount / 100)

    tax_amount = subtotal * (line.tax_rate / 100)
    subtotal_incl = subtotal + tax_amount

    return {
        "price_subtotal": round(subtotal, 2),
        "price_subtotal_incl": round(subtotal_incl, 2)
    }


async def generate_order_name(db: AsyncSession) -> str:
    """Sipariş numarası oluştur: ORD/2024/11/0001"""
    now = datetime.now()
    prefix = f"ORD/{now.year}/{now.month:02d}"

    # Bu ay için son sipariş numarasını bul
    result = await db.execute(
        select(func.count(models.POSOrder.id)).where(
            models.POSOrder.name.like(f"{prefix}%")
        )
    )
    count = result.scalar() or 0

    return f"{prefix}/{count + 1:04d}"


async def generate_session_name(db: AsyncSession) -> str:
    """Session numarası oluştur: POS/2024/11/0001"""
    now = datetime.now()
    prefix = f"POS/{now.year}/{now.month:02d}"

    result = await db.execute(
        select(func.count(models.POSSession.id)).where(
            models.POSSession.name.like(f"{prefix}%")
        )
    )
    count = result.scalar() or 0

    return f"{prefix}/{count + 1:04d}"


# ============= SESSION ENDPOINTS =============

@router.post("/sessions", response_model=schemas.POSSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: schemas.POSSessionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Yeni POS seansı aç"""

    # Kullanıcının açık seansı var mı kontrol et
    result = await db.execute(
        select(models.POSSession).where(
            and_(
                models.POSSession.user_id == session_data.user_id,
                models.POSSession.state.in_(["opening_control", "opened"])
            )
        )
    )
    existing_session = result.scalar_one_or_none()

    if existing_session:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu kullanıcının zaten açık bir POS seansı var"
        )

    # Yeni session oluştur
    session_name = await generate_session_name(db)

    db_session = models.POSSession(
        name=session_name,
        user_id=session_data.user_id,
        user_name=session_data.user_name,
        opening_cash=session_data.opening_cash,
        state="opened",
        notes=session_data.notes
    )

    db.add(db_session)
    await db.commit()
    await db.refresh(db_session)

    return db_session


@router.get("/sessions", response_model=List[schemas.POSSessionResponse])
async def list_sessions(
    skip: int = 0,
    limit: int = 50,
    state: Optional[str] = None,
    user_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """POS seanslarını listele"""
    query = select(models.POSSession).order_by(models.POSSession.start_at.desc())

    if state:
        query = query.where(models.POSSession.state == state)
    if user_id:
        query = query.where(models.POSSession.user_id == user_id)

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/sessions/{session_id}", response_model=schemas.POSSessionResponse)
async def get_session(
    session_id: int,
    db: AsyncSession = Depends(get_db)
):
    """POS seansı detayı"""
    result = await db.execute(
        select(models.POSSession).where(models.POSSession.id == session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Seans bulunamadı")

    return session


@router.put("/sessions/{session_id}/close", response_model=schemas.POSSessionResponse)
async def close_session(
    session_id: int,
    closing_data: schemas.POSSessionUpdate,
    db: AsyncSession = Depends(get_db)
):
    """POS seansını kapat"""
    result = await db.execute(
        select(models.POSSession).where(models.POSSession.id == session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Seans bulunamadı")

    if session.state == "closed":
        raise HTTPException(status_code=400, detail="Seans zaten kapalı")

    # Seansı kapat
    session.state = "closed"
    session.stop_at = datetime.utcnow()
    session.closing_cash = closing_data.closing_cash

    if closing_data.notes:
        session.notes = closing_data.notes

    # Kasa farkını hesapla
    expected_cash = session.opening_cash + session.total_sales
    if session.closing_cash:
        session.cash_register_difference = session.closing_cash - expected_cash

    await db.commit()
    await db.refresh(session)

    return session


# ============= PRODUCT ENDPOINTS =============

@router.post("/products", response_model=schemas.POSProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: schemas.POSProductCreate,
    db: AsyncSession = Depends(get_db)
):
    """Yeni ürün ekle"""

    # Barkod kontrolü
    if product.barcode:
        result = await db.execute(
            select(models.POSProduct).where(models.POSProduct.barcode == product.barcode)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bu barkod zaten kullanılıyor"
            )

    db_product = models.POSProduct(**product.model_dump())
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)

    return db_product


@router.get("/products", response_model=List[schemas.POSProductResponse])
async def list_products(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    available_in_pos: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """Ürünleri listele"""
    query = select(models.POSProduct).where(models.POSProduct.active == True)

    if available_in_pos:
        query = query.where(models.POSProduct.available_in_pos == True)

    if category_id:
        query = query.where(models.POSProduct.category_id == category_id)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                models.POSProduct.name.ilike(search_pattern),
                models.POSProduct.barcode.ilike(search_pattern),
                models.POSProduct.internal_reference.ilike(search_pattern)
            )
        )

    query = query.order_by(models.POSProduct.sequence, models.POSProduct.name)
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/products/barcode/{barcode}", response_model=schemas.POSProductResponse)
async def get_product_by_barcode(
    barcode: str,
    db: AsyncSession = Depends(get_db)
):
    """Barkod ile ürün ara"""
    result = await db.execute(
        select(models.POSProduct).where(
            and_(
                models.POSProduct.barcode == barcode,
                models.POSProduct.active == True,
                models.POSProduct.available_in_pos == True
            )
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")

    return product


@router.get("/products/{product_id}", response_model=schemas.POSProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Ürün detayı"""
    result = await db.execute(
        select(models.POSProduct).where(models.POSProduct.id == product_id)
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")

    return product


@router.put("/products/{product_id}", response_model=schemas.POSProductResponse)
async def update_product(
    product_id: int,
    product_update: schemas.POSProductUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Ürün güncelle"""
    result = await db.execute(
        select(models.POSProduct).where(models.POSProduct.id == product_id)
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")

    # Güncelleme
    update_data = product_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(product)

    return product


# ============= ORDER ENDPOINTS =============

@router.post("/orders", response_model=schemas.POSOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: schemas.POSOrderCreate,
    db: AsyncSession = Depends(get_db)
):
    """Yeni sipariş oluştur"""

    # Session kontrolü
    result = await db.execute(
        select(models.POSSession).where(models.POSSession.id == order_data.session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Seans bulunamadı")

    if session.state != "opened":
        raise HTTPException(status_code=400, detail="Seans aktif değil")

    # Sipariş adı oluştur
    order_name = await generate_order_name(db)

    # Sipariş oluştur
    db_order = models.POSOrder(
        name=order_name,
        session_id=order_data.session_id,
        customer_id=order_data.customer_id,
        customer_name=order_data.customer_name,
        customer_phone=order_data.customer_phone,
        customer_tax_id=order_data.customer_tax_id,
        note=order_data.note,
        state="draft"
    )

    db.add(db_order)
    await db.flush()  # ID almak için

    # Satırları ekle
    total_tax = 0.0
    total_amount = 0.0

    for line_data in order_data.lines:
        totals = calculate_line_totals(line_data)

        db_line = models.POSOrderLine(
            order_id=db_order.id,
            product_id=line_data.product_id,
            product_name=line_data.product_name,
            product_barcode=line_data.product_barcode,
            qty=line_data.qty,
            price_unit=line_data.price_unit,
            discount=line_data.discount,
            tax_rate=line_data.tax_rate,
            price_subtotal=totals["price_subtotal"],
            price_subtotal_incl=totals["price_subtotal_incl"]
        )

        db.add(db_line)

        total_amount += totals["price_subtotal_incl"]
        total_tax += (totals["price_subtotal_incl"] - totals["price_subtotal"])

    # Ödemeleri ekle
    total_paid = 0.0

    for payment_data in order_data.payments:
        db_payment = models.POSPayment(
            order_id=db_order.id,
            payment_method=payment_data.payment_method.value,
            payment_method_name=payment_data.payment_method_name,
            amount=payment_data.amount,
            card_type=payment_data.card_type,
            card_number_masked=payment_data.card_number_masked
        )

        db.add(db_payment)
        total_paid += payment_data.amount

    # Sipariş tutarlarını güncelle
    db_order.amount_tax = round(total_tax, 2)
    db_order.amount_total = round(total_amount, 2)
    db_order.amount_paid = round(total_paid, 2)
    db_order.amount_return = round(max(0, total_paid - total_amount), 2)
    db_order.state = "paid" if total_paid >= total_amount else "draft"

    # Session istatistiklerini güncelle
    session.order_count += 1
    session.total_sales += db_order.amount_total
    session.total_payments += db_order.amount_paid

    await db.commit()
    await db.refresh(db_order)

    return db_order


@router.get("/orders", response_model=List[schemas.POSOrderResponse])
async def list_orders(
    skip: int = 0,
    limit: int = 50,
    session_id: Optional[int] = None,
    state: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Siparişleri listele"""
    query = select(models.POSOrder).order_by(models.POSOrder.date_order.desc())

    if session_id:
        query = query.where(models.POSOrder.session_id == session_id)
    if state:
        query = query.where(models.POSOrder.state == state)

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/orders/{order_id}", response_model=schemas.POSOrderResponse)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Sipariş detayı"""
    result = await db.execute(
        select(models.POSOrder).where(models.POSOrder.id == order_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Sipariş bulunamadı")

    return order


# ============= CATEGORY ENDPOINTS =============

@router.post("/categories", response_model=schemas.POSCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: schemas.POSCategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Yeni kategori ekle"""
    db_category = models.POSCategory(**category.model_dump())
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)

    return db_category


@router.get("/categories", response_model=List[schemas.POSCategoryResponse])
async def list_categories(
    db: AsyncSession = Depends(get_db)
):
    """Kategorileri listele"""
    result = await db.execute(
        select(models.POSCategory)
        .where(models.POSCategory.active == True)
        .order_by(models.POSCategory.sequence, models.POSCategory.name)
    )
    return result.scalars().all()


# ============= CONFIG ENDPOINTS =============

@router.post("/config", response_model=schemas.POSConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_config(
    config: schemas.POSConfigCreate,
    db: AsyncSession = Depends(get_db)
):
    """POS yapılandırması oluştur"""
    db_config = models.POSConfig(**config.model_dump())
    db.add(db_config)
    await db.commit()
    await db.refresh(db_config)

    return db_config


@router.get("/config", response_model=List[schemas.POSConfigResponse])
async def get_configs(
    db: AsyncSession = Depends(get_db)
):
    """POS yapılandırmalarını getir"""
    result = await db.execute(
        select(models.POSConfig).where(models.POSConfig.active == True)
    )
    return result.scalars().all()


@router.get("/config/{config_id}", response_model=schemas.POSConfigResponse)
async def get_config(
    config_id: int,
    db: AsyncSession = Depends(get_db)
):
    """POS yapılandırması detayı"""
    result = await db.execute(
        select(models.POSConfig).where(models.POSConfig.id == config_id)
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(status_code=404, detail="Yapılandırma bulunamadı")

    return config
