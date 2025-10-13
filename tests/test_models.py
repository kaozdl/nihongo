"""
Tests for database models
"""
import pytest
from models import db
from models.user import User
from models.question import Question
from models.section import Section
from models.section_question import SectionQuestion
from models.exam import Exam
from models.exam_section import ExamSection
from models.test import Test
from models.test_answer import TestAnswer


@pytest.mark.models
def test_user_creation(app):
    """Test creating a user"""
    with app.app_context():
        user = User(email='newuser@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        assert user.id is not None
        assert user.email == 'newuser@example.com'
        assert user.password_hash is not None
        assert user.password_hash != 'password123'


@pytest.mark.models
def test_user_password_hashing(app):
    """Test password hashing and verification"""
    with app.app_context():
        user = User(email='test@example.com')
        user.set_password('secret')
        
        assert user.check_password('secret') is True
        assert user.check_password('wrong') is False


@pytest.mark.models
def test_user_repr(app):
    """Test user string representation"""
    with app.app_context():
        user = User(email='test@example.com')
        assert 'test@example.com' in repr(user)


@pytest.mark.models
def test_question_creation(app, test_user):
    """Test creating a question"""
    with app.app_context():
        question = Question(
            question_text='What is 2+2?',
            answer_1='3',
            answer_2='4',
            answer_3='5',
            answer_4='6',
            correct_answer=2,
            explanation='Basic math',
            created_by=test_user['id']
        )
        db.session.add(question)
        db.session.commit()
        
        assert question.id is not None
        assert question.question_text == 'What is 2+2?'
        assert question.correct_answer == 2
        assert question.created_at is not None
        assert question.updated_at is not None


@pytest.mark.models
def test_question_with_optional_fields(app, test_user):
    """Test question with image and audio URLs"""
    with app.app_context():
        question = Question(
            question_text='Test question',
            question_image='http://example.com/image.jpg',
            question_audio='http://example.com/audio.mp3',
            answer_1='A', answer_2='B', answer_3='C', answer_4='D',
            correct_answer=1,
            created_by=test_user['id']
        )
        db.session.add(question)
        db.session.commit()
        
        assert question.question_image == 'http://example.com/image.jpg'
        assert question.question_audio == 'http://example.com/audio.mp3'


@pytest.mark.models
def test_section_creation(app):
    """Test creating a section"""
    with app.app_context():
        section = Section(name='Grammar', number_of_questions=10)
        db.session.add(section)
        db.session.commit()
        
        assert section.id is not None
        assert section.name == 'Grammar'
        assert section.number_of_questions == 10


@pytest.mark.models
def test_section_question_relationship(app, test_user):
    """Test linking questions to sections"""
    with app.app_context():
        # Create question
        question = Question(
            question_text='Test',
            answer_1='A', answer_2='B', answer_3='C', answer_4='D',
            correct_answer=1,
            created_by=test_user['id']
        )
        db.session.add(question)
        
        # Create section
        section = Section(name='Test Section', number_of_questions=1)
        db.session.add(section)
        db.session.commit()
        
        # Link them
        sq = SectionQuestion(
            section_id=section.id,
            question_id=question.id,
            order=1
        )
        db.session.add(sq)
        db.session.commit()
        
        assert sq.id is not None
        assert sq.section_id == section.id
        assert sq.question_id == question.id


@pytest.mark.models
def test_exam_creation(app, test_user):
    """Test creating an exam"""
    with app.app_context():
        exam = Exam(name='JLPT N5', created_by=test_user['id'])
        db.session.add(exam)
        db.session.commit()
        
        assert exam.id is not None
        assert exam.name == 'JLPT N5'
        assert exam.created_at is not None


@pytest.mark.models
def test_exam_section_relationship(app, test_user):
    """Test linking sections to exams"""
    with app.app_context():
        exam = Exam(name='Test Exam', created_by=test_user['id'])
        section = Section(name='Grammar', number_of_questions=5)
        
        db.session.add_all([exam, section])
        db.session.commit()
        
        es = ExamSection(
            exam_id=exam.id,
            section_id=section.id,
            order=1
        )
        db.session.add(es)
        db.session.commit()
        
        assert es.id is not None
        assert es.exam_id == exam.id
        assert es.section_id == section.id


@pytest.mark.models
def test_test_creation(app, test_user, test_exam):
    """Test creating a test instance"""
    with app.app_context():
        test = Test(
            exam_id=test_exam,
            user_id=test_user['id']
        )
        db.session.add(test)
        db.session.commit()
        
        assert test.id is not None
        assert test.exam_id == test_exam
        assert test.user_id == test_user['id']
        assert test.started_at is not None
        assert test.completed_at is None


@pytest.mark.models
def test_test_answer_creation(app, test_user, test_question, test_exam):
    """Test creating a test answer"""
    with app.app_context():
        # Create test
        test = Test(exam_id=test_exam, user_id=test_user['id'])
        db.session.add(test)
        db.session.commit()
        
        # Create answer
        answer = TestAnswer(
            test_id=test.id,
            user_id=test_user['id'],
            question_id=test_question,
            selected_answer=2
        )
        db.session.add(answer)
        db.session.commit()
        
        assert answer.id is not None
        assert answer.selected_answer == 2
        assert answer.answered_at is not None


@pytest.mark.models
def test_user_relationships(app, test_user):
    """Test user relationships with other models"""
    with app.app_context():
        user = User.query.get(test_user['id'])
        
        # Create related objects
        question = Question(
            question_text='Test',
            answer_1='A', answer_2='B', answer_3='C', answer_4='D',
            correct_answer=1,
            created_by=user.id
        )
        exam = Exam(name='Test', created_by=user.id)
        
        db.session.add_all([question, exam])
        db.session.commit()
        
        # Check relationships
        assert len(user.created_questions) > 0
        assert len(user.created_exams) > 0


@pytest.mark.models
def test_cascade_delete_exam(app, test_user, test_exam):
    """Test that deleting an exam cascades properly"""
    with app.app_context():
        exam = Exam.query.get(test_exam)
        exam_sections_count = len(exam.exam_sections)
        
        assert exam_sections_count > 0
        
        db.session.delete(exam)
        db.session.commit()
        
        # ExamSections should be deleted
        remaining_sections = ExamSection.query.filter_by(exam_id=test_exam).count()
        assert remaining_sections == 0

