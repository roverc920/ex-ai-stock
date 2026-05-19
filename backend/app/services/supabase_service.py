"""Supabase service for data persistence."""
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from app.config import settings
from app.models.schemas import StockData, AnalysisResult, StockResponse, HistoryItem


class SupabaseService:
    """Service for Supabase database operations."""

    def __init__(self):
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        self.table = "stock_analyses"

    async def save_analysis(
        self,
        stock_code: str,
        stock_name: str,
        raw_data: StockData,
        analysis: AnalysisResult
    ) -> Dict[str, Any]:
        """Save stock analysis to database."""
        data = {
            "stock_code": stock_code,
            "stock_name": stock_name,
            "raw_data": raw_data.model_dump(),
            "analysis": analysis.model_dump(),
            "sentiment": analysis.sentiment,
            "risk_level": analysis.risk.level
        }

        result = self.client.table(self.table).insert(data).execute()

        if not result.data:
            raise ValueError("Failed to save analysis")

        return result.data[0]

    async def get_history(
        self,
        page: int = 1,
        page_size: int = 20,
        stock_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get analysis history with pagination."""
        query = self.client.table(self.table).select("*")

        if stock_code:
            query = query.eq("stock_code", stock_code)

        # Get total count
        count_result = query.execute()
        total = len(count_result.data) if count_result.data else 0

        # Get paginated results
        offset = (page - 1) * page_size
        result = query.order("created_at", desc=True).range(offset, offset + page_size - 1).execute()

        items = []
        for item in result.data or []:
            items.append(HistoryItem(
                id=item["id"],
                stock_code=item["stock_code"],
                stock_name=item["stock_name"],
                sentiment=item["sentiment"],
                risk_level=item["risk_level"],
                created_at=item["created_at"]
            ))

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    async def get_analysis_by_id(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get single analysis by ID."""
        result = self.client.table(self.table).select("*").eq("id", analysis_id).execute()

        if result.data and len(result.data) > 0:
            return result.data[0]
        return None


supabase_service = SupabaseService()
