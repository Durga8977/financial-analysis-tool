from flask import jsonify, request
from api import api_bp
from services.backtesting import BacktestingEngine, OrderType
from services.price_tracker import PriceTrackerService
import pandas as pd

@api_bp.route('/backtest/sma-strategy', methods=['POST'])
def backtest_sma_strategy():
    """
    Backtest Simple Moving Average strategy.
    Request body: {"symbol": "AAPL", "days": 90, "short_window": 20, "long_window": 50, "initial_cash": 10000}
    """
    data = request.get_json()
    symbol = data.get('symbol')
    days = data.get('days', 90)
    short_window = data.get('short_window', 20)
    long_window = data.get('long_window', 50)
    initial_cash = data.get('initial_cash', 10000)
    asset_type = data.get('asset_type', 'stock')
    
    if not symbol:
        return jsonify({'error': 'Symbol required'}), 400
    
    # Get historical prices
    prices_df = PriceTrackerService.get_historical_prices(symbol, days, asset_type)
    if prices_df.empty:
        return jsonify({'error': f'Could not fetch prices for {symbol}'}), 404
    
    prices = prices_df['Close'].tolist()
    
    # Generate signals
    signals = BacktestingEngine.simple_moving_average_strategy(prices, short_window, long_window)
    
    # Run backtest
    engine = BacktestingEngine(initial_cash)
    results = engine.backtest(symbol, prices, signals)
    
    # Convert to JSON serializable
    for key in results:
        if isinstance(results[key], (float, np.floating)):
            results[key] = float(results[key])
    
    return jsonify({
        'strategy': 'SMA Crossover',
        'parameters': {
            'short_window': short_window,
            'long_window': long_window
        },
        'results': results
    }), 200

@api_bp.route('/backtest/rsi-strategy', methods=['POST'])
def backtest_rsi_strategy():
    """
    Backtest RSI strategy.
    Request body: {"symbol": "AAPL", "days": 90, "window": 14, "oversold": 30, "overbought": 70, "initial_cash": 10000}
    """
    data = request.get_json()
    symbol = data.get('symbol')
    days = data.get('days', 90)
    window = data.get('window', 14)
    oversold = data.get('oversold', 30)
    overbought = data.get('overbought', 70)
    initial_cash = data.get('initial_cash', 10000)
    asset_type = data.get('asset_type', 'stock')
    
    if not symbol:
        return jsonify({'error': 'Symbol required'}), 400
    
    # Get historical prices
    prices_df = PriceTrackerService.get_historical_prices(symbol, days, asset_type)
    if prices_df.empty:
        return jsonify({'error': f'Could not fetch prices for {symbol}'}), 404
    
    prices = prices_df['Close'].tolist()
    
    # Generate signals
    signals = BacktestingEngine.rsi_strategy(prices, window, oversold, overbought)
    
    # Run backtest
    engine = BacktestingEngine(initial_cash)
    results = engine.backtest(symbol, prices, signals)
    
    # Convert to JSON serializable
    for key in results:
        if isinstance(results[key], (float, np.floating)):
            results[key] = float(results[key])
    
    return jsonify({
        'strategy': 'RSI',
        'parameters': {
            'window': window,
            'oversold': oversold,
            'overbought': overbought
        },
        'results': results
    }), 200

@api_bp.route('/backtest/bollinger-bands-strategy', methods=['POST'])
def backtest_bollinger_bands_strategy():
    """
    Backtest Bollinger Bands strategy.
    Request body: {"symbol": "AAPL", "days": 90, "window": 20, "num_std": 2, "initial_cash": 10000}
    """
    data = request.get_json()
    symbol = data.get('symbol')
    days = data.get('days', 90)
    window = data.get('window', 20)
    num_std = data.get('num_std', 2)
    initial_cash = data.get('initial_cash', 10000)
    asset_type = data.get('asset_type', 'stock')
    
    if not symbol:
        return jsonify({'error': 'Symbol required'}), 400
    
    # Get historical prices
    prices_df = PriceTrackerService.get_historical_prices(symbol, days, asset_type)
    if prices_df.empty:
        return jsonify({'error': f'Could not fetch prices for {symbol}'}), 404
    
    prices = prices_df['Close'].tolist()
    
    # Generate signals
    signals = BacktestingEngine.bollinger_bands_strategy(prices, window, num_std)
    
    # Run backtest
    engine = BacktestingEngine(initial_cash)
    results = engine.backtest(symbol, prices, signals)
    
    # Convert to JSON serializable
    for key in results:
        if isinstance(results[key], (float, np.floating)):
            results[key] = float(results[key])
    
    return jsonify({
        'strategy': 'Bollinger Bands',
        'parameters': {
            'window': window,
            'num_std': num_std
        },
        'results': results
    }), 200

@api_bp.route('/backtest/compare-strategies', methods=['POST'])
def compare_strategies():
    """
    Compare multiple strategies.
    Request body: {"symbol": "AAPL", "days": 90, "initial_cash": 10000}
    """
    data = request.get_json()
    symbol = data.get('symbol')
    days = data.get('days', 90)
    initial_cash = data.get('initial_cash', 10000)
    asset_type = data.get('asset_type', 'stock')
    
    if not symbol:
        return jsonify({'error': 'Symbol required'}), 400
    
    # Get historical prices
    prices_df = PriceTrackerService.get_historical_prices(symbol, days, asset_type)
    if prices_df.empty:
        return jsonify({'error': f'Could not fetch prices for {symbol}'}), 404
    
    prices = prices_df['Close'].tolist()
    
    # Generate signals for all strategies
    strategies = {
        'SMA (20/50)': BacktestingEngine.simple_moving_average_strategy(prices, 20, 50),
        'RSI (14)': BacktestingEngine.rsi_strategy(prices, 14),
        'Bollinger Bands (20/2)': BacktestingEngine.bollinger_bands_strategy(prices, 20, 2)
    }
    
    # Compare strategies
    comparison_df = BacktestingEngine.compare_strategies(symbol, prices, strategies)
    
    # Convert to JSON serializable
    comparison_dict = comparison_df.to_dict('records')
    for record in comparison_dict:
        for key in record:
            if isinstance(record[key], (float, np.floating)):
                record[key] = float(record[key])
    
    return jsonify({
        'symbol': symbol,
        'days': days,
        'initial_cash': initial_cash,
        'strategies_comparison': comparison_dict
    }), 200

import numpy as np
