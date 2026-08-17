import numpy as np
import pandas as pd
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from models import Portfolio, Holding, Transaction, PriceHistory
from app import db

class PortfolioAnalyticsService:
    """
    Service for calculating portfolio performance, returns, and analysis metrics.
    """
    
    @staticmethod
    def calculate_portfolio_value(portfolio_id: int, date: Optional[datetime] = None) -> Optional[float]:
        """
        Calculate total portfolio value at a specific date.
        
        Args:
            portfolio_id: ID of the portfolio
            date: Date to calculate value (None for current)
            
        Returns:
            Total portfolio value or None
        """
        try:
            portfolio = Portfolio.query.get(portfolio_id)
            if not portfolio:
                return None
            
            total_value = 0
            
            for holding in portfolio.holdings:
                # Get price at the specified date
                if date is None:
                    price_history = PriceHistory.query.filter(
                        PriceHistory.holding_id == holding.id
                    ).order_by(PriceHistory.timestamp.desc()).first()
                else:
                    price_history = PriceHistory.query.filter(
                        PriceHistory.holding_id == holding.id,
                        PriceHistory.timestamp <= date
                    ).order_by(PriceHistory.timestamp.desc()).first()
                
                if price_history:
                    total_value += price_history.price * holding.quantity
            
            return total_value if total_value > 0 else None
        except Exception as e:
            print(f"Error calculating portfolio value: {str(e)}")
        return None
    
    @staticmethod
    def calculate_total_invested(portfolio_id: int) -> Optional[float]:
        """
        Calculate total amount invested in portfolio.
        
        Args:
            portfolio_id: ID of the portfolio
            
        Returns:
            Total invested amount or None
        """
        try:
            portfolio = Portfolio.query.get(portfolio_id)
            if not portfolio:
                return None
            
            # Sum all buy transactions
            buy_transactions = Transaction.query.filter(
                Transaction.portfolio_id == portfolio_id,
                Transaction.transaction_type == 'buy'
            ).all()
            
            total_invested = sum(t.total_amount for t in buy_transactions)
            return total_invested
        except Exception as e:
            print(f"Error calculating total invested: {str(e)}")
        return None
    
    @staticmethod
    def calculate_total_return(portfolio_id: int) -> Optional[Dict]:
        """
        Calculate total return and percentage return.
        
        Args:
            portfolio_id: ID of the portfolio
            
        Returns:
            Dict with current_value, invested_amount, total_return, total_return_percent
        """
        try:
            current_value = PortfolioAnalyticsService.calculate_portfolio_value(portfolio_id)
            invested_amount = PortfolioAnalyticsService.calculate_total_invested(portfolio_id)
            
            if current_value is None or invested_amount is None or invested_amount == 0:
                return None
            
            total_return = current_value - invested_amount
            total_return_percent = (total_return / invested_amount) * 100
            
            return {
                'current_value': current_value,
                'invested_amount': invested_amount,
                'total_return': total_return,
                'total_return_percent': total_return_percent
            }
        except Exception as e:
            print(f"Error calculating total return: {str(e)}")
        return None
    
    @staticmethod
    def calculate_daily_returns(portfolio_id: int, days: int = 90) -> Optional[pd.DataFrame]:
        """
        Calculate daily portfolio returns over a period.
        
        Args:
            portfolio_id: ID of the portfolio
            days: Number of days to analyze
            
        Returns:
            DataFrame with daily returns or None
        """
        try:
            portfolio = Portfolio.query.get(portfolio_id)
            if not portfolio or not portfolio.holdings:
                return None
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            portfolio_values = {}
            
            # Collect price history for all holdings
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
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame([
                {'date': date, 'value': value}
                for date, value in sorted(portfolio_values.items())
            ])
            
            # Calculate daily returns
            df['daily_return'] = df['value'].pct_change()
            df['daily_return_amount'] = df['value'].diff()
            
            return df
        except Exception as e:
            print(f"Error calculating daily returns: {str(e)}")
        return None
    
    @staticmethod
    def calculate_holding_allocation(portfolio_id: int) -> Optional[Dict]:
        """
        Calculate asset allocation percentages.
        
        Args:
            portfolio_id: ID of the portfolio
            
        Returns:
            Dict with symbol as key and allocation percentage as value
        """
        try:
            portfolio = Portfolio.query.get(portfolio_id)
            if not portfolio:
                return None
            
            portfolio_value = PortfolioAnalyticsService.calculate_portfolio_value(portfolio_id)
            if portfolio_value is None or portfolio_value == 0:
                return None
            
            allocation = {}
            
            for holding in portfolio.holdings:
                # Get latest price
                price_history = PriceHistory.query.filter(
                    PriceHistory.holding_id == holding.id
                ).order_by(PriceHistory.timestamp.desc()).first()
                
                if price_history:
                    holding_value = price_history.price * holding.quantity
                    allocation[holding.symbol] = {
                        'value': holding_value,
                        'percentage': (holding_value / portfolio_value) * 100,
                        'quantity': holding.quantity,
                        'price': price_history.price
                    }
            
            return allocation
        except Exception as e:
            print(f"Error calculating allocation: {str(e)}")
        return None
    
    @staticmethod
    def calculate_asset_type_allocation(portfolio_id: int) -> Optional[Dict]:
        """
        Calculate allocation by asset type (stock vs crypto).
        
        Args:
            portfolio_id: ID of the portfolio
            
        Returns:
            Dict with asset type as key and allocation info as value
        """
        try:
            allocation = PortfolioAnalyticsService.calculate_holding_allocation(portfolio_id)
            if not allocation:
                return None
            
            portfolio = Portfolio.query.get(portfolio_id)
            asset_type_alloc = {}
            total_value = sum(h['value'] for h in allocation.values())
            
            for holding in portfolio.holdings:
                asset_type = holding.asset_type
                if asset_type not in asset_type_alloc:
                    asset_type_alloc[asset_type] = {'value': 0, 'symbols': []}
                
                if holding.symbol in allocation:
                    asset_type_alloc[asset_type]['value'] += allocation[holding.symbol]['value']
                    asset_type_alloc[asset_type]['symbols'].append(holding.symbol)
            
            # Calculate percentages
            for asset_type in asset_type_alloc:
                asset_type_alloc[asset_type]['percentage'] = (
                    asset_type_alloc[asset_type]['value'] / total_value * 100
                ) if total_value > 0 else 0
            
            return asset_type_alloc
        except Exception as e:
            print(f"Error calculating asset type allocation: {str(e)}")
        return None
    
    @staticmethod
    def calculate_holding_performance(holding_id: int) -> Optional[Dict]:
        """
        Calculate performance metrics for a single holding.
        
        Args:
            holding_id: ID of the holding
            
        Returns:
            Dict with performance metrics or None
        """
        try:
            holding = Holding.query.get(holding_id)
            if not holding:
                return None
            
            # Get all buy transactions for this holding
            buy_transactions = Transaction.query.filter(
                Transaction.portfolio_id == holding.portfolio_id,
                Transaction.symbol == holding.symbol,
                Transaction.transaction_type == 'buy'
            ).all()
            
            if not buy_transactions:
                return None
            
            total_cost = sum(t.total_amount for t in buy_transactions)
            total_qty = sum(t.quantity for t in buy_transactions)
            avg_cost = total_cost / total_qty if total_qty > 0 else 0
            
            # Get current price
            price_history = PriceHistory.query.filter(
                PriceHistory.holding_id == holding_id
            ).order_by(PriceHistory.timestamp.desc()).first()
            
            if not price_history:
                return None
            
            current_price = price_history.price
            current_value = current_price * holding.quantity
            gain_loss = current_value - total_cost
            gain_loss_percent = (gain_loss / total_cost) * 100 if total_cost > 0 else 0
            
            return {
                'holding_id': holding_id,
                'symbol': holding.symbol,
                'quantity': holding.quantity,
                'average_cost': avg_cost,
                'current_price': current_price,
                'total_cost': total_cost,
                'current_value': current_value,
                'gain_loss': gain_loss,
                'gain_loss_percent': gain_loss_percent
            }
        except Exception as e:
            print(f"Error calculating holding performance: {str(e)}")
        return None
    
    @staticmethod
    def calculate_portfolio_performance_summary(portfolio_id: int) -> Optional[Dict]:
        """
        Get comprehensive portfolio performance summary.
        
        Args:
            portfolio_id: ID of the portfolio
            
        Returns:
            Dict with complete performance summary or None
        """
        try:
            portfolio = Portfolio.query.get(portfolio_id)
            if not portfolio:
                return None
            
            # Calculate various metrics
            total_return = PortfolioAnalyticsService.calculate_total_return(portfolio_id)
            allocation = PortfolioAnalyticsService.calculate_holding_allocation(portfolio_id)
            asset_type_alloc = PortfolioAnalyticsService.calculate_asset_type_allocation(portfolio_id)
            
            if not total_return or not allocation:
                return None
            
            # Calculate holding performances
            holding_performances = []
            for holding in portfolio.holdings:
                perf = PortfolioAnalyticsService.calculate_holding_performance(holding.id)
                if perf:
                    holding_performances.append(perf)
            
            return {
                'portfolio_id': portfolio_id,
                'portfolio_name': portfolio.name,
                'total_value': total_return['current_value'],
                'invested_amount': total_return['invested_amount'],
                'total_return': total_return['total_return'],
                'total_return_percent': total_return['total_return_percent'],
                'holdings_count': len(portfolio.holdings),
                'allocation_by_symbol': allocation,
                'allocation_by_asset_type': asset_type_alloc,
                'holdings_performance': holding_performances
            }
        except Exception as e:
            print(f"Error calculating portfolio performance summary: {str(e)}")
        return None
    
    @staticmethod
    def get_top_gainers(portfolio_id: int, limit: int = 5) -> Optional[List[Dict]]:
        """
        Get top performing holdings.
        
        Args:
            portfolio_id: ID of the portfolio
            limit: Number of top holdings to return
            
        Returns:
            List of top performing holdings or None
        """
        try:
            portfolio = Portfolio.query.get(portfolio_id)
            if not portfolio:
                return None
            
            performances = []
            for holding in portfolio.holdings:
                perf = PortfolioAnalyticsService.calculate_holding_performance(holding.id)
                if perf:
                    performances.append(perf)
            
            # Sort by gain/loss percent (descending)
            performances.sort(key=lambda x: x['gain_loss_percent'], reverse=True)
            return performances[:limit]
        except Exception as e:
            print(f"Error getting top gainers: {str(e)}")
        return None
    
    @staticmethod
    def get_top_losers(portfolio_id: int, limit: int = 5) -> Optional[List[Dict]]:
        """
        Get worst performing holdings.
        
        Args:
            portfolio_id: ID of the portfolio
            limit: Number of worst holdings to return
            
        Returns:
            List of worst performing holdings or None
        """
        try:
            portfolio = Portfolio.query.get(portfolio_id)
            if not portfolio:
                return None
            
            performances = []
            for holding in portfolio.holdings:
                perf = PortfolioAnalyticsService.calculate_holding_performance(holding.id)
                if perf:
                    performances.append(perf)
            
            # Sort by gain/loss percent (ascending)
            performances.sort(key=lambda x: x['gain_loss_percent'])
            return performances[:limit]
        except Exception as e:
            print(f"Error getting top losers: {str(e)}")
        return None
