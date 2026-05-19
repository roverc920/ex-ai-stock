# AI Stock Analyzer

基于 LLM 的 A 股股票分析全栈应用，输入股票代码即可获取 AI 智能分析、风险评估和情绪指标。

**在线访问**: https://stock-analyzer-web-8hqf.onrender.com

---

## 技术栈

### 前端
- **React 18** + **TypeScript** - 组件化开发
- **Vite** - 构建工具
- **Tailwind CSS** - 样式框架
- **Lucide React** - 图标库

### 后端
- **FastAPI** - Python 异步 Web 框架
- **Pydantic** - 数据验证
- **httpx** - 异步 HTTP 客户端

### 数据源
- **腾讯股票 API** - A 股实时数据（替代 AkShare，解决国内网络问题）

### AI 模型
- **DeepSeek API** - 国产大模型分析股票数据

### 存储
- **Supabase (PostgreSQL)** - 分析历史记录持久化
- **Redis (可选)** - 股票数据缓存

### 部署
- **Render** - 全托管部署（Web Service + Static Site）
- **GitHub Actions** - CI/CD 自动部署

---

## 部署架构

```
┌─────────────────────────────────────────────────────────────┐
│                        用户浏览器                           │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     Render 静态站点                          │
│            stock-analyzer-web-8hqf.onrender.com             │
│                   (React + Vite 构建)                        │
└───────────────────────────┬─────────────────────────────────┘
                            │ API 请求
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     Render Web Service                       │
│             stock-analyzer-api-hr0b.onrender.com            │
│                     (FastAPI 后端)                          │
└───────┬───────────────────┬───────────────────┬─────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌──────────────┐   ┌──────────────┐
│  腾讯股票 API  │   │ DeepSeek API │   │   Supabase   │
│ (实时股票数据) │   │ (AI 分析)    │   │(PostgreSQL)  │
└───────────────┘   └──────────────┘   └──────────────┘
```

---

## 项目结构

```
ex-ai-stock/
├── frontend/          # React 前端
│   ├── src/
│   │   ├── components/     # UI 组件
│   │   ├── services/       # API 调用
│   │   └── types/          # TypeScript 类型
│   └── package.json
├── backend/           # FastAPI 后端
│   ├── app/
│   │   ├── routers/        # API 路由
│   │   ├── services/       # 业务逻辑
│   │   │   ├── llm_service.py      # DeepSeek AI 调用
│   │   │   ├── stock_service.py    # 腾讯股票 API
│   │   │   └── supabase_service.py # 数据库操作
│   │   ├── models/         # Pydantic 模型
│   │   └── main.py         # 应用入口
│   └── requirements.txt
├── render.yaml        # Render 部署配置
├── deploy.sh          # 部署脚本
└── docs/              # 设计文档
    └── design.md      # 系统设计文档
```

---

## LLM Prompt 设计

核心技巧：通过 System Prompt 强制 LLM 只输出 JSON，杜绝无关内容。

```python
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
```

同时配合 API 参数强制 JSON 输出：

```python
payload = {
    "model": "deepseek-chat",
    "messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ],
    "response_format": {"type": "json_object"},  # 强制 JSON 输出
    "temperature": 0.3,  # 降低随机性
    "max_tokens": 1000
}
```

---

## DEBUG 记录

### Issue 1: AkShare 股票数据获取失败（ProxyError）

**现象**: `HTTPSConnectionPool(host='github.com', port=443): Max retries exceeded with url: /akfamily/akshare/tarball/main`

**原因**: AkShare 依赖 GitHub 下载数据，国内网络环境不稳定。

**解决**: 替换为 **腾讯股票 API**，直接访问无需代理：
```python
url = f"https://qt.gtimg.cn/q=sh{stock_code}"
response = await client.get(url)
```

---

### Issue 2: 腾讯 API 字段映射错误

**现象**: 返回的 PE 比率、市值等字段为空。

**原因**: 字段索引对应错误。

**解决**: 通过实际 API 响应分析，修正字段映射：
```python
# 正确的字段映射
stock_name = fields[1]          # 股票名称
current_price = fields[3]       # 当前价格
change_percent = fields[32]     # 涨跌幅
pe_ratio = fields[39]           # 市盈率（原为 38）
market_cap_yi = fields[45]      # 总市值（原为 44）
```

---

### Issue 3: Render Blueprint "unknown type 'static'"

**现象**: Blueprint 同步失败，报错 `unknown type 'static'`。

**原因**: Render Blueprint 语法错误。

**解决**: `type: static` 需要改为 `type: web` + `runtime: static`：
```yaml
services:
  - type: web
    name: stock-analyzer-web
    runtime: static  # 正确写法
```

---

### Issue 4: 503 错误 / "Failed to fetch"

**现象**: 前端显示 "Failed to fetch"，浏览器控制台显示 503。

**原因**:
1. 后端服务未启动（Suspended 状态）
2. CORS 配置错误，前端域名不在允许列表中

**解决**:
1. 在 Render Dashboard 手动 Resume 服务
2. 配置正确的 `CORS_ORIGINS` 环境变量：
   ```
   https://stock-analyzer-web-8hqf.onrender.com,http://localhost:5173
   ```

---

### Issue 5: Supabase 数据无法保存

**现象**: 分析成功但历史记录为空，日志显示 `Supabase not available`。

**原因**: `SUPABASE_KEY` 使用了错误的 key 类型。

**排查过程**:
1. 检查 Render 环境变量，发现 `SUPABASE_KEY=sb_publishable_xxx`
2. 确认后端代码使用 `supabase-py` 客户端，需要 `anon public` key
3. `publishable` key 是浏览器客户端用的，`anon` key 才是服务端 API 用的

**解决**: 将 `SUPABASE_KEY` 替换为 **anon public** key（以 `eyJ` 开头）。

**关键区别**:

| Key 类型 | 用途 | 格式 |
|---------|------|------|
| `publishable` | 浏览器客户端直连 Supabase | `sb_publishable_...` |
| `anon public` | 服务端通过 REST API 访问 | `eyJ...` |
| `service_role` | 管理员权限（可绕过 RLS） | `eyJ...` |

---

## 部署指南

### 环境变量配置

**后端服务 (stock-analyzer-api)**:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJ...  # anon public key
DEEPSEEK_API_KEY=sk-...
CORS_ORIGINS=https://your-frontend.onrender.com,http://localhost:5173
```

**前端服务 (stock-analyzer-web)**:
```
VITE_API_BASE_URL=https://your-backend.onrender.com
```

### 数据库初始化

在 Supabase SQL Editor 执行：
```sql
CREATE TABLE IF NOT EXISTS stock_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stock_code VARCHAR(10) NOT NULL,
    stock_name VARCHAR(50) NOT NULL,
    raw_data JSONB NOT NULL,
    analysis JSONB NOT NULL,
    sentiment VARCHAR(20) NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_stock_analyses_code ON stock_analyses(stock_code);
CREATE INDEX idx_stock_analyses_created_at ON stock_analyses(created_at DESC);
```

---

## 本地开发

```bash
# 启动后端
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# 启动前端
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

---

## 项目地址

- **GitHub**: https://github.com/roverc920/ex-ai-stock
- **前端**: https://stock-analyzer-web-8hqf.onrender.com
- **后端 API**: https://stock-analyzer-api-hr0b.onrender.com
- **API 文档**: https://stock-analyzer-api-hr0b.onrender.com/docs
