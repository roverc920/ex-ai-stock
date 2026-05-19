import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Eye } from "lucide-react";
import type { HistoryItem } from "../services/api";
import { getHistory } from "../services/api";

const sentimentLabels: Record<string, string> = {
  Bullish: "看涨",
  Neutral: "中性",
  Bearish: "看跌",
};

const riskLabels: Record<string, string> = {
  Low: "低",
  Medium: "中",
  High: "高",
};

const sentimentColors: Record<string, string> = {
  Bullish: "text-green-600 bg-green-50",
  Neutral: "text-yellow-600 bg-yellow-50",
  Bearish: "text-red-600 bg-red-50",
};

export function History() {
  const navigate = useNavigate();
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      setLoading(true);
      const data = await getHistory(1, 50);
      setItems(data.items);
    } catch (err) {
      setError("加载历史记录失败");
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetail = (id: string) => {
    navigate(`/history/${id}`);
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8 text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-600">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">历史分析记录</h1>

      {items.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <p>暂无分析记录</p>
          <p className="text-sm mt-2">快去分析第一只股票吧！</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-500">
                  股票
                </th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-500">
                  情绪
                </th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-500">
                  风险等级
                </th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-500">
                  分析时间
                </th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-500">
                  操作
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {items.map((item) => (
                <tr key={item.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="font-medium text-gray-900">
                      {item.stock_name}
                    </div>
                    <div className="text-sm text-gray-500">
                      {item.stock_code}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`inline-block px-2 py-1 rounded text-sm ${
                        sentimentColors[item.sentiment] || "text-gray-600 bg-gray-50"
                      }`}
                    >
                      {sentimentLabels[item.sentiment] || item.sentiment}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`text-sm ${
                        item.risk_level === "Low"
                          ? "text-green-600"
                          : item.risk_level === "High"
                          ? "text-red-600"
                          : "text-yellow-600"
                      }`}
                    >
                      {riskLabels[item.risk_level] || item.risk_level}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {new Date(item.created_at).toLocaleString()}
                  </td>
                  <td className="px-6 py-4">
                    <button
                      onClick={() => handleViewDetail(item.id)}
                      className="flex items-center gap-1 text-blue-600 hover:text-blue-800 transition-colors"
                      title="查看详情"
                    >
                      <Eye size={18} />
                      <span className="text-sm">查看</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
