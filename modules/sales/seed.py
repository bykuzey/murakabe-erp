"""
Sales Module Demo Data Seed
"""

from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from modules.sales.models import Customer, SalesOrder, SalesOrderLine, CustomerType, PaymentTerms, SalesOrderState


async def seed_sales_data(db: AsyncSession):
    """Sales modülü için demo data"""

    print("🌱 Seeding Sales data...")

    # Mevcut müşteri sayısını kontrol et
    from sqlalchemy import select, func
    result = await db.execute(select(func.count(Customer.id)))
    existing_count = result.scalar() or 0

    if existing_count > 0:
        print(f"ℹ️  {existing_count} müşteri zaten mevcut, seed atlianıyor...")
        return

    # Müşteriler
    customers_data = [
        {
            "name": "ABC Teknoloji A.Ş.",
            "code": "C000001",
            "customer_type": CustomerType.CORPORATE,
            "email": "info@abcteknoloji.com",
            "phone": "0212 555 0101",
            "mobile": "0532 555 0101",
            "street": "Teknoloji Caddesi No: 45",
            "city": "İstanbul",
            "state": "İstanbul",
            "zip_code": "34000",
            "tax_office": "Kadıköy",
            "tax_number": "1234567890",
            "payment_term": PaymentTerms.NET30,
            "credit_limit": 100000.0,
            "is_active": True
        },
        {
            "name": "Kuzey Ticaret Ltd. Şti.",
            "code": "C000002",
            "customer_type": CustomerType.CORPORATE,
            "email": "info@kuzeyticaret.com",
            "phone": "0216 555 0202",
            "mobile": "0533 555 0202",
            "street": "Ticaret Sokak No: 12",
            "city": "İstanbul",
            "state": "İstanbul",
            "zip_code": "34100",
            "tax_office": "Üsküdar",
            "tax_number": "9876543210",
            "payment_term": PaymentTerms.NET60,
            "credit_limit": 150000.0,
            "is_active": True
        },
        {
            "name": "Ahmet Yılmaz",
            "code": "C000003",
            "customer_type": CustomerType.INDIVIDUAL,
            "email": "ahmet.yilmaz@email.com",
            "phone": "0212 555 0303",
            "mobile": "0534 555 0303",
            "street": "Örnek Mahallesi, Sokak No: 5",
            "city": "Ankara",
            "state": "Ankara",
            "zip_code": "06000",
            "tax_office": "Çankaya",
            "tax_number": "12345678901",
            "payment_term": PaymentTerms.IMMEDIATE,
            "credit_limit": 10000.0,
            "is_active": True
        },
        {
            "name": "Deniz Perakende Zinciri",
            "code": "C000004",
            "customer_type": CustomerType.CORPORATE,
            "email": "satis@denizperakende.com",
            "phone": "0232 555 0404",
            "mobile": "0535 555 0404",
            "street": "Cumhuriyet Bulvarı No: 123",
            "city": "İzmir",
            "state": "İzmir",
            "zip_code": "35000",
            "tax_office": "Konak",
            "tax_number": "5555555555",
            "payment_term": PaymentTerms.NET15,
            "credit_limit": 200000.0,
            "is_active": True
        },
        {
            "name": "Mehmet Demir",
            "code": "C000005",
            "customer_type": CustomerType.INDIVIDUAL,
            "email": "mehmet.demir@email.com",
            "phone": "0312 555 0505",
            "mobile": "0536 555 0505",
            "street": "Yeni Mahalle No: 78",
            "city": "Ankara",
            "state": "Ankara",
            "zip_code": "06200",
            "tax_office": "Keçiören",
            "tax_number": "98765432109",
            "payment_term": PaymentTerms.IMMEDIATE,
            "credit_limit": 5000.0,
            "is_active": True
        }
    ]

    customers = []
    for customer_data in customers_data:
        customer = Customer(**customer_data)
        db.add(customer)
        customers.append(customer)

    await db.commit()
    print(f"✅ Created {len(customers)} customers")

    # Satış Siparişleri
    orders_data = [
        {
            "customer": customers[0],  # ABC Teknoloji
            "state": SalesOrderState.CONFIRMED,
            "name": "SO00001",
            "order_date": datetime.utcnow() - timedelta(days=5),
            "expected_delivery": datetime.utcnow() + timedelta(days=10),
            "payment_term": PaymentTerms.NET30,
            "reference": "ABC-REF-001",
            "note": "İlk sipariş",
            "lines": [
                {
                    "product_name": "Dizüstü Bilgisayar - Dell Latitude 5420",
                    "product_code": "DELL-LAT-5420",
                    "quantity": 10,
                    "unit_price": 25000.0,
                    "discount": 5.0,
                    "tax_rate": 20.0
                },
                {
                    "product_name": "Wireless Mouse - Logitech MX Master 3",
                    "product_code": "LOG-MX3",
                    "quantity": 10,
                    "unit_price": 1500.0,
                    "discount": 0.0,
                    "tax_rate": 20.0
                }
            ]
        },
        {
            "customer": customers[1],  # Kuzey Ticaret
            "state": SalesOrderState.QUOTATION,
            "name": "SO00002",
            "order_date": datetime.utcnow() - timedelta(days=2),
            "validity_date": datetime.utcnow() + timedelta(days=15),
            "payment_term": PaymentTerms.NET60,
            "reference": "KT-TEKLIF-2024",
            "note": "Toplu alım teklifi",
            "lines": [
                {
                    "product_name": "Ofis Sandalyesi - Ergonomik",
                    "product_code": "OFIS-SND-001",
                    "quantity": 50,
                    "unit_price": 3500.0,
                    "discount": 10.0,
                    "tax_rate": 20.0
                },
                {
                    "product_name": "Çalışma Masası - 120x80cm",
                    "product_code": "MASA-120",
                    "quantity": 25,
                    "unit_price": 5000.0,
                    "discount": 10.0,
                    "tax_rate": 20.0
                },
                {
                    "product_name": "LED Aydınlatma - Masa Lambası",
                    "product_code": "LED-MASA",
                    "quantity": 25,
                    "unit_price": 850.0,
                    "discount": 5.0,
                    "tax_rate": 20.0
                }
            ]
        },
        {
            "customer": customers[2],  # Ahmet Yılmaz
            "state": SalesOrderState.CONFIRMED,
            "name": "SO00003",
            "order_date": datetime.utcnow() - timedelta(days=1),
            "expected_delivery": datetime.utcnow() + timedelta(days=3),
            "payment_term": PaymentTerms.IMMEDIATE,
            "note": "Acil teslimat",
            "lines": [
                {
                    "product_name": "iPhone 15 Pro - 256GB",
                    "product_code": "APPLE-IP15P-256",
                    "quantity": 1,
                    "unit_price": 45000.0,
                    "discount": 0.0,
                    "tax_rate": 20.0
                },
                {
                    "product_name": "AirPods Pro 2",
                    "product_code": "APPLE-APP2",
                    "quantity": 1,
                    "unit_price": 8500.0,
                    "discount": 0.0,
                    "tax_rate": 20.0
                }
            ]
        },
        {
            "customer": customers[3],  # Deniz Perakende
            "state": SalesOrderState.DRAFT,
            "name": "SO00004",
            "order_date": datetime.utcnow(),
            "payment_term": PaymentTerms.NET15,
            "internal_note": "Fiyat revizyon bekleniyor",
            "lines": [
                {
                    "product_name": "Samsung Smart TV - 55 inch",
                    "product_code": "SAMSUNG-TV55",
                    "quantity": 100,
                    "unit_price": 12000.0,
                    "discount": 15.0,
                    "tax_rate": 20.0
                },
                {
                    "product_name": "Soundbar - Samsung HW-Q600B",
                    "product_code": "SAMSUNG-SB-Q600",
                    "quantity": 50,
                    "unit_price": 6500.0,
                    "discount": 10.0,
                    "tax_rate": 20.0
                }
            ]
        }
    ]

    for order_data in orders_data:
        lines_data = order_data.pop("lines")
        customer = order_data.pop("customer")

        order = SalesOrder(**order_data, customer_id=customer.id)

        for idx, line_data in enumerate(lines_data, start=1):
            line = SalesOrderLine(**line_data, sequence=idx * 10)
            line.calculate_prices()
            order.lines.append(line)

        order.calculate_totals()

        # Confirmed olanları onayla
        if order.state == SalesOrderState.CONFIRMED:
            order.confirmation_date = order.order_date

        db.add(order)

    await db.commit()
    print(f"✅ Created {len(orders_data)} sales orders")
    print("✅ Sales data seeding completed!")


if __name__ == "__main__":
    import asyncio
    from core.database import async_session_maker, init_db

    async def main():
        # Önce tabloları oluştur
        await init_db()

        async with async_session_maker() as session:
            await seed_sales_data(session)

    asyncio.run(main())
