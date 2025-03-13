# Portfolio Management API

A comprehensive portfolio management system with AI-powered insights, technical analysis, and portfolio optimization.

## Getting Started

### Prerequisites

- Docker and Docker Compose
- API Key from Google's Gemini AI (for AI-powered features)

### Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and fill in your Gemini API key
3. Run `docker-compose up -d` to start the server

## API Documentation

### Portfolio Management

#### Get Portfolio Overview

```bash
curl -X GET "http://localhost:8000/portfolio"
```

Returns portfolio summary including assets, total value, and performance metrics.

#### Add Asset

```bash
curl -X POST "http://localhost:8000/portfolio/assets" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "quantity": 10,
    "type": "stock",
    "entry_price": 150.00
  }'
```

#### Get Portfolio Analysis

```bash
curl -X GET "http://localhost:8000/portfolio/analysis"
```

Returns detailed portfolio risk analysis including diversification metrics.

#### Get Portfolio History

```bash
curl -X GET "http://localhost:8000/portfolio/history"
```

Returns historical portfolio performance data.

### Market Analysis

#### Get Market Insights

```bash
curl -X GET "http://localhost:8000/market/insights"
```

Returns AI-generated market analysis and trends.

#### Get Market Recommendations

```bash
curl -X GET "http://localhost:8000/market/recommendations"
```

Returns AI-powered investment recommendations.

#### Get Market Sentiment

```bash
curl -X GET "http://localhost:8000/market/sentiment"
```

Returns market sentiment analysis.

#### Get Market News

```bash
curl -X GET "http://localhost:8000/market/news"
```

Returns AI-analyzed market news and impact assessment.

### Technical Analysis

#### Get Technical Analysis

```bash
curl -X GET "http://localhost:8000/technical/AAPL"
```

Returns comprehensive technical analysis for a symbol.

#### Get Price Chart

```bash
curl -X GET "http://localhost:8000/technical/AAPL/chart?timeframe=1y"
```

Returns price chart data with technical indicators.

#### Get Support and Resistance Levels

```bash
curl -X GET "http://localhost:8000/technical/AAPL/support-resistance"
```

Returns key support and resistance levels.

#### Get Trading Signals

```bash
curl -X GET "http://localhost:8000/technical/AAPL/signals"
```

Returns trading signals based on technical analysis.

#### Get Volume Analysis

```bash
curl -X GET "http://localhost:8000/technical/AAPL/volume"
```

Returns volume analysis for a symbol.

### Portfolio Optimization

#### Get Portfolio Optimization

```bash
curl -X GET "http://localhost:8000/portfolio/optimize"
```

Returns optimal portfolio weights using Modern Portfolio Theory.

#### Get Rebalancing Suggestions

```bash
curl -X GET "http://localhost:8000/portfolio/rebalance"
```

Returns portfolio rebalancing recommendations.

#### Get Correlation Analysis

```bash
curl -X GET "http://localhost:8000/portfolio/correlation"
```

Returns correlation analysis between portfolio assets.

#### Get Performance Attribution

```bash
curl -X GET "http://localhost:8000/portfolio/attribution"
```

Returns portfolio performance attribution analysis.

#### Backtest Portfolio

```bash
curl -X GET "http://localhost:8000/portfolio/backtest?start_date=2024-01-01&end_date=2024-12-31"
```

Returns backtesting results for the portfolio.

### AI Chat Interface

#### General Chat

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How is the market performing today?"
  }'
```

Returns AI-generated response to general market questions.

#### Portfolio-Specific Chat

```bash
curl -X POST "http://localhost:8000/chat/portfolio" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Analyze my portfolio performance"
  }'
```

Returns AI analysis of your portfolio.

#### Market Analysis Chat

```bash
curl -X POST "http://localhost:8000/chat/market" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the current market trends?"
  }'
```

Returns AI analysis of market conditions.

### Asset Management

#### Get Specific Asset

```bash
curl -X GET "http://localhost:8000/portfolio/assets/{asset_id}"
```

Returns details for a specific asset in the portfolio.

## Response Formats

### Portfolio Overview Response

```json
{
  "assets": {
    "AAPL": {
      "symbol": "AAPL",
      "quantity": 10,
      "current_value": 1500.0,
      "cost_basis": 1000.0
    }
  },
  "total_value": 1500.0,
  "performance_metrics": {
    "total_return": 0.5,
    "daily_returns": [],
    "volatility": 0.15,
    "sharpe_ratio": 2.1,
    "beta": 1.1,
    "alpha": 0.02
  }
}
```

### Technical Analysis Response

```json
{
  "price": {
    "current": 150.0,
    "open": 149.0,
    "high": 151.0,
    "low": 148.5,
    "close": 150.0
  },
  "moving_averages": {
    "sma_20": 148.5,
    "sma_50": 145.0,
    "sma_200": 140.0
  },
  "bollinger_bands": {
    "upper": 155.0,
    "middle": 150.0,
    "lower": 145.0
  },
  "rsi": {
    "value": 55.0,
    "signal": "Neutral"
  },
  "macd": {
    "macd": 0.5,
    "signal": 0.3,
    "histogram": 0.2
  }
}
```

## Settings API

The Settings API allows you to manage configuration parameters for the portfolio management system.

### Table of Contents

- [Endpoints](#endpoints)
  - [Get Settings](#get-settings)
  - [Update Settings](#update-settings)
  - [Validate Settings](#validate-settings)
- [Configuration Parameters](#configuration-parameters)
  - [Market Indices](#market-indices)
  - [Technical Analysis](#technical-analysis)
  - [Portfolio Limits](#portfolio-limits)

### Endpoints

#### Get Settings

`GET /settings`

Returns all current settings including market indices, sectors, technical analysis parameters, and portfolio limits.

```bash
curl -X GET "http://localhost:8000/settings"
```

Example response:

```json
{
  "market_indices": {
    "^GSPC": "S&P 500",
    "^FTSE": "FTSE 100"
  },
  "market_sectors": {
    "XLF": "Financials",
    "XLK": "Technology"
  },
  "technical_analysis": {
    "rsi_period": 14,
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9,
    "bollinger_period": 20,
    "bollinger_std": 2
  },
  "portfolio_limits": {
    "max_assets": 100,
    "min_position_size": 0.01,
    "max_position_size": 0.5
  }
}
```

#### Update Settings

`POST /settings`

Updates specified settings. All fields are optional, allowing partial updates.

```bash
# Example 1: Update multiple settings
curl -X POST "http://localhost:8000/settings" \
  -H "Content-Type: application/json" \
  -d '{
    "market_indices": {
      "^GSPC": "S&P 500",
      "^FTSE": "FTSE 100"
    },
    "technical_analysis": {
      "rsi_period": 14,
      "macd_fast": 12
    }
  }'

# Example 2: Partial update
curl -X POST "http://localhost:8000/settings" \
  -H "Content-Type: application/json" \
  -d '{
    "market_indices": {
      "^GSPC": "S&P 500"
    }
  }'
```

#### Validate Settings

`GET /settings/validate`

Validates current settings and returns any issues or warnings.

```bash
curl -X GET "http://localhost:8000/settings/validate"
```

Example response:

```json
{
  "is_valid": true,
  "issues": [],
  "warnings": ["No market indices configured"]
}
```

### Configuration Parameters

#### Market Indices

- **Format**: "symbol:name" pairs
- **Example**: "^GSPC:S&P 500,^FTSE:FTSE 100"
- **Storage**: Stored as comma-separated string in environment variable

#### Technical Analysis

| Parameter        | Range | Default | Description                            |
| ---------------- | ----- | ------- | -------------------------------------- |
| RSI Period       | 5-50  | 14      | Period for RSI calculation             |
| MACD Fast        | 5-35  | 12      | Fast period for MACD                   |
| MACD Slow        | 15-60 | 26      | Slow period for MACD                   |
| MACD Signal      | 5-25  | 9       | Signal period for MACD                 |
| Bollinger Period | 10-50 | 20      | Period for Bollinger Bands             |
| Bollinger Std    | 1-4   | 2       | Standard deviation for Bollinger Bands |

#### Portfolio Limits

| Parameter             | Range | Default | Description                                    |
| --------------------- | ----- | ------- | ---------------------------------------------- |
| Maximum Assets        | > 0   | 100     | Maximum number of assets in portfolio          |
| Minimum Position Size | 0-1   | 0.01    | Minimum position size as fraction of portfolio |
| Maximum Position Size | 0-1   | 0.5     | Maximum position size as fraction of portfolio |
