import pandas as pd
import numpy as np
from typing import Dict, Optional, List, Callable
from datetime import datetime, timedelta
from enum import Enum
from models import Portfolio, Holding, Transaction, BacktestResult
from app import db

class OrderType(Enum):
    """Order types for backtesting."""
    BUY = 'buy'
    SELL = 'sell'

class BacktestingEngine:
    """
    Engine for backtesting trading strategies against historical price data.
    """
    
    def __init__(self, initial_cash: float = 10000, commission: float = 0.001):
        """
        Initialize backtesting engine.
        
        Args:
            initial_cash: Starting cash amount
            commission: Trading commission as decimal (default 0.1%)
        """
        self.initial_cash = initial_cash
        self.commission = commission
        self.cash = initial_cash
        self.portfolio = {}
        self.trades = []
        self.equity_curve = []
        self.orders = []
    
    @staticmethod
    def simple_moving_average_strategy(prices: List[float], short_window: int = 20, long_window: int = 50) -> List[int]:
        """
        Simple Moving Average (SMA) crossover strategy.
        
        Args:
            prices: List of historical prices
            short_window: Short-term SMA window
            long_window: Long-term SMA window
            
        Returns:
            List of signals (1=buy, -1=sell, 0=hold)
        """
        df = pd.DataFrame({'price': prices})
        df['sma_short'] = df['price'].rolling(window=short_window).mean()
        df['sma_long'] = df['price'].rolling(window=long_window).mean()
        
        signals = [0] * len(prices)
        for i in range(long_window, len(prices)):
            if df['sma_short'].iloc[i] > df['sma_long'].iloc[i]:
                signals[i] = 1  # Buy signal
            elif df['sma_short'].iloc[i] < df['sma_long'].iloc[i]:
                signals[i] = -1  # Sell signal
        
        return signals
    
    @staticmethod
    def rsi_strategy(prices: List[float], window: int = 14, oversold: float = 30, overbought: float = 70) -> List[int]:
        """
        Relative Strength Index (RSI) strategy.
        
        Args:
            prices: List of historical prices
            window: RSI calculation window
            oversold: RSI threshold for oversold (buy signal)
            overbought: RSI threshold for overbought (sell signal)
            
        Returns:
            List of signals (1=buy, -1=sell, 0=hold)
        """
        df = pd.DataFrame({'price': prices})
        delta = df['price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        signals = [0] * len(prices)
        for i in range(window, len(prices)):
            if rsi.iloc[i] < oversold:
                signals[i] = 1  # Buy signal
            elif rsi.iloc[i] > overbought:
                signals[i] = -1  # Sell signal
        
        return signals
    
    @staticmethod
    def bollinger_bands_strategy(prices: List[float], window: int = 20, num_std: float = 2) -> List[int]:
        """
        Bollinger Bands strategy.
        
        Args:
            prices: List of historical prices
            window: Moving average window
            num_std: Number of standard deviations
            
        Returns:
            List of signals (1=buy, -1=sell, 0=hold)
        """
        df = pd.DataFrame({'price': prices})
        sma = df['price'].rolling(window=window).mean()
        std = df['price'].rolling(window=window).std()
        upper_band = sma + (std * num_std)
        lower_band = sma - (std * num_std)
        
        signals = [0] * len(prices)
        for i in range(window, len(prices)):
            if df['price'].iloc[i] < lower_band.iloc[i]:
                signals[i] = 1  # Buy signal
            elif df['price'].iloc[i] > upper_band.iloc[i]:
                signals[i] = -1  # Sell signal
        
        return signals
    
    def place_order(self, symbol: str, order_type: OrderType, quantity: int, price: float) -> bool:
        """
        Place an order (buy or sell).
        
        Args:
            symbol: Stock symbol
            order_type: BUY or SELL
            quantity: Number of shares
            price: Price per share
            
        Returns:
            True if order successful, False otherwise
        """
        commission_cost = quantity * price * self.commission
        
        if order_type == OrderType.BUY:
            total_cost = (quantity * price) + commission_cost
            if self.cash >= total_cost:
                self.cash -= total_cost
                if symbol not in self.portfolio:
                    self.portfolio[symbol] = 0
                self.portfolio[symbol] += quantity
                
                self.trades.append({
                    'symbol': symbol,
                    'type': 'buy',
                    'quantity': quantity,
                    'price': price,
                    'total': quantity * price,
                    'commission': commission_cost
                })
                return True
        
        elif order_type == OrderType.SELL:
            if symbol in self.portfolio and self.portfolio[symbol] >= quantity:
                proceeds = (quantity * price) - commission_cost
                self.cash += proceeds
                self.portfolio[symbol] -= quantity
                
                self.trades.append({
                    'symbol': symbol,
                    'type': 'sell',
                    'quantity': quantity,
                    'price': price,
                    'total': quantity * price,
                    'commission': commission_cost
                })
                return True
        
        return False
    
    def calculate_portfolio_value(self, prices: Dict[str, float]) -> float:
        """
        Calculate current portfolio value.
        
        Args:
            prices: Dict with symbol as key and current price as value
            
        Returns:
            Total portfolio value
        """
        holdings_value = sum(
            self.portfolio[symbol] * prices.get(symbol, 0)
            for symbol in self.portfolio
        )
        return self.cash + holdings_value
    
    def backtest(self, symbol: str, prices: List[float], signals: List[int], 
                 initial_shares: int = 0) -> Dict:
        """
        Run backtest with given signals.
        
        Args:
            symbol: Stock symbol
            prices: List of historical prices
            signals: List of signals (1=buy, -1=sell, 0=hold)
            initial_shares: Starting number of shares
            
        Returns:
            Dict with backtest results
        """
        self.cash = self.initial_cash
        self.portfolio = {symbol: initial_shares} if initial_shares > 0 else {}
        self.trades = []
        self.equity_curve = []
        
        for i in range(len(prices)):
            current_portfolio_value = self.calculate_portfolio_value({symbol: prices[i]})
            self.equity_curve.append(current_portfolio_value)
            
            if signals[i] == 1:  # Buy signal
                # Buy as many shares as possible
                max_shares = int(self.cash / (prices[i] * (1 + self.commission)))
                if max_shares > 0:
                    self.place_order(symbol, OrderType.BUY, max_shares, prices[i])
            
            elif signals[i] == -1:  # Sell signal
                # Sell all shares
                if symbol in self.portfolio and self.portfolio[symbol] > 0:
                    self.place_order(symbol, OrderType.SELL, self.portfolio[symbol], prices[i])
        
        return self.calculate_metrics(symbol, prices)
    
    def calculate_metrics(self, symbol: str, prices: List[float]) -> Dict:
        """
        Calculate backtest performance metrics.
        
        Args:
            symbol: Stock symbol
            prices: List of historical prices
            
        Returns:
            Dict with performance metrics
        """
        equity_array = np.array(self.equity_curve)
        returns = np.diff(equity_array) / equity_array[:-1]
        
        # Calculate metrics
        total_return = (self.equity_curve[-1] - self.initial_cash) / self.initial_cash
        annual_return = total_return * (252 / len(prices))
        volatility = np.std(returns) * np.sqrt(252)
        sharpe_ratio = (annual_return / volatility) if volatility > 0 else 0
        
        # Maximum drawdown
        cumulative_max = np.maximum.accumulate(equity_array)
        drawdown = (equity_array - cumulative_max) / cumulative_max
        max_drawdown = np.min(drawdown)
        
        # Number of trades
        num_trades = len(self.trades)
        winning_trades = sum(1 for t in self.trades if t['type'] == 'sell')
        losing_trades = num_trades - winning_trades
        
        return {
            'symbol': symbol,
            'initial_investment': self.initial_cash,
            'final_value': self.equity_curve[-1],
            'total_return': total_return,
            'total_return_percent': total_return * 100,
            'annual_return_percent': annual_return * 100,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'max_drawdown_percent': max_drawdown * 100,
            'num_trades': num_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': (winning_trades / num_trades) if num_trades > 0 else 0
        }
    
    @staticmethod
    def compare_strategies(symbol: str, prices: List[float], 
                          strategies: Dict[str, List[int]]) -> pd.DataFrame:
        """
        Compare multiple strategies.
        
        Args:
            symbol: Stock symbol
            prices: List of historical prices
            strategies: Dict with strategy names and signals
            
        Returns:
            DataFrame with comparison results
        """
        engine = BacktestingEngine()
        results = []
        
        for strategy_name, signals in strategies.items():
            result = engine.backtest(symbol, prices, signals)
            result['strategy'] = strategy_name
            results.append(result)
        
        return pd.DataFrame(results)
