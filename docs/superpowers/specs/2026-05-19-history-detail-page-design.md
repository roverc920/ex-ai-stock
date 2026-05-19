# 历史分析详情页设计文档

**日期**: 2026-05-19
**功能**: 历史分析记录详情查看
**状态**: 待实现

---

## 1. 功能概述

在历史记录列表页增加"查看详情"功能，点击后跳转到独立详情页面，展示完整的 AI 分析结果（包括 summary、风险因素、原始股票数据等）。

**在线访问**: https://stock-analyzer-web-8hqf.onrender.com

---

## 2. 设计决策

### 2.1 技术选型

| 决策项 | 选择 | 理由 |
|--------|------|------|
| 路由方案 | React Router | 支持页面刷新、URL 分享、浏览器前进后退 |
| 详情获取 | 新增专用 API | 历史列表保持轻量，详情按需加载完整数据 |
| 页面布局 | 复用 AnalysisResult 组件 | UI 统一，开发效率高 |

### 2.2 路由设计

```
/                    → 首页（分析页面）
/history             → 历史记录列表
/history/:id         → 历史记录详情页（新增）
```

---

## 3. 后端 API 设计

### 3.1 新增端点

```http
GET /api/analysis/{analysis_id}
```

**响应格式**: `StockResponse`

```json
{
  "id": "uuid-string",
  "stock_code": "000002",
  "stock_name": "万科A",
  "raw_data": {
    "current_price": 15.32,
    "change_percent": -1.23,
    "volume": 1234567,
    "turnover": 18923456.78,
    "pe_ratio": 8.5,
    "pb_ratio": 0.6,
    "market_cap": 178500000000
  },
  "analysis": {
    "summary": "AI分析总结文本...",
    "sentiment": "Bearish",
    "risk": {
      "level": "High",
      "factors": ["房地产行业下行风险", "负债率较高", "市场需求疲软"]
    }
  },
  "created_at": "2026-05-19T10:30:00Z"
}
```

**错误响应**:
- `404`: 分析记录不存在
- `500`: 服务器内部错误

### 3.2 后端实现

复用现有的 `supabase_service.get_analysis_by_id()` 方法，该方法的返回格式与需求一致。

---

## 4. 前端架构设计

### 4.1 组件结构

```
App.tsx (Router 包裹)
├── / (Home Tab)
│   └── Home.tsx
├── /history (History Tab)
│   └── History.tsx (列表页)
└── /history/:id (详情路由)
    └── HistoryDetail.tsx (新增)
        └── AnalysisResultCard (复用现有组件)
```

### 4.2 路由配置

```tsx
<BrowserRouter>
  <Routes>
    <Route path="/" element={<Layout />}>  {/* Layout 包含导航 Tab */}
      <Route index element={<Home />} />
      <Route path="history" element={<History />} />
    </Route>
    <Route path="/history/:id" element={<HistoryDetail />} />  {/* 独立路由，无 Tab */}
  </Routes>
</BrowserRouter>
```

### 4.3 API 客户端新增

`frontend/src/services/api.ts` 新增：

```typescript
export async function getAnalysisById(id: string): Promise<StockResponse> {
  const response = await fetch(`${API_BASE_URL}/api/analysis/${id}`);
  if (!response.ok) {
    throw new Error("获取分析详情失败");
  }
  return response.json();
}
```

### 4.4 交互流程

```
1. 用户在历史列表页点击"查看详情"
   ↓
2. 导航到 /history/:id
   ↓
3. HistoryDetail 组件加载，显示 Loading
   ↓
4. 调用 GET /api/analysis/:id 获取完整数据
   ↓
5. 使用 AnalysisResultCard 渲染详情
   ↓
6. 用户点击"返回"按钮回到 /history
```

---

## 5. 风险点与解决方案

### 风险 #1: 后端 API 安全性

| 项目 | 内容 |
|------|------|
| 风险 | 新 API 可能暴露未授权数据 |
| 评估 | 当前系统无用户认证，所有分析公开。UUID 难以猜测，风险可控 |
| 缓解 | 如需用户系统，后续增加权限校验 |

### 风险 #2: 前端路由兼容性

| 项目 | 内容 |
|------|------|
| 风险 | Tab 切换与 Router 整合不当导致导航失效 |
| 缓解 | 使用嵌套路由，Layout 组件控制 Tab 高亮状态 |
| 实现 | 通过 `useLocation` 检测当前路径，同步到 `activeTab` |

### 风险 #3: 数据获取失败

| 项目 | 内容 |
|------|------|
| 风险 | API 调用失败（记录不存在、网络错误） |
| 缓解 | HistoryDetail 组件需实现：
|      | - Loading 状态（加载动画） |
|      | - Error 状态（错误提示 + 重试按钮） |
|      | - 404 处理（记录不存在提示） |

### 风险 #4: 浏览器前进后退

| 项目 | 内容 |
|------|------|
| 风险 | 从详情页返回列表页时丢失滚动位置或数据 |
| 评估 | 当前数据量小，重新加载可接受 |
| 缓解 | 如需优化，后续可用 React Router state 或缓存 |

### 风险 #5: 部署后路由刷新 404 ⚠️ **关键风险**

| 项目 | 内容 |
|------|------|
| 风险 | 刷新 `/history/xxx` 时，Render 静态站点返回 404 |
| 原因 | React Router 使用 History API，服务器需要配置 fallback |
| 缓解 | **render.yaml 需要配置重定向规则** |

**render.yaml 配置**:

```yaml
routes:
  - type: rewrite
    source: /history/*
    destination: /index.html
  - type: rewrite
    source: /*
    destination: /index.html
```

或在 buildCommand 中生成 `_redirects` 文件：

```bash
echo '/* /index.html 200' > dist/_redirects
```

---

## 6. 文件变更清单

### 新增文件
- `frontend/src/pages/HistoryDetail.tsx` - 详情页组件
- `backend/app/routers/analysis.py` - 新增查询详情路由（或在现有 router 中添加）

### 修改文件
- `frontend/package.json` - 添加 react-router-dom 依赖
- `frontend/src/App.tsx` - 引入 Router，重构路由结构
- `frontend/src/main.tsx` - 包裹 BrowserRouter
- `frontend/src/pages/History.tsx` - 添加"查看详情"链接/按钮
- `frontend/src/services/api.ts` - 添加 `getAnalysisById` 方法
- `backend/app/routers/history.py` - 添加 `GET /api/analysis/{id}` 端点
- `render.yaml` - 添加 SPA fallback 路由配置

---

## 7. UI/UX 设计

### 7.1 历史列表页变更

在现有表格每行增加操作列：

```
| 股票    | 情绪 | 风险 | 时间      | 操作        |
|---------|------|------|-----------|-------------|
| 万科A   | 看跌 | 高   | 2026-5-19 | [查看详情 →] |
```

点击"查看详情"跳转到详情页。

### 7.2 详情页布局

```
┌──────────────────────────────────────────────┐
│  ← 返回历史列表                               │
├──────────────────────────────────────────────┤
│                                              │
│  ┌──────────────────────────────────────────┐│
│  │  万科A (000002)          [看跌]          ││  ← 复用 AnalysisResultCard
│  │  分析时间: 2026-05-19 10:30              ││
│  ├──────────────────────────────────────────┤│
│  │  当前价格: 15.32    涨跌幅: -1.23%       ││
│  │  ... (原始数据)                          ││
│  ├──────────────────────────────────────────┤│
│  │  AI分析总结                              ││
│  │  xxxxxxxxxx...                           ││
│  ├──────────────────────────────────────────┤│
│  │  风险评估 (高)                           ││
│  │  - 房地产行业下行风险                    ││
│  │  - 负债率较高                            ││
│  │  - 市场需求疲软                          ││
│  └──────────────────────────────────────────┘│
│                                              │
└──────────────────────────────────────────────┘
```

---

## 8. 测试要点

1. **功能测试**
   - 历史列表点击"查看详情"正确跳转
   - 详情页正确显示完整分析数据
   - 返回按钮正常工作

2. **异常测试**
   - 不存在的 analysis_id 显示 404 提示
   - 网络错误显示重试按钮
   - 刷新详情页不 404

3. **兼容性测试**
   - Tab 切换在首页/历史页正常工作
   - 详情页 URL 可直接访问
   - 浏览器前进后退正常

---

## 9. 后续优化（可选）

- [ ] 历史列表页缓存，返回时不重新加载
- [ ] 详情页分享功能（复制链接）
- [ ] 删除历史记录功能
- [ ] 分页加载（历史记录多时）

---

**设计确认**: 待用户审批
**下一步**: 用户审批后，创建详细实现计划
