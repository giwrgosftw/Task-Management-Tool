import os
import webbrowser
import bcrypt

from flask import Flask, render_template, request, url_for, session, redirect, flash
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
            session['active_user'] = request.form['email']
            return redirect(url_for('dashboard'))

    return 'Invalid username or password'


# Registration process (+ checking if the account already exists)
# Source: https://www.youtube.com/watch?v=vVx1737auSE&list=PLXmMXHVSvS-Db9KK1LA7lifcyZm4c-rwj&index=5
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'email': request.form['email']})

        if existing_user is None:
            hash_pass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            users.insert_one(
                {'fullname': request.form['fullname'], 'email': request.form['email'],
                 'password': hash_pass})
            session['active_session'] = request.form['email']
            return redirect(url_for('welcome_login'))  # account created successfully navigate me to the login page

        return 'That username already exists!'

    return render_template('register.html')


@app.route('/password')
def forgot_password():
    return render_template('password.html')


# Logout means: send me back to the login page (for now)
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# -----> END OF OUTSIDE DASHBOARD PAGES AND FUNCTIONS <-----


# -----> DASHBOARD PAGES <-----

@app.route('/dashboard')
def dashboard():
    if "active_user" in session:  # checking if active user exist in the session (cookies)
        user = session["active_user"]
        print(user)  # you can use this variable to check the username who is loged in during a session (remove the comment)
        projects = mongo.db.project_table.find({}, {"title": 1, "description": 1, "date": 1})
        return render_template('dashboard/home.html',projects=projects)  # https://startbootstrap.com/template/sb-admin
    else:
        session.clear()
        flash(u'You need to login', 'error')
        return render_template('login.html')


# -----> END DASHBOARD PAGES <-----

# -----> PROJECTS PAGES AND FUNCTIONS <-----
@app.route('/dashboard/projects/new_project', methods=['POST', 'GET'])
def create_new_project():
    if request.method == 'POST':

        # https://docs.mongodb.com/manual/reference/database-references/
        project_id = ObjectId()  # setup the project's id

        project_collection = mongo.db.project_table  # project collection
        existing_project = project_collection.find_one({'title': request.form['project_title']})

        if existing_project is None:
            project_collection.insert_one({"_id": project_id,
                                           'title': request.form['project_title'],
                                           'description': request.form['project_description'],
                                           'date': request.form['project_date']})
            # As soon as the project is created, the next step will be to add a new empty task to avoid the 404 issue
            # this will be deleted as soon as the user will add a new task
            insert_new_empty_task(project_id)

            return redirect(url_for('view_project', project_id=project_id))

        return 'That project already exists!'

    return render_template('dashboard/projects/new.html')


# View a Project
@app.route('/dashboard/projects/<ObjectId:project_id>', methods=['GET'])
def view_project(project_id):
    # Check if the project exists in the db table based on the id
    project = mongo.db.project_table.find_one_or_404({'_id': project_id})
    task = mongo.db.task_table.find_one_or_404({'project_id': project_id})

    tasks = mongo.db.task_table.find({}, {"title": 1, "description": 1, "date": 1, "assign_to": 1, "project_id": 1})
    users = mongo.db.users.find({}, {"fullname": 1})

    return render_template('dashboard/projects/view.html', project=project, task=task, tasks=tasks, users=users)


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

    return redirect(url_for('view_project', project_id=project_id))


# Delete a project
@app.route('/dashboard/projects/delete/<ObjectId:project_id>', methods=['POST'])
def delete_project(project_id):
    # Delete the project and the tasks from the database
    mongo.db.project_table.remove({'_id': project_id})
    mongo.db.task_table.remove({'project_id': project_id})
    return redirect(url_for('table'))


# Add an empty task in the project's table
@app.route('/dashboard/projects/<ObjectId:project_id>/new_empty_task', methods=['POST'])
def insert_new_empty_task(project_id):
    task_collection = mongo.db.task_table
    task_collection.insert_one(
        {
            "title": "",
            "description": "",
            "date": "",
            "project_id": project_id,
            "assign_to": ""
        }
    )

    return redirect(url_for('view_project', project_id=project_id))


# -----> END OF PROJECTS PAGES AND FUNCTIONS<-----

# Add new task in the project's table
@app.route('/dashboard/projects/<ObjectId:project_id>/new_task', methods=['POST', 'GET'])
def create_new_task(project_id):
    project = mongo.db.project_table.find_one_or_404({'_id': project_id})
    users = mongo.db.users.find({}, {"fullname": 1})
    if request.method == 'POST':
        task_id = ObjectId()
        task_collection = mongo.db.task_table
        task_collection.insert_one(
            {
                "_id": task_id,
                'title': request.form['task_title'],
                'description': request.form['task_description'],
                'date': request.form['task_date'],
                "assign_to": request.form['task_assign_to'],
                "project_id": project_id,
            }
        )
        task_collection.remove({'project_id': project_id, 'title': ""})  # delete now the auto-created empty task of this project

        return redirect(url_for('view_project', project_id=project_id, task_id=task_id))

    return render_template('dashboard/tasks/new.html', project=project, users=users)


# View a project's task
@app.route('/dashboard/projects/<ObjectId:project_id>/<ObjectId:task_id>', methods=['GET'])
def view_task(project_id, task_id):
    # Check if the project and task exists in the db table based on the id
    project = mongo.db.project_table.find_one_or_404({'_id': project_id})
    task = mongo.db.task_table.find_one_or_404({'_id': task_id})

    tasks = mongo.db.task_table.find({}, {"title": 1, "description": 1, "date": 1, "assign_to": 1})
    users = mongo.db.users.find({}, {"fullname": 1})

    return render_template('dashboard/tasks/view.html', project=project, task=task, tasks=tasks, users=users)


# -----> TASKS PAGES AND FUNCTIONS <-----
# HOW IT WORKS:
# <ObjectId:project_id> and <ObjectId:task_id> = project_id, task_id of the update_task(), respectively
# Then, using the redirect(url_for()) we are taking the project and task id values which are coming from the html file
# Thus, (from the app.py) project_id=project_id and task_id=task_id <--> project_id=project._id and task_id=task._id (from the html file)

# Update the Project's task details
@app.route('/dashboard/projects/<ObjectId:project_id>/<ObjectId:task_id>/update', methods=['POST'])
def update_task(project_id, task_id):
    task_collection = mongo.db.task_table
    task_collection.find_one_and_update({"_id": task_id},
                                        {"$set": {
                                            "title": request.form.get('title'),
                                            "description": request.form.get('description'),
                                            "date": request.form.get('date'),
                                            "assign_to": request.form.get('assign_to')
                                        }
                                        })

    return redirect(url_for('view_project', project_id=project_id))


# Delete a task
@app.route('/dashboard/projects/<ObjectId:project_id>/delete/<ObjectId:task_id>', methods=['POST'])
def delete_task(project_id, task_id):
    task_collection = mongo.db.task_table
    cur = mongo.db.task_table.find()
    results = list(cur)

    # Checking the cursor has at least 1 element
    # If there is only one task in the table, do not remove it because there will be an issue, just clear it ($unset could be an option)
    # else remove completely the requested task
    if len(results) == 1:
        task_collection.find_one_and_update({"_id": task_id},
                                            {"$set": {
                                                "title": "",
                                                "description": "",
                                                "date": "",
                                                "assign_to": ""
                                            }
                                            })
    else:
        task_collection.remove({"_id": task_id})

    return redirect(url_for('view_project', project_id=project_id, task_id=task_id, ))


# -----> TASKS PAGES AND FUNCTIONS <-----


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
