"""Stock data router."""
from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.models.schemas import StockInfoResponse
from app.services.akshare_service import akshare_service
from app.services.cache_service import cache_service

router = APIRouter()


@router.get("/stock/{stock_code}", response_model=StockInfoResponse)
async def get_stock(stock_code: str):
    """Get stock data (cached or fresh)."""
    try:
        # Check cache
        cached = await cache_service.get_stock(stock_code)
        if cached:
            return StockInfoResponse(
                stock_code=cached["code"],
                stock_name=cached["name"],
                data=cached["data"],
                cached=True,
                cached_at=datetime.fromisoformat(cached.get("cached_at", datetime.utcnow().isoformat()))
            )

        # Fetch fresh data
        stock_info = await akshare_service.get_stock_with_name(stock_code)

        # Cache it
        await cache_service.set_stock(stock_code, stock_info)

        return StockInfoResponse(
            stock_code=stock_info["code"],
            stock_name=stock_info["name"],
            data=stock_info["data"],
            cached=False
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail={"error": "invalid_stock", "message": str(e)})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "internal_error", "message": str(e)})
