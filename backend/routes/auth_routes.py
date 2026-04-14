# backend/routes/auth_routes.py
from flask import Blueprint, request, render_template, redirect, url_for, make_response
from services.auth_service import AuthService 

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService() 

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        result = auth_service.register_user(
            email=request.form.get('email'),
            name=request.form.get('full_name'),
            password=request.form.get('password')
        )
        if result["success"]:
            return redirect(url_for('auth.login'))
        return result["message"] 
    return render_template('signup.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        result = auth_service.authenticate_user(
            email=request.form.get('username'),
            password=request.form.get('password')
        )
        if result["success"]:
            user = result["user"]
            resp = make_response(redirect(url_for('pages.home')))
            resp.set_cookie('user_email', user.email, httponly=True, max_age=3600)
            resp.set_cookie('user_name', user.name, httponly=True, max_age=3600)
            return resp
        return result["message"]
    return render_template('login.html')



@auth_bp.route('/logout')
def logout(): 
    return redirect(url_for('auth.login'))