# -*- encoding:utf-8 -*-
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask.ext.login import login_required, login_user, logout_user, current_user
from qual import app, db, loginmanager
from qual.forms import LoginForm, RegisterForm, MypageForm
from qual.models import User, Problem, Category, ProblemSet, ProblemSetScore, solves

frontend = Blueprint('frontend', __name__)

loginmanager.login_view = 'frontend.login'
loginmanager.login_message_category = 'warning'

def fetch_problems(problems):
    score = 0
    for problem in problems:
        problem.solved = problem in current_user.solves
        if problem.solved:
            score += problem.score
    return score, problems

@loginmanager.user_loader
def load_user(userid):
    return User.query.get(userid)

@frontend.route('/')
def index():
    return render_template('index.html')

@frontend.route('/prob')
@login_required
def problem_index():
    score, problems = fetch_problems(Problem.query.all())
    return render_template('problem_list.html', problems=problems, score=score)

@frontend.route('/prob/<int:problem_id>')
@login_required
def problem(problem_id):
    problem = Problem.query.get_or_404(problem_id)
    return render_template('problem.html', problem=problem, solved=current_user.solved(problem))

@frontend.route('/category')
@login_required
def category_index():
    return render_template('category_list.html', categories=Category.query.all())

@frontend.route('/category/<int:category_id>')
@login_required
def problem_by_category(category_id):
    category = Category.query.get_or_404(category_id)
    score, problems = fetch_problems(category.problems.all())
    return render_template('problem_list.html', problems=problems, title=category.name, score=score)

@frontend.route('/set')
@login_required
def problemset_index():
    return render_template('problemset_list.html', problemsets=ProblemSet.query.all())

@frontend.route('/set/<int:problemset_id>')
@login_required
def problem_by_problemset(problemset_id):
    problemset = ProblemSet.query.get_or_404(problemset_id)
    score, problems = fetch_problems(problemset.problems.all())
    return render_template('problem_list.html', problems=problems, title=problemset.title, score=score)

@frontend.route('/rank')
def rank():
    return render_template('rank.html', users=User.query.order_by(User.score.desc(), User.updated_at.asc()).all())

@frontend.route('/set/<int:problemset_id>/rank')
@login_required
def rank_by_problemset(problemset_id):
    problemset = ProblemSet.query.get_or_404(problemset_id)
    return render_template('rank.html', users=ProblemSetScore.query.filter_by(problemset_id=problemset.id).order_by(ProblemSetScore.score.desc(), ProblemSetScore.updated_at.asc()).all(), title=problemset.title)

@frontend.route('/auth/<int:problem_id>', methods=['POST'])
@login_required
def auth(problem_id):
    problem = Problem.query.get_or_404(problem_id)
    flag = request.form.get('flag')
    if problem.check_flag(flag):
        if current_user.solved(problem):
            flash('Correct, but you already solved this problem.', 'success')
            return redirect(url_for('frontend.problem', problem_id=problem.id))
        else:
            current_user.solve(problem)
            db.session.commit()
            flash('Correct, Congratulations!', 'success')
            return redirect(url_for('frontend.problem', problem_id=problem.id))
    else:
        flash('Wrong, try again.', 'danger')
        return redirect(url_for('frontend.problem', problem_id=problem.id))

@frontend.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    next = request.args.get('next') or url_for('frontend.index')
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(next)
        else:
            flash('Login failed', 'danger')
            return render_template('login.html', form=form, next=next)
    return render_template('login.html', form=form, next=next)

@frontend.route('/logout')
def logout():
    next = request.args.get('next') or url_for('frontend.index')
    logout_user()
    return redirect(next)

@frontend.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    next = request.args.get('next') or url_for('frontend.index')
    if request.method == 'POST' and form.validate():
        if form.registerkey.data != app.config['REGISTER_KEY']:
            flash('Wrong register key!', 'danger')
            return render_template('register.html', form=form, next=next)
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            flash('Already existing username!', 'danger')
            return render_template('register.html', form=form, next=next)
        user = User(form.username.data, form.realname.data, form.nickname.data, form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(next)
    return render_template('register.html', form=form, next=next)

@frontend.route('/mypage', methods=['GET', 'POST'])
@login_required
def mypage():
    form = MypageForm(request.form)
    if request.method == 'GET':
        form.realname.data = current_user.realname
        form.nickname.data = current_user.nickname
    next = request.args.get('next') or url_for('frontend.index')
    if request.method == 'POST' and form.validate():
        current_user.realname = form.realname.data
        current_user.nickname = form.nickname.data
        current_user.set_password(form.password.data)
        db.session.commit()
        return redirect(next)
    return render_template('mypage.html', form=form, next=next)
