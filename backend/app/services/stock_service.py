"""Stock data service using Tencent API."""
import httpx
from typing import Dict, Any
from app.models.schemas import StockData


class StockService:
    """Service for fetching stock data from Tencent API."""

    def _get_market_prefix(self, stock_code: str) -> str:
        """Determine market prefix based on stock code."""
        if stock_code.startswith('6'):
            return "sh"
        else:
            return "sz"

    async def get_stock_data(self, stock_code: str) -> Dict[str, Any]:
        """Get real-time stock data from Tencent API."""
        market = self._get_market_prefix(stock_code)
        symbol = f"{market}{stock_code}"

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
                data_part = content.split('="')[1].strip('"')
                fields = data_part.split('~')

                if len(fields) < 50:
                    raise ValueError(f"股票数据不完整: {stock_code}")

                # Field mapping (verified)
                # [1] 股票名称, [2] 代码, [3] 当前价, [4] 昨收, [5] 今开
                # [6] 成交量(手), [32] 涨跌幅%, [33] 最高, [34] 最低
                # [37] 成交额(万), [38] 换手率, [39] 市盈率
                # [44] 流通市值(亿), [45] 总市值(亿), [46] 市净率

                stock_name = fields[1]
                current_price = float(fields[3]) if fields[3] else 0.0
                prev_close = float(fields[4]) if fields[4] else 0.0
                open_price = float(fields[5]) if fields[5] else 0.0

                # Volume (convert from 手 to shares, 1手=100股)
                volume_hand = int(fields[6]) if fields[6] else 0
                volume = volume_hand * 100

                change_percent = float(fields[32]) if fields[32] else 0.0
                high_price = float(fields[33]) if fields[33] else 0.0
                low_price = float(fields[34]) if fields[34] else 0.0

                # Turnover (fields[37] is in 万)
                turnover_wan = float(fields[37]) if fields[37] else 0.0
                turnover = turnover_wan * 10000

                # PE ratio
                pe_ratio = float(fields[39]) if fields[39] and fields[39] != '-' else None

                # Market cap (fields[45] is in 亿)
                market_cap_yi = float(fields[45]) if fields[45] else 0.0
                market_cap = market_cap_yi * 100000000

                # PB ratio
                pb_ratio = float(fields[46]) if fields[46] and fields[46] != '-' else None

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
                    "code": stock_code,
                    "name": stock_name,
                    "data": stock_data
                }

            except httpx.HTTPStatusError as e:
                raise ValueError(f"HTTP错误: {e.response.status_code}")
            except Exception as e:
                raise ValueError(f"获取股票数据失败: {str(e)}")


stock_service = StockService()
