from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from models import Subject, Quiz, Score

user = Blueprint('user', __name__)

@user.before_request
@login_required
def check_user():
    # Allow access to user_dashboard without redirection
    if request.endpoint == 'user.user_dashboard':
        return None

    # Redirect non-admin users to user_dashboard
    if not current_user.is_admin:
        return redirect(url_for('user.user_dashboard'))


@user.route('/user_dashboard')
@login_required
def user_dashboard():
    subjects = Subject.query.all()
    scores = Score.query.filter_by(user_id=current_user.id).all()
    return render_template('user/dashboard.html', subjects=subjects, socores=scores)