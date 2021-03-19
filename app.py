import os
import webbrowser

from flask import Flask, render_template, request, g, Blueprint
from threading import Timer
from forms.project_form import ProjectForm
from models.project import Project, db_session
from models.models import mongoDB
app = Flask(__name__)


@app.route('/')
def login():
    return render_template('login.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/password')
def forgot_password():
    return render_template('password.html')


@app.route('/logout')
def logout():
    return render_template('dashboard/index.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard/index.html')  # https://startbootstrap.com/template/sb-admin


# https://github.com/wtforms/wtforms-sqlalchemy/blob/master/examples/flask/basic.py
# 53:00
@app.route('/dashboard/projects/new', methods=['GET', 'POST'])
def new_project():
    project = Project()
    success = False
    form = ProjectForm(request.form, obj=project)

    if request.method == 'GET':
        form = ProjectForm(obj=project)
        return render_template('dashboard/projects-page/new-project.html', form=form, success=success)

    if form.validate():
        form.populate_obj(project)
        g.db.add(project)
        g.db.commit()
        success = True


@app.route("/test")
def test():
    user_collection = mongoDB.db.users
    user_collection.insert({'name': 'peter', 'password': '12345'})
    user_collection.insert({'name': 'richard', 'password': '12345'})
    return '<H1>Connected to the data base!</H1>'


# https://flask-restless.readthedocs.io/en/latest/processors.html
@app.before_request
def before_req():
    g.db = db_session()


@app.after_request
def after_req(resp):
    try:
        g.db.close()
    except Exception:
        pass
    return resp


# Open the browser automatically to the specific local port
def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')


if __name__ == "__main__":
    # db.create_all()

    app.secret_key = os.urandom(24)  # Keeps the client-side sessions secure by generating random key (output 24 bytes)
    Timer(1, open_browser).start()  # Open the browser automatically in 1sec
    app.run()
