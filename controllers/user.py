from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from models import Subject, Quiz, Score, Chapter, Question, db

user = Blueprint('user', __name__)

@user.before_request
@login_required
def check_user():
    # Allow access to certain routes without redirection
    allowed_routes = ['user.user_dashboard', 'user.chapter','user.quiz', 'user.quiz_attempt', 'user.user_history']
    if request.endpoint in allowed_routes:
        return None

    # Redirect non-admin users to the user dashboard for other routes
    if not current_user.is_admin:
        return redirect(url_for('user.user_dashboard'))

@user.route('/user_dashboard')
@login_required
def user_dashboard():
    user = current_user.username
    subjects = Subject.query.all()
    return render_template('user/dashboard.html', subjects=subjects, user=user)

@user.route('/quiz_history')
@login_required
def user_history():
    user = current_user.username
    user_id = current_user.id
    hist = Score.query.filter_by(user_id=user_id).all()
    return render_template('user/history.html', hist=hist, user=user)


@user.route('/user/<int:su_id>/chapters')
@login_required
def chapter(su_id):
    if su_id != 0:
        chap = Chapter.query.filter_by(subject_id=su_id).all()
        if chap:
            return render_template('user/chapters.html', chap = chap, su_id = su_id)
        return render_template('user/chapters.html', chap = chap, su_id = su_id)

@user.route('/<int:ch_id>/quizes')
@login_required
def quiz(ch_id):
    if ch_id != 0:
        elem = Quiz.query.filter_by(chapter_id=ch_id).all()
        if elem:
            return render_template('user/quiz.html', elem = elem, ch_id = ch_id)
        return render_template('user/quiz.html', elem = elem, ch_id = ch_id)

@user.route('/<int:q_id>/attempt', methods=['GET', 'POST'])
@login_required
def quiz_attempt(q_id):
    user_id = current_user.id
    elem = Quiz.query.filter_by(id=q_id).first()
    time = elem.time_duration
    time = time.hour*3600 + time.minute*60 + time.second # Convert time to seconds
    if elem:
        quest = elem.questions.split(',')
        answers = {} # List to store correct answers
        questions = {} # Dictionary to store questions and options

        for ques_id in quest:
            quest = Question.query.filter_by(id=ques_id).all()
            for question in quest:
                questions[question.q_statement] = question.options.split(',')
                answers[question.q_statement] = question.correct_option

        if request.method == 'GET':
                return render_template('user/quiz_attempt.html', questions=questions, user_id=user_id,
                                       time_duration=time)

        if request.method == 'POST':
            submitted_answers = {}  # Dictionary to store user-submitted answers
            for key, value in request.form.items():
                submitted_answers[key] = value  # Storing question as key and selected answer as value

            corr=0
            total=0
            total_score=0
            for key, value in answers.items():
                total+=1
                if submitted_answers.get(key) :
                    if submitted_answers[key] == value:
                        corr+=1
            if corr !=0:
                total_score = (corr/total)*100
            db.session.add(Score(user_id=user_id, quiz_id=q_id, total_score=total_score))
            db.session.commit()
            return render_template('user/score.html', corr=corr, total=total, answers=answers,
                            submitted_answers=submitted_answers, questions=questions)

