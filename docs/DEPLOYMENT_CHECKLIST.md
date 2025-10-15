# PythonAnywhere Deployment Checklist

## ✅ Pre-Deployment

- [x] Project zipped: `nihongo-pythonanywhere.zip` (125KB)
- [x] All dependencies listed in `requirements.txt`
- [x] Configuration files ready (`config.py`, `.env.example`)
- [x] Alembic migrations included
- [x] Sample data files included (3 exams)
- [x] Documentation complete

---

## 📋 Quick Deployment Steps

### 1️⃣ Upload & Extract
```bash
# Upload zip to PythonAnywhere
# Then in Bash console:
cd ~
unzip nihongo-pythonanywhere.zip -d nihongo
cd nihongo
```

### 2️⃣ Setup Environment
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3️⃣ Configure
```bash
# Create .env file
nano .env

# Add:
FLASK_ENV=production
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
DATABASE_URL=sqlite:////home/YOURUSERNAME/nihongo/jlpt.db
```

### 4️⃣ Initialize Database
```bash
flask init-db  # Creates tables + loads sample data
flask create-admin  # Create your admin user
```

### 5️⃣ Configure Web App
- Web tab → Add new web app → Manual configuration → Python 3.11
- Edit WSGI file (see full guide)
- Set virtualenv path: `/home/YOURUSERNAME/nihongo/venv`
- Set working directory: `/home/YOURUSERNAME/nihongo`
- **Reload** web app

### 6️⃣ Test
Visit: `https://YOURUSERNAME.pythonanywhere.com`

---

## 🔑 Default Credentials

**Email:** `default@nihongo.edu.uy`  
**Password:** `nihongo123`

⚠️ **Change immediately after first login!**

---

## 📦 What's Included in Zip

### Core Application
- `app.py` - Main Flask application
- `config.py` - Configuration management
- `import_exam.py` - Exam import functionality

### Models
- `models/` - All database models (User, Exam, Question, etc.)

### Templates
- `templates/` - All HTML templates
  - Login, Register, Exams, Take Exam, Results
  - Exam History, Admin templates
  
### Admin Interface
- `admin/` - Flask-Admin configuration

### Database Migrations
- `alembic/` - All migration files
- `alembic.ini` - Alembic configuration

### Sample Data
- `exam_easy.json` - N5 Easy exam (auto-loaded)
- `exam_medium.json` - N5 Medium exam (auto-loaded)
- `exam_hard.json` - N5 Hard exam (auto-loaded)
- `exam_example.json` - Template for custom exams

### Translations
- `translations/es/` - Spanish translations
- `babel.cfg` - Babel configuration

### Tests (Optional)
- `tests/` - Full test suite with pytest
- `pytest.ini` - Test configuration

### Documentation
- `README.md` - Project overview
- `docs/` - Complete documentation
  - Deployment Guide
  - Configuration Reference
  - User Content Management
  - Import Guide
  - Testing Guide
  - Migrations Guide
  - And more...

### Configuration
- `requirements.txt` - Python dependencies
- `requirements-dev.txt` - Development dependencies
- `env.local.example` - Local environment template
- `env.production.example` - Production environment template

### Scripts
- `init.sh` - Setup script (Linux/Mac)
- `init.bat` - Setup script (Windows)
- `run_tests.sh` - Test runner (Linux/Mac)
- `run_tests.bat` - Test runner (Windows)

---

## 🚫 Excluded from Zip

These files are **NOT** included (will be created on server):

- `*.pyc` - Python compiled files
- `__pycache__/` - Python cache directories
- `*.db` - Database files (create fresh)
- `venv/` - Virtual environment (create fresh)
- `.env` - Environment variables (create fresh)
- `.git/` - Git repository
- `htmlcov/` - Test coverage reports
- `.pytest_cache/` - Pytest cache
- `.ruff_cache/` - Linter cache
- `instance/` - Instance folder

---

## 🎯 Features Ready to Use

✅ User authentication (auto-login on registration)  
✅ Exam management  
✅ Test taking with auto-save  
✅ Results with explanations  
✅ Exam history tracking  
✅ Unlimited retakes  
✅ Random exam generator  
✅ User content creation  
✅ Admin panel  
✅ Bilingual (EN/ES)  
✅ Mobile-responsive  

---

## 📊 System Requirements

**Minimum:**
- Python 3.8+
- 100MB disk space
- PythonAnywhere free account

**Recommended:**
- Python 3.11
- 500MB disk space
- PythonAnywhere paid account (for PostgreSQL)

---

## 🔧 Post-Deployment Tasks

1. ✅ Change default user password
2. ✅ Create admin user(s)
3. ✅ Test all features
4. ✅ Configure custom domain (paid accounts)
5. ✅ Set up backups
6. ✅ Monitor error logs
7. ✅ Add custom content

---

## 📚 Quick Links

- Full Deployment Guide: `PYTHONANYWHERE_DEPLOYMENT.md`
- Project README: `README.md`
- Configuration Reference: `docs/CONFIGURATION_REFERENCE.md`
- User Guide: `docs/USER_CONTENT_MANAGEMENT.md`
- Testing Guide: `docs/TESTING_GUIDE.md`

---

## 🆘 Common Issues

**Issue:** Import errors  
**Fix:** Check WSGI file paths, activate venv, install requirements

**Issue:** Database not found  
**Fix:** Run `flask init-db`

**Issue:** Static files not loading  
**Fix:** Configure static files mapping in Web tab (or use CDN)

**Issue:** 500 errors  
**Fix:** Check error log in Web tab for details

---

**For detailed instructions, see: `PYTHONANYWHERE_DEPLOYMENT.md`**

**Happy Deploying! 🚀**
