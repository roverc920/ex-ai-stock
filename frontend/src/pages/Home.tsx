import { useState } from "react";
import { StockInput } from "../components/StockInput";
import { AnalysisResultCard } from "../components/AnalysisResult";
import type { StockResponse } from "../services/api";
import { analyzeStock } from "../services/api";

export function Home() {
  const [result, setResult] = useState<StockResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleAnalyze = async (code: string) => {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const data = await analyzeStock(code);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "分析失败，请重试");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">AI 股票分析</h1>
        <p className="text-gray-600">输入A股代码，获取AI智能分析</p>
      </div>

      <StockInput onSubmit={handleAnalyze} loading={loading} />

      {loading && (
        <div className="mt-8 text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-500">正在分析，请稍候...</p>
        </div>
      )}

      {error && (
        <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      {result && <AnalysisResultCard result={result} />}
    </div>
  );
}
