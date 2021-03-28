import os
import webbrowser
import bcrypt

from flask import Flask, render_template, request, url_for, session, redirect
from mongodb_models import settings_mongo
from bson import ObjectId

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
    return redirect(url_for('welcome_login'))


# -----> END OF OUTSIDE DASHBOARD PAGES AND FUNCTIONS <-----


# -----> DASHBOARD PAGES <-----

@app.route('/dashboard')
def dashboard():
    projects = mongo.db.project_table.find({}, {"title": 1, "description": 1, "date": 1})
    return render_template('dashboard/home.html', projects=projects)  # https://startbootstrap.com/template/sb-admin


@app.route('/dashboard/projects/new', methods=['POST', 'GET'])
def create_new_project():
    if request.method == 'POST':

        # https://docs.mongodb.com/manual/reference/database-references/
        project_id = ObjectId()  # setup the project's id

        project_collection = mongo.db.project_table  # project collection
        task_collection = mongo.db.task_table  # task collection
        existing_project = project_collection.find_one({'title': request.form['project_title']})

        if existing_project is None:
            project_collection.insert_one({"_id": project_id,
                                           'title': request.form['project_title'],
                                           'description': request.form['project_description'],
                                           'date': request.form['project_date']})
            task_collection.insert_one({'title': request.form['task_title'],
                                        'description': request.form['task_description'],
                                        'date': request.form['task_date'],
                                        'project_id': project_id})

            # As soon as we made the changes we want to redirect (else the url link will not change)
            return redirect(url_for('table'))

        return 'That project already exists!'

    # This is when we press the view option for first time
    return render_template('dashboard/projects/new.html')


# View a Project
@app.route('/dashboard/projects/view/<ObjectId:project_id>', methods=['GET'])
def view_project(project_id):
    # Check if the project exists in the db table based on the id
    project = mongo.db.project_table.find_one_or_404({'_id': project_id})
    task = mongo.db.task_table.find_one_or_404({'project_id': project_id})

    return render_template('dashboard/projects/view.html', project=project, task=task)


# Update Project details
@app.route('/dashboard/projects/update/<ObjectId:project_id>', methods=['POST'])
def update_project(project_id):
    project_collection = mongo.db.project_table
    project_collection.find_one_and_update({"_id": project_id},
                                           {"$set": {
                                               "title": request.form.get('title'),
                                               "description": request.form.get('description'),
                                               "date": request.form.get('date')
                                           }
                                           })
    return redirect(url_for('table', project_id=project_id))


# Delete a project
@app.route('/dashboard/projects/delete/<ObjectId:project_id>', methods=['POST'])
def delete_project(project_id):
    # Delete the project and the tasks from the database
    mongo.db.project_table.remove({'_id': project_id})
    mongo.db.task_table.remove({'project_id': project_id})
    return redirect(url_for('table'))


# Update Project details
@app.route('/dashboard/projects/update1/<ObjectId:task_id>', methods=['POST'])
def update_task(task_id):
    task_collection = mongo.db.task_table
    task_collection.find_one_and_update({"_id": task_id},
                                        {"$set": {
                                            "title": request.form.get('title'),
                                            "description": request.form.get('description'),
                                            "date": request.form.get('date')
                                        }
                                        })
    return redirect(url_for('table'))


# Delete a task
@app.route('/dashboard/projects/delete1/<ObjectId:task_id>', methods=['POST'])
def clear_task_fields(task_id):
    task_collection = mongo.db.task_table
    task_collection.find_one_and_update({"_id": task_id},
                                        {"$set": {
                                            "title": "",
                                            "description": "",
                                            "date": ""
                                        }
                                        })
    return redirect(url_for('table'))


# -----> END OF DASHBOARD PAGES AND FUNCTIONS <-----


# -----> TABLE TAB PAGES AND FUNCTIONS <-----

# https://stackoverflow.com/questions/53425222/python-flask-i-want-to-display-the-data-that-present-in-mongodb-on-a-html-page
@app.route('/dashboard/table')
def table():
    projects = mongo.db.project_table.find({}, {"title": 1, "description": 1, "date": 1})
    return render_template('dashboard/table.html', projects=projects)


# -----> END OF TABLE TAP PAGES FUNCTIONS <-----


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
