from flask import jsonify, request
from api import api_bp
from services.price_alerts import PriceAlertService, AlertType
from models import PriceAlert
from app import db

@api_bp.route('/alerts/create', methods=['POST'])
def create_alert():
    """
    Create a new price alert.
    Request body: {"symbol": "AAPL", "alert_type": "price_above", "threshold": 150, "user_email": "user@example.com", "asset_type": "stock"}
    """
    data = request.get_json()
    symbol = data.get('symbol')
    alert_type_str = data.get('alert_type')
    threshold = data.get('threshold')
    user_email = data.get('user_email')
    asset_type = data.get('asset_type', 'stock')
    portfolio_id = data.get('portfolio_id')
    
    if not all([symbol, alert_type_str, threshold, user_email]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        alert_type = AlertType(alert_type_str)
    except ValueError:
        return jsonify({'error': f'Invalid alert type. Must be one of: {[at.value for at in AlertType]}'}), 400
    
    alert = PriceAlertService.create_alert(
        symbol=symbol,
        alert_type=alert_type,
        threshold=threshold,
        user_email=user_email,
        asset_type=asset_type,
        portfolio_id=portfolio_id
    )
    
    if not alert:
        return jsonify({'error': 'Failed to create alert'}), 500
    
    return jsonify({
        'message': f'Alert created successfully',
        'alert_id': alert.id,
        'symbol': symbol,
        'alert_type': alert_type_str,
        'threshold': threshold
    }), 201

@api_bp.route('/alerts/user/<user_email>', methods=['GET'])
def get_user_alerts(user_email):
    """
    Get all alerts for a user.
    """
    alerts = PriceAlertService.get_user_alerts(user_email)
    
    return jsonify({
        'user_email': user_email,
        'alerts_count': len(alerts),
        'alerts': alerts
    }), 200

@api_bp.route('/alerts/portfolio/<int:portfolio_id>', methods=['GET'])
def get_portfolio_alerts(portfolio_id):
    """
    Get all alerts for a portfolio.
    """
    alerts = PriceAlertService.get_portfolio_alerts(portfolio_id)
    
    return jsonify({
        'portfolio_id': portfolio_id,
        'alerts_count': len(alerts),
        'alerts': alerts
    }), 200

@api_bp.route('/alerts/<int:alert_id>/update', methods=['PUT'])
def update_alert(alert_id):
    """
    Update an alert.
    Request body: {"threshold": 150, "is_active": true}
    """
    data = request.get_json()
    threshold = data.get('threshold')
    is_active = data.get('is_active')
    
    success = PriceAlertService.update_alert(alert_id, threshold, is_active)
    
    if not success:
        return jsonify({'error': 'Alert not found or update failed'}), 404
    
    return jsonify({
        'message': 'Alert updated successfully',
        'alert_id': alert_id
    }), 200

@api_bp.route('/alerts/<int:alert_id>/delete', methods=['DELETE'])
def delete_alert(alert_id):
    """
    Delete an alert.
    """
    success = PriceAlertService.delete_alert(alert_id)
    
    if not success:
        return jsonify({'error': 'Alert not found or deletion failed'}), 404
    
    return jsonify({
        'message': 'Alert deleted successfully',
        'alert_id': alert_id
    }), 200

@api_bp.route('/alerts/check-all', methods=['POST'])
def check_all_alerts():
    """
    Check all active alerts and send notifications.
    """
    triggered_alerts = PriceAlertService.check_all_alerts()
    
    results = []
    for alert in triggered_alerts:
        current_price = __import__('services.price_tracker', fromlist=['PriceTrackerService']).PriceTrackerService.get_current_price(
            alert.symbol, alert.asset_type
        )
        
        email_sent = PriceAlertService.send_email_alert(alert, current_price)
        results.append({
            'alert_id': alert.id,
            'symbol': alert.symbol,
            'alert_type': alert.alert_type,
            'current_price': current_price,
            'email_sent': email_sent
        })
    
    return jsonify({
        'triggered_alerts': len(results),
        'results': results
    }), 200

@api_bp.route('/alerts/portfolio/<int:portfolio_id>/create-for-all', methods=['POST'])
def create_portfolio_alerts(portfolio_id):
    """
    Create alerts for all holdings in a portfolio.
    Request body: {"alert_type": "price_above", "threshold": 150, "user_email": "user@example.com"}
    """
    data = request.get_json()
    alert_type_str = data.get('alert_type')
    threshold = data.get('threshold')
    user_email = data.get('user_email')
    
    if not all([alert_type_str, threshold, user_email]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        alert_type = AlertType(alert_type_str)
    except ValueError:
        return jsonify({'error': f'Invalid alert type. Must be one of: {[at.value for at in AlertType]}'}), 400
    
    alerts_created = PriceAlertService.create_portfolio_alerts(
        portfolio_id=portfolio_id,
        user_email=user_email,
        alert_type=alert_type,
        threshold=threshold
    )
    
    return jsonify({
        'message': f'Created {alerts_created} alerts for portfolio',
        'portfolio_id': portfolio_id,
        'alerts_created': alerts_created
    }), 201
