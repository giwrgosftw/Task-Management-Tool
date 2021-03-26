import os
import webbrowser
from flask import Flask, render_template, request, jsonify, url_for, session, redirect
from mongodb_models import settings_mongo
import bcrypt

app = Flask(__name__)
app.secret_key = "my_secret_key"
mongo = settings_mongo.config_mongo_db_with_app(app)


# # -----> OUTSIDE DASHBOARD PAGES & FUNCTIONS <-----

@app.route('/')
def welcome_login():
    return render_template('login.html')  # welcome and login page are one page (need to add new background)


# Check if the given credentials are successful
@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users  # connect to the db from the settings module and then rendering the users table
    login_user = users.find_one({'email': request.form['email']})  # true/false if the e-mail exists

    # if e-mail exist, check if the password is correct, if correct, navigate me to the dashboard page
    if login_user:
        if bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['password']) == login_user['password']:
            session['email'] = request.form['email']
            return redirect(url_for('dashboard'))

    return 'Invalid username or password'


# Registration process (+ checking if the account already exists)
# Source: https://www.youtube.com/watch?v=vVx1737auSE&list=PLXmMXHVSvS-Db9KK1LA7lifcyZm4c-rwj&index=5
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name': request.form['email']})

        if existing_user is None:
            hash_pass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            users.insert_one(
                {'name': request.form['name'], 'surname': request.form['surname'], 'email': request.form['email'],
                 'password': hash_pass})
            session['email'] = request.form['email']
            return redirect(url_for('welcome_login'))  # account created successfully navigate me to the login page

        return 'That username already exists!'

    return render_template('register.html')


@app.route('/password')
def forgot_password():
    return render_template('password.html')


# Logout means: send me back to the login page (for now)
@app.route('/logout')
def logout():
    return render_template('login.html')


# -----> END OF OUTSIDE DASHBOARD PAGES AND FUNCTIONS <-----


# -----> DASHBOARD PAGES <-----

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard/home.html')  # https://startbootstrap.com/template/sb-admin


# https://github.com/wtforms/wtforms-sqlalchemy/blob/master/examples/flask/basic.py
# end points for registered users
@app.route('/dashboard/projects/new', methods=['POST', 'GET'])
def create_new_project():
    if request.method == 'POST':
        project_collection = mongo.db.task_table
        existing_project = project_collection.find_one({'title': request.form['title']})

        if existing_project is None:
            project_collection.insert_one({'title': request.form['title'], 'description': request.form['description'],
                                           'date': request.form['date']})
            return redirect(url_for('create_new_project'))

        return 'That project already exists!'

    return render_template('dashboard/projects/new.html')


@app.route('/dashboard/projects/view/<ObjectId:task_id>', methods=['GET'])
def view_project(task_id):
    task = mongo.db.task_table.find_one_or_404(task_id)
    return render_template('dashboard/projects/view.html', task=task)


@app.route('/dashboard/projects/edit/<ObjectId:task_id>', methods=['POST', 'GET'])
def update_project(task_id):
    task = mongo.db.tasks.find_one({"_id": task_id})
    return render_template('dashboard/projects/edit.html', task=task)


@app.route('/dashboard/projects/search', methods=['GET'])
def search_project():
    search_query = mongo.db.task_table.find()
    output = {}
    i = 0
    for x in search_query:
        output[i] = x
        output[i].pop('_id')
        i += 1
    return jsonify(output)


# -----> END OF DASHBOARD PAGES AND FUNCTIONS <-----


# -----> DATABASE FUNCTIONS <-----

@app.route('/insert-one/<name>/<id>/', methods=['GET'])
def insert_one(name, id_):
    query_object = {
        'Name': name,
        'ID': id_
    }
    mongo.db.task_table.insert_one(query_object)
    return "Query inserted...!!!"


# To find all the entries/documents in a table/collection,
# find() function is used. If you want to find all the documents
# that matches a certain query, you can pass a queryObject as an
# argument.
@app.route('/find/', methods=['GET'])
def find_all():
    query = mongo.db.task_table.find()
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
    query = mongo.db.task_table.update_one(query_object, {'$set': update_object})
    if query.acknowledged:
        return "Update Successful"
    else:
        return "Update Unsuccessful"


# -----> END OF DATABASE FUNCTIONS <-----


# https://stackoverflow.com/a/63216793
def main():
    # The reloader has not yet run - open the browser
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        webbrowser.open_new('http://127.0.0.1:5000/')

    # Otherwise, continue as normal
    app.secret_key = os.urandom(24)  # Keeps the client-side sessions secure by generating random key (output 24 bytes)
    app.run(host="127.0.0.1", port=5000)


if __name__ == "__main__":
    main()
