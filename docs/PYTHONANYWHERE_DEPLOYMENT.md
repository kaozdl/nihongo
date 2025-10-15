# PythonAnywhere Deployment Guide

## 📦 Package Created

**File:** `nihongo-pythonanywhere.zip` (125KB)  
**Location:** `/Users/kalildelima/workspace/nihongo/`

This zip contains everything needed to deploy the JLPT Test Manager on PythonAnywhere.

---

## 🚀 Deployment Steps

### **1. Upload the Zip File**

1. Log in to [PythonAnywhere](https://www.pythonanywhere.com)
2. Go to **Files** tab
3. Click **"Upload a file"**
4. Select `nihongo-pythonanywhere.zip`
5. Upload to your home directory (e.g., `/home/yourusername/`)

---

### **2. Extract the Zip**

Open a **Bash console** in PythonAnywhere:

```bash
cd ~
unzip nihongo-pythonanywhere.zip -d nihongo
cd nihongo
```

---

### **3. Create Virtual Environment**

```bash
cd ~/nihongo
python3.11 -m venv venv
source venv/bin/activate
```

---

### **4. Install Dependencies**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note:** If you get errors with `psycopg2-binary`, you can skip it for now (only needed for PostgreSQL in production).

---

### **5. Set Environment Variables**

Create a `.env` file:

```bash
nano .env
```

Add the following content:

```bash
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-change-this
DATABASE_URL=sqlite:////home/yourusername/nihongo/jlpt.db
```

**Important:** 
- Replace `yourusername` with your actual PythonAnywhere username
- Generate a strong SECRET_KEY: `python3 -c "import secrets; print(secrets.token_hex(32))"`

Press `Ctrl+X`, then `Y`, then `Enter` to save.

---

### **6. Initialize Database**

```bash
source venv/bin/activate
cd ~/nihongo

# Run database migrations
flask db-upgrade

# Or initialize fresh database
flask init-db
```

This will:
- ✅ Create all database tables
- ✅ Create default user: `default@nihongo.edu.uy` / `nihongo123`
- ✅ Load sample exams (Easy, Medium, Hard N5)

---

### **7. Create Admin User** (Optional)

```bash
flask create-admin
```

Follow the prompts to create your admin account.

---

### **8. Configure WSGI**

Go to the **Web** tab in PythonAnywhere:

1. Click **"Add a new web app"**
2. Choose **"Manual configuration"**
3. Select **Python 3.11** (or your preferred version)
4. Click **"Next"**

---

### **9. Configure WSGI File**

Click on the WSGI configuration file link (e.g., `/var/www/yourusername_pythonanywhere_com_wsgi.py`)

**Replace the entire contents** with:

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

**Important:** 
- Replace `yourusername` with your actual PythonAnywhere username!
- The import statement uses `nihongo.app` (package-qualified) to match the project structure

Save the file (Ctrl+S or click Save).

---

### **10. Set Virtual Environment Path**

Still in the **Web** tab:

1. Find the **"Virtualenv"** section
2. Enter the path to your virtual environment:
   ```
   /home/yourusername/nihongo/venv
   ```
3. Click the checkmark to save

---

### **11. Set Working Directory**

In the **Web** tab, find **"Code"** section:

1. Set **"Source code"** to:
   ```
   /home/yourusername/nihongo
   ```

2. Set **"Working directory"** to:
   ```
   /home/yourusername/nihongo
   ```

---

### **12. Configure Static Files**

In the **Web** tab, find **"Static files"** section:

Add the following mappings:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/yourusername/nihongo/static` |

**Note:** If you don't have a `static` folder, you can skip this for now (Bootstrap is loaded from CDN).

---

### **13. Reload Web App**

Click the big green **"Reload"** button at the top of the Web tab.

---

### **14. Test Your Application**

Visit your URL:
```
https://yourusername.pythonanywhere.com
```

You should see the JLPT Test Manager login page! 🎉

---

## 🔑 Default Login

**Email:** `default@nihongo.edu.uy`  
**Password:** `nihongo123`

**⚠️ Change this password immediately after first login!**

---

## 🗄️ Database Location

Your SQLite database will be located at:
```
/home/yourusername/nihongo/jlpt.db
```

---

## 📝 Important Notes

### **For Free Accounts:**
- Your app will sleep after inactivity
- Limited to 1 web app
- 512MB disk space
- 3-month validity (refresh by logging in)

### **For Paid Accounts:**
- Always-on apps
- Multiple web apps
- More disk space
- Can use PostgreSQL (recommended for production)

---

## 🔄 Updating the Application

To update your app with new changes:

```bash
cd ~/nihongo
source venv/bin/activate

# Pull your changes (if using git)
# Or upload new files via Files tab

# Run any new migrations
flask db-upgrade

# Reload the web app from the Web tab
```

---

## 🐛 Troubleshooting

### **Error: ModuleNotFoundError: No module named 'mycontent_routes'**

This error was fixed by updating all imports to use package-qualified paths (e.g., `from nihongo.models import db`). 

**If you still see this error:**
1. Ensure your WSGI file uses: `from nihongo.app import app as application`
2. Check that all Python files use `nihongo.` prefix in imports
3. Verify the project directory is added to `sys.path` in WSGI file
4. See `IMPORT_FIX_SUMMARY.md` for details on the fix

### **Error: ModuleNotFoundError (General)**

Check that:
1. Virtual environment is activated
2. All dependencies are installed: `pip install -r requirements.txt`
3. WSGI file points to correct paths
4. Project directory is in `sys.path`

### **Error: Database Not Found**

```bash
cd ~/nihongo
source venv/bin/activate
flask init-db
```

### **Error: Import Error**

Check the **Error log** in the Web tab for detailed error messages.

### **App Shows "Something went wrong"**

1. Check **Error log** in Web tab
2. Check **Server log** in Web tab
3. Verify `.env` file exists and has correct values
4. Verify WSGI file paths are correct

### **Static Files Not Loading**

If Bootstrap styles aren't loading:
- They're loaded from CDN, so this should work automatically
- If you add custom static files, configure Static files mapping in Web tab

---

## 🔐 Security Recommendations

### **Before Going Live:**

1. **Change SECRET_KEY:**
   ```python
   import secrets
   print(secrets.token_hex(32))
   ```
   Update in `.env` file

2. **Change Default User Password:**
   - Log in as `default@nihongo.edu.uy`
   - Or delete and create new user

3. **Create Admin User:**
   ```bash
   flask create-admin
   ```

4. **Review Admin Access:**
   - Only trusted users should be admins
   - Regular users can create their own content

5. **Enable HTTPS:**
   - PythonAnywhere provides this automatically! ✅

---

## 📊 Database Migrations

If you make changes to models:

```bash
cd ~/nihongo
source venv/bin/activate

# Generate migration
flask db-migrate -m "Description of changes"

# Apply migration
flask db-upgrade

# Reload web app from Web tab
```

---

## 🌍 Features Available

Your deployed app includes:

✅ User registration and authentication (auto-login)  
✅ Exam taking with auto-save  
✅ Exam history tracking  
✅ Retake functionality  
✅ Results with explanations  
✅ Random exam generator  
✅ User content management (create own questions/exams)  
✅ Admin panel (for admin users)  
✅ Bilingual support (English/Spanish)  
✅ Responsive design (mobile-friendly)  
✅ Pre-loaded N5 practice exams  

---

## 📞 Support

**PythonAnywhere Help:**
- [PythonAnywhere Help Pages](https://help.pythonanywhere.com/)
- [PythonAnywhere Forums](https://www.pythonanywhere.com/forums/)

**Flask Help:**
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask-Admin Documentation](https://flask-admin.readthedocs.io/)

---

## 🎓 Next Steps

After deployment:

1. ✅ Log in and test all features
2. ✅ Create an admin user
3. ✅ Test taking an exam
4. ✅ Test retaking an exam
5. ✅ Check exam history
6. ✅ Test creating custom questions (My Content)
7. ✅ Test language switching
8. ✅ Share with users!

---

## 🚀 Advanced: Using PostgreSQL

For better performance with multiple users:

1. Upgrade to paid PythonAnywhere account
2. Create PostgreSQL database in PythonAnywhere
3. Update `.env`:
   ```bash
   DATABASE_URL=postgresql://username:password@hostname/database
   ```
4. Install PostgreSQL adapter:
   ```bash
   pip install psycopg2-binary
   ```
5. Run migrations:
   ```bash
   flask db-upgrade
   ```
6. Reload web app

---

**Good luck with your deployment! 🎉🚀**

