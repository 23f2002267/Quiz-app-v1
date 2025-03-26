from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user, AnonymousUserMixin
from models import Subject, Chapter, Quiz, Question, db
from datetime import datetime
from sqlalchemy import text

admin = Blueprint('admin', __name__)

def list_to_text(obj):
    x = str()
    for elem in obj:
        x += str(elem + ",")
    return x[:-1]
def op_check(csv, v):
    lis = csv.split(',')
    for i in lis :
        if v == i :
            return True
    return False

@admin.before_request
@login_required
def check_admin():
    if not current_user.is_admin:
        flash('Access denied. tag 1')
        return redirect(url_for('auth.login'))

@admin.route('/dashboard')
@login_required
def dashboard():
    subjects = Subject.query.all()
    return render_template('admin/dashboard.html', subjects=subjects)

@admin.route('/<int:id>/chapters', methods=['GET','POST'])
@login_required
def chapter(id):
    chapters = Chapter.query.filter_by(subject_id=id).all()
    return render_template('admin/chapter.html', chapters=chapters, subject_id=id)

@admin.route('/<int:su_id>/<int:ch_id>/quizes', methods=['GET','POST'])
@login_required
def quiz(su_id,ch_id):
    q = Quiz.query.filter_by(chapter_id=ch_id).all()
    return render_template('admin/quiz.html', elems=q, subject_id=su_id, id=ch_id)

@admin.route('/<int:su_id>/<int:ch_id>/<int:quiz_id>/<string:q_ids>/questions', methods=['GET','POST'])
@login_required
def quesiton(su_id,ch_id,quiz_id,q_ids):
    lis = q_ids.split(',')
    questions = db.session.query(Question).filter(Question.id.in_(lis)).all()
    print(questions)
    return render_template('admin/questions.html', questions=questions, ques_ids=q_ids,
                           quiz_id=quiz_id, subject_id=su_id, chapter_id=ch_id)

@admin.route('/subject/create', methods=['GET','POST'])
@login_required
def create_subject():
    flag=False
    if request.method == 'POST' :
        name = request.form['name']
        description = request.form['description']
        new_subject = Subject(name=name, description=description)
        try:
            db.session.add(new_subject)
            db.session.commit()
            flag = True
        except:
            db.session.rollback()
            flash('Already Exsisting subject')
            flag = False
    if flag==True:
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/update.html',func="Add",object="subject")

@admin.route('/<int:su_id>/create_chapter', methods=['GET','POST'])
@login_required
def create_chapter(su_id):
    flag = False
    if request.method == 'POST' :
        name = request.form['name']
        description = request.form['description']
        new_chapter = Chapter(subject_id=su_id, name=name ,description=description)
        try:
            db.session.add(new_chapter)
            db.session.commit()
            flag = True
        except:
            db.session.rollback()
            flash('Already Exsisting Chapter')
            flag = False
    if flag==True:
        return redirect(f'/{su_id}/chapters')
    subject=Subject.query.filter_by(id=su_id).first()
    return render_template('admin/update.html',id=f'to {subject.name}',func="Add",object="chapter")

@admin.route('/<int:su_id>/<int:ch_id>/create_quizes', methods=['GET','POST'])
@login_required
def create_quiz(su_id,ch_id):
    flag = False
    if request.method == 'POST' :
        time_duration_str = request.form['time_duration']
        time_duration = datetime.strptime(time_duration_str, "%H:%M:%S").time()
        selected_questions = request.form.getlist('questions')
        selected_questions = list_to_text(selected_questions)
        remarks = request.form['remarks']
        if selected_questions:
            new_quiz = Quiz(chapter_id=ch_id, time_duration=time_duration , 
                            questions=selected_questions, remarks=remarks)
            try:
                db.session.add(new_quiz)
                db.session.commit()
                flag = True
            except:
                db.session.rollback()
                flash('Already Exsisting quiz')
                flag = False
        else:
            flash('Atleast 1 question is required to make new quiz')
    if flag==True:
        return redirect(f'/{su_id}/{ch_id}/quizes')
    subject=Subject.query.filter_by(id=su_id).first()
    questions = Question.query.filter_by(chapter_id=ch_id).all()
    return render_template('admin/add_quiz.html',func="Add",subject_id=su_id, chapter_id=ch_id,
                            object="Quiz", subject=subject,questions=questions)

@admin.route('/<int:su_id>/<int:ch_id>/create_question', methods=['GET','POST'])
@login_required
def create_question(su_id,ch_id):
    flag = False
    if request.method == 'POST' :
        q_statement = request.form['q_statement']
        options = request.form['options'] #entered as csv in single text box
        correct_option = request.form['correct_option']
        if op_check(options, correct_option):
            try:
                new_question = Question(chapter_id=ch_id, q_statement=q_statement , 
                                options=options, correct_option=correct_option)
                db.session.add(new_question)
                db.session.commit()
                flag = True
            except:
                db.session.rollback()
                flash('Already Exsisting question')
                flag = False
        else:
            flash('Improper options/(correct option) entry')
    if flag==True:
        return redirect(f'/{su_id}/{ch_id}/create_quizes')
    subject=Subject.query.filter_by(id=su_id).first()
    return render_template('admin/add_question.html',func="Add",subject_id=su_id, chapter_id=ch_id,
                            subject=subject, quest="quest")

@admin.route('/<int:su_id>/delete', methods=['GET','POST'])
@login_required
def delete_subject(su_id):
    subs = Subject.query.filter_by(id=su_id).first()
    if subs:
        db.session.delete(subs)
        db.session.commit()
    return redirect(url_for('admin.dashboard'))

@admin.route('/<int:su_id>/<int:ch_id>/delete', methods=['GET','POST'])
@login_required
def delete_chapter(su_id,ch_id):
    subs = Chapter.query.filter_by(id=ch_id).first()
    if subs:
        db.session.delete(subs)
        db.session.commit()
    return redirect(f'/{su_id}/chapters')

@admin.route('/<int:su_id>/<int:ch_id>/<int:q_id>/delete_quiz', methods=['GET','POST'])
@login_required
def delete_quiz(su_id,ch_id,q_id):
    subs = Quiz.query.filter_by(id=q_id).first()
    if subs:
        db.session.delete(subs)
        db.session.commit()
    return redirect(f'/{su_id}/{ch_id}/quizes')

@admin.route('/<int:su_id>/<int:ch_id>/<int:ques_id>/del_ques', methods=['GET','POST'])
@login_required
def delete_question(su_id, ch_id, ques_id):
    subs = Question.query.filter_by(id=ques_id).first()
    if subs:
        db.session.delete(subs)
        db.session.commit()
    return redirect(request.referrer)

@admin.route('/<int:su_id>/<int:ch_id>/<int:quiz_id>/<int:ques_id>/del_ques', methods=['GET','POST'])
@login_required
def delete_quiz_question(su_id, ch_id, quiz_id, ques_id):
    subs = Quiz.query.filter_by(id=quiz_id).first()
    if subs :
        lis = (subs.questions).split(',')
        lis.remove(str(ques_id))
        Lis = list_to_text(lis)
        subs.questions = Lis
        db.session.commit()
    return redirect(f'/{su_id}/{ch_id}/{quiz_id}/{Lis}/questions')

@admin.route('/<int:su_id>/update', methods=['GET','POST'])
@login_required
def update_subject(su_id):
    flag = False
    subj = db.session.query(Subject).filter_by(id=su_id)
    sub = subj.first()
    if request.method == 'POST' :
        subj.update({"name":request.form['name'],"description":request.form['description']})
        try:
            db.session.commit()
            flag = True
        except:
            db.session.rollback()
            flash('Already Exsisting Subject')
            flag = False
    if flag==True:
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/update.html',id=su_id, object="Subject id", func="Update",
                           oname=sub.name, odescr=sub.description)

@admin.route('/<int:su_id>/<int:ch_id>/update', methods=['GET','POST'])
@login_required
def update_chapter(su_id,ch_id):
    flag = False
    chapt = db.session.query(Chapter).filter_by(id=ch_id)
    chap = chapt.first()
    if request.method == 'POST' :
        chapt.update({"name":request.form['name'],"description":request.form['description']})
        try:
            db.session.commit()
            flag = True
        except:
            db.session.rollback()
            flash('Already Exsisting Chapter')
            flag = False
    if flag==True:
        return redirect(f'/{su_id}/chapters')
    return render_template('admin/update.html',id=f'of Subject ID :{ch_id}',
                           oname=chap.name, odescr=chap.description, object="Chapter", func="Update")

@admin.route('/<int:su_id>/<int:ch_id>/<int:quiz_id>/update', methods=['GET','POST'])
@login_required
def update_quiz(su_id,ch_id,quiz_id):
    flag = False
    quizt = db.session.query(Quiz).filter_by(id=quiz_id)
    quiz = quizt.first()
    if request.method == 'POST' :
        time_duration_str = request.form['time_duration']
        time_duration = datetime.strptime(time_duration_str, "%H:%M:%S").time()
        selected_questions = request.form.getlist('questions')
        selected_questions = list_to_text(selected_questions)
        remarks = request.form['remarks']
        if selected_questions:
            quizt.update({"time_duration":time_duration,"questions":selected_questions,"remarks":remarks})
            try:
                db.session.commit()
                flag = True
            except:
                db.session.rollback()
                flash('Already Exsisting quiz')
                flag = False
        else:
            flash('Atleast 1 question is required to make new quiz')
    if flag==True:
        return redirect(f'/{su_id}/{ch_id}/quizes')
    subject=Subject.query.filter_by(id=su_id).first()
    questions = Question.query.filter_by(chapter_id=ch_id).all()
    return render_template('admin/add_quiz.html',func="Update", subject_id=su_id, chapter_id=ch_id, 
                           object="Quiz ID :", id=quiz_id, subject=subject, questions=questions,
                           time=quiz.time_duration, remarks=quiz.remarks, ques=(quiz.questions).split(','))

@admin.route('/<int:su_id>/<int:ch_id>/<int:quiz_id>/<string:ques_ids>/<int:ques_id>/update', methods=['GET','POST'])
@login_required
def update_question(su_id,ch_id,quiz_id,ques_ids,ques_id):
    flag = False
    quest = db.session.query(Question).filter_by(id=ques_id)
    ques = quest.first()
    if request.method == 'POST' :
        q_statement = request.form['q_statement']
        options = request.form['options'] #entered as csv in single text box
        correct_option = request.form['correct_option']
        if op_check(options, correct_option):
            try:
                quest.update({"q_statement":q_statement,"options":options,"correct_option":correct_option})
                db.session.commit()
                flag = True
            except:
                db.session.rollback()
                flash('No changes made')
                flag = False
        else:
            flash('Improper options/(correct option) entry')
    if flag==True:
        return redirect(f'/{su_id}/{ch_id}/{quiz_id}/{ques_ids}/questions')
    return render_template('admin/add_question.html',func="Update", subject_id=su_id, chapter_id=ch_id, 
                           object="Quiz ID :", id=quiz_id,
                           quest=ques)

@admin.route('/search', methods=['GET','POST'])
@login_required
def search():
    if request.method == 'POST':
        fts_query = f'"{request.form['q']}"*'
        sql = text("""
            SELECT fts_subject.rowid, fts_subject.name,
                   snippet(fts_subject, 0, '<mark>', '</mark>', '...', 64) as snippet
            FROM fts_subject
            WHERE fts_subject.name MATCH :query
            ORDER BY bm25(fts_subject)
        """)
        results = db.session.execute(sql, {'query': fts_query}).fetchall()
        flash(f"{results}")
        return render_template('admin/dashboard.html', subjects=results)
    return redirect(url_for('admin.dashboard'))