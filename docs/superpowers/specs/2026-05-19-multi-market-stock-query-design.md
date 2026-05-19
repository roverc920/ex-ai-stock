# 多市场股票查询设计文档

**日期**: 2026-05-19
**功能**: 支持 A股、港股、美股多市场股票查询
**状态**: 待实现

---

## 1. 功能概述

扩展当前仅支持 A股 6位数字的查询功能，支持：
- A股（上海/深圳）- 6位数字
- 港股 - 5位数字 或 hk前缀
- 美股 - 字母代码 或 us前缀

---

## 2. 设计方案

### 2.1 用户输入格式

| 输入格式 | 识别市场 | 示例 | 说明 |
|---------|---------|------|------|
| `sh600000` | A股上海 | 浦发银行 | 明确前缀 |
| `sz000001` | A股深圳 | 平安银行 | 明确前缀 |
| `600000` | A股上海 | 浦发银行 | 6位数字，6开头→上海 |
| `000001` | A股深圳 | 平安银行 | 6位数字，0/3开头→深圳 |
| `hk00700` | 港股 | 腾讯控股 | 明确前缀 |
| `00700` | 港股 | 腾讯控股 | 5位数字→港股 |
| `usAAPL` | 美股 | 苹果 | 明确前缀 |
| `AAPL` | 美股 | 苹果 | 纯字母→美股 |

### 2.2 智能推断规则

```python
def detect_market(code: str) -> str:
    code = code.strip().upper()

    # 1. 检查是否带前缀
    if code.startswith('SH'):
        return 'sh', code[2:]
    if code.startswith('SZ'):
        return 'sz', code[2:]
    if code.startswith('HK'):
        return 'hk', code[2:]
    if code.startswith('US'):
        return 'us', code[2:]

    # 2. 纯数字判断
    if code.isdigit():
        if len(code) == 5:
            return 'hk', code  # 5位→港股
        elif len(code) == 6:
            if code.startswith(('600', '601', '603', '605', '688')):
                return 'sh', code  # 上海
            else:
                return 'sz', code  # 深圳（000/001/002/300开头）

    # 3. 纯字母→美股
    if code.isalpha():
        return 'us', code

    # 4. 无法识别
    raise ValueError(f'无法识别股票代码格式: {code}')
```

### 2.3 腾讯 API 调用格式

```python
# 构建腾讯 API 请求代码
def build_tencent_code(market: str, code: str) -> str:
    mapping = {
        'sh': f'sh{code}',
        'sz': f'sz{code}',
        'hk': f'hk{code}',
        'us': f'us{code}',
    }
    return mapping[market]
```

**API URL**: `https://qt.gtimg.cn/q={tencent_code}`

---

## 3. 后端变更

### 3.1 修改 Pydantic 验证

**文件**: `backend/app/models/schemas.py`

```python
class StockRequest(BaseModel):
    """Request to analyze a stock - supports multi-market."""
    stock_code: str = Field(..., min_length=1, max_length=10, description="股票代码")
    market: Optional[str] = Field(None, description="市场代码(sh/sz/hk/us)，可选，自动推断")

    @field_validator('stock_code')
    @classmethod
    def validate_stock_code(cls, v: str) -> str:
        v = v.strip().upper()
        if not v:
            raise ValueError('股票代码不能为空')
        # 移除前缀后验证
        clean_code = v.removeprefix('SH').removeprefix('SZ').removeprefix('HK').removeprefix('US')
        if not (clean_code.isdigit() or clean_code.isalpha()):
            raise ValueError('股票代码只能包含数字或字母')
        return v
```

### 3.2 新增市场检测服务

**文件**: `backend/app/services/market_detector.py`

```python
"""Market detection service for multi-market stock query."""

MARKET_NAMES = {
    'sh': '上海',
    'sz': '深圳',
    'hk': '香港',
    'us': '美国',
}

def detect_market(stock_code: str) -> tuple[str, str]:
    """
    Detect market type and return (market_code, clean_code).

    Returns:
        tuple: (market_code, clean_stock_code)

    Raises:
        ValueError: If cannot detect market
    """
    code = stock_code.strip().upper()

    # 前缀判断
    for prefix in ['SH', 'SZ', 'HK', 'US']:
        if code.startswith(prefix):
            return prefix.lower(), code[len(prefix):]

    # 纯数字
    if code.isdigit():
        if len(code) == 5:
            return 'hk', code
        elif len(code) == 6:
            # 上海: 600, 601, 603, 605, 688(科创板)
            if code.startswith(('600', '601', '603', '605', '688')):
                return 'sh', code
            # 深圳: 000, 001, 002(中小板), 300(创业板)
            else:
                return 'sz', code

    # 纯字母→美股
    if code.isalpha():
        return 'us', code

    raise ValueError(f'无法识别股票代码格式: {stock_code}，支持的格式：\n'
                     f'- A股: 600000 / sh600000 / sz000001\n'
                     f'- 港股: 00700 / hk00700\n'
                     f'- 美股: AAPL / usAAPL')

def get_market_name(market_code: str) -> str:
    """Get human-readable market name."""
    return MARKET_NAMES.get(market_code, '未知')

def build_tencent_api_code(market: str, code: str) -> str:
    """Build Tencent API stock code format."""
    mapping = {
        'sh': f'sh{code}',
        'sz': f'sz{code}',
        'hk': f'hk{code}',
        'us': f'us{code}',
    }
    return mapping.get(market, f'sh{code}')  # 默认上海
```

### 3.3 修改股票服务

**文件**: `backend/app/services/stock_service.py`

主要变更：
1. 接收 `(market, code)` 而非仅 `code`
2. 构建腾讯 API URL 时使用 `market_detector.build_tencent_api_code()`
3. 返回数据中添加 `market` 字段

### 3.4 新增美股/港股字段映射

腾讯 API 不同市场的返回字段可能略有差异，需要测试并适配：

```python
# 字段映射需要测试后确定
# A股: v_sh600000="..."
# 港股: v_hk00700="..."
# 美股: v_usAAPL="..."
```

---

## 4. 前端变更

### 4.1 修改输入提示

**文件**: `frontend/src/components/StockInput.tsx`

```tsx
<input
  placeholder="600000 / usAAPL / hk00700"
  // ...
/>
<p className="text-xs text-gray-500 mt-1">
  支持 A股(600000)、港股(hk00700)、美股(usAAPL)
</p>
```

### 4.2 修改输入验证

**文件**: `frontend/src/services/api.ts`

```typescript
// 放宽验证规则
const isValidStockCode = (code: string): boolean => {
  const clean = code.trim().toUpperCase()
    .replace(/^(SH|SZ|HK|US)/, '')
  return /^[A-Z0-9]+$/.test(clean) && clean.length >= 1 && clean.length <= 6
}
```

---

## 5. 风险点及解决方案

| 风险 | 等级 | 解决方案 |
|------|------|---------|
| 腾讯 API 非官方，字段可能变更 | 中 | 添加字段存在性检查，错误友好提示 |
| 智能推断误判 | 低 | 用户可用前缀明确指定市场 |
| 不同市场字段差异 | 中 | 统一字段映射，缺失字段标记 null |
| 美股字段需测试 | 中 | 部署前测试 usAAPL、usTSLA 实际返回 |

---

## 6. 测试计划

1. **A股测试**
   - `600000` → 上海浦发银行
   - `000001` → 深圳平安银行
   - `sh600000` → 明确前缀

2. **港股测试**
   - `00700` → 腾讯控股
   - `hk00700` → 明确前缀

3. **美股测试**
   - `AAPL` → 苹果
   - `usTSLA` → 特斯拉

4. **错误测试**
   - 空输入
   - 特殊字符
   - 无法识别的格式

---

## 7. 文件变更清单

### 新增文件
- `backend/app/services/market_detector.py` - 市场检测服务

### 修改文件
- `backend/app/models/schemas.py` - 放宽 StockRequest 验证
- `backend/app/services/stock_service.py` - 使用市场检测，支持多市场
- `backend/app/routers/analyze.py` - 处理市场参数
- `frontend/src/components/StockInput.tsx` - 更新输入提示
- `frontend/src/services/api.ts` - 放宽前端验证

---

## 8. 部署注意事项

1. 部署后测试美股、港股数据是否正确解析
2. 检查字段缺失情况下的 AI 分析质量
3. 监控错误日志，看是否有大量无法识别的代码格式

---

**设计确认**: 待用户审批
