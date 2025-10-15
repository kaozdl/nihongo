"""
Pytest configuration and fixtures
"""
# Setup path for package imports
import sys
import os
_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _parent not in sys.path:
    sys.path.insert(0, _parent)

import pytest
import tempfile
from nihongo.app import app as flask_app
from nihongo.models import db
from nihongo.models.user import User
from nihongo.models.question import Question
from nihongo.models.section import Section
from nihongo.models.exam import Exam


@pytest.fixture
def app():
    """Create and configure a test Flask application"""
    # Create a temporary file for the database
    db_fd, db_path = tempfile.mkstemp()
    
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    flask_app.config['WTF_CSRF_ENABLED'] = False
    flask_app.config['SECRET_KEY'] = 'test-secret-key'
    
    # Create tables
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()
    
    # Clean up
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner"""
    return app.test_cli_runner()


@pytest.fixture
def auth_client(client, test_user):
    """Create an authenticated test client"""
    client.post('/login', data={
        'email': test_user['email'],
        'password': test_user['password']
    })
    return client


@pytest.fixture
def test_user(app):
    """Create a test user"""
    with app.app_context():
        user = User(email='test@example.com')
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()
        
        # Refresh to get ID
        db.session.refresh(user)
        user_id = user.id
        
    # Return a dict with user info since the object is detached
    return {'id': user_id, 'email': 'test@example.com', 'password': 'testpass123'}


@pytest.fixture
def test_admin(app):
    """Create a test admin user"""
    with app.app_context():
        admin = User(email='admin@example.com')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        
        db.session.refresh(admin)
        admin_id = admin.id
        
    return {'id': admin_id, 'email': 'admin@example.com', 'password': 'admin123'}


@pytest.fixture
def test_question(app, test_user):
    """Create a test question"""
    with app.app_context():
        question = Question(
            question_text='Test question?',
            answer_1='Answer 1',
            answer_2='Answer 2',
            answer_3='Answer 3',
            answer_4='Answer 4',
            correct_answer=1,
            explanation='Test explanation',
            created_by=test_user['id']
        )
        db.session.add(question)
        db.session.commit()
        
        db.session.refresh(question)
        question_id = question.id
        
    return question_id


@pytest.fixture
def test_section(app, test_question):
    """Create a test section with a question"""
    with app.app_context():
        from nihongo.models.section_question import SectionQuestion
        
        section = Section(name='Test Section', number_of_questions=1)
        db.session.add(section)
        db.session.commit()
        db.session.refresh(section)
        
        section_question = SectionQuestion(
            section_id=section.id,
            question_id=test_question,
            order=1
        )
        db.session.add(section_question)
        db.session.commit()
        
        section_id = section.id
        
    return section_id


@pytest.fixture
def test_exam(app, test_user, test_section):
    """Create a test exam"""
    with app.app_context():
        from nihongo.models.exam_section import ExamSection
        
        exam = Exam(
            name='Test Exam',
            created_by=test_user['id']
        )
        db.session.add(exam)
        db.session.commit()
        db.session.refresh(exam)
        
        exam_section = ExamSection(
            exam_id=exam.id,
            section_id=test_section,
            order=1
        )
        db.session.add(exam_section)
        db.session.commit()
        
        exam_id = exam.id
        
    return exam_id


@pytest.fixture
def sample_exam_json():
    """Sample exam JSON data for import testing"""
    return {
        "name": "Test Import Exam",
        "sections": [
            {
                "name": "Grammar",
                "questions": [
                    {
                        "question_text": "わたしは まいにち 七時___おきます。",
                        "answer_1": "に",
                        "answer_2": "で",
                        "answer_3": "を",
                        "answer_4": "が",
                        "correct_answer": 1,
                        "explanation": "Time particle に is used with specific times."
                    },
                    {
                        "question_text": "きのう えいが___みました。",
                        "answer_1": "に",
                        "answer_2": "で",
                        "answer_3": "を",
                        "answer_4": "が",
                        "correct_answer": 3,
                        "explanation": "The particle を marks the direct object."
                    }
                ]
            },
            {
                "name": "Vocabulary",
                "questions": [
                    {
                        "question_text": "あした テストが あります。だから、こんばん___します。",
                        "answer_1": "べんきょう",
                        "answer_2": "りょこう",
                        "answer_3": "しごと",
                        "answer_4": "かいもの",
                        "correct_answer": 1,
                        "explanation": "べんきょう (benkyou) means 'study'."
                    }
                ]
            }
        ]
    }

