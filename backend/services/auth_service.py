# backend/services/auth_service.py
from models import User
from db import db

class AuthService:
    def register_user(self, email, name, password):
        
        if User.query.get(email):
            return {"success": False, "message": "Email already exists!"}
        
        
        try:
            new_user = User(email=email, name=name, password=password)
            db.session.add(new_user)
            db.session.commit()
            return {"success": True, "user": new_user}
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}

    def authenticate_user(self, email, password):
        
        user = User.query.get(email)
        if user and user.password == password:
            return {"success": True, "user": user}
        return {"success": False, "message": "Invalid email or password!"}