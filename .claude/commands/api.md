# Create API Endpoint

Create a new FastAPI API endpoint with proper structure.

## Input

The user should provide: $ARGUMENTS

Parse from the arguments:
- Resource name (e.g., "users", "posts", "orders")
- HTTP methods needed (default: full CRUD - GET list, GET by id, POST, PUT, DELETE)
- Any special requirements

## Steps

1. Create or update the router file at `backend/app/routers/{resource}.py`:
   - Import dependencies (FastAPI APIRouter, SQLAlchemy session, schemas, models)
   - Define router with appropriate prefix and tags
   - Implement requested endpoint handlers
   - Include proper type hints and status codes

2. Create or update the schema file at `backend/app/schemas/{resource}.py`:
   - Define Pydantic BaseModel schemas (Create, Update, Response)
   - Include proper field types and validation

3. Register the router in `backend/app/main.py` if not already registered.

4. If a new model is needed, suggest running `/project:model` to create it first.

## Conventions

- Use async def for all route handlers
- Use Depends() for database session injection
- Use HTTPException for error responses
- Follow RESTful naming: plural nouns for collection endpoints
- Include response_model in route decorators
- Group related endpoints under the same router tag
