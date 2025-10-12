from flask import Flask, render_template, redirect, url_for, request, flash, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db
from models.user import User
from models.exam import Exam
from models.test import Test
from models.test_answer import TestAnswer
from models.exam_section import ExamSection
from models.section_question import SectionQuestion
from models.section import Section
from models.question import Question
from admin import init_admin
from datetime import datetime
import os
import json
import random
from io import BytesIO


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///jlpt.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize admin
init_admin(app, db)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('exams'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('exams'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        if not email or not password:
            flash('Email and password are required', 'danger')
            return render_template('register.html')
        
        if password != password_confirm:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('register.html')
        
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('exams'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('exams'))
        
        flash('Invalid email or password', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))


@app.route('/exams')
@login_required
def exams():
    all_exams = Exam.query.all()
    user_tests = Test.query.filter_by(user_id=current_user.id).all()
    
    # Create a dict of exam_id -> test for quick lookup
    test_dict = {test.exam_id: test for test in user_tests}
    
    # Get available sections for random exam generation
    all_sections = Section.query.all()
    section_question_counts = {}
    for section in all_sections:
        count = SectionQuestion.query.filter_by(section_id=section.id).count()
        if count > 0:
            section_question_counts[section.id] = {
                'name': section.name,
                'count': count
            }
    
    return render_template('exams.html', 
                         exams=all_exams, 
                         test_dict=test_dict,
                         sections=all_sections,
                         section_counts=section_question_counts)


@app.route('/exam/random/create', methods=['POST'])
@login_required
def create_random_exam():
    """Create a random exam from selected sections"""
    try:
        # Get form data
        section_configs = {}
        for key in request.form:
            if key.startswith('section_'):
                section_id = int(key.split('_')[1])
                num_questions = int(request.form.get(key, 0))
                if num_questions > 0:
                    section_configs[section_id] = num_questions
        
        if not section_configs:
            flash('Please select at least one section with questions', 'warning')
            return redirect(url_for('exams'))
        
        # Create the exam
        exam_name = f"Random Practice Exam - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
        exam = Exam(name=exam_name, created_by=current_user.id)
        db.session.add(exam)
        db.session.flush()
        
        # For each selected section, create a new section with random questions
        for order, (section_id, num_questions) in enumerate(section_configs.items(), start=1):
            original_section = Section.query.get(section_id)
            if not original_section:
                continue
            
            # Get all available questions for this section
            section_questions = SectionQuestion.query.filter_by(
                section_id=section_id
            ).all()
            
            available_question_ids = [sq.question_id for sq in section_questions]
            
            # Randomly select questions
            num_to_select = min(num_questions, len(available_question_ids))
            selected_question_ids = random.sample(available_question_ids, num_to_select)
            
            # Create a new section for this random exam
            new_section = Section(
                name=f"{original_section.name} (Random)",
                number_of_questions=num_to_select
            )
            db.session.add(new_section)
            db.session.flush()
            
            # Link selected questions to new section
            for q_order, question_id in enumerate(selected_question_ids, start=1):
                sq = SectionQuestion(
                    section_id=new_section.id,
                    question_id=question_id,
                    order=q_order
                )
                db.session.add(sq)
            
            # Link new section to exam
            es = ExamSection(
                exam_id=exam.id,
                section_id=new_section.id,
                order=order
            )
            db.session.add(es)
        
        db.session.commit()
        
        # Immediately create a test for this exam and start it
        test = Test(exam_id=exam.id, user_id=current_user.id)
        db.session.add(test)
        db.session.commit()
        
        flash(f'Random exam created successfully with {sum(section_configs.values())} questions!', 'success')
        return redirect(url_for('take_exam', test_id=test.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating random exam: {str(e)}', 'danger')
        return redirect(url_for('exams'))


@app.route('/exam/<int:exam_id>/start', methods=['POST'])
@login_required
def start_exam(exam_id):
    # Verify exam exists
    Exam.query.get_or_404(exam_id)
    
    # Check if user already has an incomplete test for this exam
    existing_test = Test.query.filter_by(
        exam_id=exam_id,
        user_id=current_user.id,
        completed_at=None
    ).first()
    
    if existing_test:
        return redirect(url_for('take_exam', test_id=existing_test.id))
    
    # Create new test
    test = Test(exam_id=exam_id, user_id=current_user.id)
    db.session.add(test)
    db.session.commit()
    
    return redirect(url_for('take_exam', test_id=test.id))


@app.route('/test/<int:test_id>')
@login_required
def take_exam(test_id):
    test = Test.query.get_or_404(test_id)
    
    # Security check
    if test.user_id != current_user.id:
        flash('You do not have permission to access this test', 'danger')
        return redirect(url_for('exams'))
    
    # If test is completed, redirect to results
    if test.completed_at:
        return redirect(url_for('test_results', test_id=test_id))
    
    # Get all questions for this exam
    exam_sections = ExamSection.query.filter_by(exam_id=test.exam_id).order_by(ExamSection.order).all()
    
    questions = []
    for exam_section in exam_sections:
        section_questions = SectionQuestion.query.filter_by(
            section_id=exam_section.section_id
        ).order_by(SectionQuestion.order).all()
        
        for sq in section_questions:
            questions.append({
                'section': exam_section.section.name,
                'question': sq.question
            })
    
    # Get existing answers
    existing_answers = TestAnswer.query.filter_by(test_id=test_id).all()
    answer_dict = {ans.question_id: ans.selected_answer for ans in existing_answers}
    
    return render_template('take_exam.html', test=test, questions=questions, answer_dict=answer_dict)


@app.route('/test/<int:test_id>/answer', methods=['POST'])
@login_required
def submit_answer(test_id):
    test = Test.query.get_or_404(test_id)
    
    # Security check
    if test.user_id != current_user.id:
        return {'error': 'Unauthorized'}, 403
    
    if test.completed_at:
        return {'error': 'Test already completed'}, 400
    
    question_id = request.form.get('question_id', type=int)
    selected_answer = request.form.get('selected_answer', type=int)
    
    if not question_id or not selected_answer:
        return {'error': 'Invalid data'}, 400
    
    # Check if answer already exists
    existing_answer = TestAnswer.query.filter_by(
        test_id=test_id,
        question_id=question_id
    ).first()
    
    if existing_answer:
        existing_answer.selected_answer = selected_answer
        existing_answer.answered_at = datetime.utcnow()
    else:
        answer = TestAnswer(
            test_id=test_id,
            user_id=current_user.id,
            question_id=question_id,
            selected_answer=selected_answer
        )
        db.session.add(answer)
    
    db.session.commit()
    
    return {'success': True}


@app.route('/test/<int:test_id>/submit', methods=['POST'])
@login_required
def submit_exam(test_id):
    test = Test.query.get_or_404(test_id)
    
    # Security check
    if test.user_id != current_user.id:
        flash('You do not have permission to submit this test', 'danger')
        return redirect(url_for('exams'))
    
    if test.completed_at:
        flash('Test already completed', 'warning')
        return redirect(url_for('test_results', test_id=test_id))
    
    # Mark test as completed
    test.completed_at = datetime.utcnow()
    db.session.commit()
    
    flash('Test submitted successfully!', 'success')
    return redirect(url_for('test_results', test_id=test_id))


@app.route('/test/<int:test_id>/results')
@login_required
def test_results(test_id):
    test = Test.query.get_or_404(test_id)
    
    # Security check
    if test.user_id != current_user.id:
        flash('You do not have permission to view these results', 'danger')
        return redirect(url_for('exams'))
    
    if not test.completed_at:
        flash('Test not yet completed', 'warning')
        return redirect(url_for('take_exam', test_id=test_id))
    
    # Get all questions for this exam
    exam_sections = ExamSection.query.filter_by(exam_id=test.exam_id).order_by(ExamSection.order).all()
    
    questions = []
    for exam_section in exam_sections:
        section_questions = SectionQuestion.query.filter_by(
            section_id=exam_section.section_id
        ).order_by(SectionQuestion.order).all()
        
        for sq in section_questions:
            questions.append(sq.question)
    
    # Get user's answers
    user_answers = TestAnswer.query.filter_by(test_id=test_id).all()
    answer_dict = {ans.question_id: ans.selected_answer for ans in user_answers}
    
    # Calculate score
    correct = 0
    total = len(questions)
    
    results = []
    for question in questions:
        user_answer = answer_dict.get(question.id)
        is_correct = user_answer == question.correct_answer
        if is_correct:
            correct += 1
        
        results.append({
            'question': question,
            'user_answer': user_answer,
            'is_correct': is_correct
        })
    
    percentage = (correct / total * 100) if total > 0 else 0
    
    return render_template('results.html', 
                         test=test, 
                         results=results, 
                         correct=correct, 
                         total=total, 
                         percentage=percentage)


@app.cli.command()
def init_db():
    """Initialize the database."""
    db.create_all()
    print('Database initialized!')


@app.route('/download-example-json')
@login_required
def download_example_json():
    """Download an example JSON file for exam import"""
    example_data = {
        "name": "JLPT N5 Practice Test - Example",
        "sections": [
            {
                "name": "Vocabulary",
                "questions": [
                    {
                        "question_text": "彼は___な性格です。",
                        "answer_1": "まじめ",
                        "answer_2": "まじめだ",
                        "answer_3": "まじめの",
                        "answer_4": "まじめで",
                        "correct_answer": 1,
                        "explanation": "「まじめな性格」is the correct form. な-adjectives use な before nouns."
                    },
                    {
                        "question_text": "毎日___勉強します。",
                        "answer_1": "いっしょうけんめい",
                        "answer_2": "いっしょうけんめいに",
                        "answer_3": "いっしょうけんめいで",
                        "answer_4": "いっしょうけんめいな",
                        "correct_answer": 2,
                        "explanation": "いっしょうけんめいに is an adverb modifying the verb 勉強します."
                    }
                ]
            },
            {
                "name": "Grammar",
                "questions": [
                    {
                        "question_text": "雨が___きました。",
                        "answer_1": "ふり",
                        "answer_2": "ふって",
                        "answer_3": "ふった",
                        "answer_4": "ふる",
                        "correct_answer": 2,
                        "explanation": "ふってきました indicates the rain has started falling. Use て-form + くる."
                    },
                    {
                        "question_text": "先生___相談したいことがあります。",
                        "answer_1": "に",
                        "answer_2": "を",
                        "answer_3": "が",
                        "answer_4": "へ",
                        "correct_answer": 1,
                        "explanation": "相談する takes に particle to indicate the person being consulted."
                    }
                ]
            },
            {
                "name": "Reading Comprehension",
                "questions": [
                    {
                        "question_text": "「彼女は日本語が上手です」の意味は？",
                        "answer_1": "She is good at Japanese",
                        "answer_2": "She is teaching Japanese",
                        "answer_3": "She likes Japanese",
                        "answer_4": "She is from Japan",
                        "correct_answer": 1,
                        "explanation": "上手（じょうず）means skillful or good at something."
                    }
                ]
            }
        ]
    }
    
    # Create JSON string with nice formatting
    json_str = json.dumps(example_data, ensure_ascii=False, indent=2)
    
    # Create BytesIO object
    buffer = BytesIO()
    buffer.write(json_str.encode('utf-8'))
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name='exam_example.json',
        mimetype='application/json'
    )


@app.cli.command()
def create_admin():
    """Create an admin user."""
    email = input('Enter admin email: ')
    password = input('Enter admin password: ')
    
    if User.query.filter_by(email=email).first():
        print('User already exists!')
        return
    
    user = User(email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    print(f'Admin user {email} created!')


if __name__ == '__main__':
    app.run(debug=True)

