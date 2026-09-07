from flask import jsonify, request
from api import api_bp
from services.visualization import VisualizationService
from models import Portfolio

@api_bp.route('/visualizations/portfolio/<int:portfolio_id>/allocation-pie', methods=['GET'])
def get_allocation_pie(portfolio_id):
    """
    Get portfolio allocation pie chart.
    """
    portfolio = Portfolio.query.get(portfolio_id)
    if not portfolio:
        return jsonify({'error': 'Portfolio not found'}), 404
    
    chart_html = VisualizationService.create_portfolio_allocation_pie(portfolio_id)
    if not chart_html:
        return jsonify({'error': 'Could not create chart'}), 400
    
    return chart_html, 200, {'Content-Type': 'text/html'}

@api_bp.route('/visualizations/portfolio/<int:portfolio_id>/value-chart', methods=['GET'])
def get_value_chart(portfolio_id):
    """
    Get portfolio value over time chart.
    Query params: days (default: 90)
    """
    portfolio = Portfolio.query.get(portfolio_id)
    if not portfolio:
        return jsonify({'error': 'Portfolio not found'}), 404
    
    days = request.args.get('days', 90, type=int)
    chart_html = VisualizationService.create_portfolio_value_chart(portfolio_id, days)
    if not chart_html:
        return jsonify({'error': 'Could not create chart'}), 400
    
    return chart_html, 200, {'Content-Type': 'text/html'}

@api_bp.route('/visualizations/price-chart/<symbol>', methods=['GET'])
def get_price_chart(symbol):
    """
    Get price chart for a symbol.
    Query params: days (default: 90), asset_type (default: stock)
    """
    days = request.args.get('days', 90, type=int)
    asset_type = request.args.get('asset_type', 'stock')
    
    chart_html = VisualizationService.create_price_chart(symbol, days, asset_type)
    if not chart_html:
        return jsonify({'error': 'Could not create chart'}), 400
    
    return chart_html, 200, {'Content-Type': 'text/html'}

@api_bp.route('/visualizations/portfolio/<int:portfolio_id>/holdings-comparison', methods=['GET'])
def get_holdings_comparison(portfolio_id):
    """
    Get holdings performance comparison chart.
    """
    portfolio = Portfolio.query.get(portfolio_id)
    if not portfolio:
        return jsonify({'error': 'Portfolio not found'}), 404
    
    chart_html = VisualizationService.create_holdings_comparison_chart(portfolio_id)
    if not chart_html:
        return jsonify({'error': 'Could not create chart'}), 400
    
    return chart_html, 200, {'Content-Type': 'text/html'}

@api_bp.route('/visualizations/portfolio/<int:portfolio_id>/asset-type-allocation', methods=['GET'])
def get_asset_type_allocation(portfolio_id):
    """
    Get asset type allocation pie chart.
    """
    portfolio = Portfolio.query.get(portfolio_id)
    if not portfolio:
        return jsonify({'error': 'Portfolio not found'}), 404
    
    chart_html = VisualizationService.create_asset_type_allocation_pie(portfolio_id)
    if not chart_html:
        return jsonify({'error': 'Could not create chart'}), 400
    
    return chart_html, 200, {'Content-Type': 'text/html'}

@api_bp.route('/visualizations/portfolio/<int:portfolio_id>/returns-histogram', methods=['GET'])
def get_returns_histogram(portfolio_id):
    """
    Get returns distribution histogram.
    Query params: days (default: 90)
    """
    portfolio = Portfolio.query.get(portfolio_id)
    if not portfolio:
        return jsonify({'error': 'Portfolio not found'}), 404
    
    days = request.args.get('days', 90, type=int)
    chart_html = VisualizationService.create_returns_distribution_histogram(portfolio_id, days)
    if not chart_html:
        return jsonify({'error': 'Could not create chart'}), 400
    
    return chart_html, 200, {'Content-Type': 'text/html'}

@api_bp.route('/visualizations/correlation-heatmap', methods=['POST'])
def get_correlation_heatmap():
    """
    Get correlation heatmap for multiple assets.
    Request body: {"symbols": ["AAPL", "MSFT", ...], "asset_types": {"AAPL": "stock", ...}}
    Query params: days (default: 90)
    """
    data = request.get_json()
    symbols = data.get('symbols', [])
    asset_types = data.get('asset_types', {})
    days = request.args.get('days', 90, type=int)
    
    if not symbols:
        return jsonify({'error': 'No symbols provided'}), 400
    
    chart_html = VisualizationService.create_correlation_heatmap(symbols, days, asset_types)
    if not chart_html:
        return jsonify({'error': 'Could not create chart'}), 400
    
    return chart_html, 200, {'Content-Type': 'text/html'}

@api_bp.route('/visualizations/portfolio/<int:portfolio_id>/cumulative-returns', methods=['GET'])
def get_cumulative_returns(portfolio_id):
    """
    Get cumulative returns chart.
    Query params: days (default: 90)
    """
    portfolio = Portfolio.query.get(portfolio_id)
    if not portfolio:
        return jsonify({'error': 'Portfolio not found'}), 404
    
    days = request.args.get('days', 90, type=int)
    chart_html = VisualizationService.create_cumulative_returns_chart(portfolio_id, days)
    if not chart_html:
        return jsonify({'error': 'Could not create chart'}), 400
    
    return chart_html, 200, {'Content-Type': 'text/html'}

@api_bp.route('/visualizations/portfolio/<int:portfolio_id>/dashboard', methods=['GET'])
def get_portfolio_dashboard(portfolio_id):
    """
    Get complete portfolio dashboard with multiple visualizations.
    """
    portfolio = Portfolio.query.get(portfolio_id)
    if not portfolio:
        return jsonify({'error': 'Portfolio not found'}), 404
    
    dashboard = VisualizationService.create_dashboard(portfolio_id)
    if not dashboard:
        return jsonify({'error': 'Could not create dashboard'}), 400
    
    # Return as JSON with chart URLs to fetch individually
    return jsonify({
        'portfolio_id': portfolio_id,
        'portfolio_name': portfolio.name,
        'charts': {
            'allocation_pie': f'/api/visualizations/portfolio/{portfolio_id}/allocation-pie',
            'value_chart': f'/api/visualizations/portfolio/{portfolio_id}/value-chart',
            'holdings_comparison': f'/api/visualizations/portfolio/{portfolio_id}/holdings-comparison',
            'asset_type_allocation': f'/api/visualizations/portfolio/{portfolio_id}/asset-type-allocation',
            'returns_histogram': f'/api/visualizations/portfolio/{portfolio_id}/returns-histogram',
            'cumulative_returns': f'/api/visualizations/portfolio/{portfolio_id}/cumulative-returns'
        }
    }), 200
