# Create Service Layer

Create a backend service module for business logic.

## Input

The user should provide: $ARGUMENTS

Parse from the arguments:
- Service name / domain
- Key operations it should handle
- Dependencies (other services, external APIs, etc.)

## Steps

1. Create the service file at `backend/app/services/{name}.py`:
   - Define a service class or module with business logic functions
   - Inject database session via parameter (not global)
   - Keep services independent of HTTP layer (no Request/Response objects)
   - Include proper error handling with custom exceptions

2. Create or update custom exceptions in `backend/app/exceptions.py` if needed.

3. Update the corresponding router to use the service instead of inline logic.

4. Create a test file at `backend/tests/test_service_{name}.py` with key test cases.

## Conventions

- Services contain business logic; routers handle HTTP concerns
- Services receive a db session as parameter, don't create their own
- Raise domain exceptions (NotFoundError, ValidationError), not HTTPException
- Routers catch service exceptions and map to HTTP responses
- Services should be testable without FastAPI (no Depends in service code)
- Keep services focused: one domain per service module
