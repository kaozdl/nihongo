from models import db
from datetime import datetime


class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    question_image = db.Column(db.String(500), nullable=True)
    question_audio = db.Column(db.String(500), nullable=True)
    answer_1 = db.Column(db.String(500), nullable=False)
    answer_2 = db.Column(db.String(500), nullable=False)
    answer_3 = db.Column(db.String(500), nullable=False)
    answer_4 = db.Column(db.String(500), nullable=False)
    correct_answer = db.Column(db.Integer, nullable=False)  # 1, 2, 3, or 4
    explanation = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    section_questions = db.relationship('SectionQuestion', backref='question', lazy=True)
    test_answers = db.relationship('TestAnswer', backref='question', lazy=True)
    
    def __repr__(self):
        return f'<Question {self.id}: {self.question_text[:50]}>'

