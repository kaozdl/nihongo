# JLPT Test Manager

A Flask-based web application for managing and taking Japanese Language Proficiency Test (JLPT) practice exams.

## Features

- **User Authentication**: Secure login and registration system
- **Exam Management**: Create and organize JLPT practice exams with multiple sections
- **Random Exam Generator**: Create custom practice exams by randomly selecting questions from sections
- **Question Bank**: Store questions with text, images, and audio support
- **Test Taking**: Interactive interface for taking exams with auto-save functionality
- **Results & Analytics**: View detailed results with explanations
- **Admin Interface**: Full-featured admin panel powered by Flask-Admin for managing:
  - Users
  - Questions
  - Sections
  - Exams
  - Tests and results

## Domain Model

### User
- Email (unique)
- Password (hashed)

### Question
- Question text
- Optional image URL
- Optional audio URL
- Four answer options
- Correct answer (1-4)
- Explanation
- Creator (User FK)
- Timestamps

### Section
- Name
- Number of questions
- Associated questions (via SectionQuestion)

### Exam
- Name
- Creator (User FK)
- Sections (via ExamSection)
- Created timestamp

### Test
- Associated exam
- User taking the test
- Start and completion timestamps
- Answers (via TestAnswer)

## Installation

### Prerequisites
- Python 3.8 or higher
- pip

### Setup

#### For macOS/Linux:

1. **Clone or navigate to the project directory**
```bash
cd /path/to/nihongo
```

2. **Create a virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Create environment file** (optional)
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize the database**
```bash
flask init-db
```

6. **Create an admin user**
```bash
flask create-admin
```

#### For Windows:

1. **Clone or navigate to the project directory**
```cmd
cd C:\path\to\nihongo
```

2. **Create a virtual environment**
```cmd
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies**
```cmd
pip install -r requirements.txt
```

4. **Create environment file** (optional)
```cmd
copy .env.example .env
REM Edit .env with your configuration
```

5. **Initialize the database**
```cmd
flask init-db
```

6. **Create an admin user**
```cmd
flask create-admin
```

## Running the Application

### Development Mode

**macOS/Linux:**
```bash
flask run
# Or
python app.py
```

**Windows:**
```cmd
flask run
REM Or
python app.py
```

The application will be available at `http://localhost:5000`

### Production Mode

**macOS/Linux (Gunicorn):**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

**Windows (Waitress):**
```cmd
pip install waitress
waitress-serve --port=8000 app:app
```

**Note:** Gunicorn doesn't work on Windows. Use Waitress or another WSGI server instead.

## Usage

### For Users

1. **Register/Login**: Create an account or log in at `/register` or `/login`
2. **Browse Exams**: View available exams at `/exams`
3. **Generate Random Exam**: 
   - Select sections (Grammar, Vocabulary, etc.)
   - Choose number of questions from each section
   - Click "Generate Random Exam" for instant practice
4. **Take Exam**: Click "Start Exam" to begin a test
5. **Answer Questions**: Select answers (automatically saved)
6. **Submit**: Click "Submit Exam" when finished
7. **View Results**: See your score and review answers with explanations

### For Administrators

1. **Access Admin Panel**: Navigate to `/admin` after logging in
2. **Import Exams**: Bulk import exams from JSON files (see `IMPORT_GUIDE.md`)
3. **Create Questions**: Add questions with optional images and audio
4. **Create Sections**: Organize questions into sections
5. **Create Exams**: Build exams by combining sections
6. **Manage Users**: View and manage user accounts
7. **Monitor Tests**: View test submissions and results

#### Bulk Import Feature

You can import complete exams with sections and questions from JSON files:
- Navigate to Admin → "Import Exam"
- Upload a JSON file with your exam structure
- See `IMPORT_GUIDE.md` for detailed format and examples
- Download example JSON from the import page

## Project Structure

```
nihongo/
├── app.py                 # Main Flask application
├── import_exam.py         # Exam JSON import module
├── sample_data.py         # Sample data generator
├── requirements.txt       # Python dependencies
├── init.sh                # Setup script (macOS/Linux)
├── init.bat               # Setup script (Windows)
├── run_tests.sh           # Test runner (macOS/Linux)
├── run_tests.bat          # Test runner (Windows)
├── exam_example.json      # Example JSON for import
├── IMPORT_GUIDE.md        # Import feature documentation
├── WINDOWS_SETUP.md       # Windows-specific setup guide
├── models/               # Database models
│   ├── __init__.py
│   ├── user.py
│   ├── question.py
│   ├── section.py
│   ├── section_question.py
│   ├── exam.py
│   ├── exam_section.py
│   ├── test.py
│   └── test_answer.py
├── admin/                # Admin interface
│   └── __init__.py
└── templates/            # Jinja templates
    ├── base.html
    ├── login.html
    ├── register.html
    ├── exams.html
    ├── take_exam.html
    ├── results.html
    └── admin/
        └── import_exam.html
```

## Configuration

Configure the application using environment variables or by editing `app.py`:

- `SECRET_KEY`: Flask secret key (required for sessions)
- `DATABASE_URL`: Database connection string (default: `sqlite:///jlpt.db`)

## Database

The application uses SQLite by default. The database file (`jlpt.db`) will be created automatically when you run `flask init-db`.

To use a different database (PostgreSQL, MySQL, etc.), set the `DATABASE_URL` environment variable:
```
DATABASE_URL=postgresql://user:password@localhost/jlpt
```

## CLI Commands

- `flask init-db`: Initialize the database (create all tables)
- `flask create-admin`: Create a new admin user interactively

## Features in Detail

### Random Exam Generator

The random exam generator allows users to create customized practice tests:

1. **Select Sections**: Choose from available sections (Grammar, Vocabulary, Reading, etc.)
2. **Customize Questions**: Specify how many questions to include from each section
3. **Instant Generation**: Questions are randomly selected and exam is created immediately
4. **Automatic Start**: Generated exam starts automatically for seamless practice
5. **Unique Every Time**: Each generation produces a different set of questions

Example: Select 5 Grammar questions + 3 Vocabulary questions = Custom 8-question practice exam

### How It Works

1. Admin creates sections with questions
2. Users visit the Exams page
3. Random Exam Generator shows available sections with question counts
4. User selects desired number of questions per section
5. System randomly selects questions and creates exam
6. User immediately starts taking the exam

## Technologies Used

- **Backend**: Flask 3.0
- **Database**: SQLAlchemy (SQLite default)
- **Authentication**: Flask-Login
- **Admin Panel**: Flask-Admin
- **Frontend**: Bootstrap 5, Jinja2 templates
- **Icons**: Bootstrap Icons
- **Random Generation**: Python random module for question selection

## Security Features

- Password hashing with Werkzeug
- CSRF protection with Flask-WTF
- Session-based authentication
- Secure admin access control

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

This project is provided as-is for educational purposes.

