"""
Configuration settings for the Flask application.
Different configurations for development, testing, and production.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    """Base configuration with default settings."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-please-change'
    
    # SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_ECHO = False
    
    # Flask-Babel settings
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_SUPPORTED_LOCALES = ['en', 'es']
    BABEL_TRANSLATION_DIRECTORIES = 'translations'
    
    # Flask-Login settings
    REMEMBER_COOKIE_DURATION = 604800  # 7 days in seconds
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Application settings
    QUESTIONS_PER_PAGE = 50
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file upload
    
    @classmethod
    def init_app(cls, app):
        """Initialize application with this configuration."""
        pass


class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    TESTING = False
    
    # SQLite for local development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(basedir, "jlpt.db")}'
    
    # More verbose logging
    SQLALCHEMY_ECHO = os.environ.get('SQL_ECHO', 'False').lower() == 'true'
    
    # Disable CSRF for easier development (re-enable for production)
    WTF_CSRF_ENABLED = True


class ProductionConfig(Config):
    """Production configuration."""
    
    DEBUG = False
    TESTING = False
    
    # PostgreSQL for production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Handle Heroku's postgres:// URL format (should be postgresql://)
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    
    # Production security settings
    SESSION_COOKIE_SECURE = True  # Only send cookie over HTTPS
    PREFERRED_URL_SCHEME = 'https'
    
    @classmethod
    def init_app(cls, app):
        """Validate production configuration when app initializes."""
        Config.init_app(app)
        
        # Ensure we have a database URL
        if not app.config.get('SQLALCHEMY_DATABASE_URI'):
            raise ValueError("DATABASE_URL environment variable must be set for production")
        
        # Ensure secret key is set
        if not app.config.get('SECRET_KEY') or app.config['SECRET_KEY'] == 'dev-secret-key-please-change':
            raise ValueError("SECRET_KEY environment variable must be set to a strong value for production")


class TestingConfig(Config):
    """Testing configuration."""
    
    TESTING = True
    DEBUG = True
    
    # Use in-memory SQLite for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Faster password hashing for tests
    BCRYPT_LOG_ROUNDS = 4


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """
    Get configuration object based on environment.
    
    Args:
        config_name: Name of configuration ('development', 'production', 'testing')
                    If None, uses FLASK_ENV environment variable.
    
    Returns:
        Configuration class
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    return config.get(config_name, config['default'])

