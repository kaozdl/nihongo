"""
Integration tests for complete workflows
"""
import pytest
import json
from io import BytesIO
from models import db
from models.test import Test
from models.test_answer import TestAnswer


@pytest.mark.integration
def test_complete_user_workflow(client, app):
    """Test complete workflow: register, login, take exam, view results"""
    # Register
    client.post('/register', data={
        'email': 'integration@test.com',
        'password': 'testpass',
        'password_confirm': 'testpass'
    })
    
    # Login
    response = client.post('/login', data={
        'email': 'integration@test.com',
        'password': 'testpass'
    }, follow_redirects=True)
    assert response.status_code == 200
    
    # View exams (should be empty)
    response = client.get('/exams')
    assert response.status_code == 200
    assert b'Available Exams' in response.data


@pytest.mark.integration
def test_admin_import_and_take_exam_workflow(auth_client, app, test_user, sample_exam_json):
    """Test admin imports exam and user takes it"""
    # Import exam
    json_str = json.dumps(sample_exam_json)
    data = {
        'file': (BytesIO(json_str.encode('utf-8')), 'exam.json')
    }
    
    response = auth_client.post(
        '/admin/import_exam/',
        data=data,
        content_type='multipart/form-data',
        follow_redirects=True
    )
    
    # Get exam ID
    with app.app_context():
        from models.exam import Exam
        exam = Exam.query.filter_by(name='Test Import Exam').first()
        assert exam is not None
        exam_id = exam.id
    
    # Start exam
    response = auth_client.post(
        f'/exam/{exam_id}/start',
        follow_redirects=True
    )
    assert response.status_code == 200
    
    # Get test ID
    with app.app_context():
        test = Test.query.filter_by(
            exam_id=exam_id,
            user_id=test_user['id']
        ).first()
        assert test is not None
        test_id = test.id
        
        # Get first question
        from models.section_question import SectionQuestion
        from models.exam_section import ExamSection
        
        exam_section = ExamSection.query.filter_by(exam_id=exam_id).first()
        section_question = SectionQuestion.query.filter_by(
            section_id=exam_section.section_id
        ).first()
        question_id = section_question.question_id
    
    # Answer question
    response = auth_client.post(f'/test/{test_id}/answer', data={
        'question_id': question_id,
        'selected_answer': 1
    })
    assert response.status_code == 200
    
    # Submit exam
    response = auth_client.post(
        f'/test/{test_id}/submit',
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'out of' in response.data


@pytest.mark.integration
def test_multiple_users_same_exam(client, app, test_exam):
    """Test multiple users taking the same exam"""
    users = []
    
    # Create two users
    for i in range(2):
        email = f'user{i}@test.com'
        password = 'testpass'
        
        client.post('/register', data={
            'email': email,
            'password': password,
            'password_confirm': password
        })
        
        users.append({'email': email, 'password': password})
    
    # Each user takes the exam
    for user in users:
        # Login
        client.post('/login', data={
            'email': user['email'],
            'password': user['password']
        })
        
        # Start exam
        response = client.post(
            f'/exam/{test_exam}/start',
            follow_redirects=True
        )
        assert response.status_code == 200
        
        # Logout
        client.get('/logout')
    
    # Verify two separate tests were created
    with app.app_context():
        test_count = Test.query.filter_by(exam_id=test_exam).count()
        assert test_count >= 2


@pytest.mark.integration
def test_incomplete_exam_resume(auth_client, app, test_user, test_exam, test_question):
    """Test resuming an incomplete exam"""
    # Start exam
    response = auth_client.post(
        f'/exam/{test_exam}/start',
        follow_redirects=True
    )
    
    with app.app_context():
        test = Test.query.filter_by(
            exam_id=test_exam,
            user_id=test_user['id'],
            completed_at=None
        ).first()
        test_id = test.id
    
    # Answer one question
    auth_client.post(f'/test/{test_id}/answer', data={
        'question_id': test_question,
        'selected_answer': 2
    })
    
    # Navigate away (simulate closing browser)
    auth_client.get('/exams')
    
    # Try to start exam again - should resume
    response = auth_client.post(
        f'/exam/{test_exam}/start',
        follow_redirects=True
    )
    
    # Should redirect to existing test
    assert f'/test/{test_id}' in response.request.path or b'Question' in response.data
    
    # Verify answer was saved
    with app.app_context():
        answer = TestAnswer.query.filter_by(
            test_id=test_id,
            question_id=test_question
        ).first()
        assert answer is not None
        assert answer.selected_answer == 2


@pytest.mark.integration
def test_exam_scoring(auth_client, app, test_user):
    """Test that exam scoring is calculated correctly"""
    # Create a simple exam with known questions
    with app.app_context():
        from models.exam import Exam
        from models.section import Section
        from models.question import Question
        from models.section_question import SectionQuestion
        from models.exam_section import ExamSection
        
        # Create exam
        exam = Exam(name='Scoring Test', created_by=test_user['id'])
        db.session.add(exam)
        db.session.commit()
        
        # Create section
        section = Section(name='Test Section', number_of_questions=3)
        db.session.add(section)
        db.session.commit()
        
        # Create 3 questions
        questions = []
        for i in range(3):
            q = Question(
                question_text=f'Question {i+1}',
                answer_1='A', answer_2='B', answer_3='C', answer_4='D',
                correct_answer=1,
                created_by=test_user['id']
            )
            db.session.add(q)
            questions.append(q)
        db.session.commit()
        
        # Link questions to section
        for i, q in enumerate(questions):
            sq = SectionQuestion(
                section_id=section.id,
                question_id=q.id,
                order=i+1
            )
            db.session.add(sq)
        
        # Link section to exam
        es = ExamSection(exam_id=exam.id, section_id=section.id, order=1)
        db.session.add(es)
        db.session.commit()
        
        exam_id = exam.id
        question_ids = [q.id for q in questions]
    
    # Start exam
    auth_client.post(f'/exam/{exam_id}/start')
    
    with app.app_context():
        test = Test.query.filter_by(exam_id=exam_id, user_id=test_user['id']).first()
        test_id = test.id
    
    # Answer 2 correctly, 1 incorrectly
    auth_client.post(f'/test/{test_id}/answer', data={
        'question_id': question_ids[0],
        'selected_answer': 1  # Correct
    })
    auth_client.post(f'/test/{test_id}/answer', data={
        'question_id': question_ids[1],
        'selected_answer': 1  # Correct
    })
    auth_client.post(f'/test/{test_id}/answer', data={
        'question_id': question_ids[2],
        'selected_answer': 2  # Incorrect
    })
    
    # Submit and view results
    response = auth_client.post(f'/test/{test_id}/submit', follow_redirects=True)
    
    # Check that score is 2/3
    assert b'2 out of 3' in response.data or b'2/3' in response.data


@pytest.mark.integration
def test_exam_with_multiple_sections(auth_client, app, test_user):
    """Test taking an exam with multiple sections"""
    with app.app_context():
        from models.exam import Exam
        from models.section import Section
        from models.question import Question
        from models.section_question import SectionQuestion
        from models.exam_section import ExamSection
        
        # Create exam
        exam = Exam(name='Multi-Section Test', created_by=test_user['id'])
        db.session.add(exam)
        db.session.commit()
        
        # Create 2 sections
        for section_num in range(1, 3):
            section = Section(
                name=f'Section {section_num}',
                number_of_questions=2
            )
            db.session.add(section)
            db.session.commit()
            
            # Add questions to section
            for q_num in range(2):
                q = Question(
                    question_text=f'S{section_num} Q{q_num+1}',
                    answer_1='A', answer_2='B', answer_3='C', answer_4='D',
                    correct_answer=1,
                    created_by=test_user['id']
                )
                db.session.add(q)
                db.session.commit()
                
                sq = SectionQuestion(
                    section_id=section.id,
                    question_id=q.id,
                    order=q_num+1
                )
                db.session.add(sq)
            
            # Link section to exam
            es = ExamSection(
                exam_id=exam.id,
                section_id=section.id,
                order=section_num
            )
            db.session.add(es)
        
        db.session.commit()
        exam_id = exam.id
    
    # Take the exam
    response = auth_client.post(f'/exam/{exam_id}/start', follow_redirects=True)
    assert response.status_code == 200
    
    # Should see both sections
    assert b'Section 1' in response.data
    assert b'Section 2' in response.data
    
    # Should see all 4 questions
    assert b'S1 Q1' in response.data
    assert b'S2 Q2' in response.data

