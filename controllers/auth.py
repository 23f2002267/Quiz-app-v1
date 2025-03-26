from flask import Blueprint, render_template, redirect, url_for, flash, request
from sqlalchemy import exc
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user, current_user
from models import User, db
from datetime import datetime
# from controllers.admin import admin

# admin = admin
auth = Blueprint('auth', __name__)

@auth.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            if user.is_admin :
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('user.user_dashboard'))
        flash('Invalid credentials.')
    return render_template('auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        fullname = request.form['fullname']
        qualification = request.form['qualification']
        user = User(
                username=username,
                password_hash=generate_password_hash(password),
                fullname=fullname,
                qualification=qualification,
                dob=datetime.strptime(request.form['dob'], '%Y-%m-%d').date(),
                is_admin=False,
                is_active=True)
        db.session.add(user)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))