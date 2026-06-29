# Engineering Standards

Architecture:

Controller
→ Service
→ Repository
→ Database

Rules:

- No business logic in routes.
- No direct database access from controllers.
- Use dependency injection.
- Use typed schemas.
- Follow existing project structure.

Code Quality:

- Production-ready code only.
- Explicit naming.
- Proper error handling.
- Logging where appropriate.
- No mock implementations unless requested.