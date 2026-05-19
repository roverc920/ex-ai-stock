import { useState } from "react";

interface StockInputProps {
  onSubmit: (code: string) => void;
  loading?: boolean;
}

export function StockInput({ onSubmit, loading }: StockInputProps) {
  const [code, setCode] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // Validate stock code (support multi-market)
    const trimmedCode = code.trim().toUpperCase();
    if (!trimmedCode) {
      setError("请输入股票代码");
      return;
    }

    // Remove prefix for validation
    const cleanCode = trimmedCode.replace(/^(SH|SZ|HK|US)/, "");
    if (!/^[A-Z0-9]+$/.test(cleanCode)) {
      setError("股票代码只能包含数字或字母");
      return;
    }
    if (cleanCode.length < 1 || cleanCode.length > 6) {
      setError("股票代码长度应为 1-6 位");
      return;
    }

    onSubmit(trimmedCode);
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-md mx-auto">
      <div className="flex gap-2">
        <input
          type="text"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder="600000 / usAAPL / hk00700"
          maxLength={10}
          disabled={loading}
          className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
        />
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? "分析中..." : "AI分析"}
        </button>
      </div>
      {error && <p className="mt-2 text-red-600 text-sm">{error}</p>}
      <p className="mt-2 text-gray-500 text-xs">
        支持 A股(600000)、港股(hk00700)、美股(usAAPL)
      </p>
    </form>
  );
}
