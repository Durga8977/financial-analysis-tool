from flask import jsonify, request
from api import api_bp
from services.budget_tracking import BudgetTrackingService, BudgetPeriod
from models import Budget

@api_bp.route('/budget/create', methods=['POST'])
def create_budget():
    """
    Create a new budget.
    Request body: {"user_id": 1, "name": "Monthly Budget", "total_amount": 5000, "period": "monthly"}
    """
    data = request.get_json()
    user_id = data.get('user_id')
    name = data.get('name')
    total_amount = data.get('total_amount')
    period_str = data.get('period', 'monthly')
    
    if not all([user_id, name, total_amount]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        period = BudgetPeriod(period_str)
    except ValueError:
        return jsonify({'error': f'Invalid period. Must be one of: {[p.value for p in BudgetPeriod]}'}), 400
    
    budget = BudgetTrackingService.create_budget(
        user_id=user_id,
        name=name,
        total_amount=total_amount,
        period=period
    )
    
    if not budget:
        return jsonify({'error': 'Failed to create budget'}), 500
    
    return jsonify({
        'message': 'Budget created successfully',
        'budget_id': budget.id,
        'name': name,
        'total_amount': total_amount,
        'period': period_str
    }), 201

@api_bp.route('/budget/<int:budget_id>/category/create', methods=['POST'])
def create_budget_category(budget_id):
    """
    Create a budget category.
    Request body: {"category_name": "Groceries", "allocated_amount": 500}
    """
    budget = Budget.query.get(budget_id)
    if not budget:
        return jsonify({'error': 'Budget not found'}), 404
    
    data = request.get_json()
    category_name = data.get('category_name')
    allocated_amount = data.get('allocated_amount')
    
    if not all([category_name, allocated_amount]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    category = BudgetTrackingService.create_budget_category(
        budget_id=budget_id,
        category_name=category_name,
        allocated_amount=allocated_amount
    )
    
    if not category:
        return jsonify({'error': 'Failed to create category'}), 500
    
    return jsonify({
        'message': 'Category created successfully',
        'category_id': category.id,
        'category_name': category_name,
        'allocated_amount': allocated_amount
    }), 201

@api_bp.route('/budget/<int:budget_id>/expense/add', methods=['POST'])
def add_expense(budget_id):
    """
    Add an expense to a budget category.
    Request body: {"category_id": 1, "amount": 50, "description": "Weekly groceries"}
    """
    budget = Budget.query.get(budget_id)
    if not budget:
        return jsonify({'error': 'Budget not found'}), 404
    
    data = request.get_json()
    category_id = data.get('category_id')
    amount = data.get('amount')
    description = data.get('description')
    
    if not all([category_id, amount]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    expense = BudgetTrackingService.add_expense(
        budget_id=budget_id,
        category_id=category_id,
        amount=amount,
        description=description
    )
    
    if not expense:
        return jsonify({'error': 'Failed to add expense'}), 500
    
    return jsonify({
        'message': 'Expense added successfully',
        'expense_id': expense.id,
        'amount': amount,
        'description': description
    }), 201

@api_bp.route('/budget/<int:budget_id>/summary', methods=['GET'])
def get_budget_summary(budget_id):
    """
    Get budget summary with all categories and spending.
    """
    budget = Budget.query.get(budget_id)
    if not budget:
        return jsonify({'error': 'Budget not found'}), 404
    
    summary = BudgetTrackingService.get_budget_summary(budget_id)
    
    if not summary:
        return jsonify({'error': 'Could not retrieve budget summary'}), 500
    
    return jsonify(summary), 200

@api_bp.route('/budget/<int:budget_id>/alerts', methods=['GET'])
def get_budget_alerts(budget_id):
    """
    Check for budget alerts (over budget or near limit).
    """
    budget = Budget.query.get(budget_id)
    if not budget:
        return jsonify({'error': 'Budget not found'}), 404
    
    alerts = BudgetTrackingService.check_budget_alerts(budget_id)
    
    return jsonify({
        'budget_id': budget_id,
        **alerts
    }), 200

@api_bp.route('/budget/<int:budget_id>/spending-breakdown', methods=['GET'])
def get_spending_breakdown(budget_id):
    """
    Get spending breakdown by category.
    """
    budget = Budget.query.get(budget_id)
    if not budget:
        return jsonify({'error': 'Budget not found'}), 404
    
    spending = BudgetTrackingService.get_spending_by_category(budget_id)
    
    if not spending:
        return jsonify({'error': 'Could not retrieve spending data'}), 500
    
    return jsonify({
        'budget_id': budget_id,
        'spending_by_category': spending
    }), 200

@api_bp.route('/budget/<int:budget_id>/expenses', methods=['GET'])
def get_budget_expenses(budget_id):
    """
    Get all expenses for a budget.
    Query params: days (default: 30)
    """
    budget = Budget.query.get(budget_id)
    if not budget:
        return jsonify({'error': 'Budget not found'}), 404
    
    days = request.args.get('days', 30, type=int)
    expenses = BudgetTrackingService.get_budget_expenses(budget_id, days)
    
    if expenses is None:
        return jsonify({'error': 'Could not retrieve expenses'}), 500
    
    return jsonify({
        'budget_id': budget_id,
        'expenses_count': len(expenses),
        'period_days': days,
        'expenses': expenses
    }), 200

@api_bp.route('/budget/<int:budget_id>/update', methods=['PUT'])
def update_budget(budget_id):
    """
    Update budget details.
    Request body: {"name": "Updated Budget", "total_amount": 6000}
    """
    budget = Budget.query.get(budget_id)
    if not budget:
        return jsonify({'error': 'Budget not found'}), 404
    
    data = request.get_json()
    name = data.get('name')
    total_amount = data.get('total_amount')
    
    success = BudgetTrackingService.update_budget(budget_id, name, total_amount)
    
    if not success:
        return jsonify({'error': 'Failed to update budget'}), 500
    
    return jsonify({
        'message': 'Budget updated successfully',
        'budget_id': budget_id
    }), 200

@api_bp.route('/budget/<int:budget_id>/delete', methods=['DELETE'])
def delete_budget(budget_id):
    """
    Delete a budget and all associated data.
    """
    budget = Budget.query.get(budget_id)
    if not budget:
        return jsonify({'error': 'Budget not found'}), 404
    
    success = BudgetTrackingService.delete_budget(budget_id)
    
    if not success:
        return jsonify({'error': 'Failed to delete budget'}), 500
    
    return jsonify({
        'message': 'Budget deleted successfully',
        'budget_id': budget_id
    }), 200

@api_bp.route('/user/<int:user_id>/spending-trend', methods=['GET'])
def get_spending_trend(user_id):
    """
    Get monthly spending trend for a user.
    Query params: months (default: 6)
    """
    months = request.args.get('months', 6, type=int)
    
    trend = BudgetTrackingService.get_monthly_spending_trend(user_id, months)
    
    if not trend:
        return jsonify({'error': 'Could not retrieve spending trend'}), 500
    
    return jsonify({
        'user_id': user_id,
        'months': months,
        'monthly_summary': trend
    }), 200
