# Alembic migrations (quick start)

1. Install dependencies from `requirements.txt` (see project root):

```
pip install -r requirements.txt
```

2. Ensure PostgreSQL is running and a database named `fastapidb` exists.

3. Export `DATABASE_URL` if you need custom credentials, example:

Windows (PowerShell):

```
$env:DATABASE_URL = "postgresql+psycopg2://postgres:password@localhost/fastapidb"
```

4. Create the Alembic environment (already present). To generate first migration:

```
alembic revision --autogenerate -m "create initial tables"
alembic upgrade head
```

If `alembic` is not in PATH, run it with `python -m alembic`.
