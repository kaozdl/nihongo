# Quick Deployment Guide for PythonAnywhere

## 📦 Create Deployment Package

Run the build script:

```bash
./build.sh
```

This creates a zip file like: `nihongo-v1.1.2-pythonanywhere.zip`

---

## 🚀 Deploy to PythonAnywhere

### 1. Upload the zip
- Go to **Files** tab in PythonAnywhere
- Upload the zip file to your home directory (`/home/yourusername/`)

### 2. Extract with correct structure

```bash
cd ~
rm -rf nihongo  # Remove old deployment
mkdir nihongo
cd nihongo
unzip ../nihongo-v1.1.2-pythonanywhere.zip
```

### 3. Verify directory structure

```bash
ls -la models/
```

**Should see:**
```
__init__.py
user.py
exam.py
question.py
section.py
test.py
test_answer.py
exam_section.py
section_question.py
utils.py
```

✅ If you see these files, the structure is correct!
❌ If all files are flat in the root directory, the extraction went wrong.

### 4. Setup virtual environment

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Create .env file

```bash
nano .env
```

Add:
```bash
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=sqlite:////home/yourusername/nihongo/jlpt.db
```

Generate a strong secret key:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 6. Initialize database

```bash
flask init-db
```

### 7. Configure WSGI file

In the **Web** tab, click on your WSGI file and update it:

```python
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/yourusername/nihongo'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Set environment variables
os.environ['FLASK_ENV'] = 'production'

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(os.path.join(project_home, '.env'))

# Import Flask app
from nihongo.app import app as application
```

**⚠️ Important:** Replace `yourusername` with your actual PythonAnywhere username!

### 8. Reload web app

Click the big green **"Reload"** button in the Web tab.

---

## ✅ Verify It Works

1. Visit your URL: `https://yourusername.pythonanywhere.com`
2. You should see the login page
3. Check error logs if there are issues

---

## 🔍 Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'nihongo.models'"

**Cause:** Directory structure is flat (all files in one directory)

**Fix:**
1. Delete the nihongo directory: `rm -rf ~/nihongo`
2. Re-extract following step 2 above exactly
3. Verify with `ls -la ~/nihongo/models/`

### Problem: "Port 5000 already in use" during local testing

This is normal - just means Flask is trying to start. The imports are working! ✅

### Problem: Can't run flask commands

**Check:**
1. Virtual environment is activated: `source venv/bin/activate`
2. You're in the right directory: `cd ~/nihongo`
3. FLASK_APP is found: `echo $FLASK_APP` (should show path to app.py or be empty - Flask auto-discovers app.py)

---

## 📝 Default Login

After running `flask init-db`:

**Email:** `default@nihongo.edu.uy`  
**Password:** `nihongo123`

**⚠️ Change this immediately after first login!**

---

## 🎯 Summary

The key to successful deployment is the correct directory structure:

```
~/nihongo/
├── app.py
├── config.py
├── import_exam.py
├── mycontent_routes.py
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── exam.py
│   └── ...
├── admin/
│   └── __init__.py
├── templates/
├── alembic/
└── ...
```

If `models/` is a directory with files inside (not flat), you're good to go! 🎉

