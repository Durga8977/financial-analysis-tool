from flask import jsonify, request
from api import api_bp
from services import RiskMetricsService
from models import Holding, Portfolio
import pandas as pd

@api_bp.route('/risk/volatility/<int:holding_id>', methods=['GET'])
def get_holding_volatility(holding_id):
    """
    Get volatility for a holding.
    Query params: days (default: 90)
    """
    holding = Holding.query.get(holding_id)
    if not holding:
        return jsonify({'error': 'Holding not found'}), 404
    
    days = request.args.get('days', 90, type=int)
    
    from services.price_tracker import PriceTrackerService
    prices_data = PriceTrackerService.get_historical_prices(holding.symbol, days, holding.asset_type)
    
    if prices_data.empty:
        return jsonify({'error': 'Could not fetch price data'}), 404
    
    prices = prices_data['Close'].tolist()
    volatility = RiskMetricsService.calculate_volatility(prices)
    
    if volatility is None:
        return jsonify({'error': 'Could not calculate volatility'}), 400
    
    return jsonify({
        'holding_id': holding_id,
        'symbol': holding.symbol,
        'volatility': float(volatility),
        'volatility_percent': float(volatility * 100),
        'period': 'annual',
        'days': days
    }), 200

@api_bp.route('/risk/sharpe-ratio/<int:holding_id>', methods=['GET'])
def get_holding_sharpe_ratio(holding_id):
    """
    Get Sharpe ratio for a holding.
    Query params: days (default: 90), risk_free_rate (default: 0.02)
    """
    holding = Holding.query.get(holding_id)
    if not holding:
        return jsonify({'error': 'Holding not found'}), 404
    
    days = request.args.get('days', 90, type=int)
    risk_free_rate = request.args.get('risk_free_rate', 0.02, type=float)
    
    from services.price_tracker import PriceTrackerService
    prices_data = PriceTrackerService.get_historical_prices(holding.symbol, days, holding.asset_type)
    
    if prices_data.empty:
        return jsonify({'error': 'Could not fetch price data'}), 404
    
    prices = prices_data['Close'].tolist()
    sharpe_ratio = RiskMetricsService.calculate_sharpe_ratio(prices, risk_free_rate)
    
    if sharpe_ratio is None:
        return jsonify({'error': 'Could not calculate Sharpe ratio'}), 400
    
    return jsonify({
        'holding_id': holding_id,
        'symbol': holding.symbol,
        'sharpe_ratio': float(sharpe_ratio),
        'risk_free_rate': risk_free_rate,
        'days': days
    }), 200

@api_bp.route('/risk/sortino-ratio/<int:holding_id>', methods=['GET'])
def get_holding_sortino_ratio(holding_id):
    """
    Get Sortino ratio for a holding.
    Query params: days (default: 90), risk_free_rate (default: 0.02)
    """
    holding = Holding.query.get(holding_id)
    if not holding:
        return jsonify({'error': 'Holding not found'}), 404
    
    days = request.args.get('days', 90, type=int)
    risk_free_rate = request.args.get('risk_free_rate', 0.02, type=float)
    
    from services.price_tracker import PriceTrackerService
    prices_data = PriceTrackerService.get_historical_prices(holding.symbol, days, holding.asset_type)
    
    if prices_data.empty:
        return jsonify({'error': 'Could not fetch price data'}), 404
    
    prices = prices_data['Close'].tolist()
    sortino_ratio = RiskMetricsService.calculate_sortino_ratio(prices, risk_free_rate)
    
    if sortino_ratio is None:
        return jsonify({'error': 'Could not calculate Sortino ratio'}), 400
    
    return jsonify({
        'holding_id': holding_id,
        'symbol': holding.symbol,
        'sortino_ratio': float(sortino_ratio),
        'risk_free_rate': risk_free_rate,
        'days': days
    }), 200

@api_bp.route('/risk/max-drawdown/<int:holding_id>', methods=['GET'])
def get_holding_max_drawdown(holding_id):
    """
    Get maximum drawdown for a holding.
    Query params: days (default: 90)
    """
    holding = Holding.query.get(holding_id)
    if not holding:
        return jsonify({'error': 'Holding not found'}), 404
    
    days = request.args.get('days', 90, type=int)
    
    from services.price_tracker import PriceTrackerService
    prices_data = PriceTrackerService.get_historical_prices(holding.symbol, days, holding.asset_type)
    
    if prices_data.empty:
        return jsonify({'error': 'Could not fetch price data'}), 404
    
    prices = prices_data['Close'].tolist()
    max_drawdown = RiskMetricsService.calculate_max_drawdown(prices)
    
    if max_drawdown is None:
        return jsonify({'error': 'Could not calculate max drawdown'}), 400
    
    return jsonify({
        'holding_id': holding_id,
        'symbol': holding.symbol,
        'max_drawdown': float(max_drawdown),
        'max_drawdown_percent': float(max_drawdown * 100),
        'days': days
    }), 200

@api_bp.route('/risk/value-at-risk/<int:holding_id>', methods=['GET'])
def get_holding_value_at_risk(holding_id):
    """
    Get Value at Risk (VaR) for a holding.
    Query params: days (default: 90), confidence_level (default: 0.95)
    """
    holding = Holding.query.get(holding_id)
    if not holding:
        return jsonify({'error': 'Holding not found'}), 404
    
    days = request.args.get('days', 90, type=int)
    confidence_level = request.args.get('confidence_level', 0.95, type=float)
    
    from services.price_tracker import PriceTrackerService
    prices_data = PriceTrackerService.get_historical_prices(holding.symbol, days, holding.asset_type)
    
    if prices_data.empty:
        return jsonify({'error': 'Could not fetch price data'}), 404
    
    prices = prices_data['Close'].tolist()
    var = RiskMetricsService.calculate_value_at_risk(prices, confidence_level)
    
    if var is None:
        return jsonify({'error': 'Could not calculate VaR'}), 400
    
    return jsonify({
        'holding_id': holding_id,
        'symbol': holding.symbol,
        'value_at_risk': float(var),
        'value_at_risk_percent': float(var * 100),
        'confidence_level': confidence_level,
        'days': days
    }), 200

@api_bp.route('/risk/holding-metrics/<int:holding_id>', methods=['GET'])
def get_holding_risk_metrics(holding_id):
    """
    Get all risk metrics for a holding.
    Query params: days (default: 90)
    """
    holding = Holding.query.get(holding_id)
    if not holding:
        return jsonify({'error': 'Holding not found'}), 404
    
    days = request.args.get('days', 90, type=int)
    
    metrics = RiskMetricsService.get_holding_risk_metrics(holding_id, days)
    
    if metrics is None:
        return jsonify({'error': 'Could not calculate risk metrics'}), 400
    
    # Convert numpy values to float
    for key in metrics:
        if metrics[key] is not None and key != 'symbol' and key != 'holding_id':
            try:
                metrics[key] = float(metrics[key])
            except (ValueError, TypeError):
                pass
    
    return jsonify(metrics), 200

@api_bp.route('/risk/portfolio-metrics/<int:portfolio_id>', methods=['GET'])
def get_portfolio_risk_metrics(portfolio_id):
    """
    Get all risk metrics for a portfolio.
    Query params: days (default: 90)
    """
    portfolio = Portfolio.query.get(portfolio_id)
    if not portfolio:
        return jsonify({'error': 'Portfolio not found'}), 404
    
    days = request.args.get('days', 90, type=int)
    
    metrics = RiskMetricsService.get_portfolio_risk_metrics(portfolio_id, days)
    
    if metrics is None:
        return jsonify({'error': 'Could not calculate portfolio risk metrics'}), 400
    
    # Convert numpy/pandas values to JSON serializable
    for key in metrics:
        if metrics[key] is not None:
            if isinstance(metrics[key], pd.DataFrame):
                metrics[key] = metrics[key].to_dict()
            else:
                try:
                    metrics[key] = float(metrics[key])
                except (ValueError, TypeError):
                    pass
    
    return jsonify(metrics), 200

@api_bp.route('/risk/correlation', methods=['POST'])
def get_correlation_matrix():
    """
    Get correlation matrix for multiple assets.
    Request body: {"symbols": ["AAPL", "MSFT", ...], "asset_types": {"AAPL": "stock", ...}}
    Query params: days (default: 90)
    """
    data = request.get_json()
    symbols = data.get('symbols', [])
    asset_types = data.get('asset_types', {})
    days = request.args.get('days', 90, type=int)
    
    if not symbols:
        return jsonify({'error': 'No symbols provided'}), 400
    
    correlation = RiskMetricsService.calculate_correlation_matrix(symbols, days, asset_types)
    
    if correlation is None:
        return jsonify({'error': 'Could not calculate correlation'}), 400
    
    return jsonify({
        'symbols': symbols,
        'days': days,
        'correlation_matrix': correlation.to_dict()
    }), 200
