# Create SQLAlchemy Model

Create a new SQLAlchemy ORM model with Alembic migration.

## Input

The user should provide: $ARGUMENTS

Parse from the arguments:
- Model/table name
- Fields and their types
- Relationships (if any)

## Steps

1. Create the model file at `backend/app/models/{name}.py`:
   - Import from SQLAlchemy (Column, Integer, String, ForeignKey, relationship, etc.)
   - Import Base from the project's database base
   - Define the model class with __tablename__
   - Add columns with proper types, constraints, and defaults
   - Add created_at and updated_at timestamp columns
   - Add relationships if specified

2. Register the model in `backend/app/models/__init__.py` (import it so Alembic can detect it).

3. Generate Alembic migration:
   ```bash
   cd backend && uv run alembic revision --autogenerate -m "add {name} table"
   ```

4. Apply the migration:
   ```bash
   cd backend && uv run alembic upgrade head
   ```

## Conventions

- Table names: snake_case, plural (e.g., `user_profiles`)
- Model class names: PascalCase, singular (e.g., `UserProfile`)
- Always include `id` as Integer primary key
- Always include `created_at` and `updated_at` timestamps
- Use `server_default` for database-level defaults
- Add indexes on frequently queried columns
