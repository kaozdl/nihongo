# Deployment Guide

This guide covers deploying the JLPT Test Manager application to production with PostgreSQL.

## Table of Contents
- [Configuration Overview](#configuration-overview)
- [Local Development Setup](#local-development-setup)
- [Production Deployment](#production-deployment)
- [Environment Variables](#environment-variables)
- [Database Migration](#database-migration)
- [Troubleshooting](#troubleshooting)

---

## Configuration Overview

The application supports three environments:

| Environment | Database | Debug | Use Case |
|------------|----------|-------|----------|
| **Development** | SQLite | ✅ Yes | Local development |
| **Production** | PostgreSQL | ❌ No | Production server |
| **Testing** | SQLite (memory) | ✅ Yes | Unit/integration tests |

### Configuration Files

```
nihongo/
├── config.py                    # Configuration classes
├── env.local.example            # Local development template
├── env.production.example       # Production template
└── .env                        # Active environment (not in git)
```

---

## Local Development Setup

### 1. Create Local Environment File

Copy the local example and customize:

```bash
cp env.local.example .env
```

### 2. Edit .env File

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

**Note**: Leave `DATABASE_URL` empty to use default SQLite (`sqlite:///jlpt.db`)

### 3. Install Dependencies

```bash
# Install production + development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 4. Initialize Database

```bash
flask init-db
```

This will:
- Create SQLite database (`jlpt.db`)
- Create default user: `default@nihongo.edu.uy` / `nihongo123`
- Load 3 N5 practice exams

### 5. Run Development Server

```bash
flask run
```

Or using the init script:

```bash
# macOS/Linux
./init.sh

# Windows
init.bat
```

---

## Production Deployment

### Prerequisites

1. **PostgreSQL Database**: Version 12 or higher
2. **Python**: Version 3.8 or higher
3. **Web Server**: Gunicorn, uWSGI, or similar
4. **Reverse Proxy**: Nginx or Apache (recommended)

### 1. Set Up PostgreSQL Database

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE jlpt_db;
CREATE USER jlpt_user WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE jlpt_db TO jlpt_user;
\q
```

### 2. Create Production Environment File

```bash
cp env.production.example .env
```

### 3. Configure Production Environment

Edit `.env` with production values:

```bash
# .env (PRODUCTION)
FLASK_ENV=production
FLASK_APP=app.py
FLASK_DEBUG=0

# CRITICAL: Generate a strong secret key
# Use: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=your-very-long-random-secret-key-here

# PostgreSQL connection string
DATABASE_URL=postgresql://jlpt_user:your_secure_password@localhost:5432/jlpt_db

SQL_ECHO=False

# Production server settings
FLASK_RUN_HOST=0.0.0.0
FLASK_RUN_PORT=5000
```

### 4. Install Production Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 5. Run Database Migrations

```bash
# Initialize Alembic (first time only)
alembic upgrade head

# Or use Flask CLI
flask db-upgrade
```

### 6. Load Initial Data (Optional)

```bash
# Create admin user
flask create-admin

# Or use init-db to load everything
flask init-db
```

### 7. Install Gunicorn (Production Server)

```bash
pip install gunicorn
```

### 8. Run with Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**Recommended Gunicorn Configuration:**

Create `gunicorn_config.py`:

```python
# gunicorn_config.py
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"

# Process naming
proc_name = "jlpt-manager"

# Server mechanics
daemon = False
pidfile = "gunicorn.pid"
```

Run with config:

```bash
gunicorn -c gunicorn_config.py app:app
```

### 9. Set Up Systemd Service (Linux)

Create `/etc/systemd/system/jlpt-manager.service`:

```ini
[Unit]
Description=JLPT Test Manager
After=network.target postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/nihongo
Environment="PATH=/path/to/nihongo/venv/bin"
Environment="FLASK_ENV=production"
ExecStart=/path/to/nihongo/venv/bin/gunicorn -c gunicorn_config.py app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable jlpt-manager
sudo systemctl start jlpt-manager
sudo systemctl status jlpt-manager
```

### 10. Configure Nginx Reverse Proxy

Create `/etc/nginx/sites-available/jlpt-manager`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files (if served separately)
    location /static {
        alias /path/to/nihongo/static;
        expires 30d;
    }

    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/jlpt-manager /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 11. Set Up SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

---

## Environment Variables

### Required for All Environments

| Variable | Description | Example |
|----------|-------------|---------|
| `FLASK_ENV` | Environment name | `development` or `production` |
| `FLASK_APP` | Entry point | `app.py` |
| `SECRET_KEY` | Flask secret key | Random string (32+ chars) |

### Development Only

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_DEBUG` | Enable debug mode | `1` |
| `SQL_ECHO` | Log SQL queries | `False` |
| `DATABASE_URL` | Optional SQLite path | `sqlite:///jlpt.db` |

### Production Required

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection | `postgresql://user:pass@host/db` |
| `SECRET_KEY` | **MUST** be strong & unique | Use `secrets.token_hex(32)` |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_RUN_HOST` | Bind address | `127.0.0.1` |
| `FLASK_RUN_PORT` | Port number | `5000` |

---

## Database Migration

### Creating Migrations

After changing models:

```bash
# Generate migration
flask db-migrate

# Or with Alembic directly
alembic revision --autogenerate -m "description"
```

### Applying Migrations

```bash
# Development
flask db-upgrade

# Production (recommended)
alembic upgrade head
```

### Rollback

```bash
# Rollback one migration
flask db-downgrade

# Or with Alembic
alembic downgrade -1
```

### Check Migration Status

```bash
flask db-history

# Or with Alembic
alembic current
alembic history
```

---

## Troubleshooting

### Error: "No module named psycopg2"

**Solution**: Install PostgreSQL adapter

```bash
pip install psycopg2-binary
```

### Error: "DATABASE_URL environment variable must be set"

**Solution**: Ensure `.env` file exists with `DATABASE_URL` set

```bash
# Check if .env exists
ls -la .env

# Verify variable is set
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.environ.get('DATABASE_URL'))"
```

### Error: "postgres:// URL not supported"

**Solution**: The app automatically converts `postgres://` to `postgresql://`. If you still see this error, manually update your `DATABASE_URL`:

```bash
# Wrong (old Heroku format)
DATABASE_URL=postgres://user:pass@host/db

# Correct
DATABASE_URL=postgresql://user:pass@host/db
```

### Connection Refused to PostgreSQL

**Check PostgreSQL is running:**

```bash
sudo systemctl status postgresql
```

**Check connection:**

```bash
psql -U jlpt_user -d jlpt_db -h localhost
```

### Permission Denied

**Ensure correct ownership:**

```bash
sudo chown -R www-data:www-data /path/to/nihongo
```

### Static Files Not Loading

**Collect static files (if using Flask-Assets):**

```bash
flask assets build
```

**Or configure Nginx to serve directly:**

```nginx
location /static {
    alias /path/to/nihongo/static;
}
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] Set `FLASK_ENV=production`
- [ ] Generate strong `SECRET_KEY`
- [ ] Set up PostgreSQL database
- [ ] Configure `DATABASE_URL`
- [ ] Run migrations: `flask db-upgrade`
- [ ] Load initial data: `flask init-db`
- [ ] Install `gunicorn` or production server
- [ ] Test with `gunicorn app:app`

### Security

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` (32+ characters)
- [ ] PostgreSQL has secure password
- [ ] Database user has minimal permissions
- [ ] Set up SSL/TLS (Let's Encrypt)
- [ ] Configure firewall (allow 80, 443)
- [ ] Enable HTTPS redirects
- [ ] Set secure cookie flags (automatic in production config)

### Monitoring

- [ ] Set up application logs
- [ ] Configure error tracking (Sentry, etc.)
- [ ] Monitor database performance
- [ ] Set up health checks
- [ ] Configure backups (database + uploads)

---

## Cloud Platform Deployment

### Heroku

```bash
# Install Heroku CLI
# Login
heroku login

# Create app
heroku create jlpt-manager

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")

# Deploy
git push heroku main

# Run migrations
heroku run flask db-upgrade

# Load initial data
heroku run flask init-db

# Open app
heroku open
```

### DigitalOcean App Platform

1. Connect GitHub repository
2. Set environment variables in dashboard
3. App Platform auto-detects Flask
4. Add PostgreSQL database
5. Deploy

### AWS Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.11 jlpt-manager

# Create environment
eb create jlpt-prod

# Set environment variables
eb setenv FLASK_ENV=production SECRET_KEY=your-key-here

# Deploy
eb deploy

# Open
eb open
```

---

## Maintenance

### Backup Database

```bash
# PostgreSQL backup
pg_dump -U jlpt_user jlpt_db > backup_$(date +%Y%m%d).sql

# Restore
psql -U jlpt_user jlpt_db < backup_20231201.sql
```

### Update Application

```bash
# Pull latest code
git pull origin main

# Install new dependencies
pip install -r requirements.txt

# Run migrations
flask db-upgrade

# Restart application
sudo systemctl restart jlpt-manager
```

### Monitor Logs

```bash
# Application logs
tail -f logs/error.log

# System logs
sudo journalctl -u jlpt-manager -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
```

---

## See Also

- [Configuration Reference](../config.py)
- [Database Migrations](MIGRATIONS_GUIDE.md)
- [Testing Guide](TESTING_GUIDE.md)
- [README](../README.md)

