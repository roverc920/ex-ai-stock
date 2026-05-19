import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import type { StockResponse } from "../services/api";
import { getAnalysisById } from "../services/api";
import { AnalysisResultCard } from "../components/AnalysisResult";

export function HistoryDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [result, setResult] = useState<StockResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (id) {
      loadDetail(id);
    }
  }, [id]);

  const loadDetail = async (analysisId: string) => {
    try {
      setLoading(true);
      setError("");
      const data = await getAnalysisById(analysisId);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "获取详情失败");
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    navigate("/history");
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 py-8">
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-500">加载中...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !result) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 py-8">
          <button
            onClick={handleBack}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6"
          >
            <ArrowLeft size={20} />
            返回历史列表
          </button>

          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-600">{error || "记录不存在"}</p>
            <button
              onClick={() => id && loadDetail(id)}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              重试
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <button
          onClick={handleBack}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6"
        >
          <ArrowLeft size={20} />
          返回历史列表
        </button>

        <AnalysisResultCard result={result} />
      </div>
    </div>
  );
}
