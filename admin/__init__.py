from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for, request, flash
from wtforms import TextAreaField
from wtforms.widgets import TextArea
import json
from models.utils import parse_explanation, set_explanation


class SecureModelView(ModelView):
    """Base class for admin views with authentication and admin access"""
    
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin
    
    def inaccessible_callback(self, name, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login', next=request.url))
        else:
            flash('You do not have permission to access the admin panel.', 'danger')
            return redirect(url_for('index'))


class UserAdmin(SecureModelView):
    column_list = ['id', 'email', 'is_admin']
    column_searchable_list = ['email']
    column_filters = ['is_admin']
    form_excluded_columns = ['password_hash', 'created_questions', 'created_exams', 'tests', 'test_answers']
    
    def on_model_change(self, form, model, is_created):
        if is_created and hasattr(form, 'password') and form.password.data:
            model.set_password(form.password.data)


class QuestionAdmin(SecureModelView):
    column_list = ['id', 'question_text', 'correct_answer', 'creator', 'created_at']
    column_searchable_list = ['question_text']
    column_filters = ['created_by', 'created_at']
    form_excluded_columns = ['section_questions', 'test_answers', 'created_at', 'updated_at', 'creator', 'explanation']
    
    # Override form creation to add custom explanation fields
    form_extra_fields = {
        'explanation_en': TextAreaField('Explanation (English)', widget=TextArea()),
        'explanation_es': TextAreaField('Explanation (Español)', widget=TextArea())
    }
    
    def on_model_change(self, form, model, is_created):
        if is_created:
            model.created_by = current_user.id
        
        # Handle multi-language explanation
        en_text = form.explanation_en.data if hasattr(form, 'explanation_en') else ''
        es_text = form.explanation_es.data if hasattr(form, 'explanation_es') else ''
        
        if en_text or es_text:
            model.explanation = set_explanation(en_text or '', es_text or '')
        else:
            model.explanation = ''
    
    def edit_form(self, obj=None):
        form = super(QuestionAdmin, self).edit_form(obj)
        
        # Pre-populate explanation fields from existing data
        if obj and obj.explanation:
            explanation_dict = parse_explanation(obj.explanation)
            if hasattr(form, 'explanation_en'):
                form.explanation_en.data = explanation_dict.get('EN', '')
            if hasattr(form, 'explanation_es'):
                form.explanation_es.data = explanation_dict.get('ES', '')
        
        return form


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
        return current_user.is_authenticated and current_user.is_admin
    
    def inaccessible_callback(self, name, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login', next=request.url))
        else:
            flash('You do not have permission to access the admin panel.', 'danger')
            return redirect(url_for('index'))
    
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


class UserContentView(ModelView):
    """Base class for user-specific content views"""
    
    def is_accessible(self):
        return current_user.is_authenticated
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))
    
    def get_query(self):
        """Filter query to only show user's own content"""
        query = super().get_query()
        if hasattr(self.model, 'created_by'):
            query = query.filter(self.model.created_by == current_user.id)
        return query
    
    def get_count_query(self):
        """Filter count query to only count user's own content"""
        query = super().get_count_query()
        if hasattr(self.model, 'created_by'):
            query = query.filter(self.model.created_by == current_user.id)
        return query


class AuthenticatedModelView(ModelView):
    """Base class for views that require authentication but don't filter by ownership"""
    
    def is_accessible(self):
        return current_user.is_authenticated
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))


class MyQuestionView(UserContentView):
    """View for users to manage their own questions"""
    column_list = ['id', 'question_text', 'correct_answer', 'created_at']
    column_searchable_list = ['question_text']
    column_filters = ['created_at']
    form_excluded_columns = ['section_questions', 'test_answers', 'created_at', 'updated_at', 'creator', 'created_by', 'explanation']
    
    # Override form creation to add custom explanation fields
    form_extra_fields = {
        'explanation_en': TextAreaField('Explanation (English)', widget=TextArea()),
        'explanation_es': TextAreaField('Explanation (Español)', widget=TextArea())
    }
    
    def on_model_change(self, form, model, is_created):
        if is_created:
            model.created_by = current_user.id
        else:
            # Verify user owns this question
            if model.created_by != current_user.id:
                raise ValueError('You can only edit your own questions')
        
        # Handle multi-language explanation
        en_text = form.explanation_en.data if hasattr(form, 'explanation_en') else ''
        es_text = form.explanation_es.data if hasattr(form, 'explanation_es') else ''
        
        if en_text or es_text:
            model.explanation = set_explanation(en_text or '', es_text or '')
        else:
            model.explanation = ''
    
    def edit_form(self, obj=None):
        form = super().edit_form(obj)
        
        # Pre-populate explanation fields from existing data
        if obj and obj.explanation:
            explanation_dict = parse_explanation(obj.explanation)
            if hasattr(form, 'explanation_en'):
                form.explanation_en.data = explanation_dict.get('EN', '')
            if hasattr(form, 'explanation_es'):
                form.explanation_es.data = explanation_dict.get('ES', '')
        
        return form


class MySectionView(UserContentView):
    """View for users to manage their own sections"""
    column_list = ['id', 'name', 'number_of_questions']
    column_searchable_list = ['name']
    form_excluded_columns = ['section_questions', 'exam_sections']
    can_create = True
    can_edit = True
    can_delete = True
    
    def on_model_change(self, form, model, is_created):
        # Sections don't have created_by, so we'll allow all users to create them
        # But we can still track ownership through questions
        pass


class MyExamView(UserContentView):
    """View for users to manage their own exams"""
    column_list = ['id', 'name', 'created_at']
    column_searchable_list = ['name']
    column_filters = ['created_at']
    form_excluded_columns = ['exam_sections', 'tests', 'created_at', 'updated_at', 'creator', 'created_by']
    
    def on_model_change(self, form, model, is_created):
        if is_created:
            model.created_by = current_user.id
        else:
            # Verify user owns this exam
            if model.created_by != current_user.id:
                raise ValueError('You can only edit your own exams')


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
    
    # Main admin interface (admin users only)
    admin = Admin(app, name='JLPT Admin', template_mode='bootstrap4', endpoint='admin', url='/admin')
    
    # Add model views (admin only)
    admin.add_view(UserAdmin(User, db.session, name='Users', endpoint='admin_users'))
    admin.add_view(QuestionAdmin(Question, db.session, name='Questions', endpoint='admin_questions'))
    admin.add_view(SectionAdmin(Section, db.session, name='Sections', endpoint='admin_sections'))
    admin.add_view(SecureModelView(SectionQuestion, db.session, name='Section Questions', endpoint='admin_section_questions'))
    admin.add_view(ExamAdmin(Exam, db.session, name='Exams', endpoint='admin_exams'))
    admin.add_view(SecureModelView(ExamSection, db.session, name='Exam Sections', endpoint='admin_exam_sections'))
    admin.add_view(TestAdmin(Test, db.session, name='Tests', endpoint='admin_tests'))
    admin.add_view(SecureModelView(TestAnswer, db.session, name='Test Answers', endpoint='admin_test_answers'))
    
    # Add custom import view (admin only)
    admin.add_view(ImportExamView(name='Import Exam', endpoint='import_exam'))
    
    # User content management interface (all authenticated users)
    user_admin = Admin(app, name='My Content', template_mode='bootstrap4', endpoint='mycontent', url='/mycontent')
    
    # Add user-specific views
    user_admin.add_view(MyQuestionView(Question, db.session, name='My Questions', endpoint='my_questions'))
    user_admin.add_view(MySectionView(Section, db.session, name='Sections', endpoint='my_sections'))
    user_admin.add_view(MyExamView(Exam, db.session, name='My Exams', endpoint='my_exams'))
    user_admin.add_view(AuthenticatedModelView(SectionQuestion, db.session, name='Section Questions', endpoint='my_section_questions'))
    user_admin.add_view(AuthenticatedModelView(ExamSection, db.session, name='Exam Sections', endpoint='my_exam_sections'))
    
    return admin

