from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for, request, flash, render_template
from werkzeug.utils import secure_filename
import json
import os


class SecureModelView(ModelView):
    """Base class for admin views with authentication"""
    
    def is_accessible(self):
        return current_user.is_authenticated
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))


class UserAdmin(SecureModelView):
    column_list = ['id', 'email']
    column_searchable_list = ['email']
    form_excluded_columns = ['password_hash', 'created_questions', 'created_exams', 'tests', 'test_answers']
    
    def on_model_change(self, form, model, is_created):
        if is_created and hasattr(form, 'password') and form.password.data:
            model.set_password(form.password.data)


class QuestionAdmin(SecureModelView):
    column_list = ['id', 'question_text', 'correct_answer', 'creator', 'created_at']
    column_searchable_list = ['question_text']
    column_filters = ['created_by', 'created_at']
    form_excluded_columns = ['section_questions', 'test_answers', 'created_at', 'updated_at', 'creator']
    
    def on_model_change(self, form, model, is_created):
        if is_created:
            model.created_by = current_user.id


class SectionAdmin(SecureModelView):
    column_list = ['id', 'name', 'number_of_questions']
    column_searchable_list = ['name']
    form_excluded_columns = ['exam_sections']


class ExamAdmin(SecureModelView):
    column_list = ['id', 'name', 'creator', 'created_at']
    column_searchable_list = ['name']
    column_filters = ['created_by', 'created_at']
    form_excluded_columns = ['tests', 'created_at', 'creator']
    
    def on_model_change(self, form, model, is_created):
        if is_created:
            model.created_by = current_user.id


class TestAdmin(SecureModelView):
    column_list = ['id', 'exam', 'user', 'started_at', 'completed_at']
    column_filters = ['user_id', 'exam_id', 'started_at', 'completed_at']
    can_create = False
    can_edit = False


class ImportExamView(BaseView):
    """Custom admin view for importing exams from JSON"""
    
    def is_accessible(self):
        return current_user.is_authenticated
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))
    
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        if request.method == 'POST':
            # Check if file was uploaded
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
                from import_exam import import_exam_from_json
                success, message, exam = import_exam_from_json(json_data, current_user.id)
                
                if success:
                    flash(message, 'success')
                    return redirect(url_for('exam.index_view'))
                else:
                    flash(message, 'danger')
                    
            except json.JSONDecodeError as e:
                flash(f'Invalid JSON format: {str(e)}', 'danger')
            except Exception as e:
                flash(f'Error importing exam: {str(e)}', 'danger')
        
        # Render upload form
        return self.render('admin/import_exam.html')


def init_admin(app, db):
    """Initialize Flask-Admin with all models"""
    from models.user import User
    from models.question import Question
    from models.section import Section
    from models.section_question import SectionQuestion
    from models.exam import Exam
    from models.exam_section import ExamSection
    from models.test import Test
    from models.test_answer import TestAnswer
    
    admin = Admin(app, name='JLPT Admin', template_mode='bootstrap4')
    
    # Add model views
    admin.add_view(UserAdmin(User, db.session, name='Users'))
    admin.add_view(QuestionAdmin(Question, db.session, name='Questions'))
    admin.add_view(SectionAdmin(Section, db.session, name='Sections'))
    admin.add_view(SecureModelView(SectionQuestion, db.session, name='Section Questions'))
    admin.add_view(ExamAdmin(Exam, db.session, name='Exams'))
    admin.add_view(SecureModelView(ExamSection, db.session, name='Exam Sections'))
    admin.add_view(TestAdmin(Test, db.session, name='Tests'))
    admin.add_view(SecureModelView(TestAnswer, db.session, name='Test Answers'))
    
    # Add custom import view
    admin.add_view(ImportExamView(name='Import Exam', endpoint='import_exam'))
    
    return admin

