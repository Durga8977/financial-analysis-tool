import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from models import Portfolio, Holding, PriceHistory, Transaction
from services.portfolio_analytics import PortfolioAnalyticsService
from services.price_tracker import PriceTrackerService

class VisualizationService:
    """
    Service for creating interactive visualizations using Plotly.
    """
    
    @staticmethod
    def create_portfolio_allocation_pie(portfolio_id: int) -> Optional[str]:
        """
        Create pie chart of portfolio asset allocation.
        
        Args:
            portfolio_id: ID of the portfolio
            
        Returns:
            HTML string of plotly figure or None
        """
        try:
            allocation = PortfolioAnalyticsService.calculate_holding_allocation(portfolio_id)
            if not allocation:
                return None
            
            labels = list(allocation.keys())
            values = [allocation[sym]['value'] for sym in labels]
            percentages = [allocation[sym]['percentage'] for sym in labels]
            
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hovertemplate='<b>%{label}</b><br>Value: $%{value:,.2f}<br>%{customdata}%<extra></extra>',
                customdata=percentages
            )])
            
            fig.update_layout(
                title='Portfolio Allocation',
                height=500,
                font=dict(size=12)
            )
            
            return fig.to_html(include_plotlyjs='cdn')
        except Exception as e:
            print(f"Error creating allocation pie chart: {str(e)}")
        return None
    
    @staticmethod
    def create_portfolio_value_chart(portfolio_id: int, days: int = 90) -> Optional[str]:
        """
        Create line chart of portfolio value over time.
        
        Args:
            portfolio_id: ID of the portfolio
            days: Number of days to display
            
        Returns:
            HTML string of plotly figure or None
        """
        try:
            daily_returns = PortfolioAnalyticsService.calculate_daily_returns(portfolio_id, days)
            if daily_returns is None or daily_returns.empty:
                return None
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=daily_returns['date'],
                y=daily_returns['value'],
                mode='lines',
                name='Portfolio Value',
                line=dict(color='#1f77b4', width=2),
                fill='tozeroy',
                hovertemplate='<b>%{x}</b><br>Value: $%{y:,.2f}<extra></extra>'
            ))
            
            fig.update_layout(
                title='Portfolio Value Over Time',
                xaxis_title='Date',
                yaxis_title='Value ($)',
                height=500,
                hovermode='x unified',
                template='plotly_white'
            )
            
            return fig.to_html(include_plotlyjs='cdn')
        except Exception as e:
            print(f"Error creating portfolio value chart: {str(e)}")
        return None
    
    @staticmethod
    def create_price_chart(symbol: str, days: int = 90, asset_type: str = 'stock') -> Optional[str]:
        """
        Create candlestick chart for price data.
        
        Args:
            symbol: Stock ticker or crypto symbol
            days: Number of days to display
            asset_type: 'stock' or 'crypto'
            
        Returns:
            HTML string of plotly figure or None
        """
        try:
            prices_df = PriceTrackerService.get_historical_prices(symbol, days, asset_type)
            if prices_df.empty:
                return None
            
            prices_df['Date'] = pd.to_datetime(prices_df['Date'])
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=prices_df['Date'],
                y=prices_df['Close'],
                mode='lines',
                name='Close Price',
                line=dict(color='#1f77b4', width=2),
                hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Price: $%{y:,.2f}<extra></extra>'
            ))
            
            fig.update_layout(
                title=f'{symbol} Price Chart',
                xaxis_title='Date',
                yaxis_title='Price ($)',
                height=500,
                hovermode='x unified',
                template='plotly_white'
            )
            
            return fig.to_html(include_plotlyjs='cdn')
        except Exception as e:
            print(f"Error creating price chart: {str(e)}")
        return None
    
    @staticmethod
    def create_holdings_comparison_chart(portfolio_id: int) -> Optional[str]:
        """
        Create bar chart comparing holdings performance.
        
        Args:
            portfolio_id: ID of the portfolio
            
        Returns:
            HTML string of plotly figure or None
        """
        try:
            portfolio = Portfolio.query.get(portfolio_id)
            if not portfolio:
                return None
            
            symbols = []
            gains = []
            colors = []
            
            for holding in portfolio.holdings:
                perf = PortfolioAnalyticsService.calculate_holding_performance(holding.id)
                if perf:
                    symbols.append(perf['symbol'])
                    gains.append(perf['gain_loss_percent'])
                    colors.append('green' if perf['gain_loss_percent'] >= 0 else 'red')
            
            if not symbols:
                return None
            
            fig = go.Figure(data=[go.Bar(
                x=symbols,
                y=gains,
                marker=dict(color=colors),
                hovertemplate='<b>%{x}</b><br>Return: %{y:.2f}%<extra></extra>'
            )])
            
            fig.update_layout(
                title='Holdings Performance Comparison',
                xaxis_title='Symbol',
                yaxis_title='Return (%)',
                height=500,
                template='plotly_white'
            )
            
            return fig.to_html(include_plotlyjs='cdn')
        except Exception as e:
            print(f"Error creating comparison chart: {str(e)}")
        return None
    
    @staticmethod
    def create_asset_type_allocation_pie(portfolio_id: int) -> Optional[str]:
        """
        Create pie chart of asset type allocation.
        
        Args:
            portfolio_id: ID of the portfolio
            
        Returns:
            HTML string of plotly figure or None
        """
        try:
            allocation = PortfolioAnalyticsService.calculate_asset_type_allocation(portfolio_id)
            if not allocation:
                return None
            
            labels = list(allocation.keys())
            values = [allocation[asset_type]['value'] for asset_type in labels]
            percentages = [allocation[asset_type]['percentage'] for asset_type in labels]
            
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hovertemplate='<b>%{label}</b><br>Value: $%{value:,.2f}<br>%{customdata}%<extra></extra>',
                customdata=percentages
            )])
            
            fig.update_layout(
                title='Asset Type Allocation',
                height=500,
                font=dict(size=12)
            )
            
            return fig.to_html(include_plotlyjs='cdn')
        except Exception as e:
            print(f"Error creating asset type allocation chart: {str(e)}")
        return None
    
    @staticmethod
    def create_returns_distribution_histogram(portfolio_id: int, days: int = 90) -> Optional[str]:
        """
        Create histogram of daily returns distribution.
        
        Args:
            portfolio_id: ID of the portfolio
            days: Number of days
            
        Returns:
            HTML string of plotly figure or None
        """
        try:
            daily_returns = PortfolioAnalyticsService.calculate_daily_returns(portfolio_id, days)
            if daily_returns is None or daily_returns.empty:
                return None
            
            returns = daily_returns['daily_return'].dropna() * 100  # Convert to percentage
            
            fig = go.Figure(data=[go.Histogram(
                x=returns,
                nbinsx=50,
                marker=dict(color='#1f77b4'),
                hovertemplate='Return Range: %{x:.2f}%<br>Frequency: %{y}<extra></extra>'
            )])
            
            fig.update_layout(
                title='Daily Returns Distribution',
                xaxis_title='Daily Return (%)',
                yaxis_title='Frequency',
                height=500,
                template='plotly_white'
            )
            
            return fig.to_html(include_plotlyjs='cdn')
        except Exception as e:
            print(f"Error creating returns histogram: {str(e)}")
        return None
    
    @staticmethod
    def create_correlation_heatmap(symbols: List[str], days: int = 90, asset_types: Dict[str, str] = None) -> Optional[str]:
        """
        Create correlation heatmap for multiple assets.
        
        Args:
            symbols: List of symbols
            days: Number of days
            asset_types: Dict mapping symbols to asset types
            
        Returns:
            HTML string of plotly figure or None
        """
        try:
            from services.risk_metrics import RiskMetricsService
            
            correlation = RiskMetricsService.calculate_correlation_matrix(symbols, days, asset_types)
            if correlation is None:
                return None
            
            fig = go.Figure(data=go.Heatmap(
                z=correlation.values,
                x=correlation.columns,
                y=correlation.index,
                colorscale='RdBu',
                zmid=0,
                text=correlation.values,
                texttemplate='%{text:.2f}',
                textfont={"size": 10},
                hovertemplate='%{y} vs %{x}<br>Correlation: %{z:.3f}<extra></extra>'
            ))
            
            fig.update_layout(
                title='Asset Correlation Heatmap',
                xaxis_title='Assets',
                yaxis_title='Assets',
                height=600,
                width=700,
                template='plotly_white'
            )
            
            return fig.to_html(include_plotlyjs='cdn')
        except Exception as e:
            print(f"Error creating correlation heatmap: {str(e)}")
        return None
    
    @staticmethod
    def create_cumulative_returns_chart(portfolio_id: int, days: int = 90) -> Optional[str]:
        """
        Create cumulative returns chart.
        
        Args:
            portfolio_id: ID of the portfolio
            days: Number of days
            
        Returns:
            HTML string of plotly figure or None
        """
        try:
            daily_returns = PortfolioAnalyticsService.calculate_daily_returns(portfolio_id, days)
            if daily_returns is None or daily_returns.empty:
                return None
            
            daily_returns['cumulative_return'] = (1 + daily_returns['daily_return']).cumprod() - 1
            daily_returns['cumulative_return_percent'] = daily_returns['cumulative_return'] * 100
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=daily_returns['date'],
                y=daily_returns['cumulative_return_percent'],
                mode='lines',
                name='Cumulative Return',
                line=dict(color='#2ca02c', width=2),
                fill='tozeroy',
                hovertemplate='<b>%{x}</b><br>Return: %{y:.2f}%<extra></extra>'
            ))
            
            fig.update_layout(
                title='Cumulative Returns Over Time',
                xaxis_title='Date',
                yaxis_title='Cumulative Return (%)',
                height=500,
                hovermode='x unified',
                template='plotly_white'
            )
            
            return fig.to_html(include_plotlyjs='cdn')
        except Exception as e:
            print(f"Error creating cumulative returns chart: {str(e)}")
        return None
    
    @staticmethod
    def create_dashboard(portfolio_id: int) -> Optional[Dict]:
        """
        Create complete dashboard with multiple charts.
        
        Args:
            portfolio_id: ID of the portfolio
            
        Returns:
            Dict with HTML strings for different visualizations or None
        """
        try:
            return {
                'allocation_pie': VisualizationService.create_portfolio_allocation_pie(portfolio_id),
                'value_chart': VisualizationService.create_portfolio_value_chart(portfolio_id),
                'holdings_comparison': VisualizationService.create_holdings_comparison_chart(portfolio_id),
                'asset_type_allocation': VisualizationService.create_asset_type_allocation_pie(portfolio_id),
                'returns_histogram': VisualizationService.create_returns_distribution_histogram(portfolio_id),
                'cumulative_returns': VisualizationService.create_cumulative_returns_chart(portfolio_id)
            }
        except Exception as e:
            print(f"Error creating dashboard: {str(e)}")
        return None
