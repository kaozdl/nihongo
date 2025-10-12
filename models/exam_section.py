from models import db


class ExamSection(db.Model):
    __tablename__ = 'exam_sections'
    
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)
    order = db.Column(db.Integer, nullable=False, default=0)
    
    def __repr__(self):
        return f'<ExamSection exam={self.exam_id} section={self.section_id}>'

