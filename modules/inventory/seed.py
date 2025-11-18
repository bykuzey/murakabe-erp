"""
Inventory Module Demo Data Seed
"""

from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from modules.inventory.models import (
    Product, ProductCategory, StockLocation, StockMove,
    ProductType, StockMoveType, StockMoveState
)


async def seed_inventory_data(db: AsyncSession):
    """Inventory modülü için demo data"""

    print("🌱 Seeding Inventory data...")

    # Mevcut kontrol
    from sqlalchemy import select, func
    result = await db.execute(select(func.count(Product.id)))
    existing_count = result.scalar() or 0

    if existing_count > 0:
        print(f"ℹ️  {existing_count} ürün zaten mevcut, seed atlanıyor...")
        return

    # Kategoriler
    result = await db.execute(select(func.count(ProductCategory.id)))
    cat_count = result.scalar() or 0

    if cat_count == 0:
        categories_data = [
            {"name": "Elektronik", "code": "CAT0001", "description": "Elektronik cihazlar"},
            {"name": "Mobilya", "code": "CAT0002", "description": "Ofis mobilyaları"},
            {"name": "Kırtasiye", "code": "CAT0003", "description": "Ofis malzemeleri"},
            {"name": "Bilgisayar", "code": "CAT0004", "description": "Bilgisayar ve aksesuarları"},
            {"name": "Yazılım", "code": "CAT0005", "description": "Yazılım lisansları"},
        ]

        categories = []
        for cat_data in categories_data:
            category = ProductCategory(**cat_data)
            db.add(category)
            categories.append(category)

        await db.commit()
        print(f"✅ Created {len(categories)} categories")
    else:
        # Mevcut kategorileri yükle
        result = await db.execute(select(ProductCategory))
        categories = list(result.scalars().all())
        print(f"ℹ️  {len(categories)} kategori zaten mevcut")

    # Lokasyonlar
    result = await db.execute(select(func.count(StockLocation.id)))
    loc_count = result.scalar() or 0

    if loc_count == 0:
        locations_data = [
            {"name": "Ana Depo", "code": "LOC0001", "location_type": "internal"},
            {"name": "Satış Mağazası", "code": "LOC0002", "location_type": "internal"},
            {"name": "Tedarikçiler", "code": "LOC0003", "location_type": "supplier"},
            {"name": "Müşteriler", "code": "LOC0004", "location_type": "customer"},
        ]

        locations = []
        for loc_data in locations_data:
            location = StockLocation(**loc_data)
            db.add(location)
            locations.append(location)

        await db.commit()
        print(f"✅ Created {len(locations)} locations")
    else:
        # Mevcut lokasyonları yükle
        result = await db.execute(select(StockLocation))
        locations = list(result.scalars().all())
        print(f"ℹ️  {len(locations)} lokasyon zaten mevcut")    # Ürünler
    products_data = [
        {
            "name": "Dell Latitude 5420 Dizüstü Bilgisayar",
            "code": "PRD00001",
            "barcode": "8697671005420",
            "category_id": categories[3].id,  # Bilgisayar
            "product_type": ProductType.STORABLE,
            "list_price": 25000.0,
            "cost_price": 18000.0,
            "qty_available": 15.0,
            "min_qty": 5.0,
            "reorder_point": 8.0,
            "uom": "Adet"
        },
        {
            "name": "Logitech MX Master 3 Mouse",
            "code": "PRD00002",
            "barcode": "097855123456",
            "category_id": categories[3].id,
            "product_type": ProductType.STORABLE,
            "list_price": 1500.0,
            "cost_price": 950.0,
            "qty_available": 45.0,
            "min_qty": 10.0,
            "reorder_point": 15.0,
            "uom": "Adet"
        },
        {
            "name": "Ergonomik Ofis Sandalyesi",
            "code": "PRD00003",
            "barcode": "8690000001234",
            "category_id": categories[1].id,  # Mobilya
            "product_type": ProductType.STORABLE,
            "list_price": 3500.0,
            "cost_price": 2200.0,
            "qty_available": 8.0,
            "min_qty": 3.0,
            "reorder_point": 5.0,
            "uom": "Adet"
        },
        {
            "name": "120x80cm Çalışma Masası",
            "code": "PRD00004",
            "barcode": "8690000001241",
            "category_id": categories[1].id,
            "product_type": ProductType.STORABLE,
            "list_price": 5000.0,
            "cost_price": 3200.0,
            "qty_available": 12.0,
            "min_qty": 4.0,
            "reorder_point": 6.0,
            "uom": "Adet"
        },
        {
            "name": "A4 Fotokopi Kağıdı (500'lü)",
            "code": "PRD00005",
            "barcode": "8690001234567",
            "category_id": categories[2].id,  # Kırtasiye
            "product_type": ProductType.CONSUMABLE,
            "list_price": 150.0,
            "cost_price": 95.0,
            "qty_available": 250.0,
            "min_qty": 50.0,
            "reorder_point": 100.0,
            "uom": "Paket"
        },
        {
            "name": "Tükenmez Kalem (Mavi)",
            "code": "PRD00006",
            "barcode": "8690001234574",
            "category_id": categories[2].id,
            "product_type": ProductType.CONSUMABLE,
            "list_price": 5.0,
            "cost_price": 2.5,
            "qty_available": 850.0,
            "min_qty": 100.0,
            "reorder_point": 200.0,
            "uom": "Adet"
        },
        {
            "name": "27'' Full HD Monitör",
            "code": "PRD00007",
            "barcode": "8697671027001",
            "category_id": categories[3].id,
            "product_type": ProductType.STORABLE,
            "list_price": 4500.0,
            "cost_price": 3000.0,
            "qty_available": 6.0,
            "min_qty": 3.0,
            "reorder_point": 5.0,
            "uom": "Adet"
        },
        {
            "name": "USB-C Hub (7 Port)",
            "code": "PRD00008",
            "barcode": "8690008888888",
            "category_id": categories[3].id,
            "product_type": ProductType.STORABLE,
            "list_price": 850.0,
            "cost_price": 550.0,
            "qty_available": 3.0,  # Düşük stok!
            "min_qty": 5.0,
            "reorder_point": 8.0,
            "uom": "Adet"
        },
        {
            "name": "Microsoft Office 365 Lisansı (Yıllık)",
            "code": "PRD00009",
            "barcode": "MS365YEARLY",
            "category_id": categories[4].id,  # Yazılım
            "product_type": ProductType.SERVICE,
            "list_price": 1200.0,
            "cost_price": 800.0,
            "qty_available": 0.0,  # Hizmet ürünü
            "uom": "Lisans"
        },
        {
            "name": "LED Masa Lambası",
            "code": "PRD00010",
            "barcode": "8690010101010",
            "category_id": categories[0].id,  # Elektronik
            "product_type": ProductType.STORABLE,
            "list_price": 450.0,
            "cost_price": 280.0,
            "qty_available": 22.0,
            "min_qty": 8.0,
            "reorder_point": 12.0,
            "uom": "Adet"
        },
    ]

    products = []
    for prod_data in products_data:
        product = Product(**prod_data)
        product.update_virtual_available()
        db.add(product)
        products.append(product)

    await db.commit()
    print(f"✅ Created {len(products)} products")

    # Stok Hareketleri (Son 1 ayın hareketleri)
    moves_data = [
        {
            "product": products[0],  # Dell Laptop
            "move_type": StockMoveType.IN,
            "state": StockMoveState.DONE,
            "name": "SM00001",
            "location_from_id": locations[2].id,  # Tedarikçiler
            "location_to_id": locations[0].id,  # Ana Depo
            "quantity": 10.0,
            "unit_price": 18000.0,
            "scheduled_date": datetime.utcnow() - timedelta(days=25),
            "done_date": datetime.utcnow() - timedelta(days=25),
            "reference": "PO-2024-001"
        },
        {
            "product": products[1],  # Mouse
            "move_type": StockMoveType.IN,
            "state": StockMoveState.DONE,
            "name": "SM00002",
            "location_from_id": locations[2].id,
            "location_to_id": locations[0].id,
            "quantity": 50.0,
            "unit_price": 950.0,
            "scheduled_date": datetime.utcnow() - timedelta(days=20),
            "done_date": datetime.utcnow() - timedelta(days=20),
            "reference": "PO-2024-002"
        },
        {
            "product": products[0],  # Dell Laptop - Satış
            "move_type": StockMoveType.OUT,
            "state": StockMoveState.DONE,
            "name": "SM00003",
            "location_from_id": locations[0].id,
            "location_to_id": locations[3].id,  # Müşteriler
            "quantity": 5.0,
            "unit_price": 25000.0,
            "scheduled_date": datetime.utcnow() - timedelta(days=15),
            "done_date": datetime.utcnow() - timedelta(days=15),
            "reference": "SO00001"
        },
        {
            "product": products[7],  # USB Hub - Bekleyen sipariş
            "move_type": StockMoveType.IN,
            "state": StockMoveState.CONFIRMED,
            "name": "SM00004",
            "location_from_id": locations[2].id,
            "location_to_id": locations[0].id,
            "quantity": 20.0,
            "unit_price": 550.0,
            "scheduled_date": datetime.utcnow() + timedelta(days=5),
            "reference": "PO-2024-003"
        },
    ]

    for move_data in moves_data:
        product = move_data.pop("product")
        move = StockMove(**move_data, product_id=product.id)
        move.calculate_total()
        db.add(move)

    await db.commit()
    print(f"✅ Created {len(moves_data)} stock moves")
    print("✅ Inventory data seeding completed!")


if __name__ == "__main__":
    import asyncio
    from core.database import async_session_maker, init_db

    async def main():
        # Önce tabloları oluştur
        await init_db()

        async with async_session_maker() as session:
            await seed_inventory_data(session)

    asyncio.run(main())
