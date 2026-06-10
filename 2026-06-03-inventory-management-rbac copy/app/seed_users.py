from database.dbhelper import db
from models.user import User
from core.security import hash_password

def seed_users():
    session = db.get_session()
    
    try:
        # Define dummy users with different roles
        dummy_users = [
            {
                "email": "admin@example.com",
                "password": "admin123",
                "role": "admin"
            },
            {
                "email": "manager@example.com", 
                "password": "manager123",
                "role": "manager"
            },
            {
                "email": "viewer@example.com",
                "password": "viewer123", 
                "role": "viewer"
            },
            {
                "email": "editor@example.com",
                "password": "editor123",
                "role": "editor"
            },
            {
                "email": "auditor@example.com",
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
                print(f"Created user: {user_data['email']} with role: {user_data['role']}")
            else:
                print(f"User already exists: {user_data['email']}")
        
        session.commit()
        print("Dummy users seeded successfully!")
        
    except Exception as e:
        session.rollback()
        print(f"Error seeding users: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    seed_users()