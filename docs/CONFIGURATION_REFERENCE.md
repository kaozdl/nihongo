# Configuration Reference

Quick reference for the JLPT Test Manager configuration system.

## Environment Files

| File | Purpose | In Git? |
|------|---------|---------|
| `env.local.example` | Local development template | ✅ Yes |
| `env.production.example` | Production template | ✅ Yes |
| `.env` | Active environment file | ❌ No (gitignored) |

## Quick Start

### Local Development (Default)

```bash
# 1. Copy template
cp env.local.example .env

# 2. Run (defaults work out of the box)
flask run
```

### Production

```bash
# 1. Copy template
cp env.production.example .env

# 2. Generate secret key
python -c "import secrets; print(secrets.token_hex(32))"

# 3. Edit .env with:
#    - SECRET_KEY=<generated-key>
#    - DATABASE_URL=postgresql://user:pass@host/db

# 4. Run with production server
gunicorn app:app
```

## Configuration Modes

### Development

```bash
FLASK_ENV=development
```

- **Database**: SQLite (`jlpt.db`)
- **Debug**: Enabled
- **Reload**: Auto-reload on file changes
- **Logging**: Verbose
- **Cookies**: Not secure (HTTP OK)

**Use for**: Local development, testing features

### Production

```bash
FLASK_ENV=production
```

- **Database**: PostgreSQL (required)
- **Debug**: Disabled
- **Security**: HTTPS cookies, secure headers
- **Logging**: Minimal
- **Validation**: Strict (checks SECRET_KEY, DATABASE_URL)

**Use for**: Live deployment, staging servers

### Testing

```bash
FLASK_ENV=testing
```

- **Database**: SQLite in-memory
- **Debug**: Enabled
- **CSRF**: Disabled
- **Speed**: Faster password hashing

**Use for**: Automated tests only

## Environment Variables

### Required

| Variable | Values | Description |
|----------|--------|-------------|
| `FLASK_ENV` | `development`, `production`, `testing` | Application environment |
| `FLASK_APP` | `app.py` | Flask application entry point |

### Security

| Variable | Development | Production | Description |
|----------|-------------|------------|-------------|
| `SECRET_KEY` | Optional (uses default) | **REQUIRED** | Flask secret key for sessions |

Generate production key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Database

| Variable | Development | Production | Description |
|----------|-------------|------------|-------------|
| `DATABASE_URL` | Optional (uses SQLite) | **REQUIRED** | Database connection string |

**Development Example:**
```bash
# Leave empty for default SQLite
DATABASE_URL=

# Or specify custom SQLite
DATABASE_URL=sqlite:///path/to/custom.db
```

**Production Example:**
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/jlpt_db
```

### Debugging

| Variable | Values | Default | Description |
|----------|--------|---------|-------------|
| `FLASK_DEBUG` | `0`, `1` | Depends on `FLASK_ENV` | Enable Flask debugger |
| `SQL_ECHO` | `True`, `False` | `False` | Log all SQL queries |

### Server

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_RUN_HOST` | `127.0.0.1` | Host to bind to |
| `FLASK_RUN_PORT` | `5000` | Port to listen on |

## Configuration Classes

Located in `config.py`:

```python
from config import get_config

# Get config based on FLASK_ENV
config = get_config()

# Or specify explicitly
dev_config = get_config('development')
prod_config = get_config('production')
test_config = get_config('testing')
```

### Config Properties

```python
# Flask settings
app.config['SECRET_KEY']                    # Secret key for sessions
app.config['DEBUG']                         # Debug mode
app.config['TESTING']                       # Testing mode

# Database
app.config['SQLALCHEMY_DATABASE_URI']       # Database connection
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] # False (disabled)
app.config['SQLALCHEMY_ECHO']               # Log SQL queries

# Security
app.config['SESSION_COOKIE_SECURE']         # HTTPS only cookies (prod)
app.config['SESSION_COOKIE_HTTPONLY']       # No JS access to cookies
app.config['SESSION_COOKIE_SAMESITE']       # CSRF protection

# i18n
app.config['BABEL_DEFAULT_LOCALE']          # 'en'
app.config['BABEL_SUPPORTED_LOCALES']       # ['en', 'es']

# Application
app.config['MAX_CONTENT_LENGTH']            # 16MB file upload limit
```

## Checking Current Configuration

### In Python/Flask Shell

```python
from app import app

print(f"Environment: {app.config['ENV']}")
print(f"Debug: {app.config['DEBUG']}")
print(f"Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
print(f"Secret Key: {app.config['SECRET_KEY'][:10]}...")
```

### From Command Line

```bash
# Check environment
python -c "import os; print(os.environ.get('FLASK_ENV', 'development'))"

# Check database
python -c "from app import app; print(app.config['SQLALCHEMY_DATABASE_URI'])"

# Check debug mode
python -c "from app import app; print(app.config['DEBUG'])"
```

### Startup Messages

When running `flask run`, you'll see:

```
🚀 Starting application in DEVELOPMENT mode
📊 Database: sqlite:////path/to/nihongo/jlpt.db...
```

or

```
🚀 Starting application in PRODUCTION mode
📊 Database: postgresql://user:***@localhost/jlpt_db...
```

## Common Configurations

### Local Development (Default)

```bash
# .env
FLASK_ENV=development
FLASK_APP=app.py
FLASK_DEBUG=1
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=
SQL_ECHO=False
FLASK_RUN_HOST=127.0.0.1
FLASK_RUN_PORT=5000
```

**Result:**
- SQLite at `jlpt.db`
- Debug mode ON
- Auto-reload ON
- SQL logging OFF

### Local Development with SQL Logging

```bash
# .env
FLASK_ENV=development
SQL_ECHO=True
# ... rest same as above
```

**Result:**
- All SQL queries logged to console
- Useful for debugging database issues

### Production (Heroku-style)

```bash
# .env or environment variables
FLASK_ENV=production
SECRET_KEY=<strong-random-key>
DATABASE_URL=postgres://username:password@host/db  # Auto-converted to postgresql://
```

**Result:**
- PostgreSQL connection
- HTTPS-only cookies
- No debug info
- Secure headers

### Production (Traditional Server)

```bash
# .env
FLASK_ENV=production
FLASK_APP=app.py
FLASK_DEBUG=0
SECRET_KEY=<strong-random-key>
DATABASE_URL=postgresql://jlpt_user:secure_pass@localhost:5432/jlpt_db
SQL_ECHO=False
```

**Result:**
- PostgreSQL connection
- Production security settings
- Suitable for Gunicorn/uWSGI

## Troubleshooting

### "DATABASE_URL environment variable must be set for production"

**Problem:** Running in production mode without DATABASE_URL

**Solution:**
```bash
# Set in .env
DATABASE_URL=postgresql://user:pass@host/db

# Or export directly
export DATABASE_URL=postgresql://user:pass@host/db
```

### "SECRET_KEY environment variable must be set to a strong value for production"

**Problem:** Production mode with default/weak secret key

**Solution:**
```bash
# Generate strong key
python -c "import secrets; print(secrets.token_hex(32))"

# Set in .env
SECRET_KEY=<generated-key>
```

### Changes to .env not taking effect

**Problem:** .env changes not loaded

**Solutions:**
```bash
# 1. Restart Flask server (Ctrl+C, then flask run)

# 2. Clear Python cache
find . -name "*.pyc" -delete
find . -name "__pycache__" -delete

# 3. Ensure .env is in project root
ls -la .env

# 4. Check load_dotenv() is working
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.environ.get('FLASK_ENV'))"
```

### Can't connect to PostgreSQL

**Check connection:**
```bash
# Test with psql
psql -U username -d database -h host

# Check DATABASE_URL format
echo $DATABASE_URL
# Should be: postgresql://user:pass@host:port/db
```

### "No such table" errors

**Problem:** Database not initialized

**Solution:**
```bash
# Initialize database
flask init-db

# Or use migrations
flask db-upgrade
```

## Best Practices

### Local Development

✅ **DO:**
- Use SQLite (default)
- Keep `FLASK_DEBUG=1`
- Use `.env` file
- Enable `SQL_ECHO` when debugging database issues

❌ **DON'T:**
- Set `FLASK_ENV=production` locally
- Use the production database
- Commit `.env` to git
- Use production secrets

### Production

✅ **DO:**
- Use PostgreSQL
- Set strong `SECRET_KEY` (32+ chars)
- Set `FLASK_ENV=production`
- Use environment variables (not `.env` file in some platforms)
- Use a production WSGI server (Gunicorn, uWSGI)
- Enable HTTPS
- Use database connection pooling
- Set up monitoring and logging

❌ **DON'T:**
- Use SQLite in production
- Enable `DEBUG` mode
- Use default `SECRET_KEY`
- Run with `flask run`
- Commit production `.env` to git
- Share production secrets

### Testing

✅ **DO:**
- Use `FLASK_ENV=testing`
- Use in-memory SQLite
- Use pytest fixtures

❌ **DON'T:**
- Test against production database
- Use real user credentials

## Migration from Old Configuration

If upgrading from the old configuration (before config.py):

### Old Way (app.py)

```python
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///jlpt.db')
```

### New Way (config.py)

```python
from config import get_config

app.config.from_object(get_config())
```

**Migration Steps:**

1. Create `.env` from template:
   ```bash
   cp env.local.example .env
   ```

2. No changes to environment variables needed - they're the same!

3. Old apps will work, new apps have more features (production validation, testing config, etc.)

## See Also

- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Full production deployment
- [README](../README.md) - Project overview
- [config.py](../config.py) - Configuration source code

