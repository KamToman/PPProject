from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Association table for many-to-many relationship between User and ProductionStage
user_stages = db.Table('user_stages',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('stage_id', db.Integer, db.ForeignKey('production_stages.id'), primary_key=True)
)


class User(db.Model):
    """Model for system users with authentication and role management"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, designer, worker, manager
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship to production stages (for workers with multiple process assignments)
    assigned_stages = db.relationship('ProductionStage', secondary=user_stages, 
                                     backref=db.backref('assigned_users', lazy='dynamic'))
    
    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hash"""
        return check_password_hash(self.password_hash, password)
    
    def has_stage_access(self, stage_id):
        """Check if user has access to a specific production stage"""
        if self.role in ['admin', 'manager']:
            return True
        return any(stage.id == stage_id for stage in self.assigned_stages)
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'

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
