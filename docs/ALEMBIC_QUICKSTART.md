# Alembic Quick Start

Quick reference for database migrations with Alembic.

## Setup (Already Done)

```bash
# Install Alembic
pip install alembic

# Initialize (already done in this project)
alembic init alembic

# Configure env.py to use Flask models (already done)
```

## Daily Use Commands

### Apply Migrations

```bash
# Apply all pending migrations (use this after pulling code)
flask db-upgrade

# Or use alembic directly
alembic upgrade head
```

### Create a Migration

After changing models in `models/`:

```bash
# Generate migration automatically
flask db-migrate

# Or with alembic (with a message)
alembic revision --autogenerate -m "Add user preferences"
```

### Review Migration

```bash
# Check what will be applied
alembic upgrade head --sql  # Shows SQL without executing

# View migration history
flask db-history

# Check current database version
alembic current
```

### Rollback

```bash
# Rollback last migration
flask db-downgrade

# Rollback to specific version
alembic downgrade <revision_id>

# Rollback all migrations
alembic downgrade base
```

## Common Workflows

### Making a Model Change

```bash
# 1. Edit model files in models/
vim models/user.py

# 2. Generate migration
flask db-migrate

# 3. Review generated migration file
cat alembic/versions/*latest*.py

# 4. Apply migration
flask db-upgrade

# 5. Test your changes
flask run
```

### Pulling New Code with Migrations

```bash
# 1. Pull latest code
git pull

# 2. Apply new migrations
flask db-upgrade

# 3. Restart application
flask run
```

### Fixing a Bad Migration

```bash
# 1. Rollback
flask db-downgrade

# 2. Edit migration file or model
vim alembic/versions/abc123_bad_migration.py

# 3. Re-apply
flask db-upgrade
```

## Migration File Structure

```python
def upgrade():
    # Apply schema changes
    op.add_column('users', sa.Column('is_premium', sa.Boolean(), nullable=True))

def downgrade():
    # Revert schema changes
    op.drop_column('users', 'is_premium')
```

## Tips

1. **Always review auto-generated migrations**
2. **Test both upgrade and downgrade**
3. **Backup database before migrating in production**
4. **One migration per logical change**
5. **Use descriptive migration messages**

## Help

```bash
# Show all alembic commands
alembic --help

# Show help for specific command
alembic upgrade --help
```

For detailed guide, see [MIGRATIONS_GUIDE.md](MIGRATIONS_GUIDE.md)

