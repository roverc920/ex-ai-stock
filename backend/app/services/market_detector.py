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

    Args:
        stock_code: User input stock code (e.g., '600000', 'usAAPL', 'hk00700')

    Returns:
        tuple: (market_code, clean_stock_code)

    Raises:
        ValueError: If cannot detect market
    """
    code = stock_code.strip().upper()

    # 1. Check explicit prefixes
    for prefix in ['SH', 'SZ', 'HK', 'US']:
        if code.startswith(prefix):
            return prefix.lower(), code[len(prefix):]

    # 2. Pure digits
    if code.isdigit():
        if len(code) == 5:
            return 'hk', code  # 5 digits -> Hong Kong
        elif len(code) == 6:
            # Shanghai: 600, 601, 603, 605, 688 (STAR Market)
            if code.startswith(('600', '601', '603', '605', '688')):
                return 'sh', code
            # Shenzhen: 000, 001, 002 (SME), 300 (ChiNext)
            else:
                return 'sz', code

    # 3. Pure letters -> US stock
    if code.isalpha():
        return 'us', code

    raise ValueError(
        f'无法识别股票代码格式: {stock_code}，支持的格式：\n'
        f'- A股: 600000 / sh600000 / sz000001\n'
        f'- 港股: 00700 / hk00700\n'
        f'- 美股: AAPL / usAAPL'
    )


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
    return mapping.get(market, f'sh{code}')  # Default to Shanghai
