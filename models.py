from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Order(db.Model):
    """Model for production orders"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to time logs
    time_logs = db.relationship('TimeLog', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order {self.order_number}>'


class ProductionStage(db.Model):
    """Model for different production stages"""
    __tablename__ = 'production_stages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Relationship to time logs
    time_logs = db.relationship('TimeLog', backref='stage', lazy=True)
    
    def __repr__(self):
        return f'<ProductionStage {self.name}>'


class TimeLog(db.Model):
    """Model for tracking work time on orders"""
    __tablename__ = 'time_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    stage_id = db.Column(db.Integer, db.ForeignKey('production_stages.id'), nullable=False)
    worker_name = db.Column(db.String(100), nullable=False)
    
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='in_progress')  # in_progress, paused, completed
    
    def __repr__(self):
        return f'<TimeLog {self.id} - Order: {self.order_id}, Stage: {self.stage_id}>'
    
    @property
    def duration_minutes(self):
        """Calculate duration in minutes"""
        if self.end_time:
            delta = self.end_time - self.start_time
            return round(delta.total_seconds() / 60, 2)
        return None
