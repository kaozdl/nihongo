"""
Custom routes for /mycontent using app's regular styling (not Flask-Admin)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from models import db
from models.question import Question
from models.section import Section
from models.exam import Exam
from models.section_question import SectionQuestion
from models.exam_section import ExamSection
from models.utils import parse_explanation, set_explanation
from import_exam import import_exam_from_json
import json
from io import BytesIO

# Create blueprint for My Content routes
mycontent_bp = Blueprint('mycontent', __name__, url_prefix='/mycontent')


@mycontent_bp.route('/')
@login_required
def index():
    """My Content homepage"""
    # Get user's content statistics
    my_questions = Question.query.filter_by(created_by=current_user.id).count()
    my_exams = Exam.query.filter_by(created_by=current_user.id).count()
    
    return render_template('mycontent/index.html',
                         my_questions=my_questions,
                         my_exams=my_exams)


@mycontent_bp.route('/questions')
@login_required
def questions():
    """List user's questions"""
    my_questions = Question.query.filter_by(created_by=current_user.id).order_by(Question.created_at.desc()).all()
    return render_template('mycontent/questions.html', questions=my_questions)


@mycontent_bp.route('/questions/new', methods=['GET', 'POST'])
@login_required
def new_question():
    """Create a new question"""
    if request.method == 'POST':
        try:
            # Get form data
            question_text = request.form.get('question_text')
            question_image = request.form.get('question_image')
            question_audio = request.form.get('question_audio')
            answer_1 = request.form.get('answer_1')
            answer_2 = request.form.get('answer_2')
            answer_3 = request.form.get('answer_3')
            answer_4 = request.form.get('answer_4')
            correct_answer = int(request.form.get('correct_answer'))
            explanation_en = request.form.get('explanation_en', '')
            explanation_es = request.form.get('explanation_es', '')
            
            # Validate required fields
            if not question_text or not answer_1 or not answer_2 or not answer_3 or not answer_4:
                flash('Please fill in all required fields', 'danger')
                return render_template('mycontent/question_form.html')
            
            if correct_answer not in [1, 2, 3, 4]:
                flash('Correct answer must be 1, 2, 3, or 4', 'danger')
                return render_template('mycontent/question_form.html')
            
            # Create explanation JSON
            explanation = set_explanation(explanation_en, explanation_es)
            
            # Create question
            question = Question(
                question_text=question_text,
                question_image=question_image if question_image else None,
                question_audio=question_audio if question_audio else None,
                answer_1=answer_1,
                answer_2=answer_2,
                answer_3=answer_3,
                answer_4=answer_4,
                correct_answer=correct_answer,
                explanation=explanation,
                created_by=current_user.id
            )
            
            db.session.add(question)
            db.session.commit()
            
            flash('✅ Question created successfully!', 'success')
            return redirect(url_for('mycontent.questions'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error creating question: {str(e)}', 'danger')
            return render_template('mycontent/question_form.html')
    
    return render_template('mycontent/question_form.html', question=None)


@mycontent_bp.route('/questions/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_question(id):
    """Edit a question"""
    question = Question.query.get_or_404(id)
    
    # Verify ownership
    if question.created_by != current_user.id:
        flash('You can only edit your own questions', 'danger')
        return redirect(url_for('mycontent.questions'))
    
    if request.method == 'POST':
        try:
            # Update question
            question.question_text = request.form.get('question_text')
            question.question_image = request.form.get('question_image') or None
            question.question_audio = request.form.get('question_audio') or None
            question.answer_1 = request.form.get('answer_1')
            question.answer_2 = request.form.get('answer_2')
            question.answer_3 = request.form.get('answer_3')
            question.answer_4 = request.form.get('answer_4')
            question.correct_answer = int(request.form.get('correct_answer'))
            
            explanation_en = request.form.get('explanation_en', '')
            explanation_es = request.form.get('explanation_es', '')
            question.explanation = set_explanation(explanation_en, explanation_es)
            
            db.session.commit()
            
            flash('✅ Question updated successfully!', 'success')
            return redirect(url_for('mycontent.questions'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error updating question: {str(e)}', 'danger')
    
    # Parse explanation for form
    explanation_dict = parse_explanation(question.explanation)
    
    return render_template('mycontent/question_form.html',
                         question=question,
                         explanation_en=explanation_dict.get('EN', ''),
                         explanation_es=explanation_dict.get('ES', ''))


@mycontent_bp.route('/questions/<int:id>/delete', methods=['POST'])
@login_required
def delete_question(id):
    """Delete a question"""
    question = Question.query.get_or_404(id)
    
    # Verify ownership
    if question.created_by != current_user.id:
        flash('You can only delete your own questions', 'danger')
        return redirect(url_for('mycontent.questions'))
    
    try:
        db.session.delete(question)
        db.session.commit()
        flash('✅ Question deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error deleting question: {str(e)}', 'danger')
    
    return redirect(url_for('mycontent.questions'))


@mycontent_bp.route('/import', methods=['GET', 'POST'])
@login_required
def import_exam():
    """Import exam from JSON"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file uploaded', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        if not file.filename.endswith('.json'):
            flash('Only JSON files are allowed', 'danger')
            return redirect(request.url)
        
        try:
            # Read and parse JSON
            json_content = file.read().decode('utf-8')
            json_data = json.loads(json_content)
            
            # Import the exam
            success, message, exam = import_exam_from_json(json_data, current_user.id)
            
            if success:
                flash(f'✅ {message}', 'success')
                return redirect(url_for('mycontent.index'))
            else:
                flash(f'❌ {message}', 'danger')
                
        except json.JSONDecodeError as e:
            flash(f'Invalid JSON format: {str(e)}', 'danger')
        except Exception as e:
            flash(f'Error importing exam: {str(e)}', 'danger')
    
    return render_template('mycontent/import_exam.html')


@mycontent_bp.route('/download-example')
@login_required
def download_example():
    """Download example JSON file"""
    from app import app
    import os
    example_path = os.path.join(app.root_path, 'exam_example.json')
    
    with open(example_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return send_file(
        BytesIO(content.encode('utf-8')),
        mimetype='application/json',
        as_attachment=True,
        download_name='exam_example.json'
    )


# ============================================================================
# SECTIONS MANAGEMENT
# ============================================================================

@mycontent_bp.route('/sections')
@login_required
def sections():
    """List all sections (not filtered by user since sections don't have created_by)"""
    all_sections = Section.query.order_by(Section.name).all()
    return render_template('mycontent/sections.html', sections=all_sections)


@mycontent_bp.route('/sections/new', methods=['GET', 'POST'])
@login_required
def new_section():
    """Create a new section"""
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            number_of_questions = int(request.form.get('number_of_questions', 0))
            
            if not name:
                flash('Section name is required', 'danger')
                return render_template('mycontent/section_form.html')
            
            section = Section(
                name=name,
                number_of_questions=number_of_questions
            )
            
            db.session.add(section)
            db.session.commit()
            
            flash('✅ Section created successfully!', 'success')
            return redirect(url_for('mycontent.sections'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error creating section: {str(e)}', 'danger')
    
    return render_template('mycontent/section_form.html', section=None)


@mycontent_bp.route('/sections/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_section(id):
    """Edit a section and manage its questions"""
    section = Section.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Check if we're creating a new question inline
            if 'create_question' in request.form:
                question_text = request.form.get('new_question_text')
                answer_1 = request.form.get('new_answer_1')
                answer_2 = request.form.get('new_answer_2')
                answer_3 = request.form.get('new_answer_3')
                answer_4 = request.form.get('new_answer_4')
                correct_answer = int(request.form.get('new_correct_answer'))
                explanation_en = request.form.get('new_explanation_en', '')
                explanation_es = request.form.get('new_explanation_es', '')
                
                if question_text and answer_1 and answer_2 and answer_3 and answer_4:
                    from models.question import Question
                    from models.utils import set_explanation
                    
                    # Create question
                    new_question = Question(
                        question_text=question_text,
                        answer_1=answer_1,
                        answer_2=answer_2,
                        answer_3=answer_3,
                        answer_4=answer_4,
                        correct_answer=correct_answer,
                        explanation=set_explanation(explanation_en, explanation_es),
                        created_by=current_user.id
                    )
                    db.session.add(new_question)
                    db.session.flush()
                    
                    # Link to section
                    max_order = db.session.query(db.func.max(SectionQuestion.order)).filter_by(section_id=section.id).scalar() or 0
                    section_question = SectionQuestion(
                        section_id=section.id,
                        question_id=new_question.id,
                        order=max_order + 1
                    )
                    db.session.add(section_question)
                    db.session.commit()
                    
                    flash(f'✅ Question created and added to section!', 'success')
                    return redirect(url_for('mycontent.edit_section', id=section.id))
            
            # Check if we're adding an existing question
            elif 'add_question' in request.form:
                question_id = request.form.get('question_id')
                if question_id:
                    question_id = int(question_id)
                    
                    # Check if already linked
                    existing = SectionQuestion.query.filter_by(
                        section_id=section.id,
                        question_id=question_id
                    ).first()
                    
                    if existing:
                        flash('This question is already in the section', 'warning')
                    else:
                        max_order = db.session.query(db.func.max(SectionQuestion.order)).filter_by(section_id=section.id).scalar() or 0
                        section_question = SectionQuestion(
                            section_id=section.id,
                            question_id=question_id,
                            order=max_order + 1
                        )
                        db.session.add(section_question)
                        db.session.commit()
                        
                        flash(f'✅ Question added to section!', 'success')
                    
                    return redirect(url_for('mycontent.edit_section', id=section.id))
            
            # Check if we're removing a question
            elif 'remove_question' in request.form:
                section_question_id = int(request.form.get('section_question_id'))
                section_question = SectionQuestion.query.get(section_question_id)
                
                if section_question and section_question.section_id == section.id:
                    db.session.delete(section_question)
                    db.session.commit()
                    flash('✅ Question removed from section!', 'success')
                
                return redirect(url_for('mycontent.edit_section', id=section.id))
            
            # Check if we're updating question order
            elif 'update_question_order' in request.form:
                section_question_id = int(request.form.get('section_question_id'))
                new_order = int(request.form.get('new_order'))
                
                section_question = SectionQuestion.query.get(section_question_id)
                if section_question and section_question.section_id == section.id:
                    section_question.order = new_order
                    db.session.commit()
                    flash('✅ Question order updated!', 'success')
                
                return redirect(url_for('mycontent.edit_section', id=section.id))
            
            # Otherwise, update section details
            else:
                section.name = request.form.get('name')
                section.number_of_questions = int(request.form.get('number_of_questions', 0))
                db.session.commit()
                flash('✅ Section updated successfully!', 'success')
                return redirect(url_for('mycontent.sections'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error: {str(e)}', 'danger')
    
    # Get user's questions for the dropdown
    from models.question import Question
    my_questions = Question.query.filter_by(created_by=current_user.id).order_by(Question.created_at.desc()).all()
    
    # Get current section questions with their details
    section_questions = SectionQuestion.query.filter_by(section_id=section.id).order_by(SectionQuestion.order).all()
    
    return render_template('mycontent/section_form.html', 
                         section=section,
                         my_questions=my_questions,
                         section_questions=section_questions)


@mycontent_bp.route('/sections/<int:id>/delete', methods=['POST'])
@login_required
def delete_section(id):
    """Delete a section"""
    section = Section.query.get_or_404(id)
    
    try:
        db.session.delete(section)
        db.session.commit()
        flash('✅ Section deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error deleting section: {str(e)}', 'danger')
    
    return redirect(url_for('mycontent.sections'))


# ============================================================================
# EXAMS MANAGEMENT
# ============================================================================

@mycontent_bp.route('/exams')
@login_required
def exams():
    """List user's exams"""
    my_exams = Exam.query.filter_by(created_by=current_user.id).order_by(Exam.created_at.desc()).all()
    
    # Get section counts for each exam
    exam_data = []
    for exam in my_exams:
        section_count = ExamSection.query.filter_by(exam_id=exam.id).count()
        exam_data.append({
            'exam': exam,
            'section_count': section_count
        })
    
    return render_template('mycontent/exams.html', exam_data=exam_data)


@mycontent_bp.route('/exams/new', methods=['GET', 'POST'])
@login_required
def new_exam():
    """Create a new exam"""
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            
            if not name:
                flash('Exam name is required', 'danger')
                return render_template('mycontent/exam_form.html')
            
            exam = Exam(
                name=name,
                created_by=current_user.id
            )
            
            db.session.add(exam)
            db.session.commit()
            
            flash('✅ Exam created successfully!', 'success')
            return redirect(url_for('mycontent.exams'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error creating exam: {str(e)}', 'danger')
    
    return render_template('mycontent/exam_form.html', exam=None)


@mycontent_bp.route('/exams/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_exam(id):
    """Edit an exam and manage its sections"""
    exam = Exam.query.get_or_404(id)
    
    # Verify ownership
    if exam.created_by != current_user.id:
        flash('You can only edit your own exams', 'danger')
        return redirect(url_for('mycontent.exams'))
    
    if request.method == 'POST':
        try:
            # Check if we're creating a new section inline
            if 'create_section' in request.form:
                section_name = request.form.get('new_section_name')
                section_questions = int(request.form.get('new_section_questions', 10))
                
                if section_name:
                    # Create new section
                    new_section = Section(
                        name=section_name,
                        number_of_questions=section_questions
                    )
                    db.session.add(new_section)
                    db.session.flush()  # Get the ID
                    
                    # Link to exam
                    max_order = db.session.query(db.func.max(ExamSection.order)).filter_by(exam_id=exam.id).scalar() or 0
                    exam_section = ExamSection(
                        exam_id=exam.id,
                        section_id=new_section.id,
                        order=max_order + 1
                    )
                    db.session.add(exam_section)
                    db.session.commit()
                    
                    flash(f'✅ Section "{section_name}" created and added to exam!', 'success')
                    return redirect(url_for('mycontent.edit_exam', id=exam.id))
            
            # Check if we're adding an existing section
            elif 'add_section' in request.form:
                section_id = request.form.get('section_id')
                if section_id:
                    section_id = int(section_id)
                    
                    # Check if already linked
                    existing = ExamSection.query.filter_by(
                        exam_id=exam.id,
                        section_id=section_id
                    ).first()
                    
                    if existing:
                        flash('This section is already in the exam', 'warning')
                    else:
                        max_order = db.session.query(db.func.max(ExamSection.order)).filter_by(exam_id=exam.id).scalar() or 0
                        exam_section = ExamSection(
                            exam_id=exam.id,
                            section_id=section_id,
                            order=max_order + 1
                        )
                        db.session.add(exam_section)
                        db.session.commit()
                        
                        section = Section.query.get(section_id)
                        flash(f'✅ Section "{section.name}" added to exam!', 'success')
                    
                    return redirect(url_for('mycontent.edit_exam', id=exam.id))
            
            # Check if we're removing a section
            elif 'remove_section' in request.form:
                exam_section_id = int(request.form.get('exam_section_id'))
                exam_section = ExamSection.query.get(exam_section_id)
                
                if exam_section and exam_section.exam_id == exam.id:
                    db.session.delete(exam_section)
                    db.session.commit()
                    flash('✅ Section removed from exam!', 'success')
                
                return redirect(url_for('mycontent.edit_exam', id=exam.id))
            
            # Check if we're updating section order
            elif 'update_order' in request.form:
                exam_section_id = int(request.form.get('exam_section_id'))
                new_order = int(request.form.get('new_order'))
                
                exam_section = ExamSection.query.get(exam_section_id)
                if exam_section and exam_section.exam_id == exam.id:
                    exam_section.order = new_order
                    db.session.commit()
                    flash('✅ Order updated!', 'success')
                
                return redirect(url_for('mycontent.edit_exam', id=exam.id))
            
            # Otherwise, update exam name
            else:
                exam.name = request.form.get('name')
                db.session.commit()
                flash('✅ Exam updated successfully!', 'success')
                return redirect(url_for('mycontent.exams'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error: {str(e)}', 'danger')
    
    # Get all sections for the dropdown
    all_sections = Section.query.order_by(Section.name).all()
    
    # Get current exam sections with their details
    exam_sections = ExamSection.query.filter_by(exam_id=exam.id).order_by(ExamSection.order).all()
    
    return render_template('mycontent/exam_form.html', 
                         exam=exam,
                         all_sections=all_sections,
                         exam_sections=exam_sections)


@mycontent_bp.route('/exams/<int:id>/delete', methods=['POST'])
@login_required
def delete_exam(id):
    """Delete an exam"""
    exam = Exam.query.get_or_404(id)
    
    # Verify ownership
    if exam.created_by != current_user.id:
        flash('You can only delete your own exams', 'danger')
        return redirect(url_for('mycontent.exams'))
    
    try:
        db.session.delete(exam)
        db.session.commit()
        flash('✅ Exam deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error deleting exam: {str(e)}', 'danger')
    
    return redirect(url_for('mycontent.exams'))

