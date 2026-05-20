if __name__ == "__main__" and __package__ is None:
	import sys
	from pathlib import Path

	# Allow running this file directly (python app/main.py).
	sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.database import Base, SessionLocal, engine
from app.models.user import User


def init_db() -> None:
	Base.metadata.create_all(bind=engine)


def create_sample_user():
    with SessionLocal() as session:
        name = "Harsh"
        email = "harsh@example.com"
        if session.query(User).filter_by(email=email).first():
            print(f"User with email {email} already exists.")
            return
        user = User(name=name, email=email)
        session.add(user)
        session.commit()


def list_users() -> None:
    with SessionLocal() as session:
        users = session.query(User).order_by(User.id).all()
        for user in users:
            print(f"{user.id}: {user.name} {user.email}")
            
def remove_sample_user():
    with SessionLocal() as session:
        email = "harsh@example.com"
        user = session.query(User).filter_by(email=email).first()
        if user:
            session.delete(user)
            session.commit()
            print(f"User with email {email} removed.")
        else:
            print(f"User with email {email} not found.")


if __name__ == "__main__":
	init_db()
	remove_sample_user()
	# create_sample_user()
	list_users()
