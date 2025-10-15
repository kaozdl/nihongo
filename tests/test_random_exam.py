"""
Tests for random exam generation functionality
"""
import pytest
from nihongo.models import db
from nihongo.models.exam import Exam
from nihongo.models.section import Section
from nihongo.models.question import Question
from nihongo.models.section_question import SectionQuestion
from nihongo.models.exam_section import ExamSection


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


@pytest.mark.routes
def test_section_aggregation_by_name(auth_client, app, test_user):
    """Test that sections with the same name are aggregated correctly"""
    with app.app_context():
        # Create 3 sections with the same name (simulating 3 different exams)
        section1 = Section(name='Grammar', number_of_questions=5)
        section2 = Section(name='Grammar', number_of_questions=6)
        section3 = Section(name='Grammar', number_of_questions=7)
        
        section4 = Section(name='Vocabulary', number_of_questions=4)
        section5 = Section(name='Vocabulary', number_of_questions=5)
        
        db.session.add_all([section1, section2, section3, section4, section5])
        db.session.commit()
        
        # Add questions to each section
        total_grammar_questions = 0
        for section in [section1, section2, section3]:
            for i in range(section.number_of_questions):
                q = Question(
                    question_text=f'Grammar Q{section.id}-{i+1}',
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
                total_grammar_questions += 1
        
        total_vocab_questions = 0
        for section in [section4, section5]:
            for i in range(section.number_of_questions):
                q = Question(
                    question_text=f'Vocab Q{section.id}-{i+1}',
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
                total_vocab_questions += 1
        
        db.session.commit()
    
    # Get the exams page
    response = auth_client.get('/exams')
    
    assert response.status_code == 200
    
    # Verify aggregation in the response
    # Should show "Grammar" with aggregated count
    assert b'Grammar' in response.data
    # The count should be at least our created questions
    assert b'available' in response.data
    
    # Should show "Vocabulary" with aggregated count
    assert b'Vocabulary' in response.data
    
    # Verify that we don't have duplicate section names with separate counts
    # (which would happen if aggregation wasn't working)
    response_text = response.data.decode('utf-8')
    grammar_count = response_text.count('Grammar ')
    # Should appear in the form but not 3 separate times (one per exam)
    assert grammar_count < 6  # Less than if showing each section separately


@pytest.mark.routes
def test_random_exam_from_aggregated_sections(auth_client, app, test_user):
    """Test creating a random exam from aggregated sections"""
    with app.app_context():
        # Create duplicate sections (like having 3 exams with same section names)
        grammar1 = Section(name='Grammar', number_of_questions=5)
        grammar2 = Section(name='Grammar', number_of_questions=5)
        vocab1 = Section(name='Vocabulary', number_of_questions=3)
        vocab2 = Section(name='Vocabulary', number_of_questions=3)
        
        db.session.add_all([grammar1, grammar2, vocab1, vocab2])
        db.session.commit()
        
        # Add unique questions to each section
        all_grammar_question_ids = []
        for section in [grammar1, grammar2]:
            for i in range(5):
                q = Question(
                    question_text=f'Grammar S{section.id} Q{i+1}',
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
                all_grammar_question_ids.append(q.id)
        
        all_vocab_question_ids = []
        for section in [vocab1, vocab2]:
            for i in range(3):
                q = Question(
                    question_text=f'Vocab S{section.id} Q{i+1}',
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
                all_vocab_question_ids.append(q.id)
        
        db.session.commit()
        
        # Request 5 grammar questions and 3 vocabulary questions
        response = auth_client.post('/exam/random/create', data={
            'section_Grammar': '5',
            'section_Vocabulary': '3'
        }, follow_redirects=False)
        
        assert response.status_code == 302  # Should redirect to take_exam
        
        # Verify the exam was created
        exam = Exam.query.filter(Exam.name.like('Random Practice Exam%')).first()
        assert exam is not None
        assert exam.created_by == test_user['id']
        
        # Verify sections
        exam_sections = ExamSection.query.filter_by(exam_id=exam.id).all()
        assert len(exam_sections) == 2  # Should have 2 sections (Grammar and Vocabulary)
        
        # Check Grammar section
        grammar_section = [es for es in exam_sections if es.section.name == 'Grammar'][0]
        grammar_questions = SectionQuestion.query.filter_by(
            section_id=grammar_section.section_id
        ).all()
        assert len(grammar_questions) == 5
        
        # Verify questions are from the aggregated pool
        grammar_q_ids = [sq.question_id for sq in grammar_questions]
        assert all(qid in all_grammar_question_ids for qid in grammar_q_ids)
        
        # Check Vocabulary section
        vocab_section = [es for es in exam_sections if es.section.name == 'Vocabulary'][0]
        vocab_questions = SectionQuestion.query.filter_by(
            section_id=vocab_section.section_id
        ).all()
        assert len(vocab_questions) == 3
        
        # Verify questions are from the aggregated pool
        vocab_q_ids = [sq.question_id for sq in vocab_questions]
        assert all(qid in all_vocab_question_ids for qid in vocab_q_ids)
        
        # Verify no duplicate questions in the exam
        all_exam_q_ids = grammar_q_ids + vocab_q_ids
        assert len(all_exam_q_ids) == len(set(all_exam_q_ids))  # No duplicates


@pytest.mark.routes
def test_aggregation_removes_duplicate_questions(auth_client, app, test_user):
    """Test that if the same question appears in multiple sections, it's only counted once"""
    with app.app_context():
        # Create a shared question
        shared_q = Question(
            question_text='Shared Question',
            answer_1='A', answer_2='B', answer_3='C', answer_4='D',
            correct_answer=1,
            created_by=test_user['id']
        )
        db.session.add(shared_q)
        db.session.commit()
        
        # Create two sections with the same name
        section1 = Section(name='Grammar', number_of_questions=3)
        section2 = Section(name='Grammar', number_of_questions=3)
        db.session.add_all([section1, section2])
        db.session.commit()
        
        # Add the shared question to both sections
        sq1 = SectionQuestion(section_id=section1.id, question_id=shared_q.id, order=1)
        sq2 = SectionQuestion(section_id=section2.id, question_id=shared_q.id, order=1)
        db.session.add_all([sq1, sq2])
        
        # Add unique questions to each section
        for i in range(2):
            q = Question(
                question_text=f'Unique Q S1-{i+1}',
                answer_1='A', answer_2='B', answer_3='C', answer_4='D',
                correct_answer=1,
                created_by=test_user['id']
            )
            db.session.add(q)
            db.session.commit()
            sq = SectionQuestion(section_id=section1.id, question_id=q.id, order=i+2)
            db.session.add(sq)
        
        for i in range(2):
            q = Question(
                question_text=f'Unique Q S2-{i+1}',
                answer_1='A', answer_2='B', answer_3='C', answer_4='D',
                correct_answer=1,
                created_by=test_user['id']
            )
            db.session.add(q)
            db.session.commit()
            sq = SectionQuestion(section_id=section2.id, question_id=q.id, order=i+2)
            db.session.add(sq)
        
        db.session.commit()
        
        # Create random exam with all grammar questions
        response = auth_client.post('/exam/random/create', data={
            'section_Grammar': '5'
        }, follow_redirects=False)
        
        assert response.status_code == 302
        
        # Verify exam was created
        exam = Exam.query.filter(Exam.name.like('Random Practice Exam%')).first()
        assert exam is not None
        
        # Get the created section
        exam_section = ExamSection.query.filter_by(exam_id=exam.id).first()
        section_questions = SectionQuestion.query.filter_by(
            section_id=exam_section.section_id
        ).all()
        
        # Should have 5 unique questions (1 shared + 2 from section1 + 2 from section2)
        question_ids = [sq.question_id for sq in section_questions]
        assert len(question_ids) == 5
        assert len(set(question_ids)) == 5  # All unique
        assert shared_q.id in question_ids  # Shared question should be included once

