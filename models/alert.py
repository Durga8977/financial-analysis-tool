from app import db
from datetime import datetime

class PriceAlert(db.Model):
    __tablename__ = 'price_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    symbol = db.Column(db.String(20), nullable=False, index=True)
    alert_type = db.Column(db.String(10), nullable=False)  # 'above' or 'below'
    target_price = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    triggered = db.Column(db.Boolean, nullable=False, default=False)
    triggered_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'symbol': self.symbol,
            'alert_type': self.alert_type,
            'target_price': self.target_price,
            'is_active': self.is_active,
            'triggered': self.triggered,
            'triggered_at': self.triggered_at.isoformat() if self.triggered_at else None,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<PriceAlert {self.symbol} {self.alert_type} {self.target_price}>'
