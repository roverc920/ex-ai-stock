"""AkShare service for A-share stock data."""
from typing import Dict, Any, Optional
from app.models.schemas import StockData
from app.config import settings

# Try import akshare, fallback to None if not available
try:
    import akshare as ak
except ImportError:
    ak = None


def is_mock_mode() -> bool:
    """Check if mock mode is enabled."""
    return settings.MOCK_STOCK_DATA.lower() == "true"


class AkShareService:
    """Service for fetching stock data from AkShare."""

    # Mock stock database for testing
    MOCK_STOCKS = {
        "000001": {"name": "平安银行", "price": 10.52},
        "000002": {"name": "万科A", "price": 8.35},
        "600000": {"name": "浦发银行", "price": 9.18},
        "600519": {"name": "贵州茅台", "price": 1588.00},
        "000858": {"name": "五粮液", "price": 145.20},
        "002415": {"name": "海康威视", "price": 32.65},
    }

    async def get_stock_info(self, stock_code: str) -> Dict[str, Any]:
        """Get stock name and basic info."""
        # Use mock data if enabled or akshare not available
        if is_mock_mode() or ak is None:
            return await self._get_mock_stock_info(stock_code)
        return await self._get_real_stock_info(stock_code)

    async def _get_mock_stock_info(self, stock_code: str) -> Dict[str, Any]:
        """Get mock stock info for testing."""
        if stock_code.startswith('6'):
            market = "sh"
        else:
            market = "sz"

        # Return mock data if exists, otherwise generate
        if stock_code in self.MOCK_STOCKS:
            return {
                "code": stock_code,
                "name": self.MOCK_STOCKS[stock_code]["name"],
                "market": market
            }
        else:
            # Generate generic name for unknown stocks
            return {
                "code": stock_code,
                "name": f"股票{stock_code}",
                "market": market
            }

    async def _get_real_stock_info(self, stock_code: str) -> Dict[str, Any]:
        """Get stock name and basic info."""
        try:
            # Determine exchange based on stock code prefix
            # 6开头=上海, 0/3开头=深圳
            if stock_code.startswith('6'):
                market = "sh"
            else:
                market = "sz"

            # Get stock name
            df = ak.stock_individual_info_em(symbol=stock_code)
            if df.empty:
                raise ValueError(f"股票代码 {stock_code} 不存在")

            stock_name = df.loc[df['item'] == '股票简称', 'value'].values[0]
            return {
                "code": stock_code,
                "name": stock_name,
                "market": market
            }
        except Exception as e:
            raise ValueError(f"获取股票信息失败: {str(e)}")

    async def get_stock_data(self, stock_code: str) -> StockData:
        """Get real-time stock data."""
        if is_mock_mode() or ak is None:
            return await self._get_mock_stock_data(stock_code)
        return await self._get_real_stock_data(stock_code)

    async def _get_mock_stock_data(self, stock_code: str) -> StockData:
        """Get mock stock data for testing."""
        import random

        # Get base price from mock database or generate
        if stock_code in self.MOCK_STOCKS:
            base_price = self.MOCK_STOCKS[stock_code]["price"]
        else:
            base_price = random.uniform(5.0, 200.0)

        # Add some random variation
        change_percent = random.uniform(-5.0, 5.0)
        current_price = base_price * (1 + change_percent / 100)
        open_price = base_price * (1 + random.uniform(-2.0, 2.0) / 100)
        high_price = max(current_price, open_price) * (1 + random.uniform(0, 3.0) / 100)
        low_price = min(current_price, open_price) * (1 - random.uniform(0, 3.0) / 100)
        prev_close = base_price

        volume = int(random.uniform(1000000, 100000000))
        turnover = volume * current_price

        return StockData(
            current_price=round(current_price, 2),
            change_percent=round(change_percent, 2),
            volume=volume,
            turnover=round(turnover, 2),
            pe_ratio=round(random.uniform(5.0, 50.0), 2),
            pb_ratio=round(random.uniform(0.5, 10.0), 2),
            market_cap=round(current_price * random.uniform(1000000000, 10000000000), 2),
            high_price=round(high_price, 2),
            low_price=round(low_price, 2),
            open_price=round(open_price, 2),
            prev_close=round(prev_close, 2)
        )

    async def _get_real_stock_data(self, stock_code: str) -> StockData:
        """Get real stock data from AkShare."""
        try:
            # Get real-time quote
            df = ak.stock_zh_a_spot_em()

            # Filter by stock code
            stock_row = df[df['代码'] == stock_code]

            if stock_row.empty:
                raise ValueError(f"股票代码 {stock_code} 未找到")

            row = stock_row.iloc[0]

            # Parse numeric values, handling NaN
            def parse_float(val, default=0.0):
                try:
                    return float(val) if val and str(val) not in ['-', 'NaN', 'nan'] else default
                except:
                    return default

            def parse_int(val, default=0):
                try:
                    return int(float(val)) if val and str(val) not in ['-', 'NaN', 'nan'] else default
                except:
                    return default

            return StockData(
                current_price=parse_float(row.get('最新价')),
                change_percent=parse_float(row.get('涨跌幅')),
                volume=parse_int(row.get('成交量')),
                turnover=parse_float(row.get('成交额')),
                pe_ratio=parse_float(row.get('市盈率-动态'), None),
                pb_ratio=parse_float(row.get('市净率'), None),
                market_cap=parse_float(row.get('总市值'), None),
                high_price=parse_float(row.get('最高')),
                low_price=parse_float(row.get('最低')),
                open_price=parse_float(row.get('今开')),
                prev_close=parse_float(row.get('昨收'))
            )
        except Exception as e:
            raise ValueError(f"获取股票数据失败: {str(e)}")

    async def get_stock_with_name(self, stock_code: str) -> Dict[str, Any]:
        """Get stock data with name."""
        info = await self.get_stock_info(stock_code)
        data = await self.get_stock_data(stock_code)

        return {
            "code": info["code"],
            "name": info["name"],
            "data": data
        }


akshare_service = AkShareService()
