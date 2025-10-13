# Exam Import Guide

## Overview

The JLPT Test Manager allows you to import complete exams from JSON files through the admin interface. This makes it easy to bulk-create exams with all their sections and questions in one go.

## Accessing the Import Feature

1. Login to the application
2. Navigate to the Admin panel (`/admin`)
3. Click on "Import Exam" in the navigation menu
4. Upload your JSON file
5. Click "Import Exam"

## JSON File Format

### Basic Structure

```json
{
  "name": "Exam Name",
  "sections": [
    {
      "name": "Section Name",
      "questions": [
        {
          "question_text": "Question text here",
          "answer_1": "First option",
          "answer_2": "Second option",
          "answer_3": "Third option",
          "answer_4": "Fourth option",
          "correct_answer": 1,
          "explanation": "Explanation for the correct answer"
        }
      ]
    }
  ]
}
```

### Required Fields

#### Exam Level
- **name** (string): The name of the exam

#### Section Level
- **name** (string): The name of the section
- **questions** (array): Array of question objects

#### Question Level
- **question_text** (string): The question text
- **answer_1** (string): First answer option
- **answer_2** (string): Second answer option
- **answer_3** (string): Third answer option
- **answer_4** (string): Fourth answer option
- **correct_answer** (integer): The correct answer number (1, 2, 3, or 4)

### Optional Fields

#### Question Level
- **question_image** (string): URL to an image for the question
- **question_audio** (string): URL to an audio file for the question
- **explanation** (string): Explanation for why the answer is correct

## Example JSON File

See `exam_example.json` in the project root for a complete example.

You can also download an example from the Import Exam page in the admin interface.

## Complete Example

```json
{
  "name": "JLPT N5 Practice Test",
  "sections": [
    {
      "name": "Vocabulary",
      "questions": [
        {
          "question_text": "彼は___な性格です。",
          "question_image": "https://example.com/images/question1.jpg",
          "question_audio": "https://example.com/audio/question1.mp3",
          "answer_1": "まじめ",
          "answer_2": "まじめだ",
          "answer_3": "まじめの",
          "answer_4": "まじめで",
          "correct_answer": 1,
          "explanation": "「まじめな性格」is the correct form. な-adjectives use な before nouns."
        },
        {
          "question_text": "毎日___勉強します。",
          "answer_1": "いっしょうけんめい",
          "answer_2": "いっしょうけんめいに",
          "answer_3": "いっしょうけんめいで",
          "answer_4": "いっしょうけんめいな",
          "correct_answer": 2,
          "explanation": "いっしょうけんめいに is an adverb modifying the verb 勉強します."
        }
      ]
    },
    {
      "name": "Grammar",
      "questions": [
        {
          "question_text": "雨が___きました。",
          "answer_1": "ふり",
          "answer_2": "ふって",
          "answer_3": "ふった",
          "answer_4": "ふる",
          "correct_answer": 2,
          "explanation": "ふってきました indicates the rain has started falling. Use て-form + くる."
        }
      ]
    }
  ]
}
```

## Validation

The importer performs the following validations:

1. **File Format**: Must be valid JSON
2. **Required Fields**: All required fields must be present
3. **Data Types**: Fields must be of the correct type (string, integer, array)
4. **correct_answer**: Must be 1, 2, 3, or 4
5. **Sections**: Exam must have at least one section
6. **Questions**: Each section must have at least one question

If any validation fails, the import will be rejected and an error message will be displayed.

## Tips

1. **Start Small**: Test with a small exam (1-2 sections, 2-3 questions) first
2. **Use UTF-8**: Ensure your JSON file is saved with UTF-8 encoding (especially important for Japanese characters)
3. **Validate JSON**: Use a JSON validator (like jsonlint.com) to check your file before importing
4. **URLs**: Make sure image and audio URLs are publicly accessible
5. **Backup**: Keep your JSON files as backups of your exams

## Programmatic Import

You can also import exams programmatically using the `import_exam.py` module:

```python
from import_exam import import_exam_from_file

success, message, exam = import_exam_from_file('path/to/exam.json', user_id=1)

if success:
    print(f"Success: {message}")
    print(f"Exam ID: {exam.id}")
else:
    print(f"Error: {message}")
```

## Error Messages

Common error messages and solutions:

- **"Invalid JSON format"**: Your file is not valid JSON. Check for syntax errors.
- **"Missing required field: 'name'"**: Your exam object is missing the name field.
- **"Section X missing 'questions' field"**: A section doesn't have a questions array.
- **"Question X has invalid 'correct_answer'"**: The correct_answer must be 1, 2, 3, or 4.
- **"Exam must have at least one section"**: Add at least one section to your exam.
- **"Section must have at least one question"**: Each section needs at least one question.

## Support

If you encounter issues with importing, check the application logs for detailed error messages.

