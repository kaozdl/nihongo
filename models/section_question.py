from nihongo.models import db


class SectionQuestion(db.Model):
    __tablename__ = 'section_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    order = db.Column(db.Integer, nullable=False, default=0)
    
    def __repr__(self):
        return f'<SectionQuestion section={self.section_id} question={self.question_id}>'

