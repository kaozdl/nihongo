from models import db
from datetime import datetime


class Exam(db.Model):
    __tablename__ = 'exams'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    exam_sections = db.relationship('ExamSection', backref='exam', lazy=True, cascade='all, delete-orphan')
    tests = db.relationship('Test', backref='exam', lazy=True)
    
    def __repr__(self):
        return f'<Exam {self.name}>'

