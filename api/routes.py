from flask import jsonify, request
from app import db, create_app
from models import User, Portfolio, Holding, Transaction, PriceAlert
from api import api_bp

# User Routes
@api_bp.route('/users', methods=['POST'])
def create_user():
    """
    Create a new user
    Request body: {"username": "...", "email": "..."}
    """
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email'):
        return jsonify({'error': 'Username and email are required'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409
    
    user = User(username=data['username'], email=data['email'])
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

@api_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    Get user by ID
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict()), 200

# Portfolio Routes
@api_bp.route('/portfolios', methods=['POST'])
def create_portfolio():
    """
    Create a new portfolio
    Request body: {"user_id": ..., "name": "...", "initial_investment": ...}
    """
    data = request.get_json()
    
    if not data or not data.get('user_id') or not data.get('name'):
        return jsonify({'error': 'User ID and portfolio name are required'}), 400
    
    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    portfolio = Portfolio(
        user_id=data['user_id'],
        name=data['name'],
        description=data.get('description'),
        initial_investment=data.get('initial_investment', 0.0)
    )
    db.session.add(portfolio)
    db.session.commit()
    
    return jsonify(portfolio.to_dict()), 201

@api_bp.route('/portfolios/<int:portfolio_id>', methods=['GET'])
def get_portfolio(portfolio_id):
    """
    Get portfolio by ID with holdings summary
    """
    portfolio = Portfolio.query.get(portfolio_id)
    if not portfolio:
        return jsonify({'error': 'Portfolio not found'}), 404
    
    portfolio_data = portfolio.to_dict()
    portfolio_data['holdings'] = [h.to_dict() for h in portfolio.holdings]
    
    return jsonify(portfolio_data), 200

# Holding Routes
@api_bp.route('/holdings', methods=['POST'])
def create_holding():
    """
    Create a new holding in a portfolio
    Request body: {"portfolio_id": ..., "symbol": "...", "quantity": ..., "asset_type": "stock|crypto"}
    """
    data = request.get_json()
    
    required_fields = ['portfolio_id', 'symbol', 'quantity', 'asset_type']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'error': f'Required fields: {required_fields}'}), 400
    
    portfolio = Portfolio.query.get(data['portfolio_id'])
    if not portfolio:
        return jsonify({'error': 'Portfolio not found'}), 404
    
    holding = Holding(
        portfolio_id=data['portfolio_id'],
        symbol=data['symbol'],
        quantity=data['quantity'],
        average_purchase_price=data.get('average_purchase_price', 0.0),
        asset_type=data['asset_type']
    )
    db.session.add(holding)
    db.session.commit()
    
    return jsonify(holding.to_dict()), 201

# Transaction Routes
@api_bp.route('/transactions', methods=['POST'])
def create_transaction():
    """
    Record a buy/sell transaction
    Request body: {"portfolio_id": ..., "symbol": "...", "transaction_type": "buy|sell", "quantity": ..., "price": ...}
    """
    data = request.get_json()
    
    required_fields = ['portfolio_id', 'symbol', 'transaction_type', 'quantity', 'price']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'error': f'Required fields: {required_fields}'}), 400
    
    portfolio = Portfolio.query.get(data['portfolio_id'])
    if not portfolio:
        return jsonify({'error': 'Portfolio not found'}), 404
    
    total_amount = data['quantity'] * data['price']
    
    transaction = Transaction(
        portfolio_id=data['portfolio_id'],
        symbol=data['symbol'],
        transaction_type=data['transaction_type'],
        quantity=data['quantity'],
        price=data['price'],
        total_amount=total_amount,
        transaction_date=data.get('transaction_date'),
        notes=data.get('notes')
    )
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify(transaction.to_dict()), 201

# Price Alert Routes
@api_bp.route('/alerts', methods=['POST'])
def create_alert():
    """
    Create a price alert
    Request body: {"user_id": ..., "symbol": "...", "alert_type": "above|below", "target_price": ...}
    """
    data = request.get_json()
    
    required_fields = ['user_id', 'symbol', 'alert_type', 'target_price']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'error': f'Required fields: {required_fields}'}), 400
    
    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    alert = PriceAlert(
        user_id=data['user_id'],
        symbol=data['symbol'],
        alert_type=data['alert_type'],
        target_price=data['target_price']
    )
    db.session.add(alert)
    db.session.commit()
    
    return jsonify(alert.to_dict()), 201

@api_bp.route('/alerts/<int:user_id>', methods=['GET'])
def get_user_alerts(user_id):
    """
    Get all alerts for a user
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    alerts = PriceAlert.query.filter_by(user_id=user_id).all()
    return jsonify([alert.to_dict() for alert in alerts]), 200
