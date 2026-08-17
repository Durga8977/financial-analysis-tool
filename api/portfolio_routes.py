from flask import jsonify, request
from api import api_bp
from services import PortfolioAnalyticsService
from models import Portfolio, Holding

@api_bp.route('/portfolio/<int:portfolio_id>/value', methods=['GET'])
def get_portfolio_value(portfolio_id):
    """
    Get current portfolio value.
    """
    portfolio = Portfolio.query.get(portfolio_id)
    if not portfolio:
        return jsonify({'error': 'Portfolio not found'}), 404
    
    value = PortfolioAnalyticsService.calculate_portfolio_value(portfolio_id)
    
    if value is None:
        return jsonify({'error': 'Could not calculate portfolio value'}), 400
    
    return jsonify({
        'portfolio_id': portfolio_id,
        'portfolio_name': portfolio.name,
        'total_value': float(value)
    }), 200

@api_bp.route('/portfolio/<int:portfolio_id>/total-return', methods=['GET'])
def get_portfolio_total_return(portfolio_id):
    """
    Get total return metrics for portfolio.
    """
    portfolio = Portfolio.query.get(portfolio_id)
    if not portfolio:
        return jsonify({'error': 'Portfolio not found'}), 404
    
    return_data = PortfolioAnalyticsService.calculate_total_return(portfolio_id)
    
    if return_data is None:
        return jsonify({'error': 'Could not calculate total return'}), 400
    
    return jsonify({
        'portfolio_id': portfolio_id,
        'portfolio_name': portfolio.name,
        **{k: float(v) for k, v in return_data.items()}
    }), 200

@api_bp.route('/portfolio/<int:portfolio_id>/allocation', methods=['GET'])
def get_portfolio_allocation(portfolio_id):
    """
    Get asset allocation for portfolio.
    """
    portfolio = Portfolio.query.get(portfolio_id)
    if not portfolio:
        return jsonify({'error': 'Portfolio not found'}), 404
    
    allocation = PortfolioAnalyticsService.calculate_holding_allocation(portfolio_id)
    
    if allocation is None:
        return jsonify({'error': 'Could not calculate allocation'}), 400
    
    # Convert to JSON serializable
    for symbol in allocation:
        for key in allocation[symbol]:
            if isinstance(allocation[symbol][key], (int, float)):
                allocation[symbol][key] = float(allocation[symbol][key])
    
    return jsonify({
        'portfolio_id': portfolio_id,
        'portfolio_name': portfolio.name,
        'allocation': allocation
    }), 200

@api_bp.route('/portfolio/<int:portfolio_id>/asset-type-allocation', methods=['GET'])
def get_portfolio_asset_type_allocation(portfolio_id):
    """
    Get asset type allocation (stocks vs crypto, etc.).
    """
    portfolio = Portfolio.query.get(portfolio_id)
    if not portfolio:
        return jsonify({'error': 'Portfolio not found'}), 404
    
    allocation = PortfolioAnalyticsService.calculate_asset_type_allocation(portfolio_id)
    
    if allocation is None:
        return jsonify({'error': 'Could not calculate asset type allocation'}), 400
    
    # Convert to JSON serializable
    for asset_type in allocation:
        allocation[asset_type]['value'] = float(allocation[asset_type]['value'])
        allocation[asset_type]['percentage'] = float(allocation[asset_type]['percentage'])
    
    return jsonify({
        'portfolio_id': portfolio_id,
        'portfolio_name': portfolio.name,
        'asset_type_allocation': allocation
    }), 200

@api_bp.route('/portfolio/<int:portfolio_id>/performance-summary', methods=['GET'])
def get_portfolio_performance_summary(portfolio_id):
    """
    Get comprehensive portfolio performance summary.
    """
    portfolio = Portfolio.query.get(portfolio_id)
    if not portfolio:
        return jsonify({'error': 'Portfolio not found'}), 404
    
    summary = PortfolioAnalyticsService.calculate_portfolio_performance_summary(portfolio_id)
    
    if summary is None:
        return jsonify({'error': 'Could not calculate performance summary'}), 400
    
    # Convert numpy/pandas values to JSON serializable
    def convert_values(obj):
        if isinstance(obj, dict):
            return {k: convert_values(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_values(item) for item in obj]
        elif isinstance(obj, (int, float)):
            return float(obj)
        else:
            return obj
    
    summary = convert_values(summary)
    return jsonify(summary), 200

@api_bp.route('/holding/<int:holding_id>/performance', methods=['GET'])
def get_holding_performance(holding_id):
    """
    Get performance metrics for a single holding.
    """
    holding = Holding.query.get(holding_id)
    if not holding:
        return jsonify({'error': 'Holding not found'}), 404
    
    performance = PortfolioAnalyticsService.calculate_holding_performance(holding_id)
    
    if performance is None:
        return jsonify({'error': 'Could not calculate holding performance'}), 400
    
    # Convert to JSON serializable
    for key in performance:
        if isinstance(performance[key], (int, float)):
            performance[key] = float(performance[key])
    
    return jsonify(performance), 200

@api_bp.route('/portfolio/<int:portfolio_id>/top-gainers', methods=['GET'])
def get_portfolio_top_gainers(portfolio_id):
    """
    Get top performing holdings in portfolio.
    Query params: limit (default: 5)
    """
    portfolio = Portfolio.query.get(portfolio_id)
    if not portfolio:
        return jsonify({'error': 'Portfolio not found'}), 404
    
    limit = request.args.get('limit', 5, type=int)
    gainers = PortfolioAnalyticsService.get_top_gainers(portfolio_id, limit)
    
    if gainers is None:
        return jsonify({'error': 'Could not retrieve top gainers'}), 400
    
    # Convert to JSON serializable
    for gainer in gainers:
        for key in gainer:
            if isinstance(gainer[key], (int, float)):
                gainer[key] = float(gainer[key])
    
    return jsonify({
        'portfolio_id': portfolio_id,
        'portfolio_name': portfolio.name,
        'top_gainers': gainers
    }), 200

@api_bp.route('/portfolio/<int:portfolio_id>/top-losers', methods=['GET'])
def get_portfolio_top_losers(portfolio_id):
    """
    Get worst performing holdings in portfolio.
    Query params: limit (default: 5)
    """
    portfolio = Portfolio.query.get(portfolio_id)
    if not portfolio:
        return jsonify({'error': 'Portfolio not found'}), 404
    
    limit = request.args.get('limit', 5, type=int)
    losers = PortfolioAnalyticsService.get_top_losers(portfolio_id, limit)
    
    if losers is None:
        return jsonify({'error': 'Could not retrieve top losers'}), 400
    
    # Convert to JSON serializable
    for loser in losers:
        for key in loser:
            if isinstance(loser[key], (int, float)):
                loser[key] = float(loser[key])
    
    return jsonify({
        'portfolio_id': portfolio_id,
        'portfolio_name': portfolio.name,
        'top_losers': losers
    }), 200
