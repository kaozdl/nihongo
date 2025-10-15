"""
JSON Exam Importer for JLPT Test Manager

This module provides functionality to import exams from JSON files.
"""

import json
from models import db
from models.user import User
from models.question import Question
from models.section import Section
from models.section_question import SectionQuestion
from models.exam import Exam
from models.exam_section import ExamSection


def import_exam_from_json(json_data, user_id):
    """
    Import an exam from JSON data.
    
    Args:
        json_data: Dictionary containing exam data (can be from JSON file)
        user_id: ID of the user creating the exam
    
    Returns:
        tuple: (success: bool, message: str, exam: Exam or None)
    
    Expected JSON format:
    {
        "name": "JLPT N5 Practice Test",
        "sections": [
            {
                "name": "Vocabulary",
                "questions": [
                    {
                        "question_text": "Question text here",
                        "question_image": "http://example.com/image.jpg",  # optional
                        "question_audio": "http://example.com/audio.mp3",  # optional
                        "answer_1": "First option",
                        "answer_2": "Second option",
                        "answer_3": "Third option",
                        "answer_4": "Fourth option",
                        "correct_answer": 1,  # 1, 2, 3, or 4
                        "explanation": "Explanation here"  # optional
                    }
                ]
            }
        ]
    }
    """
    
    try:
        # Validate user exists
        user = User.query.get(user_id)
        if not user:
            return False, f"User with ID {user_id} not found", None
        
        # Validate required fields
        if 'name' not in json_data:
            return False, "Missing required field: 'name'", None
        
        if 'sections' not in json_data or not isinstance(json_data['sections'], list):
            return False, "Missing or invalid 'sections' field", None
        
        if len(json_data['sections']) == 0:
            return False, "Exam must have at least one section", None
        
        # Create exam
        exam = Exam(
            name=json_data['name'],
            created_by=user_id
        )
        db.session.add(exam)
        db.session.flush()  # Get exam.id without committing
        
        # Process sections
        for section_order, section_data in enumerate(json_data['sections'], start=1):
            if 'name' not in section_data:
                db.session.rollback()
                return False, f"Section {section_order} missing 'name' field", None
            
            if 'questions' not in section_data or not isinstance(section_data['questions'], list):
                db.session.rollback()
                return False, f"Section '{section_data.get('name')}' missing or invalid 'questions' field", None
            
            if len(section_data['questions']) == 0:
                db.session.rollback()
                return False, f"Section '{section_data.get('name')}' must have at least one question", None
            
            # Create section
            section = Section(
                name=section_data['name'],
                number_of_questions=len(section_data['questions'])
            )
            db.session.add(section)
            db.session.flush()
            
            # Create questions
            for question_order, question_data in enumerate(section_data['questions'], start=1):
                # Validate question fields
                required_question_fields = [
                    'question_text', 'answer_1', 'answer_2', 
                    'answer_3', 'answer_4', 'correct_answer'
                ]
                
                for field in required_question_fields:
                    if field not in question_data:
                        db.session.rollback()
                        return False, f"Question {question_order} in section '{section.name}' missing '{field}'", None
                
                # Validate correct_answer
                correct_answer = question_data['correct_answer']
                if not isinstance(correct_answer, int) or correct_answer not in [1, 2, 3, 4]:
                    db.session.rollback()
                    return False, f"Question {question_order} in section '{section.name}' has invalid 'correct_answer' (must be 1, 2, 3, or 4)", None
                
                # Process explanation (convert dict to JSON string if needed)
                explanation = question_data.get('explanation')
                if isinstance(explanation, dict):
                    # If explanation is a dict, convert to JSON string
                    explanation = json.dumps(explanation, ensure_ascii=False)
                
                # Create question
                question = Question(
                    question_text=question_data['question_text'],
                    question_image=question_data.get('question_image'),
                    question_audio=question_data.get('question_audio'),
                    answer_1=question_data['answer_1'],
                    answer_2=question_data['answer_2'],
                    answer_3=question_data['answer_3'],
                    answer_4=question_data['answer_4'],
                    correct_answer=correct_answer,
                    explanation=explanation,
                    created_by=user_id
                )
                db.session.add(question)
                db.session.flush()
                
                # Link question to section
                section_question = SectionQuestion(
                    section_id=section.id,
                    question_id=question.id,
                    order=question_order
                )
                db.session.add(section_question)
            
            # Link section to exam
            exam_section = ExamSection(
                exam_id=exam.id,
                section_id=section.id,
                order=section_order
            )
            db.session.add(exam_section)
        
        # Commit all changes
        db.session.commit()
        
        total_questions = sum(len(s['questions']) for s in json_data['sections'])
        message = f"Successfully imported exam '{exam.name}' with {len(json_data['sections'])} sections and {total_questions} questions"
        
        return True, message, exam
        
    except Exception as e:
        db.session.rollback()
        return False, f"Error importing exam: {str(e)}", None


def import_exam_from_file(file_path, user_id):
    """
    Import an exam from a JSON file.
    
    Args:
        file_path: Path to JSON file
        user_id: ID of the user creating the exam
    
    Returns:
        tuple: (success: bool, message: str, exam: Exam or None)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        return import_exam_from_json(json_data, user_id)
    except FileNotFoundError:
        return False, f"File not found: {file_path}", None
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON format: {str(e)}", None
    except Exception as e:
        return False, f"Error reading file: {str(e)}", None


def reload_exam_from_json(json_data, exam_name_or_id, user_id):
    """
    Reload/update an existing exam from JSON data.
    This updates questions and sections while preserving user test data.
    
    Args:
        json_data: Dictionary containing exam data
        exam_name_or_id: Name or ID of the exam to reload
        user_id: ID of the user performing the reload
    
    Returns:
        tuple: (success: bool, message: str, exam: Exam or None)
    """
    try:
        # Find the exam
        if isinstance(exam_name_or_id, int):
            exam = Exam.query.get(exam_name_or_id)
        else:
            exam = Exam.query.filter_by(name=exam_name_or_id).first()
        
        if not exam:
            return False, f"Exam '{exam_name_or_id}' not found", None
        
        # Validate required fields
        if 'name' not in json_data:
            return False, "Missing required field: 'name'", None
        
        if 'sections' not in json_data or not isinstance(json_data['sections'], list):
            return False, "Missing or invalid 'sections' field", None
        
        if len(json_data['sections']) == 0:
            return False, "Exam must have at least one section", None
        
        # Update exam name if different
        exam.name = json_data['name']
        
        # Get existing sections for this exam
        existing_exam_sections = {es.section.name: es for es in exam.exam_sections}
        processed_sections = set()
        
        # Process sections from JSON
        for section_order, section_data in enumerate(json_data['sections'], start=1):
            if 'name' not in section_data:
                db.session.rollback()
                return False, f"Section {section_order} missing 'name' field", None
            
            if 'questions' not in section_data or not isinstance(section_data['questions'], list):
                db.session.rollback()
                return False, f"Section '{section_data.get('name')}' missing or invalid 'questions' field", None
            
            section_name = section_data['name']
            processed_sections.add(section_name)
            
            # Find or create section
            if section_name in existing_exam_sections:
                # Update existing section
                exam_section = existing_exam_sections[section_name]
                section = exam_section.section
                exam_section.order = section_order
            else:
                # Create new section
                section = Section(
                    name=section_name,
                    number_of_questions=len(section_data['questions'])
                )
                db.session.add(section)
                db.session.flush()
                
                exam_section = ExamSection(
                    exam_id=exam.id,
                    section_id=section.id,
                    order=section_order
                )
                db.session.add(exam_section)
            
            # Update section question count
            section.number_of_questions = len(section_data['questions'])
            
            # Get existing questions for this section
            existing_questions = {sq.order: sq for sq in section.section_questions}
            
            # Process questions
            for question_order, question_data in enumerate(section_data['questions'], start=1):
                # Validate question fields
                required_question_fields = [
                    'question_text', 'answer_1', 'answer_2',
                    'answer_3', 'answer_4', 'correct_answer'
                ]
                
                for field in required_question_fields:
                    if field not in question_data:
                        db.session.rollback()
                        return False, f"Question {question_order} in section '{section.name}' missing '{field}'", None
                
                # Validate correct_answer
                correct_answer = question_data['correct_answer']
                if not isinstance(correct_answer, int) or correct_answer not in [1, 2, 3, 4]:
                    db.session.rollback()
                    return False, f"Question {question_order} in section '{section.name}' has invalid 'correct_answer'", None
                
                # Process explanation
                explanation = question_data.get('explanation')
                if isinstance(explanation, dict):
                    explanation = json.dumps(explanation, ensure_ascii=False)
                
                # Update or create question
                if question_order in existing_questions:
                    # Update existing question
                    section_question = existing_questions[question_order]
                    question = section_question.question
                    
                    question.question_text = question_data['question_text']
                    question.question_image = question_data.get('question_image')
                    question.question_audio = question_data.get('question_audio')
                    question.answer_1 = question_data['answer_1']
                    question.answer_2 = question_data['answer_2']
                    question.answer_3 = question_data['answer_3']
                    question.answer_4 = question_data['answer_4']
                    question.correct_answer = correct_answer
                    question.explanation = explanation
                else:
                    # Create new question
                    question = Question(
                        question_text=question_data['question_text'],
                        question_image=question_data.get('question_image'),
                        question_audio=question_data.get('question_audio'),
                        answer_1=question_data['answer_1'],
                        answer_2=question_data['answer_2'],
                        answer_3=question_data['answer_3'],
                        answer_4=question_data['answer_4'],
                        correct_answer=correct_answer,
                        explanation=explanation,
                        created_by=user_id
                    )
                    db.session.add(question)
                    db.session.flush()
                    
                    section_question = SectionQuestion(
                        section_id=section.id,
                        question_id=question.id,
                        order=question_order
                    )
                    db.session.add(section_question)
            
            # Remove questions that no longer exist in JSON
            for question_order in list(existing_questions.keys()):
                if question_order > len(section_data['questions']):
                    section_question = existing_questions[question_order]
                    # Note: Question is preserved in DB (for test history), just unlinked from section
                    db.session.delete(section_question)
        
        # Remove sections that no longer exist in JSON
        for section_name, exam_section in existing_exam_sections.items():
            if section_name not in processed_sections:
                # Note: Section is preserved in DB (for test history), just unlinked from exam
                db.session.delete(exam_section)
        
        # Commit all changes
        db.session.commit()
        
        total_questions = sum(len(s['questions']) for s in json_data['sections'])
        message = f"Successfully reloaded exam '{exam.name}' with {len(json_data['sections'])} sections and {total_questions} questions"
        
        return True, message, exam
        
    except Exception as e:
        db.session.rollback()
        return False, f"Error reloading exam: {str(e)}", None


def reload_exam_from_file(file_path, exam_name_or_id, user_id):
    """
    Reload an exam from a JSON file.
    
    Args:
        file_path: Path to JSON file
        exam_name_or_id: Name or ID of the exam to reload
        user_id: ID of the user performing the reload
    
    Returns:
        tuple: (success: bool, message: str, exam: Exam or None)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        return reload_exam_from_json(json_data, exam_name_or_id, user_id)
    except FileNotFoundError:
        return False, f"File not found: {file_path}", None
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON format: {str(e)}", None
    except Exception as e:
        return False, f"Error reading file: {str(e)}", None


def validate_exam_json(json_data):
    """
    Validate exam JSON structure without importing.
    
    Args:
        json_data: Dictionary to validate
    
    Returns:
        tuple: (valid: bool, errors: list)
    """
    errors = []
    
    if not isinstance(json_data, dict):
        errors.append("Root element must be a JSON object")
        return False, errors
    
    if 'name' not in json_data:
        errors.append("Missing required field: 'name'")
    
    if 'sections' not in json_data:
        errors.append("Missing required field: 'sections'")
    elif not isinstance(json_data['sections'], list):
        errors.append("'sections' must be an array")
    elif len(json_data['sections']) == 0:
        errors.append("Exam must have at least one section")
    else:
        for i, section in enumerate(json_data['sections'], start=1):
            if not isinstance(section, dict):
                errors.append(f"Section {i} must be a JSON object")
                continue
            
            if 'name' not in section:
                errors.append(f"Section {i} missing 'name' field")
            
            if 'questions' not in section:
                errors.append(f"Section {i} missing 'questions' field")
            elif not isinstance(section['questions'], list):
                errors.append(f"Section {i} 'questions' must be an array")
            elif len(section['questions']) == 0:
                errors.append(f"Section {i} must have at least one question")
            else:
                for j, question in enumerate(section['questions'], start=1):
                    if not isinstance(question, dict):
                        errors.append(f"Section {i}, Question {j} must be a JSON object")
                        continue
                    
                    required_fields = [
                        'question_text', 'answer_1', 'answer_2',
                        'answer_3', 'answer_4', 'correct_answer'
                    ]
                    
                    for field in required_fields:
                        if field not in question:
                            errors.append(f"Section {i}, Question {j} missing '{field}'")
                    
                    if 'correct_answer' in question:
                        if not isinstance(question['correct_answer'], int) or question['correct_answer'] not in [1, 2, 3, 4]:
                            errors.append(f"Section {i}, Question {j} 'correct_answer' must be 1, 2, 3, or 4")
    
    return len(errors) == 0, errors

