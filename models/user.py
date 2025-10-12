from models import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Relationships
    created_questions = db.relationship('Question', backref='creator', lazy=True, foreign_keys='Question.created_by')
    created_exams = db.relationship('Exam', backref='creator', lazy=True, foreign_keys='Exam.created_by')
    tests = db.relationship('Test', backref='user', lazy=True)
    test_answers = db.relationship('TestAnswer', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'

