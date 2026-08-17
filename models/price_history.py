from app import db
from datetime import datetime

class PriceHistory(db.Model):
    __tablename__ = 'price_history'
    
    id = db.Column(db.Integer, primary_key=True)
    holding_id = db.Column(db.Integer, db.ForeignKey('holdings.id'), nullable=False, index=True)
    price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'holding_id': self.holding_id,
            'price': self.price,
            'timestamp': self.timestamp.isoformat()
        }
    
    def __repr__(self):
        return f'<PriceHistory {self.price} @ {self.timestamp}>'
