# Financial Analysis Tool

A comprehensive Python-based financial analysis tool for tracking stocks, cryptocurrencies, portfolio performance, and risk metrics.

## Features

- **Real-time Stock & Crypto Price Tracking** - Track prices from multiple data sources
- **Portfolio Performance Analysis** - Monitor portfolio value and returns
- **Risk Assessment** - Calculate Sharpe ratio, volatility, and other risk metrics
- **Asset Allocation Visualization** - Visual breakdown of portfolio allocation
- **Expense & Budget Tracking** - Monitor spending and budget limits
- **Price Alerts** - Get notified when assets reach target prices
- **Historical Data Analysis** - Analyze historical price trends
- **Backtesting Strategies** - Test trading strategies on historical data

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite (development) / PostgreSQL (production)
- **Data Analysis**: Pandas, NumPy, SciPy
- **Data Sources**: yfinance, CoinGecko
- **Scheduling**: APScheduler
- **Visualization**: Plotly, Matplotlib
- **Notebooks**: Jupyter Lab

## Project Structure

```
financial-analysis-tool/
├── app.py                 # Flask application factory
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── models/                # SQLAlchemy ORM models
│   ├── __init__.py
│   ├── user.py
│   ├── portfolio.py
│   ├── holding.py
│   ├── price_history.py
│   ├── transaction.py
│   └── alert.py
├── api/                   # Flask API routes
│   ├── __init__.py
│   └── routes.py
├── services/              # Business logic services (coming soon)
├── notebooks/             # Jupyter notebooks for analysis
└── utils/                 # Utility functions (coming soon)
```

## Installation

### Prerequisites
- Python 3.8+
- pip or conda
- Virtual environment (recommended)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Durga8977/financial-analysis-tool.git
cd financial-analysis-tool
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the application:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Users
- `POST /api/users` - Create a new user
- `GET /api/users/<user_id>` - Get user details

### Portfolios
- `POST /api/portfolios` - Create a new portfolio
- `GET /api/portfolios/<portfolio_id>` - Get portfolio details

### Holdings
- `POST /api/holdings` - Add a holding to a portfolio

### Transactions
- `POST /api/transactions` - Record a buy/sell transaction

### Alerts
- `POST /api/alerts` - Create a price alert
- `GET /api/alerts/<user_id>` - Get user's alerts

## Usage Examples

### Create a User
```bash
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "email": "john@example.com"}'
```

### Create a Portfolio
```bash
curl -X POST http://localhost:5000/api/portfolios \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "name": "My Portfolio", "initial_investment": 10000}'
```

### Add a Holding
```bash
curl -X POST http://localhost:5000/api/holdings \
  -H "Content-Type: application/json" \
  -d '{"portfolio_id": 1, "symbol": "AAPL", "quantity": 10, "asset_type": "stock"}'
```

## Coming Next

- [ ] Price tracking service with real-time updates
- [ ] Risk metrics calculation (Sharpe ratio, volatility, etc.)
- [ ] Portfolio performance analytics
- [ ] Visualization dashboards
- [ ] Jupyter notebooks for analysis
- [ ] Backtesting engine
- [ ] User authentication & authorization
- [ ] Frontend dashboard (React/Vue)

## Contributing

Contributions are welcome! Please create a pull request with your changes.

## License

MIT License - see LICENSE file for details
