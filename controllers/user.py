from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from models import Subject, Quiz, Score, Chapter, Question

user = Blueprint('user', __name__)
global answers
global questions
@user.before_request
@login_required
def check_user():
    # Allow access to certain routes without redirection
    allowed_routes = ['user.user_dashboard', 'user.chapter','user.quiz', 'user.quiz_attempt']
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

    if q_id != 0 and request.method == 'GET':
        elem = Quiz.query.filter_by(id=q_id).first()
        if elem:
            quest = elem.questions.split(',')
            answers = []  # List to store correct answers
            questions = {}  # Dictionary to store questions and options

            for ques_id in quest:
                quest = Question.query.filter_by(id=ques_id).all()
                for question in quest:
                    questions[question.q_statement] = question.options.split(',')
                    answers.append(question.correct_option)  # Appending correct answer in sequence
            
            print(questions)
            print('????????????????????????????????????????????????????????????????????')
            return render_template('user/quiz_attempt.html', questions=questions, user_id=user_id)

    elif request.method == 'POST':
        submitted_answers = {}  # Dictionary to store user-submitted answers
        for key, value in request.form.items():
            submitted_answers[key] = value  # Storing question as key and selected answer as value

        print('############################################################')
        print("User Submitted Answers:", submitted_answers)

        # Create a dictionary of correct answers mapped to questions
        correct_answers = dict(zip(questions.keys(), answers))  

        # Evaluate the score
        score = sum(1 for q, a in submitted_answers.items() if correct_answers.get(q) == a)

        print(f"User Score: {score}/{len(questions)}")

        # Pass the data to the score template
        # return render_template(
        #     'user/score.html',
        #     submitted=submitted_answers,
        #     correct_answers=correct_answers,
        #     score=score,
        #     total=len(questions)
# )        
        return redirect(url_for('user.user_dashboard'))

