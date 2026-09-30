from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    __allow_unmapped__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='Developer')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    assigned_issues = db.relationship('Issue', backref='assignee', lazy=True, foreign_keys='Issue.assigned_to_id')
    created_issues = db.relationship('Issue', backref='reporter', lazy=True, foreign_keys='Issue.reported_by_id')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Project(db.Model):
    __tablename__ = 'projects'
    __allow_unmapped__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    technology_stack = db.Column(db.String(200), default='Python, Flask, SQLite')
    status = db.Column(db.String(50), default='Active')
    repository_url = db.Column(db.String(250), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    issues = db.relationship('Issue', backref='project', cascade='all, delete-orphan', lazy=True)

class Issue(db.Model):
    __tablename__ = 'issues'
    __allow_unmapped__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    issue_type = db.Column(db.String(50), default='Bug')
    priority = db.Column(db.String(30), default='Medium')
    status = db.Column(db.String(30), default='Open')
    
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reported_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    comments = db.relationship('Comment', backref='issue', cascade='all, delete-orphan', lazy=True)

class Comment(db.Model):
    __tablename__ = 'comments'
    __allow_unmapped__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    issue_id = db.Column(db.Integer, db.ForeignKey('issues.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='comments')
