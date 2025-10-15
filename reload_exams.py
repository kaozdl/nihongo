#!/usr/bin/env python3
"""
Reload Exam Content Script

This script allows you to reload exam content from JSON files without dumping the database.
It preserves user test history while updating questions and sections.

Usage:
    python reload_exams.py

Or from Flask shell:
    from reload_exams import reload_all_standard_exams
    reload_all_standard_exams()
"""

# Setup path for package imports
import sys
import os
_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _parent not in sys.path:
    sys.path.insert(0, _parent)

from nihongo.app import app, db  # noqa: E402
from nihongo.import_exam import reload_exam_from_file, import_exam_from_file  # noqa: E402
from nihongo.models.user import User  # noqa: E402


def reload_all_standard_exams(create=False):
    """
    Reload all standard exam files (exam_easy.json, exam_medium.json, exam_hard.json).
    
    Args:
        create: If True, creates exams if they don't exist. If False (default), 
                only updates existing exams.
    """
    with app.app_context():
        # Get the first admin user (or create one if needed)
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            # Try to find default user
            admin = User.query.filter_by(email='default@nihongo.edu.uy').first()
            if admin:
                # Make them admin
                admin.is_admin = True
                db.session.commit()
                print("✅ Using default@nihongo.com as admin user")
            else:
                print("⚠️  No admin user found. Creating default admin...")
                admin = User(email='default@nihongo.com', is_admin=True)
                admin.set_password('admin')
                db.session.add(admin)
                db.session.commit()
                print("✅ Created admin user (email: default@nihongo.edu.uy, password: admin)")
        
        # Define exam files to reload
        exam_files = [
            ('exam_easy.json', 'JLPT N5 Practice Test - Easy (Basic)'),
            ('exam_medium.json', 'JLPT N5 Practice Test - Medium'),
            ('exam_hard.json', 'JLPT N5 Practice Test - Hard (Challenge)'),
            ('exam_long.json', 'JLPT N5 Practice Test - Hard (Long)'),
        ]
        
        results = []
        for file_name, exam_name in exam_files:
            file_path = os.path.join(os.path.dirname(__file__), file_name)
            
            if not os.path.exists(file_path):
                print(f"⚠️  File not found: {file_name}")
                results.append((file_name, False, "File not found"))
                continue
            
            print(f"🔄 Reloading {exam_name}...")
            success, message, exam = reload_exam_from_file(file_path, exam_name, admin.id)
            
            # If reload failed because exam doesn't exist and create flag is True, try importing
            if not success and create and "not found" in message.lower():
                print("📝 Exam not found, creating new exam...")
                success, message, exam = import_exam_from_file(file_path, admin.id)
            
            if success:
                print(f"✅ {message}")
            else:
                print(f"❌ {message}")
            
            results.append((file_name, success, message))
        
        # Summary
        print("\n" + "="*60)
        print("📊 RELOAD SUMMARY")
        print("="*60)
        successful = sum(1 for _, success, _ in results if success)
        failed = len(results) - successful
        
        for file_name, success, message in results:
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"{status}: {file_name}")
        
        print(f"\nTotal: {successful} succeeded, {failed} failed")
        print("="*60)
        
        return results


def reload_single_exam(file_path, exam_name):
    """
    Reload a single exam from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        exam_name: Name of the exam to reload
    
    Returns:
        tuple: (success, message, exam)
    """
    with app.app_context():
        # Get any admin user, or first user available
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            # Try default user
            admin = User.query.filter_by(email='default@nihongo.com').first()
        if not admin:
            # Use any user
            admin = User.query.first()
        
        if not admin:
            return False, "No users found in database", None
        
        print(f"🔄 Reloading exam from {file_path}...")
        success, message, exam = reload_exam_from_file(file_path, exam_name, admin.id)
        
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
        
        return success, message, exam


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        # Reload specific file
        file_path = sys.argv[1]
        exam_name = sys.argv[2] if len(sys.argv) > 2 else None
        
        if not exam_name:
            print("Usage: python reload_exams.py <file_path> <exam_name>")
            print("   or: python reload_exams.py  (to reload all standard exams)")
            sys.exit(1)
        
        reload_single_exam(file_path, exam_name)
    else:
        # Reload all standard exams
        reload_all_standard_exams()

