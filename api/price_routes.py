from flask import jsonify, request
from api import api_bp
from services import PriceTrackerService
from models import Holding, Portfolio
from app import db

@api_bp.route('/prices/current/<symbol>', methods=['GET'])
def get_current_price(symbol):
    """
    Get current price for a symbol.
    Query params: asset_type (stock|crypto, default: stock)
    """
    asset_type = request.args.get('asset_type', 'stock')
    price = PriceTrackerService.get_current_price(symbol, asset_type)
    
    if price is None:
        return jsonify({'error': f'Could not fetch price for {symbol}'}), 404
    
    return jsonify({
        'symbol': symbol,
        'price': price,
        'asset_type': asset_type
    }), 200

@api_bp.route('/prices/historical/<symbol>', methods=['GET'])
def get_historical_prices(symbol):
    """
    Get historical prices for a symbol.
    Query params: days (default: 30), asset_type (stock|crypto)
    """
    days = request.args.get('days', 30, type=int)
    asset_type = request.args.get('asset_type', 'stock')
    
    df = PriceTrackerService.get_historical_prices(symbol, days, asset_type)
    
    if df.empty:
        return jsonify({'error': f'Could not fetch historical data for {symbol}'}), 404
    
    data = df.to_dict('records')
    for record in data:
        record['Date'] = record['Date'].isoformat() if hasattr(record['Date'], 'isoformat') else str(record['Date'])
    
    return jsonify({
        'symbol': symbol,
        'asset_type': asset_type,
        'days': days,
        'prices': data
    }), 200

@api_bp.route('/prices/change/<symbol>', methods=['GET'])
def get_price_change(symbol):
    """
    Get price change for a symbol.
    Query params: asset_type (stock|crypto), period (1d|1wk|1mo|3mo|1y)
    """
    asset_type = request.args.get('asset_type', 'stock')
    period = request.args.get('period', '1mo')
    
    change_data = PriceTrackerService.get_price_change(symbol, asset_type, period)
    
    if change_data is None:
        return jsonify({'error': f'Could not calculate price change for {symbol}'}), 404
    
    return jsonify(change_data), 200

@api_bp.route('/stock/info/<symbol>', methods=['GET'])
def get_stock_info(symbol):
    """
    Get comprehensive stock information.
    """
    info = PriceTrackerService.get_stock_info(symbol)
    
    if info is None:
        return jsonify({'error': f'Could not fetch stock info for {symbol}'}), 404
    
    return jsonify(info), 200

@api_bp.route('/holdings/<int:holding_id>/prices', methods=['GET'])
def get_holding_prices(holding_id):
    """
    Get price history for a holding.
    Query params: days (default: 30)
    """
    holding = Holding.query.get(holding_id)
    if not holding:
        return jsonify({'error': 'Holding not found'}), 404
    
    days = request.args.get('days', 30, type=int)
    prices = PriceTrackerService.get_holding_price_history(holding_id, days)
    
    return jsonify({
        'holding_id': holding_id,
        'symbol': holding.symbol,
        'asset_type': holding.asset_type,
        'days': days,
        'prices': prices
    }), 200

@api_bp.route('/portfolios/<int:portfolio_id>/update-prices', methods=['POST'])
def update_portfolio_prices(portfolio_id):
    """
    Update all prices for a portfolio.
    """
    portfolio = Portfolio.query.get(portfolio_id)
    if not portfolio:
        return jsonify({'error': 'Portfolio not found'}), 404
    
    success = PriceTrackerService.update_portfolio_prices(portfolio_id)
    
    if success:
        return jsonify({
            'message': f'Successfully updated prices for portfolio {portfolio_id}',
            'holdings_count': len(portfolio.holdings)
        }), 200
    else:
        return jsonify({'error': 'Failed to update portfolio prices'}), 500

@api_bp.route('/prices/compare', methods=['POST'])
def compare_prices():
    """
    Compare current prices for multiple symbols.
    Request body: {"symbols": ["AAPL", "BTC-USD", ...], "asset_types": {"AAPL": "stock", ...}}
    """
    data = request.get_json()
    symbols = data.get('symbols', [])
    asset_types = data.get('asset_types', {})
    
    if not symbols:
        return jsonify({'error': 'No symbols provided'}), 400
    
    prices = {}
    for symbol in symbols:
        asset_type = asset_types.get(symbol, 'stock')
        price = PriceTrackerService.get_current_price(symbol, asset_type)
        if price:
            prices[symbol] = {
                'price': price,
                'asset_type': asset_type
            }
    
    return jsonify({
        'symbols': prices,
        'count': len(prices),
        'timestamp': __import__('datetime').datetime.utcnow().isoformat()
    }), 200
