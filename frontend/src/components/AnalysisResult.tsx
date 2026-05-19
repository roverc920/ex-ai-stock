import type { StockResponse } from "../services/api";

interface AnalysisResultProps {
  result: StockResponse;
}

const sentimentColors = {
  Bullish: "bg-green-100 text-green-800 border-green-200",
  Neutral: "bg-yellow-100 text-yellow-800 border-yellow-200",
  Bearish: "bg-red-100 text-red-800 border-red-200",
};

const riskLevelColors = {
  Low: "text-green-600",
  Medium: "text-yellow-600",
  High: "text-red-600",
};

function formatNumber(num: number | undefined): string {
  if (num === undefined || num === null) return "N/A";
  if (num >= 100000000) {
    return (num / 100000000).toFixed(2) + "亿";
  }
  if (num >= 10000) {
    return (num / 10000).toFixed(2) + "万";
  }
  return num.toLocaleString();
}

export function AnalysisResultCard({ result }: AnalysisResultProps) {
  const { stock_name, stock_code, raw_data, analysis, created_at } = result;

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 mt-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            {stock_name} ({stock_code})
          </h2>
          <p className="text-sm text-gray-500">
            分析时间：{new Date(created_at).toLocaleString()}
          </p>
        </div>
        <span
          className={`px-3 py-1 rounded-full text-sm font-medium border ${
            sentimentColors[analysis.sentiment]
          }`}
        >
          {analysis.sentiment === "Bullish"
            ? "看涨"
            : analysis.sentiment === "Bearish"
            ? "看跌"
            : "中性"}
        </span>
      </div>

      {/* Stock Data */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
        <div>
          <p className="text-sm text-gray-500">当前价格</p>
          <p className="text-lg font-semibold">{raw_data.current_price.toFixed(2)}</p>
        </div>
        <div>
          <p className="text-sm text-gray-500">涨跌幅</p>
          <p
            className={`text-lg font-semibold ${
              raw_data.change_percent >= 0 ? "text-red-600" : "text-green-600"
            }`}
          >
            {raw_data.change_percent >= 0 ? "+" : ""}
            {raw_data.change_percent.toFixed(2)}%
          </p>
        </div>
        <div>
          <p className="text-sm text-gray-500">成交量</p>
          <p className="text-lg font-semibold">{formatNumber(raw_data.volume)}</p>
        </div>
        <div>
          <p className="text-sm text-gray-500">市值</p>
          <p className="text-lg font-semibold">{formatNumber(raw_data.market_cap)}</p>
        </div>
        {raw_data.pe_ratio && (
          <div>
            <p className="text-sm text-gray-500">市盈率</p>
            <p className="text-lg font-semibold">{raw_data.pe_ratio.toFixed(2)}</p>
          </div>
        )}
        {raw_data.pb_ratio && (
          <div>
            <p className="text-sm text-gray-500">市净率</p>
            <p className="text-lg font-semibold">{raw_data.pb_ratio.toFixed(2)}</p>
          </div>
        )}
      </div>

      {/* AI Analysis */}
      <div className="space-y-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">AI分析总结</h3>
          <p className="text-gray-700 leading-relaxed">{analysis.summary}</p>
        </div>

        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            风险评估
            <span className={`ml-2 ${riskLevelColors[analysis.risk.level]}`}>
              ({analysis.risk.level === "Low" ? "低" : analysis.risk.level === "Medium" ? "中" : "高"})
            </span>
          </h3>
          <ul className="list-disc list-inside space-y-1">
            {analysis.risk.factors.map((factor, index) => (
              <li key={index} className="text-gray-700">
                {factor}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
