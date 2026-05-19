"""History router."""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.models.schemas import HistoryResponse, StockResponse
from app.services.supabase_service import supabase_service

router = APIRouter()


@router.get("/history", response_model=HistoryResponse)
async def get_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    stock_code: Optional[str] = None
):
    """Get analysis history."""
    try:
        result = await supabase_service.get_history(
            page=page,
            page_size=page_size,
            stock_code=stock_code
        )
        return HistoryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "internal_error", "message": str(e)})


@router.get("/history/{analysis_id}", response_model=StockResponse)
async def get_analysis_detail(analysis_id: str):
    """Get single analysis detail."""
    try:
        result = await supabase_service.get_analysis_by_id(analysis_id)
        if not result:
            raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Analysis not found"})
        return StockResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "internal_error", "message": str(e)})
