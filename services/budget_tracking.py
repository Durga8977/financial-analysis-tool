from typing import Dict, Optional, List
from datetime import datetime, timedelta
from enum import Enum
from models import Budget, BudgetCategory, Expense, User
from app import db

class BudgetPeriod(Enum):
    """Budget period types."""
    DAILY = 'daily'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'
    QUARTERLY = 'quarterly'
    YEARLY = 'yearly'

class BudgetTrackingService:
    """
    Service for managing budgets and tracking expenses.
    """
    
    @staticmethod
    def create_budget(user_id: int, name: str, total_amount: float, period: BudgetPeriod,
                     start_date: datetime = None) -> Optional[Budget]:
        """
        Create a new budget.
        
        Args:
            user_id: User ID
            name: Budget name
            total_amount: Total budget amount
            period: Budget period (daily, weekly, monthly, etc.)
            start_date: Budget start date (default: today)
            
        Returns:
            Budget object or None
        """
        try:
            if start_date is None:
                start_date = datetime.utcnow()
            
            budget = Budget(
                user_id=user_id,
                name=name,
                total_amount=total_amount,
                period=period.value,
                start_date=start_date,
                created_at=datetime.utcnow()
            )
            db.session.add(budget)
            db.session.commit()
            return budget
        except Exception as e:
            print(f"Error creating budget: {str(e)}")
            db.session.rollback()
        return None
    
    @staticmethod
    def create_budget_category(budget_id: int, category_name: str, allocated_amount: float) -> Optional[BudgetCategory]:
        """
        Create a budget category with allocated amount.
        
        Args:
            budget_id: Budget ID
            category_name: Category name
            allocated_amount: Amount allocated to this category
            
        Returns:
            BudgetCategory object or None
        """
        try:
            category = BudgetCategory(
                budget_id=budget_id,
                category_name=category_name,
                allocated_amount=allocated_amount,
                spent_amount=0,
                created_at=datetime.utcnow()
            )
            db.session.add(category)
            db.session.commit()
            return category
        except Exception as e:
            print(f"Error creating budget category: {str(e)}")
            db.session.rollback()
        return None
    
    @staticmethod
    def add_expense(budget_id: int, category_id: int, amount: float, 
                   description: str = None) -> Optional[Expense]:
        """
        Add an expense to a budget category.
        
        Args:
            budget_id: Budget ID
            category_id: Budget Category ID
            amount: Expense amount
            description: Expense description
            
        Returns:
            Expense object or None
        """
        try:
            # Update category spent amount
            category = BudgetCategory.query.get(category_id)
            if not category or category.budget_id != budget_id:
                return None
            
            expense = Expense(
                budget_id=budget_id,
                category_id=category_id,
                amount=amount,
                description=description,
                date=datetime.utcnow(),
                created_at=datetime.utcnow()
            )
            
            category.spent_amount += amount
            
            db.session.add(expense)
            db.session.commit()
            return expense
        except Exception as e:
            print(f"Error adding expense: {str(e)}")
            db.session.rollback()
        return None
    
    @staticmethod
    def get_budget_summary(budget_id: int) -> Optional[Dict]:
        """
        Get comprehensive budget summary.
        
        Args:
            budget_id: Budget ID
            
        Returns:
            Dict with budget summary or None
        """
        try:
            budget = Budget.query.get(budget_id)
            if not budget:
                return None
            
            categories = BudgetCategory.query.filter_by(budget_id=budget_id).all()
            
            total_spent = sum(c.spent_amount for c in categories)
            total_allocated = sum(c.allocated_amount for c in categories)
            remaining = budget.total_amount - total_spent
            spent_percent = (total_spent / budget.total_amount * 100) if budget.total_amount > 0 else 0
            
            category_summaries = []
            for category in categories:
                category_spent_percent = (category.spent_amount / category.allocated_amount * 100) if category.allocated_amount > 0 else 0
                category_summaries.append({
                    'id': category.id,
                    'name': category.category_name,
                    'allocated': category.allocated_amount,
                    'spent': category.spent_amount,
                    'remaining': category.allocated_amount - category.spent_amount,
                    'spent_percent': category_spent_percent
                })
            
            return {
                'budget_id': budget_id,
                'name': budget.name,
                'period': budget.period,
                'total_budget': budget.total_amount,
                'total_allocated': total_allocated,
                'total_spent': total_spent,
                'total_remaining': remaining,
                'spent_percent': spent_percent,
                'categories': category_summaries
            }
        except Exception as e:
            print(f"Error getting budget summary: {str(e)}")
        return None
    
    @staticmethod
    def get_category_expenses(category_id: int, days: int = 30) -> Optional[List[Dict]]:
        """
        Get expenses for a category.
        
        Args:
            category_id: Budget Category ID
            days: Number of days to look back
            
        Returns:
            List of expenses or None
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            expenses = Expense.query.filter(
                Expense.category_id == category_id,
                Expense.date >= cutoff_date
            ).order_by(Expense.date.desc()).all()
            
            return [{
                'id': e.id,
                'amount': e.amount,
                'description': e.description,
                'date': e.date.isoformat(),
                'category_id': e.category_id
            } for e in expenses]
        except Exception as e:
            print(f"Error getting category expenses: {str(e)}")
        return None
    
    @staticmethod
    def get_budget_expenses(budget_id: int, days: int = 30) -> Optional[List[Dict]]:
        """
        Get all expenses for a budget.
        
        Args:
            budget_id: Budget ID
            days: Number of days to look back
            
        Returns:
            List of expenses or None
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            expenses = Expense.query.filter(
                Expense.budget_id == budget_id,
                Expense.date >= cutoff_date
            ).order_by(Expense.date.desc()).all()
            
            return [{
                'id': e.id,
                'amount': e.amount,
                'description': e.description,
                'date': e.date.isoformat(),
                'category_id': e.category_id
            } for e in expenses]
        except Exception as e:
            print(f"Error getting budget expenses: {str(e)}")
        return None
    
    @staticmethod
    def check_budget_alerts(budget_id: int) -> Dict:
        """
        Check if budget categories are approaching their limits.
        
        Args:
            budget_id: Budget ID
            
        Returns:
            Dict with alerts for categories over/near limits
        """
        try:
            budget = Budget.query.get(budget_id)
            if not budget:
                return {}
            
            categories = BudgetCategory.query.filter_by(budget_id=budget_id).all()
            alerts = []
            
            for category in categories:
                spent_percent = (category.spent_amount / category.allocated_amount * 100) if category.allocated_amount > 0 else 0
                
                if spent_percent >= 100:
                    alerts.append({
                        'category': category.category_name,
                        'status': 'over_budget',
                        'spent_percent': spent_percent,
                        'amount_over': category.spent_amount - category.allocated_amount
                    })
                elif spent_percent >= 80:
                    alerts.append({
                        'category': category.category_name,
                        'status': 'near_limit',
                        'spent_percent': spent_percent,
                        'amount_remaining': category.allocated_amount - category.spent_amount
                    })
            
            return {'alerts': alerts, 'total_alerts': len(alerts)}
        except Exception as e:
            print(f"Error checking budget alerts: {str(e)}")
        return {}
    
    @staticmethod
    def get_spending_by_category(budget_id: int) -> Optional[Dict]:
        """
        Get breakdown of spending by category.
        
        Args:
            budget_id: Budget ID
            
        Returns:
            Dict with spending by category or None
        """
        try:
            categories = BudgetCategory.query.filter_by(budget_id=budget_id).all()
            
            spending = {}
            for category in categories:
                spending[category.category_name] = {
                    'spent': category.spent_amount,
                    'allocated': category.allocated_amount,
                    'percent': (category.spent_amount / category.allocated_amount * 100) if category.allocated_amount > 0 else 0
                }
            
            return spending
        except Exception as e:
            print(f"Error getting spending breakdown: {str(e)}")
        return None
    
    @staticmethod
    def get_monthly_spending_trend(user_id: int, months: int = 6) -> Optional[List[Dict]]:
        """
        Get monthly spending trend for a user.
        
        Args:
            user_id: User ID
            months: Number of months to look back
            
        Returns:
            List of monthly summaries or None
        """
        try:
            budgets = Budget.query.filter_by(user_id=user_id).all()
            budget_ids = [b.id for b in budgets]
            
            if not budget_ids:
                return None
            
            cutoff_date = datetime.utcnow() - timedelta(days=30 * months)
            expenses = Expense.query.filter(
                Expense.budget_id.in_(budget_ids),
                Expense.date >= cutoff_date
            ).all()
            
            # Group by month
            monthly_data = {}
            for expense in expenses:
                month_key = expense.date.strftime('%Y-%m')
                if month_key not in monthly_data:
                    monthly_data[month_key] = 0
                monthly_data[month_key] += expense.amount
            
            return [{
                'month': month,
                'total_spent': amount
            } for month, amount in sorted(monthly_data.items())]
        except Exception as e:
            print(f"Error getting monthly spending trend: {str(e)}")
        return None
    
    @staticmethod
    def update_budget(budget_id: int, name: str = None, total_amount: float = None) -> bool:
        """
        Update a budget.
        
        Args:
            budget_id: Budget ID
            name: New budget name
            total_amount: New total amount
            
        Returns:
            True if successful, False otherwise
        """
        try:
            budget = Budget.query.get(budget_id)
            if not budget:
                return False
            
            if name is not None:
                budget.name = name
            if total_amount is not None:
                budget.total_amount = total_amount
            
            db.session.commit()
            return True
        except Exception as e:
            print(f"Error updating budget: {str(e)}")
            db.session.rollback()
        return False
    
    @staticmethod
    def delete_budget(budget_id: int) -> bool:
        """
        Delete a budget and all associated data.
        
        Args:
            budget_id: Budget ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            budget = Budget.query.get(budget_id)
            if not budget:
                return False
            
            # Delete all expenses
            Expense.query.filter_by(budget_id=budget_id).delete()
            
            # Delete all categories
            BudgetCategory.query.filter_by(budget_id=budget_id).delete()
            
            # Delete budget
            db.session.delete(budget)
            db.session.commit()
            return True
        except Exception as e:
            print(f"Error deleting budget: {str(e)}")
            db.session.rollback()
        return False
