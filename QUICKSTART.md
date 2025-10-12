# Quick Start Guide

## Option 1: Automated Setup (Recommended)

Run the initialization script:

```bash
./init.sh
```

This will automatically:
- Create a virtual environment
- Install all dependencies
- Initialize the database

## Option 2: Manual Setup

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Initialize Database

```bash
flask init-db
```

## Create Admin User

```bash
source venv/bin/activate  # if not already activated
flask create-admin
```

Follow the prompts to enter email and password.

## Load Sample Data (Optional)

To quickly test the application with sample questions and exams:

```bash
python sample_data.py
```

This creates:
- Admin user: `admin@example.com` / `admin123`
- Sample JLPT N5 Practice Test with 5 questions across 3 sections

## Run the Application

```bash
flask run
```

Visit: http://localhost:5000

## First Steps

### As a Regular User:

1. Register at `/register` or login at `/login`
2. Browse available exams at `/exams`
3. Click "Start Exam" to begin
4. Answer questions (auto-saved)
5. Submit and view results

### As an Administrator:

1. Login to the application
2. Navigate to `/admin`
3. Create questions, sections, and exams:
   - **Questions**: Add individual questions with answers
   - **Sections**: Group questions into sections
   - **Section Questions**: Link questions to sections
   - **Exams**: Create exams
   - **Exam Sections**: Add sections to exams

## Project Structure

```
nihongo/
├── app.py                    # Main application
├── init.sh                   # Setup script
├── sample_data.py            # Sample data generator
├── requirements.txt          # Dependencies
├── models/                   # Database models
├── admin/                    # Admin interface
└── templates/                # HTML templates
```

## Common Tasks

### Create a New Question

1. Go to `/admin`
2. Click "Questions" → "Create"
3. Fill in:
   - Question text
   - Four answer options
   - Correct answer (1-4)
   - Optional: image URL, audio URL, explanation
4. Select creator (yourself)
5. Save

### Create a New Exam

1. Create questions (if not already done)
2. Create a section and link questions to it:
   - Go to "Sections" → Create
   - Go to "Section Questions" → Add questions to the section
3. Create an exam:
   - Go to "Exams" → Create
4. Link sections to the exam:
   - Go to "Exam Sections" → Add sections to the exam

### View Test Results

1. Go to `/admin`
2. Click "Tests" to see all completed tests
3. Click "Test Answers" to see individual answers

## Troubleshooting

### "Import not found" errors

Make sure you activated the virtual environment:
```bash
source venv/bin/activate
```

### Database errors

Reinitialize the database:
```bash
flask init-db
```

### Port already in use

Run on a different port:
```bash
flask run --port 8000
```

## Security Notes

- Change the `SECRET_KEY` in production
- Use a production database (PostgreSQL, MySQL)
- Enable HTTPS in production
- Use strong passwords for admin accounts

## Support

For issues or questions, refer to the main README.md file.

