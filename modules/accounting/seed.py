"""
MinimalERP - Accounting Seed Data

Utilities to seed Turkish Uniform Chart of Accounts (Tekdüzen Hesap Planı).
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from modules.accounting.models import Account, AccountType


DEFAULT_ACCOUNTS = [
    # Assets (Varlıklar)
    ("100", "Kasa", AccountType.ASSET),
    ("101", "Alınan Çekler", AccountType.ASSET),
    ("102", "Bankalar", AccountType.ASSET),
    ("120", "Alıcılar", AccountType.ASSET),
    ("153", "Ticari Mallar", AccountType.ASSET),
    ("191", "İndirilecek KDV", AccountType.ASSET),
    # Liabilities (Borçlar)
    ("320", "Satıcılar", AccountType.LIABILITY),
    ("360", "Ödenecek Vergi ve Fonlar", AccountType.LIABILITY),
    ("391", "Hesaplanan KDV", AccountType.LIABILITY),
    # Equity (Özkaynaklar)
    ("500", "Sermaye", AccountType.EQUITY),
    # Revenues (Gelirler)
    ("600", "Yurtiçi Satışlar", AccountType.REVENUE),
    ("601", "Yurtdışı Satışlar", AccountType.REVENUE),
    # Expenses (Giderler)
    ("620", "Satılan Mamul Maliyeti", AccountType.EXPENSE),
    ("630", "Araştırma ve Geliştirme Giderleri", AccountType.EXPENSE),
    ("770", "Genel Yönetim Giderleri", AccountType.EXPENSE),
]


async def seed_default_accounts(db: AsyncSession) -> int:
    """
    Seed a minimal Turkish chart of accounts if not present.

    Returns number of newly created accounts.
    """
    created = 0

    for code, name, acc_type in DEFAULT_ACCOUNTS:
        result = await db.execute(select(Account).where(Account.code == code))
        if result.scalar_one_or_none():
            continue

        account = Account(
            code=code,
            name=name,
            account_type=acc_type,
            currency="TRY",
        )
        db.add(account)
        created += 1

    if created:
        await db.commit()

    return created

