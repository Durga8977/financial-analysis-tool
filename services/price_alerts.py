from typing import Dict, Optional, List
from datetime import datetime, timedelta
from enum import Enum
from models import PriceAlert, Holding, Portfolio
from app import db
from services.price_tracker import PriceTrackerService
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class AlertType(Enum):
    """Types of price alerts."""
    PRICE_ABOVE = 'price_above'
    PRICE_BELOW = 'price_below'
    PERCENT_CHANGE = 'percent_change'
    VOLUME_SPIKE = 'volume_spike'

class PriceAlertService:
    """
    Service for managing and triggering price alerts.
    """
    
    # Email configuration (should be moved to environment variables)
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    
    @staticmethod
    def create_alert(symbol: str, alert_type: AlertType, threshold: float, 
                    user_email: str, asset_type: str = 'stock', 
                    portfolio_id: Optional[int] = None) -> Optional[PriceAlert]:
        """
        Create a new price alert.
        
        Args:
            symbol: Stock symbol or crypto symbol
            alert_type: Type of alert (PRICE_ABOVE, PRICE_BELOW, PERCENT_CHANGE)
            threshold: Alert threshold value
            user_email: Email to send alert to
            asset_type: 'stock' or 'crypto'
            portfolio_id: Optional portfolio ID
            
        Returns:
            PriceAlert object or None
        """
        try:
            alert = PriceAlert(
                symbol=symbol,
                alert_type=alert_type.value,
                threshold=threshold,
                user_email=user_email,
                asset_type=asset_type,
                portfolio_id=portfolio_id,
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.session.add(alert)
            db.session.commit()
            return alert
        except Exception as e:
            print(f"Error creating alert: {str(e)}")
            db.session.rollback()
        return None
    
    @staticmethod
    def check_price_above_alert(alert: PriceAlert) -> bool:
        """
        Check if price is above threshold.
        
        Args:
            alert: PriceAlert object
            
        Returns:
            True if alert should trigger, False otherwise
        """
        current_price = PriceTrackerService.get_current_price(alert.symbol, alert.asset_type)
        if current_price is None:
            return False
        
        return current_price >= alert.threshold
    
    @staticmethod
    def check_price_below_alert(alert: PriceAlert) -> bool:
        """
        Check if price is below threshold.
        
        Args:
            alert: PriceAlert object
            
        Returns:
            True if alert should trigger, False otherwise
        """
        current_price = PriceTrackerService.get_current_price(alert.symbol, alert.asset_type)
        if current_price is None:
            return False
        
        return current_price <= alert.threshold
    
    @staticmethod
    def check_percent_change_alert(alert: PriceAlert) -> bool:
        """
        Check if price has changed by threshold percent.
        
        Args:
            alert: PriceAlert object (threshold is percent change)
            
        Returns:
            True if alert should trigger, False otherwise
        """
        change_data = PriceTrackerService.get_price_change(alert.symbol, alert.asset_type, '1d')
        if change_data is None:
            return False
        
        percent_change = abs(change_data['change_percent'])
        return percent_change >= alert.threshold
    
    @staticmethod
    def check_alert(alert: PriceAlert) -> bool:
        """
        Check if alert condition is met.
        
        Args:
            alert: PriceAlert object
            
        Returns:
            True if alert should trigger, False otherwise
        """
        if not alert.is_active:
            return False
        
        alert_type = AlertType(alert.alert_type)
        
        if alert_type == AlertType.PRICE_ABOVE:
            return PriceAlertService.check_price_above_alert(alert)
        elif alert_type == AlertType.PRICE_BELOW:
            return PriceAlertService.check_price_below_alert(alert)
        elif alert_type == AlertType.PERCENT_CHANGE:
            return PriceAlertService.check_percent_change_alert(alert)
        
        return False
    
    @staticmethod
    def check_all_alerts() -> List[PriceAlert]:
        """
        Check all active alerts and return triggered ones.
        
        Returns:
            List of triggered alerts
        """
        active_alerts = PriceAlert.query.filter_by(is_active=True).all()
        triggered_alerts = []
        
        for alert in active_alerts:
            if PriceAlertService.check_alert(alert):
                triggered_alerts.append(alert)
                # Optionally deactivate single-use alerts
                # alert.is_active = False
                # db.session.commit()
        
        return triggered_alerts
    
    @staticmethod
    def send_email_alert(alert: PriceAlert, current_price: float) -> bool:
        """
        Send email notification for triggered alert.
        
        Args:
            alert: PriceAlert object
            current_price: Current price of the asset
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            subject = f"Price Alert: {alert.symbol}"
            
            alert_type = AlertType(alert.alert_type)
            if alert_type == AlertType.PRICE_ABOVE:
                message = f"Alert: {alert.symbol} price has risen above ${alert.threshold:.2f}\nCurrent price: ${current_price:.2f}"
            elif alert_type == AlertType.PRICE_BELOW:
                message = f"Alert: {alert.symbol} price has dropped below ${alert.threshold:.2f}\nCurrent price: ${current_price:.2f}"
            elif alert_type == AlertType.PERCENT_CHANGE:
                change_data = PriceTrackerService.get_price_change(alert.symbol, alert.asset_type)
                percent_change = change_data['change_percent'] if change_data else 0
                message = f"Alert: {alert.symbol} has changed by {percent_change:.2f}% (threshold: {alert.threshold:.2f}%)\nCurrent price: ${current_price:.2f}"
            else:
                message = f"Alert triggered for {alert.symbol}"
            
            # Email sending logic (requires SMTP configuration)
            # This is a placeholder - implement with actual email service
            print(f"Email alert sent to {alert.user_email}: {message}")
            return True
        except Exception as e:
            print(f"Error sending email alert: {str(e)}")
        
        return False
    
    @staticmethod
    def get_user_alerts(user_email: str) -> List[Dict]:
        """
        Get all alerts for a user.
        
        Args:
            user_email: User's email address
            
        Returns:
            List of alert dictionaries
        """
        try:
            alerts = PriceAlert.query.filter_by(user_email=user_email).all()
            return [{
                'id': a.id,
                'symbol': a.symbol,
                'alert_type': a.alert_type,
                'threshold': a.threshold,
                'asset_type': a.asset_type,
                'is_active': a.is_active,
                'created_at': a.created_at.isoformat()
            } for a in alerts]
        except Exception as e:
            print(f"Error retrieving alerts: {str(e)}")
        return []
    
    @staticmethod
    def get_portfolio_alerts(portfolio_id: int) -> List[Dict]:
        """
        Get all alerts for a portfolio.
        
        Args:
            portfolio_id: Portfolio ID
            
        Returns:
            List of alert dictionaries
        """
        try:
            alerts = PriceAlert.query.filter_by(portfolio_id=portfolio_id).all()
            return [{
                'id': a.id,
                'symbol': a.symbol,
                'alert_type': a.alert_type,
                'threshold': a.threshold,
                'is_active': a.is_active,
                'created_at': a.created_at.isoformat()
            } for a in alerts]
        except Exception as e:
            print(f"Error retrieving portfolio alerts: {str(e)}")
        return []
    
    @staticmethod
    def update_alert(alert_id: int, threshold: Optional[float] = None, 
                    is_active: Optional[bool] = None) -> bool:
        """
        Update an alert.
        
        Args:
            alert_id: Alert ID
            threshold: New threshold value
            is_active: New active status
            
        Returns:
            True if successful, False otherwise
        """
        try:
            alert = PriceAlert.query.get(alert_id)
            if not alert:
                return False
            
            if threshold is not None:
                alert.threshold = threshold
            if is_active is not None:
                alert.is_active = is_active
            
            db.session.commit()
            return True
        except Exception as e:
            print(f"Error updating alert: {str(e)}")
            db.session.rollback()
        return False
    
    @staticmethod
    def delete_alert(alert_id: int) -> bool:
        """
        Delete an alert.
        
        Args:
            alert_id: Alert ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            alert = PriceAlert.query.get(alert_id)
            if not alert:
                return False
            
            db.session.delete(alert)
            db.session.commit()
            return True
        except Exception as e:
            print(f"Error deleting alert: {str(e)}")
            db.session.rollback()
        return False
    
    @staticmethod
    def create_portfolio_alerts(portfolio_id: int, user_email: str, 
                               alert_type: AlertType, threshold: float) -> int:
        """
        Create alerts for all holdings in a portfolio.
        
        Args:
            portfolio_id: Portfolio ID
            user_email: User's email
            alert_type: Type of alert
            threshold: Alert threshold
            
        Returns:
            Number of alerts created
        """
        try:
            portfolio = Portfolio.query.get(portfolio_id)
            if not portfolio:
                return 0
            
            alerts_created = 0
            for holding in portfolio.holdings:
                alert = PriceAlertService.create_alert(
                    symbol=holding.symbol,
                    alert_type=alert_type,
                    threshold=threshold,
                    user_email=user_email,
                    asset_type=holding.asset_type,
                    portfolio_id=portfolio_id
                )
                if alert:
                    alerts_created += 1
            
            return alerts_created
        except Exception as e:
            print(f"Error creating portfolio alerts: {str(e)}")
        return 0
