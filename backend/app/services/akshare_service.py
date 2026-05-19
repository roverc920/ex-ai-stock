"""AkShare service for A-share stock data."""
import akshare as ak
from typing import Dict, Any, Optional
from app.models.schemas import StockData


class AkShareService:
    """Service for fetching stock data from AkShare."""

    async def get_stock_info(self, stock_code: str) -> Dict[str, Any]:
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
