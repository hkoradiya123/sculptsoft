# FastAPI RBAC (SQLite)

This example demonstrates a professional FastAPI app with:

- SQLite with SQLAlchemy for user storage
- Password hashing with `passlib` (bcrypt)
- JWT access tokens including `role` claim
- Reusable RBAC dependency `require_roles(...)`

Quick start:

1. Create a virtualenv and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Run the app (Uvicorn):

```bash
uvicorn app:app --reload
```

3. Open docs: http://127.0.0.1:8000/docs

Default seeded users:

- admin / admin123 (role: admin)
- user1 / user123 (role: user)

Endpoints:

- `POST /login` (form data) → returns JWT
- `GET /dashboard` → any authenticated user
- `GET /admin` → admin only
- `POST /users` → create new user (admin only)
