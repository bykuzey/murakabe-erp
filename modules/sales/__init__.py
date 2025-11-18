"""
MinimalERP - Sales Module (Placeholder)
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def sales_root():
    """Sales module root"""
    return {"message": "Sales & CRM Module - Coming Soon"}
