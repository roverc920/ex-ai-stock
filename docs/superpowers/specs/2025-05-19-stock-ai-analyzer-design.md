# AI 股票分析应用设计文档

**日期:** 2025-05-19
**版本:** v1.0
**状态:** 待实现

---

## 1. 项目概述

构建一个全栈应用，用户输入股票代码后，获取A股实时行情数据，调用DeepSeek LLM进行AI分析，并将结果存储到Supabase。

### 1.1 核心功能

1. **数据获取**: 用户输入股票代码，调用AkShare获取A股行情
2. **AI分析**: 调用DeepSeek API分析数据，返回严格JSON格式
3. **数据存储**: 原始数据和分析结果存入Supabase
4. **历史记录**: 展示过往分析记录

### 1.2 技术栈

| 层级 | 技术 | 部署方式 |
|------|------|----------|
| 前端 | React + Vite | Render Static Site (免费) |
| 后端 | Python + FastAPI | Render Web Service (免费) |
| 数据库 | Supabase PostgreSQL | 免费额度 |
| 缓存 | Upstash Redis | Serverless 免费版 |
| AI | DeepSeek API | 按量付费 |

---

## 2. 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                           用户浏览器                              │
└───────────────────────────────┬─────────────────────────────────┘
                                │ HTTPS
┌───────────────────────────────▼─────────────────────────────────┐
│                      React Frontend (Vite)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ 股票输入表单 │  │ 分析结果展示 │  │      历史记录列表        │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└───────────────────────────────┬─────────────────────────────────┘
                                │ fetch API
┌───────────────────────────────▼─────────────────────────────────┐
│                     FastAPI Backend (Python)                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  POST /api/analyze          │  GET  /api/history        │    │
│  │  POST /api/health           │  GET  /api/stock/:code    │    │
│  └─────────────────────────────────────────────────────────┘    │
│         │                              │                        │
│         ▼                              ▼                        │
│  ┌─────────────┐              ┌──────────────┐                  │
│  │   AkShare   │              │  DeepSeek API│                  │
│  │  (A股数据)   │              │  (AI分析)    │                  │
│  └─────────────┘              └──────────────┘                  │
│         │                              │                        │
│         └──────────────┬───────────────┘                        │
│                        ▼                                        │
│               ┌────────────────┐                                │
│               │  Upstash Redis │                                │
│               │  (数据缓存)     │                                │
│               └───────┬────────┘                                │
│                       │                                         │
│                       ▼                                         │
│               ┌────────────────┐                                │
│               │   Supabase     │                                │
│               │  (持久化存储)   │                                │
│               └────────────────┘                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. API设计

### 3.1 接口清单

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/analyze` | 分析股票（获取数据+AI分析+存储） |
| GET | `/api/stock/{code}` | 仅获取股票行情数据 |
| GET | `/api/history` | 获取历史分析记录 |
| GET | `/api/history/{id}` | 获取单条分析详情 |
| GET | `/health` | 健康检查（Render保活用） |

### 3.2 请求/响应格式

#### POST /api/analyze

**Request:**
```json
{
  "stock_code": "000001"
}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "stock_code": "000001",
  "stock_name": "平安银行",
  "raw_data": {
    "current_price": 10.52,
    "change_percent": 1.25,
    "volume": 152345678,
    "turnover": 1601234567.89,
    "pe_ratio": 4.85,
    "pb_ratio": 0.58,
    "market_cap": 204500000000
  },
  "analysis": {
    "summary": "平安银行今日表现稳健，股价小幅上涨1.25%。从估值角度看，市盈率仅4.85倍，处于历史低位，具备一定的安全边际。成交量较近期平均水平有所放大，显示市场关注度提升。",
    "sentiment": "Bullish",
    "risk": {
      "level": "Medium",
      "factors": [
        "银行业整体受宏观经济影响较大",
        "房地产风险暴露可能拖累资产质量",
        "净息差持续收窄压力"
      ]
    }
  },
  "created_at": "2025-05-19T14:30:00Z"
}
```

**Error Response (400/500):**
```json
{
  "error": "invalid_stock_code",
  "message": "股票代码格式错误或股票不存在"
}
```

#### GET /api/history

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "stock_code": "000001",
      "stock_name": "平安银行",
      "sentiment": "Bullish",
      "risk_level": "Medium",
      "created_at": "2025-05-19T14:30:00Z"
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 20
}
```

---

## 4. 数据模型

### 4.1 Supabase 表结构

```sql
-- 股票分析记录表
CREATE TABLE stock_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stock_code VARCHAR(10) NOT NULL,
    stock_name VARCHAR(50) NOT NULL,
    raw_data JSONB NOT NULL,
    analysis JSONB NOT NULL,
    sentiment VARCHAR(20) NOT NULL CHECK (sentiment IN ('Bullish', 'Neutral', 'Bearish')),
    risk_level VARCHAR(20) NOT NULL CHECK (risk_level IN ('Low', 'Medium', 'High')),
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- 索引
    CONSTRAINT valid_stock_code CHECK (stock_code ~ '^[0-9]{6}$')
);

-- 索引
CREATE INDEX idx_stock_analyses_code ON stock_analyses(stock_code);
CREATE INDEX idx_stock_analyses_created_at ON stock_analyses(created_at DESC);
CREATE INDEX idx_stock_analyses_sentiment ON stock_analyses(sentiment);
```

### 4.2 Redis 缓存策略

| 缓存Key | 内容 | TTL | 说明 |
|---------|------|-----|------|
| `stock:{code}` | 行情数据 | 300s (5分钟) | 避免频繁调用AkShare |
| `analysis:{code}` | AI分析结果 | 3600s (1小时) | 相同股票短时间内不重复分析 |

---

## 5. LLM Prompt 设计

### 5.1 系统Prompt

```
你是一位专业的A股股票分析师。请基于提供的股票数据，给出专业的投资分析。

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
```

### 5.2 用户Prompt示例

```
请分析以下股票数据：

股票代码：000001
股票名称：平安银行
当前价格：10.52元
涨跌幅：+1.25%
成交量：1.52亿股
成交额：16.01亿元
市盈率：4.85倍
市净率：0.58倍
总市值：2045亿元

近期走势：近5日上涨3.2%，近20日下跌2.1%
```

---

## 6. 部署方案

### 6.1 Render 部署配置

#### 前端 (Static Site)

```yaml
# render.yaml (前端)
services:
  - type: static
    name: stock-analyzer-frontend
    runtime: static
    buildCommand: npm run build
    staticPublishPath: dist
    envVars:
      - key: VITE_API_BASE_URL
        value: https://stock-analyzer-api.onrender.com
```

#### 后端 (Web Service)

```yaml
# render.yaml (后端)
services:
  - type: web
    name: stock-analyzer-api
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_KEY
        sync: false
      - key: DEEPSEEK_API_KEY
        sync: false
      - key: REDIS_URL
        sync: false
```

### 6.2 环境变量清单

| 变量名 | 说明 | 获取方式 |
|--------|------|----------|
| `SUPABASE_URL` | Supabase项目URL | Supabase Console |
| `SUPABASE_KEY` | Supabase服务角色密钥 | Supabase Console |
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | DeepSeek开放平台 |
| `REDIS_URL` | Upstash Redis连接URL | Upstash Console |

### 6.3 免费版限制与应对

| 限制 | 影响 | 应对方案 |
|------|------|----------|
| Web Service 15分钟休眠 | 首次请求慢 | 前端显示"服务唤醒中"提示，30秒超时 |
| 冷启动5-10秒 | 用户体验差 | 可选：Cron-job.org定时ping保活 |
| 带宽限制 | 影响不大 | 响应数据量小，无问题 |

---

## 7. 项目结构

```
stock-analyzer/
├── frontend/                  # React + Vite 前端
│   ├── src/
│   │   ├── components/        # UI组件
│   │   ├── pages/             # 页面
│   │   ├── services/          # API调用
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                   # FastAPI 后端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI入口
│   │   ├── routers/           # API路由
│   │   ├── services/          # 业务逻辑
│   │   │   ├── akshare_service.py
│   │   │   ├── llm_service.py
│   │   │   ├── cache_service.py
│   │   │   └── supabase_service.py
│   │   └── models/            # Pydantic模型
│   ├── requirements.txt
│   └── render.yaml
│
├── docs/                      # 文档
│   └── superpowers/
│       └── specs/
│           └── 2025-05-19-stock-ai-analyzer-design.md
│
└── README.md
```

---

## 8. 风险与注意事项

### 8.1 已知风险

1. **AkShare稳定性**: 非官方API，可能随时变更或失效
2. **DeepSeek API**: 需要账户充值，新用户有免费额度
3. **A股数据延迟**: AkShare数据可能有15分钟延迟，非实时
4. **Render免费版休眠**: 影响用户体验，如需7x24建议升级

### 8.2 安全事项

1. **API Key保密**: DeepSeek key仅存储在Render环境变量，绝不提交到代码库
2. **Supabase RLS**: 生产环境启用Row Level Security
3. **CORS限制**: FastAPI配置只允许前端域名访问

---

## 9. 后续扩展建议

1. **用户系统**: 添加登录功能，保存个人分析历史
2. **推送通知**: 股票价格达到目标值时邮件/短信提醒
3. **批量分析**: 支持同时分析多只股票
4. **图表展示**: 集成echarts展示K线图和技术指标
5. **定时任务**: 每日自动分析自选股，推送简报

---

## 10. 验收标准

- [ ] 输入6位股票代码，能正确获取A股行情
- [ ] 点击分析按钮，5-15秒内返回AI分析结果
- [ ] AI返回结果严格符合JSON格式，包含summary/sentiment/risk
- [ ] 分析结果正确存储到Supabase
- [ ] 能查看历史分析记录列表
- [ ] 部署到Render后功能正常

---

**设计完成，等待实现。**
