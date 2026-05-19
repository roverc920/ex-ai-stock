"""DeepSeek LLM service for stock analysis."""
import json
import httpx
from typing import Dict, Any, Optional
from app.config import settings
from app.models.schemas import AnalysisResult, RiskAnalysis


class LLMService:
    """Service for DeepSeek LLM analysis."""

    SYSTEM_PROMPT = """你是一位专业的A股股票分析师。请基于提供的股票数据，给出专业的投资分析。

必须严格按照以下JSON格式返回，不要包含任何其他内容：

{
  "summary": "对股票的综合分析总结，200字以内",
  "sentiment": "Bullish | Neutral | Bearish",
  "risk": {
    "level": "Low | Medium | High",
    "factors": ["风险因素1", "风险因素2", "风险因素3"]
  }
}

分析要求：
1. sentiment只能三选一，基于技术面和基本面综合判断
2. risk.level也是三选一，考虑行业风险、估值风险、市场风险
3. risk.factors列出3-5个主要风险点
4. summary要客观，包含具体数据支撑
5. 不要输出JSON以外的任何内容，包括markdown代码块标记"""

    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.api_url = settings.DEEPSEEK_API_URL
        self.model = settings.DEEPSEEK_MODEL

    def _build_user_prompt(
        self,
        stock_code: str,
        stock_name: str,
        stock_data: Dict[str, Any]
    ) -> str:
        """Build user prompt with stock data."""
        return f"""请分析以下股票数据：

股票代码：{stock_code}
股票名称：{stock_name}
当前价格：{stock_data.get('current_price', 'N/A')}元
涨跌幅：{stock_data.get('change_percent', 'N/A')}%
成交量：{stock_data.get('volume', 'N/A')}股
成交额：{stock_data.get('turnover', 'N/A')}元
市盈率：{stock_data.get('pe_ratio', 'N/A')}倍
市净率：{stock_data.get('pb_ratio', 'N/A')}倍
总市值：{stock_data.get('market_cap', 'N/A')}元
最高价：{stock_data.get('high_price', 'N/A')}元
最低价：{stock_data.get('low_price', 'N/A')}元
今开价：{stock_data.get('open_price', 'N/A')}元
昨收价：{stock_data.get('prev_close', 'N/A')}元"""

    async def analyze_stock(
        self,
        stock_code: str,
        stock_name: str,
        stock_data: Dict[str, Any]
    ) -> AnalysisResult:
        """Analyze stock using DeepSeek LLM."""
        user_prompt = self._build_user_prompt(stock_code, stock_name, stock_data)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.3,
            "max_tokens": 1000
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self.api_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()

                result = response.json()
                content = result["choices"][0]["message"]["content"]

                # Parse JSON response
                analysis_data = json.loads(content)

                # Validate and construct AnalysisResult
                return AnalysisResult(
                    summary=analysis_data.get("summary", ""),
                    sentiment=analysis_data.get("sentiment", "Neutral"),
                    risk=RiskAnalysis(
                        level=analysis_data.get("risk", {}).get("level", "Medium"),
                        factors=analysis_data.get("risk", {}).get("factors", [])
                    )
                )

            except httpx.HTTPStatusError as e:
                raise ValueError(f"DeepSeek API error: {e.response.status_code} - {e.response.text}")
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse LLM response: {str(e)}")
            except Exception as e:
                raise ValueError(f"Analysis failed: {str(e)}")


llm_service = LLMService()
