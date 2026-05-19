"""Supabase service for data persistence."""
from typing import List, Dict, Any, Optional
from uuid import uuid4
from app.config import settings
from app.models.schemas import StockData, AnalysisResult, HistoryItem

# Optional Supabase import
try:
    from supabase import create_client, Client
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False


class SupabaseService:
    """Service for Supabase database operations."""

    def __init__(self):
        self.client = None
        self.table = "stock_analyses"
        self.enabled = False

        # Check if Supabase is configured
        if not HAS_SUPABASE:
            print("ℹ️ Supabase not installed, running without persistence")
            return

        if not settings.SUPABASE_URL or "your-project" in settings.SUPABASE_URL:
            print("ℹ️ Supabase not configured, running without persistence")
            return

        try:
            self.client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_KEY
            )
            self.enabled = True
            print("✅ Supabase connected")
        except Exception as e:
            print(f"⚠️ Supabase connection failed: {e}")
            self.client = None

    async def save_analysis(
        self,
        stock_code: str,
        stock_name: str,
        raw_data: StockData,
        analysis: AnalysisResult
    ) -> Dict[str, Any]:
        """Save stock analysis to database."""
        # Generate a mock ID when Supabase is not available
        mock_id = str(uuid4())

        if not self.enabled or not self.client:
            print(f"ℹ️ Supabase not available, skipping persistence for {stock_code}")
            return {
                "id": mock_id,
                "stock_code": stock_code,
                "stock_name": stock_name,
                "raw_data": raw_data.model_dump(),
                "analysis": analysis.model_dump(),
                "sentiment": analysis.sentiment,
                "risk_level": analysis.risk.level,
                "created_at": "2025-01-01T00:00:00Z"
            }

        data = {
            "stock_code": stock_code,
            "stock_name": stock_name,
            "raw_data": raw_data.model_dump(),
            "analysis": analysis.model_dump(),
            "sentiment": analysis.sentiment,
            "risk_level": analysis.risk.level
        }

        try:
            result = self.client.table(self.table).insert(data).execute()

            if not result.data:
                raise ValueError("Failed to save analysis")

            return result.data[0]
        except Exception as e:
            print(f"⚠️ Failed to save to Supabase: {e}")
            # Return mock data on failure
            return {
                "id": mock_id,
                "stock_code": stock_code,
                "stock_name": stock_name,
                "raw_data": raw_data.model_dump(),
                "analysis": analysis.model_dump(),
                "sentiment": analysis.sentiment,
                "risk_level": analysis.risk.level,
                "created_at": "2025-01-01T00:00:00Z"
            }

    async def get_history(
        self,
        page: int = 1,
        page_size: int = 20,
        stock_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get analysis history with pagination."""
        if not self.enabled or not self.client:
            print("ℹ️ Supabase not available, returning empty history")
            return {
                "items": [],
                "total": 0,
                "page": page,
                "page_size": page_size
            }

        try:
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
        except Exception as e:
            print(f"⚠️ Failed to get history from Supabase: {e}")
            return {
                "items": [],
                "total": 0,
                "page": page,
                "page_size": page_size
            }

    async def get_analysis_by_id(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get single analysis by ID."""
        if not self.enabled or not self.client:
            return None

        try:
            result = self.client.table(self.table).select("*").eq("id", analysis_id).execute()

            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
        except Exception as e:
            print(f"⚠️ Failed to get analysis from Supabase: {e}")
            return None


supabase_service = SupabaseService()
