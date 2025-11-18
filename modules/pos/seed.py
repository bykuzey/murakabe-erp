"""
POS Module - Seed Data

Demo ürünler ve kategoriler ekle.
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import async_session_maker
from modules.pos.models import POSProduct, POSCategory, POSConfig


async def seed_pos_data():
    """POS demo verilerini ekle"""
    async with async_session_maker() as session:
        # Kategoriler
        categories = [
            POSCategory(name="İçecekler", color="#3b82f6", icon="coffee", sequence=1),
            POSCategory(name="Gıda", color="#10b981", icon="shopping-bag", sequence=2),
            POSCategory(name="Şarküteri", color="#f59e0b", icon="meat", sequence=3),
            POSCategory(name="Temizlik", color="#8b5cf6", icon="spray", sequence=4),
            POSCategory(name="Kırtasiye", color="#ec4899", icon="pen", sequence=5),
        ]

        session.add_all(categories)
        await session.flush()

        # Ürünler
        products = [
            # İçecekler
            POSProduct(
                name="Coca Cola 330ml",
                barcode="8690632003003",
                category_id=categories[0].id,
                list_price=25.00,
                cost_price=15.00,
                tax_rate=20.0,
                qty_available=100,
                color="#ef4444",
                is_favorite=True,
                sequence=1
            ),
            POSProduct(
                name="Fanta 330ml",
                barcode="8690632003010",
                category_id=categories[0].id,
                list_price=25.00,
                cost_price=15.00,
                tax_rate=20.0,
                qty_available=80,
                color="#f97316",
                sequence=2
            ),
            POSProduct(
                name="Sprite 330ml",
                barcode="8690632003027",
                category_id=categories[0].id,
                list_price=25.00,
                cost_price=15.00,
                tax_rate=20.0,
                qty_available=75,
                color="#22c55e",
                sequence=3
            ),
            POSProduct(
                name="Su 500ml",
                barcode="8690632003034",
                category_id=categories[0].id,
                list_price=5.00,
                cost_price=2.50,
                tax_rate=20.0,
                qty_available=200,
                color="#06b6d4",
                is_favorite=True,
                sequence=4
            ),
            POSProduct(
                name="Çay Bardak",
                barcode="8690632003041",
                category_id=categories[0].id,
                list_price=10.00,
                cost_price=3.00,
                tax_rate=20.0,
                qty_available=150,
                color="#ca8a04",
                sequence=5
            ),

            # Gıda
            POSProduct(
                name="Ekmek 350g",
                barcode="1234567890123",
                category_id=categories[1].id,
                list_price=15.00,
                cost_price=8.00,
                tax_rate=1.0,
                qty_available=50,
                color="#f59e0b",
                is_favorite=True,
                sequence=10
            ),
            POSProduct(
                name="Süt 1L",
                barcode="8690632004001",
                category_id=categories[1].id,
                list_price=45.00,
                cost_price=30.00,
                tax_rate=1.0,
                qty_available=40,
                color="#3b82f6",
                sequence=11
            ),
            POSProduct(
                name="Yoğurt 500g",
                barcode="8690632004002",
                category_id=categories[1].id,
                list_price=35.00,
                cost_price=22.00,
                tax_rate=1.0,
                qty_available=30,
                color="#f8fafc",
                sequence=12
            ),
            POSProduct(
                name="Yumurta 10'lu",
                barcode="8690632004003",
                category_id=categories[1].id,
                list_price=65.00,
                cost_price=45.00,
                tax_rate=1.0,
                qty_available=25,
                color="#fbbf24",
                sequence=13
            ),
            POSProduct(
                name="Peynir Beyaz 500g",
                barcode="8690632004004",
                category_id=categories[1].id,
                list_price=180.00,
                cost_price=120.00,
                tax_rate=1.0,
                qty_available=15,
                color="#f1f5f9",
                is_favorite=True,
                sequence=14
            ),

            # Şarküteri
            POSProduct(
                name="Salam 150g",
                barcode="8690632005001",
                category_id=categories[2].id,
                list_price=75.00,
                cost_price=50.00,
                tax_rate=20.0,
                qty_available=20,
                color="#dc2626",
                sequence=20
            ),
            POSProduct(
                name="Sucuk 250g",
                barcode="8690632005002",
                category_id=categories[2].id,
                list_price=120.00,
                cost_price=85.00,
                tax_rate=20.0,
                qty_available=18,
                color="#b91c1c",
                sequence=21
            ),

            # Temizlik
            POSProduct(
                name="Deterjan 3kg",
                barcode="8690632006001",
                category_id=categories[3].id,
                list_price=125.00,
                cost_price=80.00,
                tax_rate=20.0,
                qty_available=30,
                color="#06b6d4",
                sequence=30
            ),
            POSProduct(
                name="Bulaşık Deterjanı 750ml",
                barcode="8690632006002",
                category_id=categories[3].id,
                list_price=45.00,
                cost_price=28.00,
                tax_rate=20.0,
                qty_available=40,
                color="#22c55e",
                sequence=31
            ),

            # Kırtasiye
            POSProduct(
                name="Tükenmez Kalem",
                barcode="8690632007001",
                category_id=categories[4].id,
                list_price=15.00,
                cost_price=8.00,
                tax_rate=20.0,
                qty_available=100,
                color="#3b82f6",
                sequence=40
            ),
            POSProduct(
                name="Defter A4",
                barcode="8690632007002",
                category_id=categories[4].id,
                list_price=35.00,
                cost_price=20.00,
                tax_rate=20.0,
                qty_available=50,
                color="#f59e0b",
                sequence=41
            ),
        ]

        session.add_all(products)

        # POS Config
        config = POSConfig(
            name="Ana Kasa",
            company_name="Murakabe Market",
            company_vat="1234567890",
            company_address="İstanbul, Türkiye",
            company_phone="0212 123 45 67",
            receipt_header="MURAKABE MARKET\nHoş Geldiniz",
            receipt_footer="Tekrar Bekleriz\nwww.murakabe.com",
            auto_print_receipt=True,
            payment_methods=[
                {"id": 1, "name": "Nakit", "type": "cash"},
                {"id": 2, "name": "Kredi Kartı", "type": "card"},
                {"id": 3, "name": "Banka Transferi", "type": "bank_transfer"},
            ],
            allow_discount=True,
            max_discount=50.0,
            require_customer=False,
            allow_invoice=True,
            receipt_prefix="FIS",
            receipt_sequence=1
        )

        session.add(config)

        await session.commit()

        print("✅ POS demo verileri başarıyla eklendi!")
        print(f"   - {len(categories)} kategori")
        print(f"   - {len(products)} ürün")
        print(f"   - 1 POS konfigürasyonu")


if __name__ == "__main__":
    asyncio.run(seed_pos_data())
