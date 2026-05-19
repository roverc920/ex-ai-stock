const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export interface StockData {
  current_price: number;
  change_percent: number;
  volume: number;
  turnover: number;
  pe_ratio?: number;
  pb_ratio?: number;
  market_cap?: number;
  high_price?: number;
  low_price?: number;
  open_price?: number;
  prev_close?: number;
}

export interface RiskAnalysis {
  level: "Low" | "Medium" | "High";
  factors: string[];
}

export interface AnalysisResult {
  summary: string;
  sentiment: "Bullish" | "Neutral" | "Bearish";
  risk: RiskAnalysis;
}

export interface StockResponse {
  id: string;
  stock_code: string;
  stock_name: string;
  raw_data: StockData;
  analysis: AnalysisResult;
  created_at: string;
}

export interface HistoryItem {
  id: string;
  stock_code: string;
  stock_name: string;
  sentiment: string;
  risk_level: string;
  created_at: string;
}

export interface HistoryResponse {
  items: HistoryItem[];
  total: number;
  page: number;
  page_size: number;
}

export async function analyzeStock(stockCode: string): Promise<StockResponse> {
  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ stock_code: stockCode }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail?.message || "分析失败");
  }

  return response.json();
}

export async function getHistory(page = 1, pageSize = 20): Promise<HistoryResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/history?page=${page}&page_size=${pageSize}`
  );

  if (!response.ok) {
    throw new Error("获取历史记录失败");
  }

  return response.json();
}

export async function getStockData(stockCode: string): Promise<{
  stock_code: string;
  stock_name: string;
  data: StockData;
}> {
  const response = await fetch(`${API_BASE_URL}/api/stock/${stockCode}`);

  if (!response.ok) {
    throw new Error("获取股票数据失败");
  }

  return response.json();
}
