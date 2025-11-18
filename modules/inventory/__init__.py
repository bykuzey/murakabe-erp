"""
MinimalERP - Inventory Module (Placeholder)
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def inventory_root():
    """Inventory module root"""
    return {"message": "Inventory Module - Coming Soon"}
