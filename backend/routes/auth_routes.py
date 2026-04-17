# backend/routes/auth_routes.py
from flask import Blueprint, request, render_template, redirect, url_for, make_response, jsonify
from services.auth_service import AuthService 
from db import db
from models import User
from datetime import datetime, timedelta

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
        return render_template('login.html', error=result["message"])
    return render_template('login.html')

@auth_bp.route('/api/subscribe', methods=['POST'])
def update_subscription():
    """
    Subscribes the current user to a specific bike plan.
    
    Request Body:
    {
        "plan_name": str ("Day Pass", "Monthly", or "Annual")
    }
    
    Response Schema:
    {
        "success": bool,
        "message": str (optional, on failure)
    }
    """
    user_email = request.cookies.get('user_email') 
    user = User.query.filter_by(email=user_email).first()
    if user:
        data = request.json
        user.current_plan = data.get('plan_name') 
        user.plan_start_date = datetime.now()
        if user.current_plan == 'Day Pass':
            user.plan_end_date = datetime.now() + timedelta(days=1)
        elif user.current_plan == 'Annual':
            user.plan_end_date = datetime.now() + timedelta(days=365)
        else: # Monthly
            user.plan_end_date = datetime.now() + timedelta(days=30)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "User not found"}), 404

@auth_bp.route('/api/renew', methods=['POST'])
def handle_renew():
    """
    Extends the current user's active subscription.
    
    Response Schema:
    {
        "success": bool,
        "message": str (optional, on failure)
    }
    """
    user_email = request.cookies.get('user_email') 
    found_user = User.query.filter_by(email=user_email).first()
    
    if found_user:
        if not found_user.current_plan or found_user.current_plan == "None":
            return jsonify({
                "success": False, 
                "message": "Please select a plan first!"
            }), 400
        days = 30
        if found_user.current_plan == 'Annual': 
            days = 365
        elif found_user.current_plan == 'Day Pass': 
            days = 1
            
        if not found_user.plan_end_date:
            found_user.plan_end_date = datetime.now()
            
        found_user.plan_end_date += timedelta(days=days)
        db.session.commit()
        return jsonify({"success": True})
    
    return jsonify({"success": False, "message": "User not found"}), 404


@auth_bp.route('/logout')
def logout():
    resp = make_response(redirect(url_for('auth.login')))
    resp.delete_cookie('user_email')
    resp.delete_cookie('user_name')
    return resp