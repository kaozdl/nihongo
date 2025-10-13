# Database Initialization Guide

## Quick Start

To initialize your database with all sample data, simply run:

```bash
flask init-db
```

This single command will:

✅ **Create all database tables**
✅ **Create default user**: `default@nihongo.edu.uy` / `nihongo123`
✅ **Load 3 N5 practice exams**:
  - JLPT N5 Practice Test - Easy (Basic) - 19 questions
  - JLPT N5 Practice Test - Medium - 19 questions
  - JLPT N5 Practice Test - Hard (Challenge) - 25 questions

## What Gets Loaded

### User
- **Email**: default@nihongo.edu.uy
- **Password**: nihongo123
- This user owns all imported exams

### Exams

#### Easy Exam (19 questions)
- Grammar (5 questions)
- Vocabulary (5 questions)
- Reading Comprehension (2 questions)
- Sentence Ordering (3 questions)
- Kanji Reading (2 questions)
- Kanji Writing (2 questions)

#### Medium Exam (19 questions)
- Grammar (5 questions)
- Vocabulary (4 questions)
- Reading Comprehension (2 questions)
- Sentence Ordering (2 questions)
- Kanji Reading (3 questions)
- Kanji Writing (3 questions)

#### Hard Exam (25 questions)
- Grammar (6 questions)
- Vocabulary (5 questions)
- Reading Comprehension (3 questions)
- Sentence Ordering (3 questions)
- Kanji Reading (4 questions)
- Kanji Writing (4 questions)

**Total**: 63 questions across 18 sections

## Features of Loaded Exams

### 🌍 Bilingual Support
All questions include explanations in:
- English (EN)
- Spanish (ES)

### 🈴 Kanji Questions
Two new question types:

1. **Kanji Reading**: Underlined kanji with reading options
   ```
   わたしは【日】本人です。
   Question: 【日】の読み方は？
   ```

2. **Kanji Writing**: Hiragana to kanji conversion
   ```
   わたしは まいにち【がっこう】へ いきます。
   Question: 【がっこう】の漢字は？
   ```

### 📝 Question Types
- Grammar fill-in-the-blank
- Vocabulary in context
- Reading comprehension passages
- Sentence ordering (_X_ marks the answer position)
- Kanji reading (【】 brackets mark target kanji)
- Kanji writing (【】 brackets mark target hiragana)

## Idempotency

The `flask init-db` command is **idempotent**:
- ✅ Safe to run multiple times
- ✅ Won't create duplicate users
- ✅ Won't duplicate exams with the same name
- ✅ Will show status messages for existing data

Example output when run twice:
```
✅ Database tables created!
ℹ️  Default user already exists: default@nihongo.edu.uy
ℹ️  Exam already exists: JLPT N5 Practice Test - Easy (Basic)
ℹ️  Exam already exists: JLPT N5 Practice Test - Medium
ℹ️  Exam already exists: JLPT N5 Practice Test - Hard (Challenge)

🎉 Database initialization complete!
```

## Login Credentials

After initialization, you can login with:
- **URL**: http://localhost:5000/login
- **Email**: default@nihongo.edu.uy
- **Password**: nihongo123

## Admin Access

The default user can access the admin panel:
- **URL**: http://localhost:5000/admin
- Use the same credentials as above

## Verifying Installation

To verify the data was loaded correctly, run:

```bash
python3 -c "
from app import app
from models import db
from models.user import User
from models.exam import Exam
from models.question import Question

with app.app_context():
    print(f'Users: {User.query.count()}')
    print(f'Exams: {Exam.query.count()}')
    print(f'Questions: {Question.query.count()}')
"
```

Expected output:
```
Users: 1
Exams: 3
Questions: 63
```

## Resetting the Database

To start fresh, delete the database and run init-db again:

```bash
# macOS/Linux
rm -f jlpt.db instance/jlpt.db
flask init-db

# Windows
del jlpt.db
del instance\jlpt.db
flask init-db
```

## Advanced: Using Migrations

For production, consider using Alembic migrations instead:

```bash
# Initial setup
flask db-upgrade

# Then load data separately
python3 -c "
from app import app
from models.user import User
from models import db

with app.app_context():
    user = User(email='default@nihongo.edu.uy')
    user.set_password('nihongo123')
    db.session.add(user)
    db.session.commit()
"

# Import exams via admin panel at /admin
```

## Troubleshooting

### Error: "No such table"
Run `flask init-db` to create tables

### Error: "User already exists"
This is normal - the command is idempotent

### Error: "File not found: exam_*.json"
Make sure you're running the command from the project root directory

### Exams not visible
1. Make sure you're logged in
2. Check that init-db completed successfully
3. Try accessing /exams directly

## See Also

- [QUICKSTART.md](docs/QUICKSTART.md) - Quick setup guide
- [IMPORT_GUIDE.md](docs/IMPORT_GUIDE.md) - Import custom exams
- [README.md](README.md) - Full project documentation
