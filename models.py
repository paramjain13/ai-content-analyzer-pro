from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    analyses = db.relationship('Analysis', backref='user', lazy=True, cascade='all, delete-orphan')
    collections = db.relationship('Collection', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'

class Collection(db.Model):
    __tablename__ = 'collections'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(20), default='#667eea')  # Hex color
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    analyses = db.relationship('Analysis', backref='collection', lazy=True)
    
    def __repr__(self):
        return f'<Collection {self.name}>'

class Analysis(db.Model):
    __tablename__ = 'analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    collection_id = db.Column(db.Integer, db.ForeignKey('collections.id'), nullable=True)
    
    # Document info
    title = db.Column(db.String(500), nullable=False)
    source_type = db.Column(db.String(50))
    source_url = db.Column(db.Text)
    doc_id = db.Column(db.String(100))
    
    # Summary data
    summary_format = db.Column(db.String(50))
    summary_mode = db.Column(db.String(50))
    summary_length = db.Column(db.String(50))
    
    # Results
    result_data = db.Column(db.Text)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    word_count = db.Column(db.Integer)
    reading_time = db.Column(db.String(50))
    
    # Organization
    tags = db.Column(db.String(500))
    is_favorite = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)  # User notes
    
    def set_result_data(self, data):
        """Store result data as JSON"""
        self.result_data = json.dumps(data)
    
    def get_result_data(self):
        """Get result data as dict"""
        if self.result_data:
            return json.loads(self.result_data)
        return {}
    
    def get_tags_list(self):
        """Get tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    
    def set_tags_list(self, tags_list):
        """Set tags from a list"""
        self.tags = ','.join(tags_list)
    
    def __repr__(self):
        return f'<Analysis {self.title}>'