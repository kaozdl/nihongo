# Setup path for package imports (makes 'nihongo' package available in both local dev and deployment)
import sys
import os
_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _parent not in sys.path:
    sys.path.insert(0, _parent)

from flask import Flask, render_template, redirect, url_for, request, flash, send_file, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_babel import Babel, gettext, get_locale
from nihongo.models import db
from nihongo.models.user import User
from nihongo.models.exam import Exam
from nihongo.models.test import Test
from nihongo.models.test_answer import TestAnswer
from nihongo.models.exam_section import ExamSection
from nihongo.models.section_question import SectionQuestion
from nihongo.models.section import Section
from nihongo.models.utils import get_explanation
from nihongo.admin import init_admin
from nihongo.mycontent_routes import mycontent_bp
from nihongo.config import get_config
from datetime import datetime
import json
import random
from io import BytesIO


# Create Flask app with configuration
app = Flask(__name__)
config_name = os.environ.get('FLASK_ENV', 'development')
config_class = get_config(config_name)
app.config.from_object(config_class)

# Initialize app with configuration (validates production config)
config_class.init_app(app)

# Log current environment
print(f"🚀 Starting application in {config_name.upper()} mode")
print(f"📊 Database: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize Babel
babel = Babel(app)

def get_locale_func():
    # Check if user manually selected language
    if 'language' in session:
        return session['language']
    # Try to get from browser
    return request.accept_languages.best_match(['es', 'en']) or 'es'

babel.init_app(app, locale_selector=get_locale_func)

# Make Babel functions available in templates
@app.context_processor
def inject_babel():
    """Inject Babel functions into template context."""
    return dict(
        get_locale=lambda: str(get_locale()),
        _=gettext
    )

# Initialize admin
init_admin(app, db)

# Register My Content blueprint (custom routes with app styling, not Flask-Admin)
app.register_blueprint(mycontent_bp)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('exams'))
    return redirect(url_for('login'))


@app.route('/language/<lang>')
def set_language(lang):
    """Set the user's language preference"""
    if lang in ['en', 'es']:
        session['language'] = lang
        flash(gettext('Language changed successfully'), 'success')
    return redirect(request.referrer or url_for('index'))


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
        
        # Automatically log in the user after registration
        login_user(user)
        flash('Registration successful! Welcome!', 'success')
        return redirect(url_for('exams'))
    
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
    
    # For each exam, get the most recent incomplete test OR the most recent completed test
    test_dict = {}
    for exam in all_exams:
        # First, check for incomplete tests (highest priority)
        incomplete_test = Test.query.filter_by(
            user_id=current_user.id,
            exam_id=exam.id,
            completed_at=None
        ).order_by(Test.started_at.desc()).first()
        
        if incomplete_test:
            test_dict[exam.id] = incomplete_test
        else:
            # Get most recent completed test
            completed_test = Test.query.filter_by(
                user_id=current_user.id,
                exam_id=exam.id
            ).filter(
                Test.completed_at.isnot(None)
            ).order_by(Test.completed_at.desc()).first()
            
            if completed_test:
                test_dict[exam.id] = completed_test
    
    # Get available sections for random exam generation
    # Aggregate sections by name to avoid duplicates
    all_sections = Section.query.all()
    section_aggregated = {}
    
    for section in all_sections:
        count = SectionQuestion.query.filter_by(section_id=section.id).count()
        if count > 0:
            if section.name not in section_aggregated:
                section_aggregated[section.name] = {
                    'name': section.name,
                    'count': 0,
                    'section_ids': []
                }
            section_aggregated[section.name]['count'] += count
            section_aggregated[section.name]['section_ids'].append(section.id)
    
    return render_template('exams.html', 
                         exams=all_exams, 
                         test_dict=test_dict,
                         section_aggregated=section_aggregated)


@app.route('/exam/random/create', methods=['POST'])
@login_required
def create_random_exam():
    """Create a random exam from selected sections"""
    try:
        # Get form data - now organized by section name instead of section ID
        section_configs = {}
        for key in request.form:
            if key.startswith('section_'):
                section_name = key.replace('section_', '').replace('_', ' ')
                num_questions = int(request.form.get(key, 0))
                if num_questions > 0:
                    section_configs[section_name] = num_questions
        
        if not section_configs:
            flash(gettext('Please select at least one section with questions'), 'warning')
            return redirect(url_for('exams'))
        
        # Create the exam
        exam_name = f"Random Practice Exam - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
        exam = Exam(name=exam_name, created_by=current_user.id)
        db.session.add(exam)
        db.session.flush()
        
        # For each selected section type, aggregate questions from all sections with that name
        for order, (section_name, num_questions) in enumerate(section_configs.items(), start=1):
            # Get all sections with this name
            sections_with_name = Section.query.filter_by(name=section_name).all()
            
            if not sections_with_name:
                continue
            
            # Collect all available questions from all sections with this name
            available_question_ids = []
            for section in sections_with_name:
                section_questions = SectionQuestion.query.filter_by(
                    section_id=section.id
                ).all()
                available_question_ids.extend([sq.question_id for sq in section_questions])
            
            # Remove duplicates (in case same question is in multiple sections)
            available_question_ids = list(set(available_question_ids))
            
            if not available_question_ids:
                continue
            
            # Randomly select questions
            num_to_select = min(num_questions, len(available_question_ids))
            selected_question_ids = random.sample(available_question_ids, num_to_select)
            
            # Create a new section for this random exam
            new_section = Section(
                name=section_name,
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
        
        flash(gettext('Random exam created successfully with %(count)d questions!', count=sum(section_configs.values())), 'success')
        return redirect(url_for('take_exam', test_id=test.id))
        
    except Exception as e:
        db.session.rollback()
        flash(gettext('Error creating random exam: %(error)s', error=str(e)), 'danger')
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


@app.route('/my-exams')
@login_required
def my_exam_history():
    """Display user's exam history with all completed tests"""
    # Get all user's tests, ordered by completion date (most recent first)
    completed_tests = Test.query.filter_by(
        user_id=current_user.id
    ).filter(
        Test.completed_at.isnot(None)
    ).order_by(Test.completed_at.desc()).all()
    
    # Calculate scores for each test
    test_history = []
    for test in completed_tests:
        # Get all questions for this exam
        exam_sections = ExamSection.query.filter_by(exam_id=test.exam_id).order_by(ExamSection.order).all()
        
        questions = []
        for exam_section in exam_sections:
            section_questions = SectionQuestion.query.filter_by(
                section_id=exam_section.section_id
            ).order_by(SectionQuestion.order).all()
            
            for sq in section_questions:
                questions.append(sq.question)
        
        total_questions = len(questions)
        
        # Get user's answers
        user_answers = TestAnswer.query.filter_by(test_id=test.id).all()
        answer_dict = {ans.question_id: ans.selected_answer for ans in user_answers}
        
        # Calculate correct answers by comparing with question's correct_answer
        correct = 0
        for question in questions:
            user_answer = answer_dict.get(question.id)
            if user_answer == question.correct_answer:
                correct += 1
        
        percentage = (correct / total_questions * 100) if total_questions > 0 else 0
        
        test_history.append({
            'test': test,
            'exam_name': test.exam.name,
            'total_questions': total_questions,
            'correct': correct,
            'percentage': percentage,
            'started_at': test.started_at,
            'completed_at': test.completed_at
        })
    
    return render_template('exam_history.html', test_history=test_history)


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
            'is_correct': is_correct,
            'explanation': get_explanation(question.explanation)
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
    """Initialize the database and load sample exams."""
    from nihongo.import_exam import import_exam_from_json
    
    # Create all tables
    db.create_all()
    print('✅ Database tables created!')
    
    # Create default user if it doesn't exist
    default_email = 'default@nihongo.edu.uy'
    default_user = User.query.filter_by(email=default_email).first()
    
    if not default_user:
        default_user = User(email=default_email, is_admin=False)
        default_user.set_password('nihongo123')
        db.session.add(default_user)
        db.session.commit()
        print(f'✅ Default user created: {default_email} / nihongo123 (not admin)')
    else:
        print(f'ℹ️  Default user already exists: {default_email}')
    
    # Load exam JSON files
    exam_files = [
        'exam_easy.json',
        'exam_medium.json',
        'exam_hard.json'
    ]
    
    for exam_file in exam_files:
        file_path = os.path.join(os.path.dirname(__file__), exam_file)
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                
                # Check if exam already exists
                exam_name = json_data.get('name', '')
                existing_exam = Exam.query.filter_by(name=exam_name).first()
                
                if not existing_exam:
                    success, message, exam = import_exam_from_json(json_data, default_user.id)
                    if success:
                        print(f'✅ Loaded: {exam_file} - {exam_name}')
                    else:
                        print(f'❌ Error loading {exam_file}: {message}')
                else:
                    print(f'ℹ️  Exam already exists: {exam_name}')
            except Exception as e:
                print(f'❌ Error reading {exam_file}: {str(e)}')
        else:
            print(f'⚠️  File not found: {exam_file}')
    
    print('\n🎉 Database initialization complete!')


@app.cli.command('create-admin')
def create_admin():
    """Create a new admin user interactively."""
    import getpass
    
    print('Create Admin User')
    print('=' * 50)
    
    # Get email
    email = input('Enter admin email: ').strip()
    if not email:
        print('❌ Email is required')
        return
    
    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        print(f'❌ User with email {email} already exists')
        
        # Ask if they want to promote to admin
        promote = input('Would you like to promote this user to admin? (y/n): ').strip().lower()
        if promote == 'y':
            existing_user.is_admin = True
            db.session.commit()
            print(f'✅ User {email} promoted to admin')
        return
    
    # Get password
    while True:
        password = getpass.getpass('Enter password: ')
        password_confirm = getpass.getpass('Confirm password: ')
        
        if password != password_confirm:
            print('❌ Passwords do not match. Try again.')
            continue
        
        if len(password) < 6:
            print('❌ Password must be at least 6 characters. Try again.')
            continue
        
        break
    
    # Create admin user
    admin_user = User(email=email, is_admin=True)
    admin_user.set_password(password)
    db.session.add(admin_user)
    db.session.commit()
    
    print('\n✅ Admin user created successfully!')
    print(f'   Email: {email}')
    print('   Admin: Yes')


@app.cli.command()
def db_migrate():
    """Generate a new migration."""
    import subprocess
    result = subprocess.run(['alembic', 'revision', '--autogenerate'], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)


@app.cli.command()
def db_upgrade():
    """Apply all pending migrations."""
    import subprocess
    result = subprocess.run(['alembic', 'upgrade', 'head'], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)


@app.cli.command()
def db_downgrade():
    """Rollback the last migration."""
    import subprocess
    result = subprocess.run(['alembic', 'downgrade', '-1'], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)


@app.cli.command()
def db_history():
    """Show migration history."""
    import subprocess
    result = subprocess.run(['alembic', 'history'], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)


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


if __name__ == '__main__':
    app.run(debug=True)

