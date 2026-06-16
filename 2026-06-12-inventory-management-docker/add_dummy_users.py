#!/usr/bin/env python3

# The project uses a package structure where the `app` directory is a top‑level package.
# Import the database helper, user model, and password hashing utility using the full
# package paths to avoid import errors when the script is executed from the project root.
from app.database.dbhelper import db
from app.models.user import User
from app.core.security import hash_password

def seed_users():
    session = db.get_session()
    
    try:
        # Define dummy users with different roles
        dummy_users = [
            {
                "email": "admin@ss.com", 
                "password": "admin123",
                "role": "admin"
            },
            {
                "email": "manager@ss.com", 
                "password": "manager123",
                "role": "manager"
            },
            {
                "email": "viewer@ss.com",
                "password": "viewer123", 
                "role": "viewer"
            },
            {
                "email": "editor@ss.com",
                "password": "editor123",
                "role": "editor"
            },
            {
                "email": "auditor@ss.com",
                "password": "auditor123",
                "role": "auditor"
            }
        ]
        # Create users
        for user_data in dummy_users:
            # Check if user already exists
            existing_user = session.query(User).filter(User.email == user_data["email"]).first()
            
            if not existing_user:
                user = User(
                    email=user_data["email"],
                    hashed_password=hash_password(user_data["password"]),
                    role=user_data["role"]
                )
                session.add(user)
                print(f"✓ Created user: {user_data['email']} with role: {user_data['role']}")
            else:
                print(f"- User already exists: {user_data['email']}")
        
        session.commit()
        print("\n🎉 Dummy users seeded successfully!")
        print("\nUser credentials:")
        for user_data in dummy_users:
            print(f"  {user_data['email']} / {user_data['password']} (Role: {user_data['role']})")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error seeding users: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    seed_users()