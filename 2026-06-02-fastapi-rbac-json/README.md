# FastAPI RBAC (JSON-driven)

This project demonstrates dynamic RBAC in FastAPI using:

- route + method permission config from JSON
- JWT authentication backed by DB user lookup
- centralized access checks via dependency
- O(1) permission lookup through startup cache
- PostgreSQL + SQLAlchemy + Alembic

## Project structure

```text
app/
├── config/
│   └── permissions.json
├── middleware/
│   └── rbac.py
├── auth/
│   └── jwt_auth.py
├── routes/
│   ├── auth.py
│   └── users.py
└── main.py
```

## Run

```bash
pip install -r requirements.txt
alembic upgrade head
python code.py
```

## Test role-based access

Authenticate with `POST /api/v1/auth/login` to receive a bearer token.

Default seeded users:

- admin (role: admin)
- manager1 (role: manager)
- employee1 (role: employee)

Examples:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
curl -X GET http://127.0.0.1:8000/api/v1/users -H "Authorization: Bearer <token>"
curl -X POST http://127.0.0.1:8000/api/v1/users -H "Authorization: Bearer <token>"
curl -X DELETE http://127.0.0.1:8000/api/v1/users/1 -H "Authorization: Bearer <token>"
```

Expected:

- `GET /api/v1/users` works for `admin`, `manager`, `employee`
- `POST /api/v1/users` works for `admin`, `manager`
- `DELETE /api/v1/users/{id}` works for `admin` only

## PostgreSQL config

Default connection URL:

`postgresql+psycopg2://postgres:Hkoradiya@localhost/fastapidb`

Override with env var if needed:

```bash
set DATABASE_URL=postgresql+psycopg2://postgres:Hkoradiya@localhost/fastapidb
```

JWT config defaults:

```bash
set JWT_SECRET_KEY=change-me-in-production
set JWT_ALGORITHM=HS256
set JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
```
