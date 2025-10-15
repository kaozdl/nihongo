from nihongo.models import db


class Section(db.Model):
    __tablename__ = 'sections'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    number_of_questions = db.Column(db.Integer, nullable=False)
    
    # Relationships
    section_questions = db.relationship('SectionQuestion', backref='section', lazy=True, cascade='all, delete-orphan')
    exam_sections = db.relationship('ExamSection', backref='section', lazy=True)
    
    def __repr__(self):
        return f'<Section {self.name}>'

