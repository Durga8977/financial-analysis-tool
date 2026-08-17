import yfinance as yf
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
from app import db
from models import Holding, PriceHistory

class PriceTrackerService:
    """
    Service for tracking real-time and historical prices for stocks and cryptocurrencies.
    Uses yfinance for stocks and CoinGecko API for cryptocurrencies.
    """
    
    # CoinGecko API endpoints
    COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
    CRYPTO_SYMBOLS_MAP = {
        'BTC-USD': 'bitcoin',
        'ETH-USD': 'ethereum',
        'XRP-USD': 'ripple',
        'LTC-USD': 'litecoin',
        'ADA-USD': 'cardano',
        'SOL-USD': 'solana',
        'DOGE-USD': 'dogecoin',
        'DOT-USD': 'polkadot',
        'MATIC-USD': 'matic-network',
        'LINK-USD': 'chainlink'
    }
    
    @staticmethod
    def get_current_price(symbol: str, asset_type: str = 'stock') -> Optional[float]:
        """
        Get current price for a symbol.
        
        Args:
            symbol: Stock ticker or crypto symbol (e.g., 'AAPL' or 'BTC-USD')
            asset_type: 'stock' or 'crypto'
            
        Returns:
            Current price or None if error
        """
        try:
            if asset_type == 'stock':
                ticker = yf.Ticker(symbol)
                data = ticker.history(period='1d')
                if len(data) > 0:
                    return float(data['Close'].iloc[-1])
            else:  # crypto
                price = PriceTrackerService._get_crypto_price(symbol)
                return price
        except Exception as e:
            print(f"Error fetching price for {symbol}: {str(e)}")
            return None
        return None
    
    @staticmethod
    def _get_crypto_price(symbol: str) -> Optional[float]:
        """
        Get cryptocurrency price from CoinGecko API.
        
        Args:
            symbol: Crypto symbol (e.g., 'BTC-USD')
            
        Returns:
            Current price or None if error
        """
        try:
            coin_id = PriceTrackerService.CRYPTO_SYMBOLS_MAP.get(symbol)
            if not coin_id:
                return None
            
            url = f"{PriceTrackerService.COINGECKO_BASE_URL}/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd',
                'include_market_cap': 'false',
                'include_24hr_vol': 'true'
            }
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data[coin_id]['usd']
        except Exception as e:
            print(f"Error fetching crypto price for {symbol}: {str(e)}")
        return None
    
    @staticmethod
    def get_historical_prices(symbol: str, days: int = 30, asset_type: str = 'stock') -> pd.DataFrame:
        """
        Get historical price data.
        
        Args:
            symbol: Stock ticker or crypto symbol
            days: Number of days of historical data
            asset_type: 'stock' or 'crypto'
            
        Returns:
            DataFrame with Date and Close columns
        """
        try:
            if asset_type == 'stock':
                ticker = yf.Ticker(symbol)
                period = f"{days}d"
                data = ticker.history(period=period)[['Close']]
                data = data.reset_index()
                data.columns = ['Date', 'Close']
                return data
            else:  # crypto
                return PriceTrackerService._get_crypto_historical(symbol, days)
        except Exception as e:
            print(f"Error fetching historical prices for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    @staticmethod
    def _get_crypto_historical(symbol: str, days: int = 30) -> pd.DataFrame:
        """
        Get historical cryptocurrency prices from CoinGecko.
        
        Args:
            symbol: Crypto symbol (e.g., 'BTC-USD')
            days: Number of days of historical data
            
        Returns:
            DataFrame with Date and Close columns
        """
        try:
            coin_id = PriceTrackerService.CRYPTO_SYMBOLS_MAP.get(symbol)
            if not coin_id:
                return pd.DataFrame()
            
            url = f"{PriceTrackerService.COINGECKO_BASE_URL}/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': 'daily'
            }
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                prices = data['prices']
                
                df = pd.DataFrame(prices, columns=['Timestamp', 'Close'])
                df['Date'] = pd.to_datetime(df['Timestamp'], unit='ms')
                df = df[['Date', 'Close']]
                return df
        except Exception as e:
            print(f"Error fetching crypto historical data for {symbol}: {str(e)}")
        return pd.DataFrame()
    
    @staticmethod
    def get_price_change(symbol: str, asset_type: str = 'stock', period: str = '1mo') -> Optional[Dict]:
        """
        Get price change metrics for a symbol.
        
        Args:
            symbol: Stock ticker or crypto symbol
            asset_type: 'stock' or 'crypto'
            period: '1d', '1wk', '1mo', '3mo', '1y'
            
        Returns:
            Dict with 'current', 'previous', 'change', 'change_percent'
        """
        try:
            if asset_type == 'stock':
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period)
                if len(hist) < 2:
                    return None
                
                current = float(hist['Close'].iloc[-1])
                previous = float(hist['Close'].iloc[-2])
                change = current - previous
                change_percent = (change / previous) * 100 if previous != 0 else 0
                
                return {
                    'symbol': symbol,
                    'current': current,
                    'previous': previous,
                    'change': change,
                    'change_percent': change_percent,
                    'period': period
                }
        except Exception as e:
            print(f"Error calculating price change for {symbol}: {str(e)}")
        return None
    
    @staticmethod
    def get_stock_info(symbol: str) -> Optional[Dict]:
        """
        Get comprehensive stock information.
        
        Args:
            symbol: Stock ticker
            
        Returns:
            Dict with stock info (name, sector, market cap, etc.)
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'name': info.get('longName', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 'N/A'),
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'dividend_yield': info.get('dividendYield', 'N/A'),
                '52week_high': info.get('fiftyTwoWeekHigh', 'N/A'),
                '52week_low': info.get('fiftyTwoWeekLow', 'N/A')
            }
        except Exception as e:
            print(f"Error fetching stock info for {symbol}: {str(e)}")
        return None
    
    @staticmethod
    def record_price_history(holding_id: int, price: float) -> bool:
        """
        Record a price point for a holding.
        
        Args:
            holding_id: ID of the holding
            price: Current price
            
        Returns:
            True if successful, False otherwise
        """
        try:
            holding = Holding.query.get(holding_id)
            if not holding:
                return False
            
            price_record = PriceHistory(
                holding_id=holding_id,
                price=price,
                timestamp=datetime.utcnow()
            )
            db.session.add(price_record)
            db.session.commit()
            return True
        except Exception as e:
            print(f"Error recording price history: {str(e)}")
            db.session.rollback()
        return False
    
    @staticmethod
    def get_holding_price_history(holding_id: int, days: int = 30) -> List[Dict]:
        """
        Get price history for a holding.
        
        Args:
            holding_id: ID of the holding
            days: Number of days to retrieve
            
        Returns:
            List of price records
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            price_history = PriceHistory.query.filter(
                PriceHistory.holding_id == holding_id,
                PriceHistory.timestamp >= cutoff_date
            ).order_by(PriceHistory.timestamp.asc()).all()
            
            return [ph.to_dict() for ph in price_history]
        except Exception as e:
            print(f"Error retrieving price history: {str(e)}")
        return []
    
    @staticmethod
    def update_portfolio_prices(portfolio_id: int) -> bool:
        """
        Update all prices for holdings in a portfolio.
        
        Args:
            portfolio_id: ID of the portfolio
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from models import Portfolio
            portfolio = Portfolio.query.get(portfolio_id)
            if not portfolio:
                return False
            
            for holding in portfolio.holdings:
                price = PriceTrackerService.get_current_price(
                    holding.symbol,
                    holding.asset_type
                )
                if price:
                    PriceTrackerService.record_price_history(holding.id, price)
            
            return True
        except Exception as e:
            print(f"Error updating portfolio prices: {str(e)}")
        return False
