"""
Utility functions for models
"""
import json
from flask import session


def get_explanation(explanation_field, language=None):
    """
    Get explanation in the specified language.
    
    Args:
        explanation_field: String or JSON dict with language keys
        language: 'en' or 'es', defaults to session language or 'en'
    
    Returns:
        Explanation string in requested language
    """
    if not explanation_field:
        return ""
    
    # Get language from session if not specified
    if language is None:
        language = session.get('language', 'en').upper()
    else:
        language = language.upper()
    
    # Try to parse as JSON
    try:
        explanation_dict = json.loads(explanation_field)
        if isinstance(explanation_dict, dict):
            # Try requested language first
            if language in explanation_dict:
                return explanation_dict[language]
            # Fallback to EN
            if 'EN' in explanation_dict:
                return explanation_dict['EN']
            # Return first available
            return list(explanation_dict.values())[0] if explanation_dict else ""
    except (json.JSONDecodeError, TypeError):
        # Not JSON, treat as plain string (English)
        return explanation_field
    
    return ""


def set_explanation(en_text, es_text=None):
    """
    Create a JSON explanation field.
    
    Args:
        en_text: English explanation
        es_text: Spanish explanation (optional)
    
    Returns:
        JSON string with language keys
    """
    explanation = {"EN": en_text}
    if es_text:
        explanation["ES"] = es_text
    return json.dumps(explanation)


def parse_explanation(explanation_field):
    """
    Parse explanation field into dict.
    
    Args:
        explanation_field: String or JSON dict
    
    Returns:
        Dict with language keys (at least EN)
    """
    if not explanation_field:
        return {"EN": ""}
    
    try:
        explanation_dict = json.loads(explanation_field)
        if isinstance(explanation_dict, dict):
            return explanation_dict
    except (json.JSONDecodeError, TypeError):
        pass
    
    # Treat as plain English string
    return {"EN": explanation_field}

