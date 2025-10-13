# Internationalization (i18n) Guide

This guide explains how the JLPT Test Manager supports multiple languages (English and Spanish).

## Features

### 🌍 Supported Languages

- **English (EN)** - Default language
- **Spanish (ES)** - Full translation

### 🔄 Language Switching

Users can switch languages at any time using the language dropdown in the navigation bar:
- 🇬🇧 English
- 🇪🇸 Español

The selected language is stored in the user's session and persists across pages.

### 📝 Multi-Language Explanations

Question explanations can be provided in both English and Spanish. The system will automatically display the explanation in the user's selected language.

## For Administrators

### Creating Multi-Language Questions

When creating or editing a question in the admin panel, you'll see two fields for explanations:

1. **Explanation (English)** - English explanation text
2. **Explanation (Español)** - Spanish explanation text

Both fields are optional, but providing translations in both languages enhances the user experience.

#### Example:

**English Explanation:**
```
The particle は (wa) is used to mark the topic of a sentence. In this case, it indicates what the sentence is about.
```

**Spanish Explanation:**
```
La partícula は (wa) se usa para marcar el tema de una oración. En este caso, indica de qué trata la oración.
```

### Importing Multi-Language Exams

When importing exams via JSON, the `explanation` field can be provided in two ways:

#### Option 1: Simple String (English only)
```json
{
  "question_text": "彼は___な性格です。",
  "explanation": "「まじめな性格」is the correct form."
}
```

This will be treated as an English-only explanation.

#### Option 2: Multi-Language Object
```json
{
  "question_text": "彼は___な性格です。",
  "explanation": {
    "EN": "「まじめな性格」is the correct form. な-adjectives use な before nouns.",
    "ES": "「まじめな性格」es la forma correcta. Los adjetivos な usan な antes de sustantivos."
  }
}
```

This provides explanations in both languages.

## For Developers

### Technology Stack

- **Flask-Babel** - i18n/l10n extension for Flask
- **Babel** - Internationalization utilities
- **gettext** - Translation system

### Translation Files

Translation files are located in:
```
translations/
├── es/
│   └── LC_MESSAGES/
│       ├── messages.po  # Spanish translations (editable)
│       └── messages.mo  # Compiled translations (auto-generated)
└── messages.pot         # Translation template (auto-generated)
```

### Updating Translations

#### 1. Extract new translatable strings
```bash
pybabel extract -F babel.cfg -o messages.pot .
```

#### 2. Update translation catalogs
```bash
pybabel update -i messages.pot -d translations
```

#### 3. Edit translations
Edit `translations/es/LC_MESSAGES/messages.po` and add Spanish translations:
```po
msgid "Login"
msgstr "Iniciar sesión"
```

#### 4. Compile translations
```bash
pybabel compile -d translations
```

### Adding New Languages

To add a new language (e.g., Japanese):

```bash
pybabel init -i messages.pot -d translations -l ja
```

Then edit `translations/ja/LC_MESSAGES/messages.po` and compile.

Update `app.py` to include the new language:
```python
app.config['BABEL_SUPPORTED_LOCALES'] = ['en', 'es', 'ja']
```

### Using Translations in Templates

Use the `_()` function to mark strings for translation:

```jinja
<h1>{{ _('Welcome') }}</h1>
<p>{{ _('Hello, %(name)s!', name=user.name) }}</p>
```

### Using Translations in Python Code

```python
from flask_babel import gettext

flash(gettext('Login successful'), 'success')
```

### Explanation Utility Functions

The `models/utils.py` module provides helper functions for multi-language explanations:

#### `get_explanation(explanation_field, language=None)`
Retrieves explanation in the requested language.

```python
from models.utils import get_explanation

# Automatically uses user's session language
explanation = get_explanation(question.explanation)

# Or specify language explicitly
explanation_es = get_explanation(question.explanation, 'es')
```

#### `set_explanation(en_text, es_text=None)`
Creates a JSON explanation field.

```python
from models.utils import set_explanation

question.explanation = set_explanation(
    "English explanation",
    "Explicación en español"
)
```

#### `parse_explanation(explanation_field)`
Parses explanation field into a dict.

```python
from models.utils import parse_explanation

explanation_dict = parse_explanation(question.explanation)
# Returns: {"EN": "...", "ES": "..."}
```

## Backward Compatibility

### Existing Questions

Questions created before the multi-language feature was added will continue to work. Their explanations are treated as English-only and will be displayed regardless of the selected language.

### Migration

No database migration is required. The `explanation` field is stored as TEXT and can contain either:
- Plain text (treated as English)
- JSON string with language keys

## Language Selection Behavior

### Automatic Detection

The system attempts to detect the user's preferred language in this order:

1. **Session Language** - If user manually selected a language
2. **Browser Language** - From Accept-Language header
3. **Default Language** - English (EN)

### Persistence

The selected language is stored in the Flask session and persists until:
- User selects a different language
- Session expires (browser closed)
- User logs out

## Testing

### Test Multi-Language Support

1. **Switch Language**
   - Log in to the application
   - Click the language dropdown (EN/ES)
   - Select a different language
   - Verify all UI elements are translated

2. **Create Multi-Language Question**
   - Go to Admin → Questions → Create
   - Fill in both English and Spanish explanations
   - Save the question

3. **Take Exam**
   - Start an exam with multi-language questions
   - Complete and submit
   - View results in English
   - Switch to Spanish
   - View results again - explanations should be in Spanish

### Example Test Data

```python
from models.utils import set_explanation

question = Question(
    question_text="彼は___な性格です。",
    answer_1="まじめ",
    answer_2="まじめだ",
    answer_3="まじめの",
    answer_4="まじめで",
    correct_answer=1,
    explanation=set_explanation(
        "「まじめな性格」is the correct form. な-adjectives use な before nouns.",
        "「まじめな性格」es la forma correcta. Los adjetivos な usan な antes de sustantivos."
    ),
    created_by=1
)
```

## Troubleshooting

### Translations Not Showing

1. **Verify compiled translations exist:**
   ```bash
   ls translations/es/LC_MESSAGES/messages.mo
   ```

2. **Recompile translations:**
   ```bash
   pybabel compile -d translations
   ```

3. **Restart Flask application:**
   ```bash
   flask run
   ```

### Language Not Switching

1. **Check browser console** for JavaScript errors
2. **Verify session is working** - try logging out and back in
3. **Clear browser cache** and cookies

### Missing Translations

If you see English text when Spanish is selected:

1. **Check if string is marked for translation** in templates (`{{ _('...') }}`)
2. **Extract and update translations:**
   ```bash
   pybabel extract -F babel.cfg -o messages.pot .
   pybabel update -i messages.pot -d translations
   ```
3. **Edit** `translations/es/LC_MESSAGES/messages.po`
4. **Compile** translations:
   ```bash
   pybabel compile -d translations
   ```

## Best Practices

### For Administrators

1. ✅ Always provide explanations in both languages when possible
2. ✅ Use clear, simple language appropriate for language learners
3. ✅ Keep translations consistent in style and terminology
4. ✅ Test questions in both languages before publishing

### For Developers

1. ✅ Always mark user-facing strings with `_()`
2. ✅ Use named parameters for dynamic content: `_('Hello, %(name)s!', name=user.name)`
3. ✅ Extract and compile translations before deploying
4. ✅ Test all features in both languages
5. ✅ Keep translation files organized and up-to-date

## Future Enhancements

Potential features for future versions:

- 🇯🇵 Japanese language support
- 🇰🇷 Korean language support
- 🇫🇷 French language support
- 📝 Multi-language question text (not just explanations)
- 🌐 User profile language preference (persistent)
- 📊 Language statistics and coverage reports

## Resources

- [Flask-Babel Documentation](https://python-babel.github.io/flask-babel/)
- [Babel Documentation](http://babel.pocoo.org/)
- [GNU gettext Manual](https://www.gnu.org/software/gettext/manual/)

