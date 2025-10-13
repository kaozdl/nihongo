# Windows Setup Guide

Complete guide for setting up and running the JLPT Test Manager on Windows.

## Prerequisites

### Required Software

1. **Python 3.8 or higher**
   - Download from: https://www.python.org/downloads/
   - ✅ **Important**: Check "Add Python to PATH" during installation
   - Verify installation:
     ```cmd
     python --version
     ```

2. **pip** (usually included with Python)
   - Verify installation:
     ```cmd
     pip --version
     ```

### Optional (Recommended)

- **Git for Windows**: https://git-scm.com/download/win
- **VS Code**: https://code.visualstudio.com/

## Quick Start

### Option 1: Automated Setup (Recommended)

1. **Download the project** (or clone with Git)
   ```cmd
   cd C:\path\to\nihongo
   ```

2. **Run the setup script**
   ```cmd
   init.bat
   ```
   This will:
   - Create virtual environment
   - Install dependencies
   - Initialize database

3. **Create admin user**
   ```cmd
   venv\Scripts\activate
   flask create-admin
   ```

4. **Run the application**
   ```cmd
   flask run
   ```

5. **Open browser**
   - Visit: http://localhost:5000

### Option 2: Manual Setup

1. **Navigate to project directory**
   ```cmd
   cd C:\path\to\nihongo
   ```

2. **Create virtual environment**
   ```cmd
   python -m venv venv
   ```

3. **Activate virtual environment**
   ```cmd
   venv\Scripts\activate
   ```
   
   You should see `(venv)` in your command prompt.

4. **Install dependencies**
   ```cmd
   pip install -r requirements.txt
   ```

5. **Initialize database**
   ```cmd
   flask init-db
   ```

6. **Create admin user**
   ```cmd
   flask create-admin
   ```
   Enter your email and password when prompted.

7. **Run the application**
   ```cmd
   flask run
   ```

8. **Access the application**
   - Open browser: http://localhost:5000

## Running Tests

### Install Test Dependencies
```cmd
venv\Scripts\activate
pip install -r requirements-dev.txt
```

### Run All Tests
```cmd
pytest
```

### Using Test Script
```cmd
run_tests.bat          REM All tests
run_tests.bat models   REM Model tests only
run_tests.bat routes   REM Route tests only
run_tests.bat admin    REM Admin tests only
run_tests.bat coverage REM With coverage report
```

## Common Windows Issues & Solutions

### Issue 1: "python is not recognized"

**Problem**: Python not in PATH

**Solution**:
1. Reinstall Python, check "Add Python to PATH"
2. Or manually add to PATH:
   - Search "Environment Variables" in Windows
   - Edit PATH
   - Add: `C:\Users\YourName\AppData\Local\Programs\Python\Python3X`

### Issue 2: "Execution of scripts is disabled"

**Problem**: PowerShell execution policy

**Solution** (Run PowerShell as Administrator):
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue 3: Virtual environment activation fails

**Problem**: Permission issues

**Solutions**:
1. Use Command Prompt instead of PowerShell
2. Or in PowerShell:
   ```powershell
   venv\Scripts\Activate.ps1
   ```

### Issue 4: Port 5000 already in use

**Problem**: Another application using port 5000

**Solution**: Use different port
```cmd
flask run --port 5001
```

### Issue 5: Cannot find 'flask' command

**Problem**: Virtual environment not activated or Flask not installed

**Solution**:
```cmd
venv\Scripts\activate
pip install Flask
```

### Issue 6: Database errors

**Problem**: Database not initialized

**Solution**:
```cmd
venv\Scripts\activate
flask init-db
```

## PowerShell Alternative

If you prefer PowerShell over Command Prompt:

### Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

### Run Application
```powershell
flask run
```

## File Paths on Windows

Windows uses backslashes (`\`) for paths:
```
C:\Users\YourName\Documents\nihongo\
```

In Python/Flask, forward slashes (`/`) also work:
```python
'C:/Users/YourName/Documents/nihongo/'
```

## Environment Variables

### Setting Environment Variables (Command Prompt)
```cmd
set FLASK_ENV=development
set FLASK_DEBUG=1
set SECRET_KEY=your-secret-key
```

### Setting Environment Variables (PowerShell)
```powershell
$env:FLASK_ENV="development"
$env:FLASK_DEBUG="1"
$env:SECRET_KEY="your-secret-key"
```

### Permanent Environment Variables
1. Search "Environment Variables" in Windows
2. Click "Environment Variables" button
3. Add new variables under "User variables"

## Database Location

The SQLite database is created at:
```
C:\path\to\nihongo\instance\jlpt.db
```

To reset the database:
```cmd
del instance\jlpt.db
flask init-db
```

## Production Deployment (Windows)

### Using Waitress (Recommended for Windows)

1. **Install Waitress**
   ```cmd
   pip install waitress
   ```

2. **Run with Waitress**
   ```cmd
   waitress-serve --port=8000 app:app
   ```

### Using IIS (Advanced)

1. Install IIS
2. Install wfastcgi
3. Configure web.config
4. See IIS deployment guides for Flask

## Troubleshooting

### Check Python Installation
```cmd
python --version
pip --version
```

### Check Virtual Environment
```cmd
where python
```
Should show path inside `venv` folder when activated.

### Check Flask Installation
```cmd
pip show Flask
```

### View All Installed Packages
```cmd
pip list
```

### Upgrade pip
```cmd
python -m pip install --upgrade pip
```

## Quick Reference

### Virtual Environment
```cmd
REM Create
python -m venv venv

REM Activate
venv\Scripts\activate

REM Deactivate
deactivate
```

### Flask Commands
```cmd
REM Initialize database
flask init-db

REM Create admin
flask create-admin

REM Run development server
flask run

REM Run on different port
flask run --port 5001

REM Run on all interfaces
flask run --host 0.0.0.0
```

### Testing
```cmd
REM Run all tests
pytest

REM Verbose output
pytest -v

REM Specific test file
pytest tests\test_models.py

REM With coverage
pytest --cov=. --cov-report=html
```

## Directory Structure

```
C:\path\to\nihongo\
├── venv\                  # Virtual environment (Windows)
├── instance\              # Database files
│   └── jlpt.db           # SQLite database
├── models\               # Database models
├── templates\            # HTML templates
├── tests\                # Test files
├── app.py                # Main application
├── init.bat              # Windows setup script
├── run_tests.bat         # Windows test script
└── requirements.txt      # Dependencies
```

## Next Steps

After setup:

1. **Login** at http://localhost:5000/login
2. **Access Admin** at http://localhost:5000/admin
3. **Import Sample Data**:
   - Admin → Import Exam
   - Upload `exam_easy.json`
4. **Take Practice Exam**:
   - Go to Exams
   - Start an exam or generate random one

## Getting Help

If you encounter issues:

1. Check this guide
2. Review error messages carefully
3. Ensure virtual environment is activated
4. Check Python and pip versions
5. Try reinstalling dependencies

## Performance Tips

1. **Use SSD**: Store project on SSD for better database performance
2. **Antivirus**: Add project folder to antivirus exclusions
3. **Windows Defender**: May slow down Python execution
4. **Close unnecessary apps**: Free up system resources

## Backup

To backup your data:

1. **Database**:
   ```cmd
   copy instance\jlpt.db instance\jlpt.db.backup
   ```

2. **Entire Project**:
   ```cmd
   xcopy nihongo nihongo_backup\ /E /I
   ```

## Uninstall

To remove the project:

1. **Deactivate virtual environment**
   ```cmd
   deactivate
   ```

2. **Delete project folder**
   ```cmd
   rmdir /s /q C:\path\to\nihongo
   ```

## Additional Resources

- Python Documentation: https://docs.python.org/3/
- Flask Documentation: https://flask.palletsprojects.com/
- Python on Windows: https://docs.python.org/3/using/windows.html
- pip Documentation: https://pip.pypa.io/

---

**Happy Learning! 📚🇯🇵**

