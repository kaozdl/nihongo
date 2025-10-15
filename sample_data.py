"""
Sample Data Generator for JLPT Test Manager
Run this script to populate the database with sample data for testing.

Usage:
    flask shell
    >>> from sample_data import create_sample_data
    >>> create_sample_data()
"""

# Setup path for package imports
import sys
import os
_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _parent not in sys.path:
    sys.path.insert(0, _parent)

from nihongo.app import app  # noqa: E402
from nihongo.models import db  # noqa: E402
from nihongo.models.user import User  # noqa: E402
from nihongo.models.question import Question  # noqa: E402
from nihongo.models.section import Section  # noqa: E402
from nihongo.models.section_question import SectionQuestion  # noqa: E402
from nihongo.models.exam import Exam  # noqa: E402
from nihongo.models.exam_section import ExamSection  # noqa: E402
from nihongo.models.utils import set_explanation  # noqa: E402


def create_sample_data():
    """Create sample data for testing the application"""
    
    with app.app_context():
        # Create a sample user
        print("Creating sample user...")
        user = User.query.filter_by(email='admin@example.com').first()
        if not user:
            user = User(email='admin@example.com')
            user.set_password('admin123')
            db.session.add(user)
            db.session.commit()
            print("✅ Created user: admin@example.com / admin123")
        else:
            print("✅ User already exists")
        
        # Create sample questions
        print("\nCreating sample questions...")
        questions = []
        
        # Vocabulary questions (with multi-language explanations)
        vocab_questions = [
            {
                'question_text': '彼は___な性格です。',
                'answer_1': 'まじめ',
                'answer_2': 'まじめだ',
                'answer_3': 'まじめの',
                'answer_4': 'まじめで',
                'correct_answer': 1,
                'explanation': set_explanation(
                    '「まじめな性格」is the correct form. な-adjectives use な before nouns.',
                    '「まじめな性格」es la forma correcta. Los adjetivos な usan な antes de sustantivos.'
                )
            },
            {
                'question_text': '毎日___勉強します。',
                'answer_1': 'いっしょうけんめい',
                'answer_2': 'いっしょうけんめいに',
                'answer_3': 'いっしょうけんめいで',
                'answer_4': 'いっしょうけんめいな',
                'correct_answer': 2,
                'explanation': set_explanation(
                    'いっしょうけんめいに is an adverb modifying the verb 勉強します.',
                    'いっしょうけんめいに es un adverbio que modifica el verbo 勉強します.'
                )
            },
        ]
        
        # Grammar questions
        grammar_questions = [
            {
                'question_text': '雨が___きました。',
                'answer_1': 'ふり',
                'answer_2': 'ふって',
                'answer_3': 'ふった',
                'answer_4': 'ふる',
                'correct_answer': 2,
                'explanation': 'ふってきました indicates the rain has started falling. Use て-form + くる.'
            },
            {
                'question_text': '先生___相談したいことがあります。',
                'answer_1': 'に',
                'answer_2': 'を',
                'answer_3': 'が',
                'answer_4': 'へ',
                'correct_answer': 1,
                'explanation': '相談する takes に particle to indicate the person being consulted.'
            },
        ]
        
        # Reading comprehension
        reading_questions = [
            {
                'question_text': '「彼女は日本語が上手です」の意味は？',
                'answer_1': 'She is good at Japanese',
                'answer_2': 'She is teaching Japanese',
                'answer_3': 'She likes Japanese',
                'answer_4': 'She is from Japan',
                'correct_answer': 1,
                'explanation': '上手（じょうず）means skillful or good at something.'
            },
        ]
        
        all_question_data = vocab_questions + grammar_questions + reading_questions
        
        for q_data in all_question_data:
            q = Question(
                question_text=q_data['question_text'],
                answer_1=q_data['answer_1'],
                answer_2=q_data['answer_2'],
                answer_3=q_data['answer_3'],
                answer_4=q_data['answer_4'],
                correct_answer=q_data['correct_answer'],
                explanation=q_data['explanation'],
                created_by=user.id
            )
            db.session.add(q)
            questions.append(q)
        
        db.session.commit()
        print(f"✅ Created {len(questions)} questions")
        
        # Create sections
        print("\nCreating sections...")
        vocab_section = Section(name='Vocabulary', number_of_questions=2)
        grammar_section = Section(name='Grammar', number_of_questions=2)
        reading_section = Section(name='Reading', number_of_questions=1)
        
        db.session.add_all([vocab_section, grammar_section, reading_section])
        db.session.commit()
        print("✅ Created 3 sections")
        
        # Link questions to sections
        print("\nLinking questions to sections...")
        for i, question in enumerate(questions[:2]):
            sq = SectionQuestion(section_id=vocab_section.id, question_id=question.id, order=i)
            db.session.add(sq)
        
        for i, question in enumerate(questions[2:4]):
            sq = SectionQuestion(section_id=grammar_section.id, question_id=question.id, order=i)
            db.session.add(sq)
        
        for i, question in enumerate(questions[4:]):
            sq = SectionQuestion(section_id=reading_section.id, question_id=question.id, order=i)
            db.session.add(sq)
        
        db.session.commit()
        print("✅ Linked questions to sections")
        
        # Create exam
        print("\nCreating exam...")
        exam = Exam(name='JLPT N5 Practice Test', created_by=user.id)
        db.session.add(exam)
        db.session.commit()
        print("✅ Created exam")
        
        # Link sections to exam
        print("\nLinking sections to exam...")
        es1 = ExamSection(exam_id=exam.id, section_id=vocab_section.id, order=1)
        es2 = ExamSection(exam_id=exam.id, section_id=grammar_section.id, order=2)
        es3 = ExamSection(exam_id=exam.id, section_id=reading_section.id, order=3)
        
        db.session.add_all([es1, es2, es3])
        db.session.commit()
        print("✅ Linked sections to exam")
        
        print("\n" + "="*50)
        print("✨ Sample data created successfully!")
        print("="*50)
        print("\nYou can now login with:")
        print("  Email: admin@example.com")
        print("  Password: admin123")
        print("\nVisit http://localhost:5000 to start testing!")


if __name__ == '__main__':
    create_sample_data()

