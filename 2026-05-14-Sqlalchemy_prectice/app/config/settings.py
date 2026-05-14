import os


class Settings:
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:Hkoradiya@localhost/userdb",
    )


settings = Settings()
