# Testing Guide for JLPT Test Manager

## Quick Start

### 1. Start the Application

```bash
cd /Users/kalildelima/workspace/nihongo
pyenv activate nihongo
flask init-db  # Only needed first time
flask run
```

The application will be available at: **http://localhost:5000**

### 2. Create Admin User

If you haven't already:

```bash
flask create-admin
# Enter email: admin@test.com
# Enter password: admin123
```

Or use the sample data script to create everything at once:

```bash
python sample_data.py
# Creates: admin@example.com / admin123
```

## Testing the Import Feature

### Step 1: Login

1. Go to http://localhost:5000
2. Click "Login"
3. Enter your admin credentials
4. You'll be redirected to the Exams page

### Step 2: Access Admin Panel

1. Click "Admin" in the navigation bar
2. You'll see the admin dashboard with all models

### Step 3: Import an Exam

1. Click "Import Exam" in the admin navigation
2. You'll see the import page with instructions
3. Click "Choose File" and select one of:
   - `exam_easy.json` - JLPT N5 (10 questions)
   - `exam_medium.json` - JLPT N4 (13 questions)
   - `exam_hard.json` - JLPT N2 (15 questions)
4. Click "Import Exam"
5. You should see a success message

### Step 4: Take the Exam

1. Click "Exams" in the navigation
2. You'll see your imported exam(s)
3. Click "Start Exam"
4. Answer the questions (they auto-save)
5. Click "Submit Exam"
6. View your results with explanations

## Available Test Files

### Easy Exam (exam_easy.json)
- **Level**: JLPT N5 (Beginner)
- **Sections**: Grammar (5) + Vocabulary (5)
- **Total**: 10 questions
- **Topics**: Basic particles, daily vocabulary

### Medium Exam (exam_medium.json)
- **Level**: JLPT N4 (Intermediate)
- **Sections**: Grammar (7) + Vocabulary (6)
- **Total**: 13 questions
- **Topics**: Grammar patterns, expressions, business terms

### Hard Exam (exam_hard.json)
- **Level**: JLPT N2 (Advanced)
- **Sections**: Grammar (8) + Vocabulary (7)
- **Total**: 15 questions
- **Topics**: Advanced grammar, business vocabulary, abstract concepts

## Testing Checklist

### Basic Functionality
- [ ] User registration works
- [ ] User login works
- [ ] Admin panel accessible
- [ ] Can view exams list

### Import Feature
- [ ] Can access Import Exam page
- [ ] Can download example JSON
- [ ] Can upload JSON file
- [ ] Receives success message on import
- [ ] Exam appears in exams list

### Taking Exams
- [ ] Can start an exam
- [ ] Questions display correctly
- [ ] Can select answers
- [ ] Answers auto-save
- [ ] Can submit exam
- [ ] Results page shows score

### Results Page
- [ ] Shows correct score percentage
- [ ] Lists all questions
- [ ] Shows user's answers
- [ ] Shows correct answers
- [ ] Displays explanations
- [ ] Can return to exams list

### Admin Features
- [ ] Can create questions manually
- [ ] Can create sections
- [ ] Can create exams
- [ ] Can view all tests
- [ ] Can view test answers

## Common Issues

### Port Already in Use
```bash
# Use a different port
flask run --port 5001
```

### Database Not Initialized
```bash
flask init-db
```

### Cache Issues
```bash
# Clear Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete
```

### Import Errors
- Make sure JSON is valid UTF-8
- Check JSON syntax with a validator
- Ensure all required fields are present
- Verify correct_answer is 1, 2, 3, or 4

## Example Test Workflow

1. **Import Easy Exam**
   - Login as admin
   - Go to Admin → Import Exam
   - Upload `exam_easy.json`
   - Verify success message

2. **Take the Test**
   - Go to Exams
   - Click "Start Exam" on the easy test
   - Answer all 10 questions
   - Submit the exam

3. **Review Results**
   - Check your score
   - Review wrong answers
   - Read explanations
   - Return to exam list

4. **Import More Exams**
   - Repeat with medium and hard exams
   - Take multiple tests
   - Track your progress

## API Testing (Advanced)

### Programmatic Import

```python
from app import app
from import_exam import import_exam_from_file

with app.app_context():
    success, message, exam = import_exam_from_file('exam_easy.json', user_id=1)
    if success:
        print(f"✅ {message}")
        print(f"Exam ID: {exam.id}")
    else:
        print(f"❌ {message}")
```

### Create Custom JSON

Use the example files as templates:

```json
{
  "name": "My Custom Test",
  "sections": [
    {
      "name": "My Section",
      "questions": [
        {
          "question_text": "Your question here",
          "answer_1": "Option 1",
          "answer_2": "Option 2",
          "answer_3": "Option 3",
          "answer_4": "Option 4",
          "correct_answer": 1,
          "explanation": "Why this is correct"
        }
      ]
    }
  ]
}
```

## Performance Testing

### Import Multiple Exams
```bash
# Import all three exams
cd /Users/kalildelima/workspace/nihongo
python -c "
from app import app
from import_exam import import_exam_from_file

with app.app_context():
    for level in ['easy', 'medium', 'hard']:
        success, msg, exam = import_exam_from_file(f'exam_{level}.json', 1)
        print(f'{level}: {msg}')
"
```

## Next Steps

1. Try importing all three difficulty levels
2. Take each exam and compare scores
3. Create your own custom exam JSON
4. Review the admin interface features
5. Explore the codebase structure

## Support

- See `README.md` for general documentation
- See `IMPORT_GUIDE.md` for JSON format details
- See `QUICKSTART.md` for setup instructions

## Feedback

Test the app and note:
- What works well
- What could be improved
- Any bugs or issues
- Feature requests

