import numpy as np
import pandas as pd
from typing import Dict, Optional, List, Tuple
from datetime import datetime, timedelta
from models import Portfolio, Holding, PriceHistory, Transaction
from services.price_tracker import PriceTrackerService

class RiskMetricsService:
    """
    Service for calculating risk metrics including Sharpe ratio, volatility,
    Value at Risk (VaR), correlation, and other risk indicators.
    """
    
    RISK_FREE_RATE = 0.02  # 2% annual risk-free rate
    
    @staticmethod
    def calculate_returns(prices: List[float]) -> np.ndarray:
        """
        Calculate daily returns from price data.
        
        Args:
            prices: List of prices
            
        Returns:
            Array of daily returns (percentage change)
        """
        if len(prices) < 2:
            return np.array([])
        
        prices_array = np.array(prices, dtype=float)
        returns = np.diff(prices_array) / prices_array[:-1]
        return returns
    
    @staticmethod
    def calculate_volatility(prices: List[float], period: str = 'daily') -> Optional[float]:
        """
        Calculate volatility (standard deviation of returns).
        
        Args:
            prices: List of prices
            period: 'daily', 'weekly', 'monthly', 'annual'
            
        Returns:
            Annualized volatility or None
        """
        try:
            returns = RiskMetricsService.calculate_returns(prices)
            if len(returns) < 2:
                return None
            
            daily_volatility = np.std(returns)
            
            # Annualize volatility
            if period == 'daily':
                annual_volatility = daily_volatility * np.sqrt(252)  # 252 trading days
            elif period == 'weekly':
                annual_volatility = daily_volatility * np.sqrt(52)
            elif period == 'monthly':
                annual_volatility = daily_volatility * np.sqrt(12)
            else:
                annual_volatility = daily_volatility
            
            return annual_volatility
        except Exception as e:
            print(f"Error calculating volatility: {str(e)}")
        return None
    
    @staticmethod
    def calculate_sharpe_ratio(prices: List[float], risk_free_rate: Optional[float] = None) -> Optional[float]:
        """
        Calculate Sharpe Ratio (return per unit of risk).
        
        Args:
            prices: List of prices
            risk_free_rate: Annual risk-free rate (default: 2%)
            
        Returns:
            Sharpe ratio or None
        """
        try:
            if risk_free_rate is None:
                risk_free_rate = RiskMetricsService.RISK_FREE_RATE
            
            returns = RiskMetricsService.calculate_returns(prices)
            if len(returns) < 2:
                return None
            
            # Annualize metrics
            annual_return = np.mean(returns) * 252
            annual_volatility = np.std(returns) * np.sqrt(252)
            
            if annual_volatility == 0:
                return None
            
            sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility
            return sharpe_ratio
        except Exception as e:
            print(f"Error calculating Sharpe ratio: {str(e)}")
        return None
    
    @staticmethod
    def calculate_sortino_ratio(prices: List[float], risk_free_rate: Optional[float] = None) -> Optional[float]:
        """
        Calculate Sortino Ratio (return per unit of downside risk).
        Similar to Sharpe but only considers downside volatility.
        
        Args:
            prices: List of prices
            risk_free_rate: Annual risk-free rate (default: 2%)
            
        Returns:
            Sortino ratio or None
        """
        try:
            if risk_free_rate is None:
                risk_free_rate = RiskMetricsService.RISK_FREE_RATE
            
            returns = RiskMetricsService.calculate_returns(prices)
            if len(returns) < 2:
                return None
            
            # Annualize return
            annual_return = np.mean(returns) * 252
            
            # Calculate downside deviation (only negative returns)
            negative_returns = returns[returns < 0]
            if len(negative_returns) == 0:
                downside_deviation = 0
            else:
                downside_deviation = np.sqrt(np.mean(negative_returns ** 2)) * np.sqrt(252)
            
            if downside_deviation == 0:
                return None
            
            sortino_ratio = (annual_return - risk_free_rate) / downside_deviation
            return sortino_ratio
        except Exception as e:
            print(f"Error calculating Sortino ratio: {str(e)}")
        return None
    
    @staticmethod
    def calculate_max_drawdown(prices: List[float]) -> Optional[float]:
        """
        Calculate Maximum Drawdown (largest peak-to-trough decline).
        
        Args:
            prices: List of prices
            
        Returns:
            Maximum drawdown as percentage or None
        """
        try:
            prices_array = np.array(prices, dtype=float)
            if len(prices_array) < 2:
                return None
            
            cumulative_max = np.maximum.accumulate(prices_array)
            drawdown = (prices_array - cumulative_max) / cumulative_max
            max_drawdown = np.min(drawdown)
            
            return abs(max_drawdown)
        except Exception as e:
            print(f"Error calculating max drawdown: {str(e)}")
        return None
    
    @staticmethod
    def calculate_value_at_risk(prices: List[float], confidence_level: float = 0.95) -> Optional[float]:
        """
        Calculate Value at Risk (VaR) - maximum expected loss at a given confidence level.
        
        Args:
            prices: List of prices
            confidence_level: Confidence level (default: 0.95 for 95%)
            
        Returns:
            VaR as percentage or None
        """
        try:
            returns = RiskMetricsService.calculate_returns(prices)
            if len(returns) < 2:
                return None
            
            var = np.percentile(returns, (1 - confidence_level) * 100)
            return var
        except Exception as e:
            print(f"Error calculating VaR: {str(e)}")
        return None
    
    @staticmethod
    def calculate_correlation_matrix(symbols: List[str], days: int = 90, asset_types: Dict[str, str] = None) -> Optional[pd.DataFrame]:
        """
        Calculate correlation matrix between multiple assets.
        
        Args:
            symbols: List of symbols
            days: Number of days for historical data
            asset_types: Dict mapping symbols to asset types
            
        Returns:
            Correlation matrix DataFrame or None
        """
        try:
            if asset_types is None:
                asset_types = {symbol: 'stock' for symbol in symbols}
            
            price_data = {}
            
            # Fetch historical prices for all symbols
            for symbol in symbols:
                asset_type = asset_types.get(symbol, 'stock')
                df = PriceTrackerService.get_historical_prices(symbol, days, asset_type)
                
                if not df.empty:
                    # Convert to datetime if needed
                    df['Date'] = pd.to_datetime(df['Date'])
                    price_data[symbol] = df.set_index('Date')['Close']
            
            if not price_data:
                return None
            
            # Align all series and calculate returns
            combined_df = pd.DataFrame(price_data)
            returns_df = combined_df.pct_change().dropna()
            
            # Calculate correlation
            correlation = returns_df.corr()
            return correlation
        except Exception as e:
            print(f"Error calculating correlation matrix: {str(e)}")
        return None
    
    @staticmethod
    def calculate_beta(asset_prices: List[float], market_prices: List[float]) -> Optional[float]:
        """
        Calculate Beta (systematic risk relative to market).
        
        Args:
            asset_prices: List of asset prices
            market_prices: List of market index prices
            
        Returns:
            Beta coefficient or None
        """
        try:
            if len(asset_prices) != len(market_prices):
                return None
            
            asset_returns = RiskMetricsService.calculate_returns(asset_prices)
            market_returns = RiskMetricsService.calculate_returns(market_prices)
            
            if len(asset_returns) < 2 or len(market_returns) < 2:
                return None
            
            covariance = np.cov(asset_returns, market_returns)[0, 1]
            market_variance = np.var(market_returns)
            
            if market_variance == 0:
                return None
            
            beta = covariance / market_variance
            return beta
        except Exception as e:
            print(f"Error calculating beta: {str(e)}")
        return None
    
    @staticmethod
    def get_holding_risk_metrics(holding_id: int, days: int = 90) -> Optional[Dict]:
        """
        Get comprehensive risk metrics for a holding.
        
        Args:
            holding_id: ID of the holding
            days: Number of days for historical data
            
        Returns:
            Dict with risk metrics or None
        """
        try:
            from models import Holding
            holding = Holding.query.get(holding_id)
            if not holding:
                return None
            
            # Get price history
            price_history = PriceHistory.query.filter(
                PriceHistory.holding_id == holding_id
            ).order_by(PriceHistory.timestamp.asc()).all()
            
            if len(price_history) < 2:
                return None
            
            prices = [ph.price for ph in price_history]
            
            return {
                'holding_id': holding_id,
                'symbol': holding.symbol,
                'volatility': RiskMetricsService.calculate_volatility(prices),
                'sharpe_ratio': RiskMetricsService.calculate_sharpe_ratio(prices),
                'sortino_ratio': RiskMetricsService.calculate_sortino_ratio(prices),
                'max_drawdown': RiskMetricsService.calculate_max_drawdown(prices),
                'value_at_risk_95': RiskMetricsService.calculate_value_at_risk(prices, 0.95),
                'value_at_risk_99': RiskMetricsService.calculate_value_at_risk(prices, 0.99)
            }
        except Exception as e:
            print(f"Error getting holding risk metrics: {str(e)}")
        return None
    
    @staticmethod
    def get_portfolio_risk_metrics(portfolio_id: int, days: int = 90) -> Optional[Dict]:
        """
        Get comprehensive risk metrics for a portfolio.
        
        Args:
            portfolio_id: ID of the portfolio
            days: Number of days for historical data
            
        Returns:
            Dict with portfolio risk metrics or None
        """
        try:
            portfolio = Portfolio.query.get(portfolio_id)
            if not portfolio:
                return None
            
            if not portfolio.holdings:
                return None
            
            symbols = [h.symbol for h in portfolio.holdings]
            asset_types = {h.symbol: h.asset_type for h in portfolio.holdings}
            
            # Get portfolio price history
            portfolio_values = RiskMetricsService._calculate_portfolio_values(portfolio_id, days)
            if not portfolio_values:
                return None
            
            return {
                'portfolio_id': portfolio_id,
                'holdings_count': len(portfolio.holdings),
                'volatility': RiskMetricsService.calculate_volatility(portfolio_values),
                'sharpe_ratio': RiskMetricsService.calculate_sharpe_ratio(portfolio_values),
                'sortino_ratio': RiskMetricsService.calculate_sortino_ratio(portfolio_values),
                'max_drawdown': RiskMetricsService.calculate_max_drawdown(portfolio_values),
                'value_at_risk_95': RiskMetricsService.calculate_value_at_risk(portfolio_values, 0.95),
                'value_at_risk_99': RiskMetricsService.calculate_value_at_risk(portfolio_values, 0.99),
                'correlation_matrix': RiskMetricsService.calculate_correlation_matrix(symbols, days, asset_types)
            }
        except Exception as e:
            print(f"Error getting portfolio risk metrics: {str(e)}")
        return None
    
    @staticmethod
    def _calculate_portfolio_values(portfolio_id: int, days: int = 90) -> List[float]:
        """
        Calculate daily portfolio values over a period.
        
        Args:
            portfolio_id: ID of the portfolio
            days: Number of days
            
        Returns:
            List of portfolio values
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            portfolio = Portfolio.query.get(portfolio_id)
            
            portfolio_values = {}
            
            for holding in portfolio.holdings:
                price_history = PriceHistory.query.filter(
                    PriceHistory.holding_id == holding.id,
                    PriceHistory.timestamp >= cutoff_date
                ).order_by(PriceHistory.timestamp.asc()).all()
                
                for ph in price_history:
                    date_key = ph.timestamp.date()
                    holding_value = ph.price * holding.quantity
                    
                    if date_key not in portfolio_values:
                        portfolio_values[date_key] = 0
                    portfolio_values[date_key] += holding_value
            
            if not portfolio_values:
                return []
            
            # Sort by date and return values
            sorted_values = sorted(portfolio_values.items())
            return [value for _, value in sorted_values]
        except Exception as e:
            print(f"Error calculating portfolio values: {str(e)}")
        return []
