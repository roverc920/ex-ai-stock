"""Stock analysis router."""
from fastapi import APIRouter, HTTPException
from app.models.schemas import StockRequest, StockResponse
from app.services.akshare_service import akshare_service
from app.services.llm_service import llm_service
from app.services.cache_service import cache_service
from app.services.supabase_service import supabase_service

router = APIRouter()


@router.post("/analyze", response_model=StockResponse)
async def analyze_stock(request: StockRequest):
    """Analyze a stock and save results."""
    stock_code = request.stock_code

    try:
        # Check cache for analysis first
        cached_analysis = await cache_service.get_analysis(stock_code)
        if cached_analysis:
            return StockResponse(**cached_analysis)

        # Get stock data
        stock_info = await akshare_service.get_stock_with_name(stock_code)
        stock_name = stock_info["name"]
        stock_data = stock_info["data"]

        # Cache stock data
        await cache_service.set_stock(stock_code, stock_info)

        # AI analysis
        analysis = await llm_service.analyze_stock(
            stock_code=stock_code,
            stock_name=stock_name,
            stock_data=stock_data.model_dump()
        )

        # Save to database
        saved = await supabase_service.save_analysis(
            stock_code=stock_code,
            stock_name=stock_name,
            raw_data=stock_data,
            analysis=analysis
        )

        # Prepare response
        response = StockResponse(
            id=saved["id"],
            stock_code=stock_code,
            stock_name=stock_name,
            raw_data=stock_data,
            analysis=analysis,
            created_at=saved["created_at"]
        )

        # Cache analysis result
        await cache_service.set_analysis(stock_code, response.model_dump())

        return response

    except ValueError as e:
        raise HTTPException(status_code=400, detail={"error": "analysis_failed", "message": str(e)})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "internal_error", "message": str(e)})
