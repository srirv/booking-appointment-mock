# Database Migrations

This directory contains migration scripts to keep the database schema in sync with the application models.

## Migration: DateTime to separate Date and Time fields

The `migrate_datetime_to_date_time.py` script migrates the database schema from using a single `dateTime` column to separate `date` and `time` columns in the appointments table.

### Running the migration

1. Make sure the correct database connection is configured in your `.env` file:

```
DATABASE_URL=postgresql://neondb_owner:<password>@ep-fancy-lab-a5kqy0m9-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require
```

2. Run the migration script:

```bash
python -m migrations.migrate_datetime_to_date_time
```

### What this migration does

1. Adds new `date` and `time` columns to the appointments table
2. Copies data from the `dateTime` column to the new columns
3. Removes the original `dateTime` column

### Handling failures

If the migration fails for any reason:

1. Check the error message
2. Fix any issues
3. Run the script again - it's designed to be idempotent and will skip steps that have already been completed

## Adding New Migrations

When you need to make changes to the database schema:

1. Create a new Python file in this directory
2. Follow the pattern in existing migration scripts
3. Document the migration in this README file 