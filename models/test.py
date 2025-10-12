from models import db
from datetime import datetime


class Test(db.Model):
    __tablename__ = 'tests'
    
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    test_answers = db.relationship('TestAnswer', backref='test', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Test {self.id} user={self.user_id} exam={self.exam_id}>'

