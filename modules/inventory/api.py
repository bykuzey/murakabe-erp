"""
MinimalERP - Inventory API
Product and Stock Management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from typing import List, Optional
from datetime import datetime

from core.database import get_db
from modules.inventory.models import (
    Product, ProductCategory, StockLocation, StockMove, StockQuant,
    StockMoveType, StockMoveState
)
from modules.inventory import schemas

router = APIRouter(
    prefix="/api/inventory",
    tags=["Inventory"]
)


# ==================== CATEGORIES ====================

@router.post("/categories", response_model=schemas.ProductCategory, status_code=201)
async def create_category(
    category: schemas.ProductCategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Yeni kategori oluştur"""
    # Kod oluştur
    result = await db.execute(select(func.count(ProductCategory.id)))
    count = result.scalar() or 0
    code = f"CAT{str(count + 1).zfill(4)}"

    db_category = ProductCategory(**category.model_dump(), code=code)
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)

    return db_category


@router.get("/categories", response_model=List[schemas.ProductCategory])
async def list_categories(db: AsyncSession = Depends(get_db)):
    """Kategori listesi"""
    result = await db.execute(select(ProductCategory).order_by(ProductCategory.name))
    categories = result.scalars().all()
    return categories


# ==================== PRODUCTS ====================

def generate_product_code(count: int) -> str:
    """Ürün kodu oluştur: PRD001, PRD002..."""
    return f"PRD{str(count + 1).zfill(5)}"


@router.post("/products", response_model=schemas.Product, status_code=201)
async def create_product(
    product: schemas.ProductCreate,
    db: AsyncSession = Depends(get_db)
):
    """Yeni ürün oluştur"""
    # Ürün kodu oluştur
    result = await db.execute(select(func.count(Product.id)))
    count = result.scalar() or 0
    product_code = generate_product_code(count)

    db_product = Product(**product.model_dump(), code=product_code)
    db_product.update_virtual_available()

    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)

    return db_product


@router.get("/products", response_model=List[schemas.ProductSummary])
async def list_products(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    low_stock: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Ürün listesi"""
    query = select(Product)

    # Filtreler
    if search:
        query = query.where(
            or_(
                Product.name.ilike(f"%{search}%"),
                Product.code.ilike(f"%{search}%"),
                Product.barcode.ilike(f"%{search}%")
            )
        )

    if category_id:
        query = query.where(Product.category_id == category_id)

    if is_active is not None:
        query = query.where(Product.is_active == is_active)

    if low_stock:
        query = query.where(
            and_(
                Product.reorder_point > 0,
                Product.virtual_available <= Product.reorder_point
            )
        )

    query = query.offset(skip).limit(limit).order_by(Product.name)

    result = await db.execute(query)
    products = result.scalars().all()

    return products


@router.get("/products/{product_id}", response_model=schemas.Product)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Ürün detayı"""
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")

    return product


@router.put("/products/{product_id}", response_model=schemas.Product)
async def update_product(
    product_id: int,
    product_update: schemas.ProductUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Ürün güncelle"""
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    db_product = result.scalar_one_or_none()

    if not db_product:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")

    update_data = product_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)

    db_product.update_virtual_available()

    await db.commit()
    await db.refresh(db_product)

    return db_product


@router.delete("/products/{product_id}", status_code=204)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Ürün sil"""
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")

    await db.delete(product)
    await db.commit()

    return None


# ==================== STOCK LOCATIONS ====================

@router.post("/locations", response_model=schemas.StockLocation, status_code=201)
async def create_location(
    location: schemas.StockLocationCreate,
    db: AsyncSession = Depends(get_db)
):
    """Yeni lokasyon oluştur"""
    result = await db.execute(select(func.count(StockLocation.id)))
    count = result.scalar() or 0
    code = location.code or f"LOC{str(count + 1).zfill(4)}"

    db_location = StockLocation(**location.model_dump(exclude={'code'}), code=code)
    db.add(db_location)
    await db.commit()
    await db.refresh(db_location)

    return db_location


@router.get("/locations", response_model=List[schemas.StockLocation])
async def list_locations(db: AsyncSession = Depends(get_db)):
    """Lokasyon listesi"""
    result = await db.execute(
        select(StockLocation)
        .where(StockLocation.is_active == True)
        .order_by(StockLocation.name)
    )
    locations = result.scalars().all()
    return locations


# ==================== STOCK MOVES ====================

def generate_move_name(count: int) -> str:
    """Hareket numarası oluştur: SM001, SM002..."""
    return f"SM{str(count + 1).zfill(5)}"


@router.post("/moves", response_model=schemas.StockMove, status_code=201)
async def create_stock_move(
    move: schemas.StockMoveCreate,
    db: AsyncSession = Depends(get_db)
):
    """Yeni stok hareketi oluştur"""
    # Ürün kontrolü
    result = await db.execute(
        select(Product).where(Product.id == move.product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")

    # Hareket numarası
    result = await db.execute(select(func.count(StockMove.id)))
    count = result.scalar() or 0
    move_name = generate_move_name(count)

    db_move = StockMove(**move.model_dump(), name=move_name)
    db_move.calculate_total()

    db.add(db_move)
    await db.commit()
    await db.refresh(db_move)

    return db_move


@router.get("/moves", response_model=List[schemas.StockMoveSummary])
async def list_stock_moves(
    skip: int = 0,
    limit: int = 100,
    product_id: Optional[int] = None,
    move_type: Optional[StockMoveType] = None,
    state: Optional[StockMoveState] = None,
    db: AsyncSession = Depends(get_db)
):
    """Stok hareketi listesi"""
    query = select(
        StockMove.id,
        StockMove.name,
        StockMove.product_id,
        Product.name.label("product_name"),
        StockMove.move_type,
        StockMove.state,
        StockMove.quantity,
        StockMove.unit_price,
        StockMove.total_value,
        StockMove.scheduled_date,
        StockMove.done_date,
        StockMove.created_at
    ).join(Product)

    if product_id:
        query = query.where(StockMove.product_id == product_id)

    if move_type:
        query = query.where(StockMove.move_type == move_type)

    if state:
        query = query.where(StockMove.state == state)

    query = query.offset(skip).limit(limit).order_by(StockMove.created_at.desc())

    result = await db.execute(query)
    moves = result.all()

    return [
        schemas.StockMoveSummary(
            id=row.id,
            name=row.name,
            product_id=row.product_id,
            product_name=row.product_name,
            move_type=row.move_type,
            state=row.state,
            quantity=row.quantity,
            unit_price=row.unit_price,
            total_value=row.total_value,
            scheduled_date=row.scheduled_date,
            done_date=row.done_date,
            created_at=row.created_at
        )
        for row in moves
    ]


@router.post("/moves/{move_id}/confirm", response_model=schemas.StockMove)
async def confirm_stock_move(
    move_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Stok hareketini onayla"""
    result = await db.execute(
        select(StockMove).where(StockMove.id == move_id)
    )
    move = result.scalar_one_or_none()

    if not move:
        raise HTTPException(status_code=404, detail="Hareket bulunamadı")

    move.confirm()
    await db.commit()
    await db.refresh(move)

    return move


@router.post("/moves/{move_id}/execute", response_model=schemas.StockMove)
async def execute_stock_move(
    move_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Stok hareketini gerçekleştir"""
    result = await db.execute(
        select(StockMove).where(StockMove.id == move_id)
    )
    move = result.scalar_one_or_none()

    if not move:
        raise HTTPException(status_code=404, detail="Hareket bulunamadı")

    try:
        move.execute()
        await db.commit()
        await db.refresh(move)
        return move
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== DASHBOARD ====================

@router.get("/stats/dashboard")
async def inventory_dashboard(db: AsyncSession = Depends(get_db)):
    """Envanter dashboard istatistikleri"""
    # Toplam ürün sayısı
    result = await db.execute(
        select(func.count(Product.id)).where(Product.is_active == True)
    )
    total_products = result.scalar() or 0

    # Düşük stok uyarıları
    result = await db.execute(
        select(Product).where(
            and_(
                Product.reorder_point > 0,
                Product.virtual_available <= Product.reorder_point,
                Product.is_active == True
            )
        )
    )
    low_stock_products = result.scalars().all()

    # Toplam stok değeri
    result = await db.execute(
        select(func.sum(Product.qty_available * Product.cost_price))
        .where(Product.is_active == True)
    )
    total_stock_value = result.scalar() or 0

    # Son hareketler
    result = await db.execute(
        select(StockMove.state, func.count(StockMove.id))
        .group_by(StockMove.state)
    )
    moves_by_state = {row[0].value: row[1] for row in result.all()}

    return {
        "total_products": total_products,
        "low_stock_count": len(low_stock_products),
        "low_stock_products": [
            schemas.LowStockAlert(
                product_id=p.id,
                product_code=p.code,
                product_name=p.name,
                qty_available=p.qty_available,
                reorder_point=p.reorder_point,
                min_qty=p.min_qty
            )
            for p in low_stock_products[:10]  # İlk 10
        ],
        "total_stock_value": float(total_stock_value),
        "moves_by_state": moves_by_state,
        "generated_at": datetime.utcnow()
    }

