# JLPT Test Manager

A Flask-based web application for managing and taking Japanese Language Proficiency Test (JLPT) practice exams.

## Features

- **User Authentication**: Secure login and registration system with admin roles (auto-login on registration)
- **Exam Management**: Create and organize JLPT practice exams with multiple sections
- **Random Exam Generator**: Create custom practice exams by randomly selecting questions from sections
- **Question Bank**: Store questions with text, images, and audio support
- **Test Taking**: Interactive interface for taking exams with auto-save functionality
- **Results & Analytics**: View detailed results with explanations
- **Exam History**: Track all completed exams with:
  - Start and completion dates/times
  - Test duration
  - All answers and scores
  - Performance statistics
  - Grade badges
  - Quick access to detailed results
- **User Content Management**: Regular users can create and manage their own:
  - Questions (with multi-language explanations)
  - Sections
  - Exams
  - Import exams from JSON files
  - Users only see and edit their own content
- **Admin Interface**: Full-featured admin panel powered by Flask-Admin for admins to manage:
  - All users and permissions
  - All questions across all users
  - All sections and exams
  - Tests and results
  - Bulk import exams from JSON

## Domain Model

### User
- Email (unique)
- Password (hashed)
- Is Admin (boolean) - determines access to admin panel

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

This command will:
- ✅ Create all database tables
- ✅ Create default user: `default@nihongo.edu.uy` / `nihongo123`
- ✅ Load sample exams: Easy, Medium, and Hard N5 practice tests

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
REM Or use migrations (recommended)
flask db-upgrade
```

This command will:
- ✅ Create all database tables
- ✅ Create default user: `default@nihongo.edu.uy` / `nihongo123`
- ✅ Load sample exams: Easy, Medium, and Hard N5 practice tests

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

### For All Users (Regular Users)

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

### Content Creation (All Users)

Regular users can create and manage their own content:

1. **Access My Content**: Navigate to `/mycontent` after logging in (or click "My Content" in navbar)
2. **Create Questions**: 
   - Add your own questions with bilingual explanations (English/Spanish)
   - Include optional images and audio
   - Only you can see and edit your questions
3. **Manage Sections**: Create sections to organize questions
4. **Build Exams**: Create custom exams using your sections
5. **Import Exams**: 
   - Upload JSON files to quickly import complete exams
   - Same format as admin import (see `docs/IMPORT_GUIDE.md`)
   - Imported content becomes yours automatically
6. **Privacy**: Your content is private - other users cannot see or edit it

### For Administrators

Administrators have additional privileges:

1. **Access Admin Panel**: Navigate to `/admin` after logging in
2. **Import Exams**: Bulk import exams from JSON files (see `docs/IMPORT_GUIDE.md`)
3. **Manage All Content**: View and edit ALL questions, sections, and exams across all users
4. **User Management**: 
   - View all user accounts
   - Promote users to admin
   - See user statistics
5. **Monitor Tests**: View all test submissions and results across all users
6. **Create Admin Users**: Use `flask create-admin` command to create/promote admin users

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
├── sample_data.py         # Sample data generator (optional)
├── requirements.txt       # Python dependencies
├── init.sh                # Setup script (macOS/Linux)
├── init.bat               # Setup script (Windows)
├── run_tests.sh           # Test runner (macOS/Linux)
├── run_tests.bat          # Test runner (Windows)
├── exam_easy.json         # N5 Easy exam (auto-loaded)
├── exam_medium.json       # N5 Medium exam (auto-loaded)
├── exam_hard.json         # N5 Hard exam (auto-loaded)
├── exam_example.json      # Example JSON for import
├── alembic.ini            # Alembic configuration
├── babel.cfg              # Babel configuration
├── docs/                  # Documentation
│   ├── QUICKSTART.md
│   ├── IMPORT_GUIDE.md
│   ├── TESTING_GUIDE.md
│   ├── WINDOWS_SETUP.md
│   ├── RANDOM_EXAM_FEATURE.md
│   ├── I18N_GUIDE.md
│   ├── MIGRATIONS_GUIDE.md
│   └── ALEMBIC_QUICKSTART.md
├── alembic/               # Database migrations
│   ├── versions/          # Migration scripts
│   └── env.py             # Migration environment
├── translations/          # i18n translations
│   └── es/                # Spanish translations
│       └── LC_MESSAGES/
│           ├── messages.po
│           └── messages.mo
├── models/               # Database models
│   ├── utils.py          # Utility functions (i18n)
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

The application uses environment-based configuration with three modes:

| Environment | Database | Use Case |
|------------|----------|----------|
| **Development** | SQLite | Local development (default) |
| **Production** | PostgreSQL | Production deployment |
| **Testing** | SQLite (memory) | Automated tests |

### Quick Setup

**For Local Development:**

```bash
# Copy the local environment template
cp env.local.example .env

# Edit if needed (defaults work out of the box)
nano .env
```

**For Production:**

```bash
# Copy the production environment template
cp env.production.example .env

# Edit with your production settings
nano .env
```

### Environment Variables

**Required:**
- `FLASK_ENV`: `development` or `production`
- `SECRET_KEY`: Flask secret key (generate with `python -c "import secrets; print(secrets.token_hex(32))"`)

**Optional:**
- `DATABASE_URL`: Override default database (PostgreSQL for production)
- `SQL_ECHO`: Set to `True` to log SQL queries
- `FLASK_RUN_HOST`: Server host (default: `127.0.0.1`)
- `FLASK_RUN_PORT`: Server port (default: `5000`)

See **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** for detailed production setup.

## Database

### Local Development (SQLite)

The application uses SQLite by default. The database file (`jlpt.db`) will be created automatically when you run `flask init-db`.

No additional setup required!

### Production (PostgreSQL)

For production, PostgreSQL is required:

```bash
# Install PostgreSQL adapter
pip install psycopg2-binary

# Set DATABASE_URL in .env
DATABASE_URL=postgresql://user:password@localhost:5432/jlpt_db
```

See **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** for complete production setup instructions.

## CLI Commands

### Database Management
- `flask init-db`: Initialize the database (creates tables, default user, and loads sample exams)
- `flask db-upgrade`: Apply all pending migrations (recommended for production)
- `flask db-migrate`: Generate a new migration after model changes
- `flask db-downgrade`: Rollback the last migration
- `flask db-history`: Show migration history

### User Management
- `flask create-admin`: Create a new admin user interactively (optional)

### Alembic (Advanced)
- `alembic upgrade head`: Apply all migrations
- `alembic revision --autogenerate -m "message"`: Create a new migration
- `alembic downgrade -1`: Rollback one migration
- `alembic current`: Show current database version
- `alembic history`: Show migration history

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
- **Migrations**: Alembic 1.17
- **Authentication**: Flask-Login
- **Admin Panel**: Flask-Admin
- **i18n**: Flask-Babel (English/Spanish)
- **Frontend**: Bootstrap 5, Jinja2 templates
- **Icons**: Bootstrap Icons
- **Random Generation**: Python random module for question selection

## Security Features

- Password hashing with Werkzeug
- CSRF protection with Flask-WTF
- Session-based authentication
- Secure admin access control

## Documentation

Comprehensive guides are available in the `docs/` directory:

### Getting Started
- **[Initialization Guide](docs/INITIALIZATION_GUIDE.md)** - Database setup and sample data loading
- **[Quick Start Guide](docs/QUICKSTART.md)** - Quick setup with automated scripts
- **[Windows Setup](docs/WINDOWS_SETUP.md)** - Complete Windows setup guide

### Deployment & Configuration
- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - 🚀 Production deployment with PostgreSQL
- **[Migrations Guide](docs/MIGRATIONS_GUIDE.md)** - Database migrations with Alembic
- **[Alembic Quick Start](docs/ALEMBIC_QUICKSTART.md)** - Quick Alembic reference

### Features
- **[User Content Management](docs/USER_CONTENT_MANAGEMENT.md)** - Create and manage your own questions and exams
- **[Import Guide](docs/IMPORT_GUIDE.md)** - JSON exam import instructions (admin only)
- **[Random Exam Feature](docs/RANDOM_EXAM_FEATURE.md)** - Random exam generator
- **[i18n Guide](docs/I18N_GUIDE.md)** - Internationalization (EN/ES)

### Development
- **[Testing Guide](docs/TESTING_GUIDE.md)** - Running and writing tests

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

This project is provided as-is for educational purposes.

