# User Content Management Guide

## Overview

The JLPT Test Manager now supports **user content management**, allowing regular (non-admin) users to create and manage their own questions, sections, and exams. This feature promotes collaborative learning while maintaining privacy and security.

## Key Features

### 🔒 **Privacy & Security**
- Users can only see and edit **their own content**
- Content created by one user is invisible to other users
- Admin users can see and manage **all content** across all users
- Automatic ownership tracking for questions and exams

### ✏️ **What Users Can Create**

1. **Questions**
   - Multiple choice questions with 4 answer options
   - Bilingual explanations (English/Spanish)
   - Optional image URLs
   - Optional audio URLs
   - Automatic creator tracking

2. **Sections**
   - Organize questions by topic (e.g., Grammar, Vocabulary, Kanji)
   - Specify number of questions
   - Reusable across multiple exams

3. **Exams**
   - Combine multiple sections
   - Link existing questions through sections
   - Set exam metadata (name, description)
   - Automatic creator tracking

## Access Levels

### Regular Users (is_admin=False)
- ✅ Create and edit own questions
- ✅ Create and edit own exams
- ✅ Create and manage sections
- ✅ Take any available exam
- ✅ View own test results
- ❌ Cannot see other users' questions or exams
- ❌ Cannot access admin panel
- ❌ Cannot bulk import exams from JSON

### Admin Users (is_admin=True)
- ✅ All regular user permissions
- ✅ View and edit ALL content (all users)
- ✅ Manage user accounts
- ✅ Promote users to admin
- ✅ Bulk import exams from JSON
- ✅ View all test results
- ✅ Access full admin panel at `/admin`

## How to Use

### Accessing My Content

1. **Log in** to your account
2. Click **"My Content"** in the navigation bar
3. Or navigate directly to `/mycontent`

### Creating Questions

1. In **My Content**, click **"My Questions"**
2. Click **"Create"**
3. Fill in the question details:
   ```
   Question Text: 私は___学生です。
   Question Image: (optional URL)
   Question Audio: (optional URL)
   
   Answer 1: が
   Answer 2: の
   Answer 3: を
   Answer 4: に
   
   Correct Answer: 2 (select "の")
   
   Explanation (English): "の" is used to indicate possession or attribution
   Explanation (Español): "の" se usa para indicar posesión o atribución
   ```
4. Click **"Save"**

### Managing Sections

1. In **My Content**, click **"Sections"**
2. Click **"Create"**
3. Enter section details:
   ```
   Name: Grammar - Particles
   Number of Questions: 10
   ```
4. Click **"Save"**

### Linking Questions to Sections

1. In **My Content**, click **"Section Questions"**
2. Click **"Create"**
3. Select:
   - **Section**: Choose the section
   - **Question**: Choose one of YOUR questions
4. Click **"Save"**
5. Repeat for each question you want to add to the section

### Creating Exams

1. In **My Content**, click **"My Exams"**
2. Click **"Create"**
3. Enter exam details:
   ```
   Name: JLPT N5 Practice - Week 1
   ```
4. Click **"Save"**

### Linking Sections to Exams

1. In **My Content**, click **"Exam Sections"**
2. Click **"Create"**
3. Select:
   - **Exam**: Choose your exam
   - **Section**: Choose a section
4. Click **"Save"**
5. Repeat for each section you want in the exam

### Taking Your Own Exams

1. Navigate to `/exams`
2. Your custom exams will appear in the exam list
3. Click **"Start Exam"** to take your own exam
4. Complete and submit as usual

## Interface Comparison

### Regular User Navigation
```
Exams | My Content | [email] | Language | Logout
```

### Admin User Navigation
```
Exams | My Content | Admin | [email] | Language | Logout
```

## URLs

| Interface | URL | Access Level |
|-----------|-----|--------------|
| My Content Home | `/mycontent` | All authenticated users |
| My Questions | `/mycontent/myquestion` | All authenticated users |
| My Exams | `/mycontent/myexam` | All authenticated users |
| Admin Panel | `/admin` | Admin users only |

## Database Ownership

### Questions Table
```sql
CREATE TABLE questions (
    id INTEGER PRIMARY KEY,
    question_text TEXT NOT NULL,
    -- ... other fields ...
    created_by INTEGER NOT NULL,  -- User ID of creator
    FOREIGN KEY (created_by) REFERENCES users(id)
);
```

### Exams Table
```sql
CREATE TABLE exams (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    created_by INTEGER NOT NULL,  -- User ID of creator
    FOREIGN KEY (created_by) REFERENCES users(id)
);
```

### Filtering Logic
- **My Content views**: `WHERE created_by = current_user.id`
- **Admin views**: No filter (shows all content)

## Creating Admin Users

To create or promote a user to admin:

```bash
flask create-admin
```

Follow the interactive prompts:
```
Create Admin User
==================================================
Enter admin email: teacher@example.com
Enter password: ********
Confirm password: ********

✅ Admin user created successfully!
   Email: teacher@example.com
   Admin: Yes
```

To promote an existing user:
```bash
flask create-admin
```
```
Create Admin User
==================================================
Enter admin email: existing@example.com
❌ User with email existing@example.com already exists
Would you like to promote this user to admin? (y/n): y
✅ User existing@example.com promoted to admin
```

## Bilingual Explanations

Questions support bilingual explanations (English/Spanish):

### In My Content Interface
- Separate fields for **Explanation (English)** and **Explanation (Español)**
- Both fields are optional
- Data is stored as JSON in the database

### Storage Format
```json
{
  "EN": "English explanation text",
  "ES": "Spanish explanation text"
}
```

### Display
- Automatically displays the correct language based on user's selected locale
- Falls back to English if Spanish translation is not available

## Best Practices

### For Content Creators

1. **Use Clear Question Text**
   - Be specific and unambiguous
   - Use proper Japanese characters (hiragana, katakana, kanji)

2. **Provide Quality Explanations**
   - Explain **why** the correct answer is correct
   - Explain **why** other answers are wrong
   - Provide both English and Spanish explanations if possible

3. **Organize with Sections**
   - Group related questions together
   - Use clear section names (e.g., "Grammar - Particles", "Vocabulary - Food")
   - Keep sections focused on specific topics

4. **Test Your Exams**
   - Take your own exams to verify they work correctly
   - Check that questions appear in the correct order
   - Ensure all answers are properly validated

### For Administrators

1. **User Management**
   - Only promote trusted users to admin
   - Regularly review admin user list
   - Use `flask create-admin` for secure admin creation

2. **Content Moderation**
   - Review user-created content periodically
   - Ensure content quality standards are met
   - Help users improve their question writing

3. **Data Backup**
   - Regularly backup the database
   - Keep backups of exam JSON files
   - Document your backup and restore procedures

## Troubleshooting

### "You can only edit your own questions"
- You're trying to edit a question created by another user
- Check that you're logged in as the correct user
- Admins: Use `/admin` panel to edit other users' content

### Can't see my questions in the exam
- Make sure you've linked questions to a section
- Make sure you've linked the section to your exam
- Check that the question was created by your account

### My Content link not appearing
- Ensure you're logged in
- Clear browser cache and refresh
- Check that `/mycontent` URL works directly

### Questions appear in other users' exams
- Sections are shared across all users
- If you add your questions to a widely-used section name, they may appear in others' exams
- Consider using unique section names for your private content

## Migration from Admin-Only Model

If upgrading from a previous version:

1. **Existing Questions**: All existing questions keep their original `created_by` value
2. **New Users**: Registered users can immediately create content
3. **Admin Access**: Existing admins retain full access to all content
4. **Default User**: The default user (`default@nihongo.edu.uy`) is **not** an admin

## Technical Implementation

### View Classes

```python
class UserContentView(ModelView):
    """Filters content by current user's ID"""
    def get_query(self):
        query = super().get_query()
        if hasattr(self.model, 'created_by'):
            query = query.filter(self.model.created_by == current_user.id)
        return query
```

### Security Checks

```python
def on_model_change(self, form, model, is_created):
    if is_created:
        model.created_by = current_user.id
    else:
        # Verify user owns this content
        if model.created_by != current_user.id:
            raise ValueError('You can only edit your own content')
```

## See Also

- [Quick Start Guide](QUICKSTART.md)
- [Admin Import Guide](IMPORT_GUIDE.md)
- [Testing Guide](TESTING_GUIDE.md)
- [Configuration Reference](CONFIGURATION_REFERENCE.md)
- [Main README](../README.md)

---

**Happy Learning! 📚🇯🇵**

