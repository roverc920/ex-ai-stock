"""Stock data service using Tencent API."""
import httpx
from typing import Dict, Any, Optional
from app.models.schemas import StockData
from app.services.market_detector import detect_market, build_tencent_api_code, get_market_name


class StockService:
    """Service for fetching stock data from Tencent API."""

    def _find_field_by_type(self, fields: list, index: int, default="") -> str:
        """Safely get field by index with default."""
        if index < len(fields):
            return fields[index] if fields[index] else default
        return default

    def _parse_float(self, value: str, default: float = 0.0) -> float:
        """Parse float safely, return default if invalid."""
        if not value or value == '-':
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    def _parse_int(self, value: str, default: int = 0) -> int:
        """Parse int safely, return default if invalid."""
        if not value:
            return default
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return default

    async def get_stock_data(self, stock_code: str) -> Dict[str, Any]:
        """Get real-time stock data from Tencent API - supports multi-market."""
        # Detect market type
        market, clean_code = detect_market(stock_code)

        # Build Tencent API symbol
        symbol = build_tencent_api_code(market, clean_code)

        url = f"https://qt.gtimg.cn/q={symbol}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url)
                response.encoding = 'gbk'
                response.raise_for_status()

                content = response.text.strip()
                if not content or '~' not in content:
                    raise ValueError(f"无效的股票代码: {stock_code}")

                # Parse data
                if '="' in content:
                    data_part = content.split('="')[1].strip('"').rstrip(';')
                else:
                    raise ValueError(f"无效的数据格式: {stock_code}")

                fields = data_part.split('~')

                if len(fields) < 10:
                    raise ValueError(f"股票数据不完整: {stock_code} (字段数: {len(fields)})")

                # Different markets have different field layouts
                # Try to detect and parse accordingly
                stock_name = self._find_field_by_type(fields, 1, clean_code)
                code_in_data = self._find_field_by_type(fields, 2, clean_code)


                # Parse based on market type
                if market == 'us':
                    # US stocks: v_usAAPL="1~Apple Inc.~AAPL~150.00~...
                    # Fields: [0]=market, [1]=name, [2]=code, [3]=price, [4]=change, [5]=change%, ...
                    current_price = self._parse_float(self._find_field_by_type(fields, 3))
                    # For US stocks, we need to find the right fields
                    # Try common indices
                    change_percent = self._parse_float(self._find_field_by_type(fields, 5))  # Often at index 5
                    prev_close = self._parse_float(self._find_field_by_type(fields, 4))
                    open_price = current_price  # Default if not found
                    high_price = current_price
                    low_price = current_price

                    # Find volume (usually a large number)
                    volume = 0
                    for i in range(6, min(20, len(fields))):
                        val = self._find_field_by_type(fields, i)
                        if val.isdigit() and len(val) > 5:
                            volume = int(val)
                            break

                    # US stocks may not have all fields
                    pe_ratio = None
                    pb_ratio = None
                    market_cap = None
                    turnover = 0

                elif market == 'hk':
                    # Hong Kong stocks similar to A-shares but different indices
                    # Need testing, use safe parsing
                    current_price = self._parse_float(self._find_field_by_type(fields, 3))
                    prev_close = self._parse_float(self._find_field_by_type(fields, 4))
                    open_price = self._parse_float(self._find_field_by_type(fields, 5))
                    change_percent = self._parse_float(self._find_field_by_type(fields, 32))
                    high_price = self._parse_float(self._find_field_by_type(fields, 33))
                    low_price = self._parse_float(self._find_field_by_type(fields, 34))

                    volume_hand = self._parse_int(self._find_field_by_type(fields, 6))
                    volume = volume_hand * 100

                    turnover_wan = self._parse_float(self._find_field_by_type(fields, 37))
                    turnover = turnover_wan * 10000

                    pe_ratio = self._parse_float(self._find_field_by_type(fields, 39)) if fields[39] != '-' else None
                    pb_ratio = self._parse_float(self._find_field_by_type(fields, 46)) if len(fields) > 46 and fields[46] != '-' else None
                    market_cap_yi = self._parse_float(self._find_field_by_type(fields, 45))
                    market_cap = market_cap_yi * 100000000

                else:
                    # A-shares (sh/sz) - verified field mapping
                    current_price = self._parse_float(self._find_field_by_type(fields, 3))
                    prev_close = self._parse_float(self._find_field_by_type(fields, 4))
                    open_price = self._parse_float(self._find_field_by_type(fields, 5))

                    volume_hand = self._parse_int(self._find_field_by_type(fields, 6))
                    volume = volume_hand * 100

                    change_percent = self._parse_float(self._find_field_by_type(fields, 32))
                    high_price = self._parse_float(self._find_field_by_type(fields, 33))
                    low_price = self._parse_float(self._find_field_by_type(fields, 34))

                    turnover_wan = self._parse_float(self._find_field_by_type(fields, 37))
                    turnover = turnover_wan * 10000

                    pe_ratio = self._parse_float(self._find_field_by_type(fields, 39)) if len(fields) > 39 and fields[39] != '-' else None
                    pb_ratio = self._parse_float(self._find_field_by_type(fields, 46)) if len(fields) > 46 and fields[46] != '-' else None
                    market_cap_yi = self._parse_float(self._find_field_by_type(fields, 45))
                    market_cap = market_cap_yi * 100000000

                stock_data = StockData(
                    current_price=current_price,
                    change_percent=change_percent,
                    volume=volume,
                    turnover=turnover,
                    pe_ratio=pe_ratio,
                    pb_ratio=pb_ratio,
                    market_cap=market_cap,
                    high_price=high_price,
                    low_price=low_price,
                    open_price=open_price,
                    prev_close=prev_close
                )

                return {
                    "code": clean_code,
                    "name": stock_name,
                    "market": market,
                    "market_name": get_market_name(market),
                    "data": stock_data
                }

            except httpx.HTTPStatusError as e:
                raise ValueError(f"HTTP错误: {e.response.status_code}")
            except Exception as e:
                raise ValueError(f"获取股票数据失败: {str(e)}")


stock_service = StockService()
