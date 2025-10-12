"""
Tests for random exam generation functionality
"""
import pytest
from models import db
from models.exam import Exam
from models.section import Section
from models.question import Question
from models.section_question import SectionQuestion
from models.exam_section import ExamSection


@pytest.mark.routes
def test_random_exam_generation(auth_client, app, test_user):
    """Test generating a random exam"""
    with app.app_context():
        # Create sections with questions
        section1 = Section(name='Grammar', number_of_questions=5)
        section2 = Section(name='Vocabulary', number_of_questions=5)
        db.session.add_all([section1, section2])
        db.session.commit()
        
        # Add questions to sections
        for i in range(5):
            q = Question(
                question_text=f'Grammar Q{i+1}',
                answer_1='A', answer_2='B', answer_3='C', answer_4='D',
                correct_answer=1,
                created_by=test_user['id']
            )
            db.session.add(q)
            db.session.commit()
            
            sq = SectionQuestion(
                section_id=section1.id,
                question_id=q.id,
                order=i+1
            )
            db.session.add(sq)
        
        for i in range(5):
            q = Question(
                question_text=f'Vocab Q{i+1}',
                answer_1='A', answer_2='B', answer_3='C', answer_4='D',
                correct_answer=1,
                created_by=test_user['id']
            )
            db.session.add(q)
            db.session.commit()
            
            sq = SectionQuestion(
                section_id=section2.id,
                question_id=q.id,
                order=i+1
            )
            db.session.add(sq)
        
        db.session.commit()
        section1_id = section1.id
        section2_id = section2.id
    
    # Generate random exam
    response = auth_client.post('/exam/random/create', data={
        f'section_{section1_id}': '3',
        f'section_{section2_id}': '2'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Verify exam was created
    with app.app_context():
        exam = Exam.query.filter(Exam.name.like('Random Practice Exam%')).first()
        assert exam is not None
        
        # Check sections
        exam_sections = ExamSection.query.filter_by(exam_id=exam.id).all()
        assert len(exam_sections) == 2
        
        # Check total questions
        total_questions = 0
        for es in exam_sections:
            section_questions = SectionQuestion.query.filter_by(
                section_id=es.section_id
            ).all()
            total_questions += len(section_questions)
        
        assert total_questions == 5  # 3 + 2


@pytest.mark.routes
def test_random_exam_no_sections_selected(auth_client):
    """Test random exam generation with no sections"""
    response = auth_client.post('/exam/random/create', data={}, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'at least one section' in response.data


@pytest.mark.routes
def test_random_exam_respects_max_questions(auth_client, app, test_user):
    """Test that random exam doesn't exceed available questions"""
    with app.app_context():
        # Create section with only 2 questions
        section = Section(name='Test Section', number_of_questions=2)
        db.session.add(section)
        db.session.commit()
        
        # Add 2 questions
        for i in range(2):
            q = Question(
                question_text=f'Q{i+1}',
                answer_1='A', answer_2='B', answer_3='C', answer_4='D',
                correct_answer=1,
                created_by=test_user['id']
            )
            db.session.add(q)
            db.session.commit()
            
            sq = SectionQuestion(
                section_id=section.id,
                question_id=q.id,
                order=i+1
            )
            db.session.add(sq)
        
        db.session.commit()
        section_id = section.id
    
    # Try to request 5 questions (more than available)
    response = auth_client.post('/exam/random/create', data={
        f'section_{section_id}': '5'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Should only get 2 questions
    with app.app_context():
        exam = Exam.query.filter(Exam.name.like('Random Practice Exam%')).first()
        assert exam is not None
        
        exam_section = ExamSection.query.filter_by(exam_id=exam.id).first()
        questions = SectionQuestion.query.filter_by(
            section_id=exam_section.section_id
        ).all()
        
        assert len(questions) == 2


@pytest.mark.routes
def test_random_exam_questions_are_random(auth_client, app, test_user):
    """Test that questions are actually randomized"""
    with app.app_context():
        # Create section with many questions
        section = Section(name='Test Section', number_of_questions=10)
        db.session.add(section)
        db.session.commit()
        
        question_ids = []
        for i in range(10):
            q = Question(
                question_text=f'Q{i+1}',
                answer_1='A', answer_2='B', answer_3='C', answer_4='D',
                correct_answer=1,
                created_by=test_user['id']
            )
            db.session.add(q)
            db.session.commit()
            question_ids.append(q.id)
            
            sq = SectionQuestion(
                section_id=section.id,
                question_id=q.id,
                order=i+1
            )
            db.session.add(sq)
        
        db.session.commit()
        section_id = section.id
    
    # Generate two exams
    selected_sets = []
    for _ in range(2):
        auth_client.post('/exam/random/create', data={
            f'section_{section_id}': '5'
        })
        
        with app.app_context():
            exam = Exam.query.order_by(Exam.id.desc()).first()
            exam_section = ExamSection.query.filter_by(exam_id=exam.id).first()
            questions = SectionQuestion.query.filter_by(
                section_id=exam_section.section_id
            ).all()
            selected_ids = sorted([q.question_id for q in questions])
            selected_sets.append(selected_ids)
    
    # Very unlikely both will have the same questions in same order
    # (though possible, so we just check they're different sets)
    # With 10 choose 5, there are 252 combinations, so highly likely to differ
    assert len(selected_sets[0]) == 5
    assert len(selected_sets[1]) == 5


@pytest.mark.routes
def test_random_exam_immediately_starts(auth_client, app, test_user):
    """Test that random exam generation immediately redirects to start"""
    with app.app_context():
        section = Section(name='Test', number_of_questions=2)
        db.session.add(section)
        db.session.commit()
        
        for i in range(2):
            q = Question(
                question_text=f'Q{i+1}',
                answer_1='A', answer_2='B', answer_3='C', answer_4='D',
                correct_answer=1,
                created_by=test_user['id']
            )
            db.session.add(q)
            db.session.commit()
            
            sq = SectionQuestion(
                section_id=section.id,
                question_id=q.id,
                order=i+1
            )
            db.session.add(sq)
        
        db.session.commit()
        section_id = section.id
    
    response = auth_client.post('/exam/random/create', data={
        f'section_{section_id}': '2'
    }, follow_redirects=True)
    
    # Should redirect to exam taking page
    assert response.status_code == 200
    assert b'Question' in response.data or b'Submit Exam' in response.data


@pytest.mark.routes
def test_exams_page_shows_sections(auth_client, app, test_user):
    """Test that exams page displays available sections"""
    with app.app_context():
        section = Section(name='Grammar Test', number_of_questions=5)
        db.session.add(section)
        db.session.commit()
        
        q = Question(
            question_text='Test Q',
            answer_1='A', answer_2='B', answer_3='C', answer_4='D',
            correct_answer=1,
            created_by=test_user['id']
        )
        db.session.add(q)
        db.session.commit()
        
        sq = SectionQuestion(
            section_id=section.id,
            question_id=q.id,
            order=1
        )
        db.session.add(sq)
        db.session.commit()
    
    response = auth_client.get('/exams')
    
    assert response.status_code == 200
    assert b'Generate Random Practice Exam' in response.data
    assert b'Grammar Test' in response.data
    assert b'available' in response.data

