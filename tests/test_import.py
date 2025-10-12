"""
Tests for exam import functionality
"""
import pytest
import json
from io import BytesIO
from import_exam import import_exam_from_json, validate_exam_json
from models import db
from models.exam import Exam
from models.section import Section
from models.question import Question


@pytest.mark.exam_import
def test_import_exam_from_json_success(app, test_user, sample_exam_json):
    """Test successful import of exam from JSON"""
    with app.app_context():
        success, message, exam = import_exam_from_json(sample_exam_json, test_user['id'])
        
        assert success is True
        assert 'Successfully imported' in message
        assert exam is not None
        assert exam.name == 'Test Import Exam'


@pytest.mark.exam_import
def test_import_exam_creates_sections(app, test_user, sample_exam_json):
    """Test that import creates sections"""
    with app.app_context():
        success, message, exam = import_exam_from_json(sample_exam_json, test_user['id'])
        
        assert success is True
        sections = Section.query.join(
            Section.exam_sections
        ).filter_by(exam_id=exam.id).all()
        
        assert len(sections) == 2
        assert sections[0].name in ['Grammar', 'Vocabulary']


@pytest.mark.exam_import
def test_import_exam_creates_questions(app, test_user, sample_exam_json):
    """Test that import creates questions"""
    with app.app_context():
        initial_count = Question.query.count()
        
        success, message, exam = import_exam_from_json(sample_exam_json, test_user['id'])
        
        assert success is True
        final_count = Question.query.count()
        assert final_count == initial_count + 3  # 2 grammar + 1 vocab


@pytest.mark.exam_import
def test_import_exam_missing_name(app, test_user):
    """Test import fails with missing exam name"""
    bad_json = {"sections": []}
    
    with app.app_context():
        success, message, exam = import_exam_from_json(bad_json, test_user['id'])
        
        assert success is False
        assert 'name' in message.lower()
        assert exam is None


@pytest.mark.exam_import
def test_import_exam_missing_sections(app, test_user):
    """Test import fails with missing sections"""
    bad_json = {"name": "Test"}
    
    with app.app_context():
        success, message, exam = import_exam_from_json(bad_json, test_user['id'])
        
        assert success is False
        assert 'sections' in message.lower()


@pytest.mark.exam_import
def test_import_exam_empty_sections(app, test_user):
    """Test import fails with empty sections array"""
    bad_json = {"name": "Test", "sections": []}
    
    with app.app_context():
        success, message, exam = import_exam_from_json(bad_json, test_user['id'])
        
        assert success is False
        assert 'at least one section' in message.lower()


@pytest.mark.exam_import
def test_import_exam_section_without_questions(app, test_user):
    """Test import fails when section has no questions"""
    bad_json = {
        "name": "Test",
        "sections": [{"name": "Grammar"}]
    }
    
    with app.app_context():
        success, message, exam = import_exam_from_json(bad_json, test_user['id'])
        
        assert success is False
        assert 'questions' in message.lower()


@pytest.mark.exam_import
def test_import_exam_question_missing_fields(app, test_user):
    """Test import fails when question is missing required fields"""
    bad_json = {
        "name": "Test",
        "sections": [{
            "name": "Grammar",
            "questions": [{
                "question_text": "Test?",
                "answer_1": "A"
                # Missing other required fields
            }]
        }]
    }
    
    with app.app_context():
        success, message, exam = import_exam_from_json(bad_json, test_user['id'])
        
        assert success is False
        assert 'missing' in message.lower()


@pytest.mark.exam_import
def test_import_exam_invalid_correct_answer(app, test_user):
    """Test import fails with invalid correct_answer"""
    bad_json = {
        "name": "Test",
        "sections": [{
            "name": "Grammar",
            "questions": [{
                "question_text": "Test?",
                "answer_1": "A",
                "answer_2": "B",
                "answer_3": "C",
                "answer_4": "D",
                "correct_answer": 5  # Invalid
            }]
        }]
    }
    
    with app.app_context():
        success, message, exam = import_exam_from_json(bad_json, test_user['id'])
        
        assert success is False
        assert 'correct_answer' in message.lower()


@pytest.mark.exam_import
def test_import_exam_with_optional_fields(app, test_user):
    """Test import with optional question fields"""
    json_data = {
        "name": "Test Exam",
        "sections": [{
            "name": "Section 1",
            "questions": [{
                "question_text": "Test?",
                "question_image": "http://example.com/img.jpg",
                "question_audio": "http://example.com/audio.mp3",
                "answer_1": "A",
                "answer_2": "B",
                "answer_3": "C",
                "answer_4": "D",
                "correct_answer": 1,
                "explanation": "Test explanation"
            }]
        }]
    }
    
    with app.app_context():
        success, message, exam = import_exam_from_json(json_data, test_user['id'])
        
        assert success is True
        questions = Question.query.filter_by(created_by=test_user['id']).all()
        question = questions[-1]  # Get the latest
        
        assert question.question_image == "http://example.com/img.jpg"
        assert question.question_audio == "http://example.com/audio.mp3"
        assert question.explanation == "Test explanation"


@pytest.mark.exam_import
def test_import_exam_rollback_on_error(app, test_user):
    """Test that import rolls back on error"""
    bad_json = {
        "name": "Test",
        "sections": [{
            "name": "Grammar",
            "questions": [{
                "question_text": "Q1",
                "answer_1": "A", "answer_2": "B",
                "answer_3": "C", "answer_4": "D",
                "correct_answer": 1
            }, {
                "question_text": "Q2",
                "answer_1": "A"
                # Missing fields - should cause error
            }]
        }]
    }
    
    with app.app_context():
        initial_exam_count = Exam.query.count()
        initial_question_count = Question.query.count()
        
        success, message, exam = import_exam_from_json(bad_json, test_user['id'])
        
        assert success is False
        # Nothing should be created
        assert Exam.query.count() == initial_exam_count
        assert Question.query.count() == initial_question_count


@pytest.mark.exam_import
def test_validate_exam_json_valid(sample_exam_json):
    """Test validation of valid exam JSON"""
    valid, errors = validate_exam_json(sample_exam_json)
    assert valid is True
    assert len(errors) == 0


@pytest.mark.exam_import
def test_validate_exam_json_invalid():
    """Test validation of invalid exam JSON"""
    invalid_json = {"name": "Test"}  # Missing sections
    
    valid, errors = validate_exam_json(invalid_json)
    assert valid is False
    assert len(errors) > 0


@pytest.mark.exam_import
def test_validate_exam_json_not_dict():
    """Test validation fails for non-dictionary"""
    valid, errors = validate_exam_json([])
    assert valid is False
    assert 'object' in errors[0].lower()


@pytest.mark.exam_import
def test_import_exam_invalid_user_id(app):
    """Test import fails with invalid user ID"""
    json_data = {
        "name": "Test",
        "sections": [{
            "name": "Section",
            "questions": [{
                "question_text": "Q",
                "answer_1": "A", "answer_2": "B",
                "answer_3": "C", "answer_4": "D",
                "correct_answer": 1
            }]
        }]
    }
    
    with app.app_context():
        success, message, exam = import_exam_from_json(json_data, 99999)
        
        assert success is False
        assert 'not found' in message.lower()


@pytest.mark.exam_import
def test_import_multiple_sections_with_questions(app, test_user):
    """Test importing exam with multiple sections and questions"""
    json_data = {
        "name": "Multi-Section Exam",
        "sections": [
            {
                "name": "Section 1",
                "questions": [
                    {
                        "question_text": "Q1",
                        "answer_1": "A", "answer_2": "B",
                        "answer_3": "C", "answer_4": "D",
                        "correct_answer": 1
                    },
                    {
                        "question_text": "Q2",
                        "answer_1": "A", "answer_2": "B",
                        "answer_3": "C", "answer_4": "D",
                        "correct_answer": 2
                    }
                ]
            },
            {
                "name": "Section 2",
                "questions": [
                    {
                        "question_text": "Q3",
                        "answer_1": "A", "answer_2": "B",
                        "answer_3": "C", "answer_4": "D",
                        "correct_answer": 3
                    }
                ]
            }
        ]
    }
    
    with app.app_context():
        success, message, exam = import_exam_from_json(json_data, test_user['id'])
        
        assert success is True
        assert '2 sections' in message
        assert '3 questions' in message

