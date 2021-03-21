import os
import webbrowser

from flask import Flask, render_template, request, g, jsonify, url_for, session, redirect

from threading import Timer
from forms.project_form import ProjectForm
from models.project import Project, db_session
from models.models import mongoDB, create_app
from models import settings
import bcrypt

app = Flask(__name__)
app.secret_key = "mysecret"
app.debug = os.environ.get('DEBUG', True)


@app.route('/')
def index():
    if 'email' in session:
        return 'You are logged in as ' + session['email']

    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    users = settings.db.users
    login_user = users.find_one({'email': request.form['email']})

    if login_user:
        if bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['password']) == login_user['password']:
            session['email'] = request.form['email']
            return redirect(url_for('index'))

    return 'Invalid username or password'

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = settings.db.users
        existing_user = users.find_one({'name': request.form['email']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            users.insert_one({'name': request.form['name'], 'surname': request.form['surname'], 'email': request.form['email'], 'password': hashpass})
            session['email'] =  request.form['email']
            return redirect(url_for('index'))

        return 'That username already exists!'

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


# https://www.geeksforgeeks.org/make-python-api-to-access-mongo-atlas-database/
@app.route('/test')
def test():
    # collections (aka tables) can be created on the third argument eg. tasks_table
    add_task = settings.db.task_table.insert({"Task": "Add data", 'assigned': 'Patryk'})
    return render_template('/test.html', addtask=add_task)


@app.route('/insert-one/<name>/<id>/', methods=['GET'])
def insert_one(name, id_):
    query_object = {
        'Name': name,
        'ID': id_
    }
    query = settings.db.task_table.insert_one(query_object)
    return "Query inserted...!!!"


# To find all the entries/documents in a table/collection,
# find() function is used. If you want to find all the documents
# that matches a certain query, you can pass a queryObject as an
# argument.
@app.route('/find/', methods=['GET'])
def find_all():
    query = settings.db.task_table.find()
    output = {}
    i = 0
    for x in query:
        output[i] = x
        output[i].pop('_id')
        i += 1
    return jsonify(output)


# To update a document in a collection, update_one()
# function is used. The queryObject to find the document is passed as
# the first argument, the corresponding updateObject is passed as the
# second argument under the '$set' index.
@app.route('/update/<key>/<value>/<element>/<updateValue>/', methods=['GET'])
def update(key, value, element, update_value):
    query_object = {key: value}
    update_object = {element: update_value}
    query = settings.db.task_table.update_one(query_object, {'$set': update_object})
    if query.acknowledged:
        return "Update Successful"
    else:
        return "Update Unsuccessful"


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


def main():
    # The reloader has not yet run - open the browser
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        webbrowser.open_new('http://127.0.0.1:5000/')

    # Otherwise, continue as normal
    app.secret_key = os.urandom(24)  # Keeps the client-side sessions secure by generating random key (output 24 bytes)
    app.run(host="127.0.0.1", port=5000)


if __name__ == "__main__":
    main()
