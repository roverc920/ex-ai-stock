"""Pydantic models for request/response schemas."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class StockData(BaseModel):
    """Stock market data."""
    current_price: float = Field(..., description="当前价格")
    change_percent: float = Field(..., description="涨跌幅(%)")
    volume: int = Field(..., description="成交量(股)")
    turnover: float = Field(..., description="成交额(元)")
    pe_ratio: Optional[float] = Field(None, description="市盈率")
    pb_ratio: Optional[float] = Field(None, description="市净率")
    market_cap: Optional[float] = Field(None, description="总市值(元)")
    high_price: Optional[float] = Field(None, description="最高价")
    low_price: Optional[float] = Field(None, description="最低价")
    open_price: Optional[float] = Field(None, description="开盘价")
    prev_close: Optional[float] = Field(None, description="昨收价")


class RiskAnalysis(BaseModel):
    """Risk analysis result."""
    level: str = Field(..., description="风险等级: Low/Medium/High")
    factors: List[str] = Field(default_factory=list, description="风险因素列表")


class AnalysisResult(BaseModel):
    """AI analysis result."""
    summary: str = Field(..., description="分析总结", max_length=500)
    sentiment: str = Field(..., description="情绪: Bullish/Neutral/Bearish")
    risk: RiskAnalysis = Field(..., description="风险分析")


class StockRequest(BaseModel):
    """Request to analyze a stock - supports multi-market."""
    stock_code: str = Field(..., min_length=1, max_length=10, description="股票代码")

    @field_validator('stock_code')
    @classmethod
    def validate_stock_code(cls, v: str) -> str:
        """Validate stock code format."""
        v = v.strip().upper()
        if not v:
            raise ValueError('股票代码不能为空')
        # Remove prefixes for validation
        clean_code = v
        for prefix in ['SH', 'SZ', 'HK', 'US']:
            if clean_code.startswith(prefix):
                clean_code = clean_code[len(prefix):]
                break
        if not clean_code:
            raise ValueError('股票代码无效')
        if not (clean_code.isdigit() or clean_code.isalpha()):
            raise ValueError('股票代码只能包含数字或字母')
        return v


class StockResponse(BaseModel):
    """Response containing stock data and analysis."""
    id: str = Field(..., description="分析记录ID")
    stock_code: str = Field(..., description="股票代码")
    stock_name: str = Field(..., description="股票名称")
    raw_data: StockData = Field(..., description="原始行情数据")
    analysis: AnalysisResult = Field(..., description="AI分析结果")
    created_at: datetime = Field(..., description="分析时间")


class HistoryItem(BaseModel):
    """History item for list view."""
    id: str = Field(..., description="分析记录ID")
    stock_code: str = Field(..., description="股票代码")
    stock_name: str = Field(..., description="股票名称")
    sentiment: str = Field(..., description="情绪")
    risk_level: str = Field(..., description="风险等级")
    created_at: datetime = Field(..., description="分析时间")


class HistoryResponse(BaseModel):
    """Response for history list."""
    items: List[HistoryItem] = Field(default_factory=list)
    total: int = Field(0, description="总数")
    page: int = Field(1, description="当前页")
    page_size: int = Field(20, description="每页数量")


class StockInfoResponse(BaseModel):
    """Response for stock info only."""
    stock_code: str = Field(..., description="股票代码")
    stock_name: str = Field(..., description="股票名称")
    data: StockData = Field(..., description="行情数据")
    cached: bool = Field(False, description="是否来自缓存")
    cached_at: Optional[datetime] = Field(None, description="缓存时间")


class ErrorResponse(BaseModel):
    """Error response."""
    error: str = Field(..., description="错误代码")
    message: str = Field(..., description="错误信息")
