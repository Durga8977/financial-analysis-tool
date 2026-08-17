from app import db
from datetime import datetime

class Holding(db.Model):
    __tablename__ = 'holdings'
    
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolios.id'), nullable=False, index=True)
    symbol = db.Column(db.String(20), nullable=False, index=True)  # e.g., AAPL, BTC-USD
    quantity = db.Column(db.Float, nullable=False, default=0.0)
    average_purchase_price = db.Column(db.Float, nullable=False, default=0.0)
    asset_type = db.Column(db.String(20), nullable=False)  # 'stock' or 'crypto'
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    price_history = db.relationship('PriceHistory', backref='holding', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'portfolio_id': self.portfolio_id,
            'symbol': self.symbol,
            'quantity': self.quantity,
            'average_purchase_price': self.average_purchase_price,
            'asset_type': self.asset_type,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Holding {self.symbol} x{self.quantity}>'
