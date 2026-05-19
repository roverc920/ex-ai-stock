# AI Stock Analyzer

基于 LLM 的股票分析全栈应用

## 技术栈
- 前端: React + Vite
- 后端: Python FastAPI
- 数据源: AkShare (A股)
- AI: DeepSeek API
- 存储: Supabase + Upstash Redis
- 部署: Render

## 项目结构
```
├── frontend/     # React 前端
├── backend/      # FastAPI 后端
└── docs/         # 设计文档
```

## 部署常见问题

### 1. Supabase 连接失败（数据无法保存）

**现象**：后端日志显示 `Supabase not available`，分析结果无法存入数据库。

**原因**：`SUPABASE_KEY` 环境变量使用了错误的 key 类型。

**排查过程**：
1. 查看 Render 后端日志，发现 `Supabase not available` 提示
2. 检查环境变量配置，发现 `SUPABASE_KEY` 用的是 `sb_publishable_xxx`（publishable key）
3. 实际上 `supabase-py` 客户端需要通过 REST API 访问数据库，应该使用 `anon public` key

**解决方案**：
- 在 Supabase Dashboard → Project Settings → Data API 中找到 **anon public** key（以 `eyJ` 开头）
- 替换 Render 环境变量中的 `SUPABASE_KEY`
- 重新部署服务

**关键区别**：
| Key 类型 | 用途 | 格式 |
|---------|------|------|
| `publishable` | 浏览器客户端直连 | `sb_publishable_...` |
| `anon public` | 服务端 API 调用 | `eyJ...` |
| `service_role` | 管理员权限 | `eyJ...` |

### 2. CORS 跨域错误

**现象**：前端调用 API 时浏览器报 CORS 错误。

**正确解决方案**：
1. 访问 Render Dashboard → 后端服务 → Environment
2. 添加环境变量 `CORS_ORIGINS`，值为前端实际域名，例如：
   ```
   https://stock-analyzer-web-8hqf.onrender.com,http://localhost:5173
   ```
3. 重新部署服务

**注意**：不要使用 `*`，这会带来安全风险。应该明确指定允许的前端域名。

