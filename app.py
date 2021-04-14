import os
import webbrowser
import bcrypt
import gridfs
from datetime import timedelta
import re
from flask import Flask, render_template, request, url_for, session, redirect, flash
from mongodb_models import settings_mongo
from bson import ObjectId

import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

app = Flask(__name__)
mongo = settings_mongo.config_mongo_db_with_app(app)
fs = gridfs.GridFS(mongo.db)  # create GridFS instance


# # -----> Before request - Session will last 10 min before user is logged out <-----
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=10)


# # -----> OUTSIDE DASHBOARD PAGES & FUNCTIONS <-----


@app.route('/')
def welcome_login():
    return render_template('login.html')  # welcome and login page are one page (need to add new background)


# Check if the given credentials are successful
@app.route('/login', methods=['POST'])
def login():
    try:
        users = mongo.db.user_table  # connect to the db from the settings module and then rendering the users table
        login_user = users.find_one({'email': request.form['email']})  # true/false if the e-mail exists

        # if e-mail exist, check if the password is correct, if correct, navigate me to the dashboard page
        if login_user:
            if bcrypt.hashpw(request.form['password'].encode('utf-8'),
                             login_user['password']) != login_user['password']:
                error = 'Invalid credentials'
            else:
                session['active_user'] = request.form['email']
                print("You logged in as: " + session['active_user'])
                return redirect(url_for('dashboard', user_email=session['active_user']))
        else:
            error = 'Account not found, please create one'
        return render_template('login.html', error=error)
    except Exception as e:
        print("There was an error with the login process: %s" % e)


# Registration process (+ checking if the account already exists)
# Source: https://www.youtube.com/watch?v=vVx1737auSE&list=PLXmMXHVSvS-Db9KK1LA7lifcyZm4c-rwj&index=5
@app.route('/register', methods=['POST', 'GET'])
def register():
    try:
        error = None
        if request.method == 'POST':
            users = mongo.db.user_table
            existing_user = users.find_one({'email': request.form['email']})

            # If there is no other account with the given e-mail
            if existing_user is None:

                # If the input and confirmation password are the same
                if request.form['password'] == request.form['password2']:
                    hash_pass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
                    users.insert_one(
                        {'fullname': request.form['fullname'],
                         'email': request.form['email'],
                         'password': hash_pass})
                    return render_template(
                        'dashboard/alerts/alertRegisterUser.html')  # account created successfully navigate me to the login page
                else:
                    error = 'These passwords are not identical!'
            else:
                error = 'An account already exists with this e-mail address!'
        return render_template('register.html', error=error)
    except Exception as e:
        print("There was an error with the register process: %s" % e)


@app.route('/password')
def forgot_password():
    return render_template('password.html')


# Logout means: send me back to the login page (for now)
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/dashboard/<user_email>/view_profile', methods=['POST', 'GET'])
def view_profile(user_email):
    user_fullname = get_user_fullname(user_email)
    user_password = get_user_password(user_email)
    return render_template('dashboard/users/view.html',
                           user_email=user_email,
                           user_fullname=user_fullname,
                           user_password=user_password)


@app.route('/dashboard/<user_email>/update_profile', methods=['POST'])
def update_profile(user_email):
    try:

        if "active_user" in session:  # checking if active user exist in the session (cookies)

            users = mongo.db.user_table
            existing_user = users.find_one({'email': request.form['email']})

            if existing_user is None:

                fullname = get_user_fullname(user_email)

                # If the input and confirmation password are the same
                if request.form['password'] == request.form['password2']:

                    # https://stackoverflow.com/questions/58716927/insert-field-only-if-not-null
                    # This is when the user does not type in any of the page's fields
                    # Simulate your incoming record
                    # As soon as the password will be encoded we do not want to encode an empty password
                    if request.form['password'] == "":
                        record = {"email": request.form.get('email'),
                                  "fullname": request.form.get('fullname'),
                                  }
                    else:
                        record = {"email": request.form.get('email'),
                                  "fullname": request.form.get('fullname'),
                                  "password": bcrypt.hashpw(request.form.get('password').encode('utf-8'),
                                                            bcrypt.gensalt())
                                  }

                    # Remove any empty items (this is when the user left everything empty)
                    for k, v in list(record.items()):
                        if v == '' or v is None:
                            record.pop(k)

                    # The update cannot be implemented if the record is empty
                    if record:
                        # 1: update the columns of the user in the user_table
                        mongo.db.user_table.find_one_and_update({"email": user_email}, {"$set": record})

                        if request.form['email'] != "":  # update it only if the user's name has changed
                            # 2: update the user's e-mail in the project table
                            mongo.db.project_table.find_one_and_update({"project_creator_email": user_email},
                                                                       {"$set": {
                                                                           "project_creator_email": record['email']}})

                            # 3: update the user's e-mail in the project table
                            mongo.db.assigned_table.find_one_and_update({"email": user_email},
                                                                        {"$set": {"email": record['email']}})
                            user_email = record['email']  # update the user_email for the url

                        # 4: update the user's e-mail in the task table
                        if request.form['fullname'] != "":  # update it only if the user's name has changed
                            mongo.db.task_table.find_one_and_update({"assign_to": fullname},
                                                                    {"$set": {"assign_to": record['fullname']}})

                    return render_template(
                        'dashboard/alerts/alertUpdateProfile.html',
                        user_email=user_email)  # account created successfully navigate me to the login page
                else:
                    error = 'These passwords are not identical'
                    return render_template('dashboard/users/view.html', user_email=user_email, error=error)

            else:
                error = 'An account already exists with this e-mail address!'
                return render_template('dashboard/users/view.html', user_email=user_email, error=error)
        else:
            error = 'You need to login first'
            session.clear()
            return render_template('login.html', error=error)

    except Exception as e:
        print("There was an error with the update process of the user's profile: %s" % e)


# Delete the user
@app.route('/dashboard/<user_email>/delete_user', methods=['POST'])
def delete_user(user_email):

    # 1. Do not forget to delete the user from every assigned task
    fullname = get_user_fullname(user_email)
    mongo.db.task_table.update({'assign_to': fullname}, {'$unset': {'assign_to': 1}}, multi=True)

    # 2. Do not forget to delete the user from the assigned_user table
    mongo.db.assigned_table.remove({'email': user_email})

    # 3. Delete all the project's of the user including everything related to it
    project_collection_list = list(mongo.db.project_table.find({'project_creator_email': user_email}, {'_id': 1}))

    if project_collection_list:
        for x in project_collection_list:
            # we want to take only the substring which is inside the parenthesis (the id)
            # but it will be easier to convert the whole dict to a string first
            project_id_string = str(x)
            # gives '6060530cf082cd618caaad54' and then 6060530cf082cd618caaad54
            project_id = project_id_string[project_id_string.find("(") + 1:project_id_string.find(")")].replace("'", "")
            project_id = ObjectId(project_id)

            # 3A. Delete the uploaded files of the project
            upload_results = mongo.db.upload_table.find(
                {
                    "project_id": project_id})  # find the collection of the files which we want to delete based on the project_id

            for file_document in upload_results:  # iterate all the files which are included in the project that we want to delete

                file_name = file_document[
                    'filename']  # keep the name of the file that we want to delete which exist in the upload_table
                fs_result = mongo.db.fs.files.find_one({
                    "filename": file_name})  # use the above filename in order to collect the data of the file which we want to delete and also exist in the fs.file table
                fs_id = fs_result[
                    '_id']  # keep the id of the file that we want to delete which it is also exist in the fs.file table

                fs.delete(fs_id)  # delete the file from the fs.files and fs.chunks table
                mongo.db.upload_table.remove({'project_id': project_id})  # delete the file from the upload_table

            # 3B. Delete the tasks of the user's project
            mongo.db.task_table.remove({'project_id': project_id})

            # 3C. Delete all the user's projects
            mongo.db.project_table.remove({'_id': project_id})

    # 4: Finally delete the user
    mongo.db.user_table.remove({'email': user_email})

    return render_template('dashboard/alerts/alertDeleteProfile.html', user_email=user_email)


# Get the fullname of the user
def get_user_fullname(user_email):
    try:
        user_email_dict = mongo.db.user_table.find_one({'email': user_email},
                                                       {'fullname': 1,
                                                        '_id': 0})
        user_email_string = str(user_email_dict)
        user_email_string = user_email_string.replace("'fullname'", '')

        user_fullname_list = re.findall(r"'([^']*)'", user_email_string)
        return user_fullname_list[0]
    except Exception as e:
        print("There was an error getting the user's email: %s" % e)


# Get the user's password
def get_user_password(user_email):
    try:
        user_email_dict = mongo.db.user_table.find_one({'email': user_email},
                                                       {'password': 1,
                                                        '_id': 0})
        user_email_string = str(user_email_dict)
        user_email_string = user_email_string.replace("'password'", '')

        user_password_list = re.findall(r"'([^']*)'", user_email_string)
        return user_password_list[0]
    except Exception as e:
        print("There was an error getting the user's password: %s" % e)


# -----> END OF OUTSIDE DASHBOARD PAGES AND FUNCTIONS <-----


# -----> DASHBOARD PAGES <-----
@app.route('/dashboard/<user_email>')
def dashboard(user_email):
    try:
        if "active_user" in session:  # checking if active user exist in the session (cookies)

            # use this variable to check the email who is logged in during a session
            users = mongo.db.user_table.find({}, {"email": 1})
            projects = mongo.db.project_table.find({}, {"title": 1, "description": 1, "date": 1, "status": 1,
                                                        "project_creator_email": 1})

            # CHARTS
            months = []  # create an empty list
            # Refresh the list by adding the number of project of each month
            for x in range(1, 13):  # 12 months counting from 1
                # Source: https://stackoverflow.com/a/41157529
                # Source: https://docs.mongodb.com/manual/reference/method/db.collection.count/
                # Create a list of data, find and count the projects which belong to a specific month
                # find({..},{..}) --> one condition, find({... , ...}, {..}) --> two conditions
                months.append([mongo.db.project_table.find(
                    {'project_creator_email': user_email,
                     'date': {'$regex': "2021-0" + str(x), '$options': 'i'}}).count()])

            project_sum = mongo.db.project_table.find(
                {'project_creator_email': user_email}).count()  # calculate the sum of all project of the current user

            # https://stackoverflow.com/questions/41271299/how-can-i-get-the-first-two-digits-of-a-number
            try:
                status = [float(str((mongo.db.project_table.find(
                    {'project_creator_email': user_email, 'status': 'Not started'}).count()) / project_sum * 100)[:3]),
                          float(str((mongo.db.project_table.find(
                              {'project_creator_email': user_email,
                               'status': 'In-progress'}).count()) / project_sum * 100)[
                                :3]),
                          float(str((mongo.db.project_table.find(
                              {'project_creator_email': user_email,
                               'status': 'Completed'}).count()) / project_sum * 100)[
                                :3]),
                          float(str((mongo.db.project_table.find(
                              {'project_creator_email': user_email,
                               'status': 'Emergency'}).count()) / project_sum * 100)[
                                :3])]
            except ZeroDivisionError:
                status = [0, 0, 0, 0]

            assigned_users = list(mongo.db.assigned_table.find({}, {"email": 1, "project_id": 1, "_id": 0}))
            # remove duplicates: https://stackoverflow.com/a/9427216
            assigned_users = [dict(t) for t in {tuple(d.items()) for d in assigned_users}]

            # render these data to the home.html which sending the charts data to base.html
            return render_template('dashboard/home.html', users=users, user_email=user_email, projects=projects,
                                   project_sum=project_sum, dataMonth=months,
                                   dataStatus=status,
                                   assigned_users=assigned_users)  # https://startbootstrap.com/template/sb-admin
        else:
            error = 'Invalid credentials'
            print(error)
            session.clear()
            flash(u'You need to login', 'error')
            return render_template('login.html', error=error)
    except Exception as e:
        print("There was an error with the loading process of the dashboard page: %s" % e)


# -----> END DASHBOARD PAGES <-----


# -----> PROJECTS PAGES AND FUNCTIONS <-----
@app.route('/dashboard/<user_email>/projects/new_project', methods=['POST', 'GET'])
def create_new_project(user_email):
    try:
        if "active_user" in session:  # checking if active user exist in the session (cookies)
            if request.method == 'POST':

                # https://docs.mongodb.com/manual/reference/database-references/
                project_id = ObjectId()  # setup the project's id

                project_collection = mongo.db.project_table  # project collection (creates the project_table)
                existing_project = project_collection.find_one(
                    {'title': request.form['project_title']})  # check if the project already exists based on the title

                if existing_project is None:
                    project_collection.insert_one({"_id": project_id,
                                                   'title': request.form['project_title'],
                                                   'description': request.form['project_description'],
                                                   'date': request.form['project_date'],
                                                   'status': "Not started",
                                                   'project_creator_email': user_email,
                                                   })
                    # As soon as the project is created, the next step will be to add a new empty task to avoid the 404 issue
                    # this will be deleted when the user adds the first task
                    insert_new_empty_task(user_email, project_id)

                    return redirect(url_for('view_project', user_email=user_email, project_id=project_id))

                return 'That project already exists!'

            return render_template('dashboard/projects/new.html', user_email=user_email)
        else:
            error = 'You need to login first'
            session.clear()
            return render_template('login.html', error=error)
    except Exception as e:
        print("There was an error with the creation of a new project: %s" % e)


# View a Project
@app.route('/dashboard/<user_email>/projects/<ObjectId:project_id>', methods=['GET'])
def view_project(user_email, project_id):
    try:
        if "active_user" in session:  # checking if active user exist in the session (cookies)
            # Check if the project exists in the db table based on the id
            project = mongo.db.project_table.find_one_or_404({'_id': project_id})
            task = mongo.db.task_table.find_one_or_404({'project_id': project_id})

            # Collect all the variables which we want to display in the project page
            tasks = mongo.db.task_table.find({},
                                             {"title": 1, "description": 1, "date": 1, "assign_to": 1, "project_id": 1,
                                              "status": 1})
            users = mongo.db.user_table.find({}, {"fullname": 1})

            return render_template('dashboard/projects/view.html', user_email=user_email, project=project, task=task,
                                   tasks=tasks, users=users)
        else:
            error = 'You need to login first'
            session.clear()
            return render_template('login.html', error=error)
    except Exception as e:
        print("There was an error with the loading process of the project's view: %s" % e)


# Update Project details
@app.route('/dashboard/<user_email>/projects/update/<ObjectId:project_id>', methods=['POST'])
def update_project(user_email, project_id):
    try:
        if "active_user" in session:  # checking if active user exist in the session (cookies)
            project_collection = mongo.db.project_table
            project_collection.find_one_and_update({"_id": project_id},
                                                   {"$set": {
                                                       "title": request.form.get('title'),
                                                       "description": request.form.get('description'),
                                                       "date": request.form.get('date'),
                                                       'status': request.form.get('status')
                                                   }
                                                   })

            return redirect(url_for('table', user_email=user_email))
        else:
            error = 'You need to login first'
            session.clear()
            return render_template('login.html', error=error)
    except Exception as e:
        print("There was an error with the update process of the project: %s" % e)


# Delete a project
@app.route('/dashboard/<user_email>/projects/delete/<ObjectId:project_id>', methods=['POST'])
def delete_project(user_email, project_id):
    try:
        if "active_user" in session:  # checking if active user exist in the session (cookies)
            # 1. Do not forget to delete the assigned users of the project's tasks
            mongo.db.assigned_table.remove({"project_id": project_id})  #

            # 2. Delete the uploaded files of the project
            upload_results = mongo.db.upload_table.find(
                {
                    "project_id": project_id})  # find the collection of the files which we want to delete based on the project_id

            for file_document in upload_results:  # iterate all the files which are included in the project that we want to delete

                file_name = file_document[
                    'filename']  # keep the name of the file that we want to delete which exist in the upload_table
                fs_result = mongo.db.fs.files.find_one({
                    "filename": file_name})  # use the above filename in order to collect the data of the file which we want to delete and also exist in the fs.file table
                fs_id = fs_result[
                    '_id']  # keep the id of the file that we want to delete which it is also exist in the fs.file table

                fs.delete(fs_id)  # delete the file from the fs.files and fs.chunks table
                mongo.db.upload_table.remove({'project_id': project_id})  # delete the file from the upload_table

            # 3. Delete the tasks of the project
            mongo.db.task_table.remove({'project_id': project_id})  # Delete the project's tasks from the database

            # 4. Finally delete the project
            mongo.db.project_table.remove({'_id': project_id})  # Delete the project from the database

            return redirect(url_for('table', user_email=user_email))
        else:
            error = 'You need to login first'
            session.clear()
            return render_template('login.html', error=error)
    except Exception as e:
        print("There was an error with the deletion of the project: %s" % e)


# Add an empty task in the project's table
@app.route('/dashboard/<user_email>/projects/<ObjectId:project_id>/new_empty_task', methods=['POST'])
def insert_new_empty_task(user_email, project_id):
    try:
        if "active_user" in session:  # checking if active user exist in the session (cookies)
            task_collection = mongo.db.task_table
            task_collection.insert_one(
                {
                    "title": "",
                    "description": "First always empty, it will be removed automatically",
                    "date": "",
                    "project_id": project_id,
                    "assign_to": "",
                    "status": ""
                }
            )

            return redirect(url_for('view_project', user_email=user_email, project_id=project_id))
        else:
            error = 'You need to login first'
            session.clear()
            return render_template('login.html', error=error)
    except Exception as e:
        print("There was an error with the insert process of an empty task: %s" % e)


# -----> END OF PROJECTS PAGES AND FUNCTIONS<-----

# Add new task in the project's table
@app.route('/dashboard/<user_email>/projects/<ObjectId:project_id>/new_task', methods=['POST', 'GET'])
def create_new_task(user_email, project_id):
    try:
        if "active_user" in session:  # checking if active user exist in the session (cookies)
            project = mongo.db.project_table.find_one_or_404({'_id': project_id})
            users = mongo.db.user_table.find({}, {"fullname": 1})
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
                        "status": "Not started"
                    }
                )
                # delete now the auto-created empty task of this project
                task_collection.remove({'project_id': project_id, 'title': ""})

                # Keep the email of the assigned user
                assigned_email = get_assigned_user_email(request.form['task_assign_to'])
                # create a table with the assigned users of each project task
                add_assigned_user(assigned_email, project_id, task_id)

                return redirect(url_for('view_project', user_email=user_email, project_id=project_id, task_id=task_id))

            return render_template('dashboard/tasks/new.html', user_email=user_email, project=project, users=users)
        else:
            error = 'You need to login first'
            session.clear()
            return render_template('login.html', error=error)
    except Exception as e:
        print("There was an error with the creation of a new task: %s" % e)


# View a project's task
@app.route('/dashboard/<user_email>/projects/<ObjectId:project_id>/<ObjectId:task_id>', methods=['GET'])
def view_task(user_email, project_id, task_id):
    try:
        if "active_user" in session:  # checking if active user exist in the session (cookies)
            # Check if the project and task exists in the db table based on the id
            project = mongo.db.project_table.find_one_or_404({'_id': project_id})
            task = mongo.db.task_table.find_one_or_404({'_id': task_id})

            tasks = mongo.db.task_table.find({}, {"title": 1, "description": 1, "date": 1, "assign_to": 1, "status": 1})
            users = mongo.db.user_table.find({}, {"fullname": 1})

            return render_template('dashboard/tasks/view.html', user_email=user_email, project=project, task=task,
                                   tasks=tasks,
                                   users=users)
        else:
            error = 'You need to login first'
            session.clear()
            return render_template('login.html', error=error)
    except Exception as e:
        print("There was an error with the loading process of the task: %s" % e)


# -----> TASKS PAGES AND FUNCTIONS <-----
# HOW IT WORKS:
# <ObjectId:project_id> and <ObjectId:task_id> = project_id, task_id of the update_task(), respectively
# Then, using the redirect(url_for()) we are taking the project and task id values which are coming from the html file
# Thus, (from the app.py) project_id=project_id and task_id=task_id <--> project_id=project._id and task_id=task._id (from the html file)

# Update the Project's task details
@app.route('/dashboard/<user_email>/projects/<ObjectId:project_id>/<ObjectId:task_id>/update', methods=['POST'])
def update_task(user_email, project_id, task_id):
    try:
        if "active_user" in session:  # checking if active user exist in the session (cookies)
            task_collection = mongo.db.task_table
            task_collection.find_one_and_update({"_id": task_id},
                                                {"$set": {
                                                    "title": request.form.get('title'),
                                                    "description": request.form.get('description'),
                                                    "date": request.form.get('date'),
                                                    "assign_to": request.form.get('assign_to'),
                                                    'status': request.form.get('status')
                                                }
                                                })
            # Keep the email of the assigned user
            assigned_email = get_assigned_user_email(request.form.get('assign_to'))
            # update the assigned user of the specific task (if changed)
            update_assigned_user(assigned_email, task_id)

            return redirect(url_for('view_project', user_email=user_email, project_id=project_id))
        else:
            error = 'You need to login first'
            session.clear()
            return render_template('login.html', error=error)
    except Exception as e:
        print("There was an error with the update process of the task: %s" % e)


# Delete a task
@app.route('/dashboard/<user_email>/projects/<ObjectId:project_id>/delete/<ObjectId:task_id>', methods=['POST'])
def delete_task(user_email, project_id, task_id):
    try:
        if "active_user" in session:  # checking if active user exist in the session (cookies)
            task_collection = mongo.db.task_table
            cur = mongo.db.task_table.find({"project_id": project_id})
            results = list(cur)

            # Do not forget to delete the assigned user from the assigned_table first (automatically)
            delete_assigned_user(project_id, task_id)

            # Checking the cursor has at least 1 element
            # If there is only one task of the specific project in the table, do not remove it because there will be an issue
            # just clear it ($unset could be an option)
            # else remove completely the requested task
            if len(results) == 1:
                task_collection.find_one_and_update({"_id": task_id},
                                                    {"$set": {
                                                        "title": "",
                                                        "description": "First always empty, it will be removed automatically",
                                                        "date": "",
                                                        "assign_to": "",
                                                        "status": ""
                                                    }
                                                    })
            else:
                task_collection.remove({"_id": task_id})

            return redirect(url_for('view_project', user_email=user_email, project_id=project_id, task_id=task_id))
        else:
            error = 'You need to login first'
            session.clear()
            return render_template('login.html', error=error)
    except Exception as e:
        print("There was an error with the deletion of the task: %s" % e)


# -----> END OF TASKS PAGES AND FUNCTIONS <-----

# -----> ASSIGNED_TABLE FUNCTIONS <-----

# create the assign_table, this will include the assign users of each task
# and it will be used in order to let the users to see the projects which
# they did not create but they have been assigned
def add_assigned_user(email, project_id, task_id):
    try:
        assigned_user_collection = mongo.db.assigned_table
        assigned_user_collection.insert_one(
            {
                'email': email,
                "task_id": task_id,
                "project_id": project_id
            }
        )
    except Exception as e:
        print("There was an error with the addition of the user to the assigned list: %s" % e)


# Update the assigned user of the specific task
def update_assigned_user(email, task_id):
    try:
        assigned_user_collection = mongo.db.assigned_table
        assigned_user_collection.find_one_and_update(
            {"task_id": task_id},
            {"$set": {
                'email': email
            }
            }
        )
    except Exception as e:
        print("There was an error with the update process of the assigned user: %s" % e)


# As soon as the task is deleted, this will delete the assigned user from the assigned table
def delete_assigned_user(project_id, task_id):
    try:
        assigned_user_collection = mongo.db.assigned_table
        assigned_user_collection.remove({"project_id": project_id, "task_id": task_id})
    except Exception as e:
        print("There was an error with the deletion of the assigned user: %s" % e)


# Get the e-mail of the assigned user
def get_assigned_user_email(fullname):
    try:
        user_email_dict = mongo.db.user_table.find_one({'fullname': fullname},
                                                       {'email': 1,
                                                        '_id': 0})  # gives e.g, {'email': georgios@gmail.com')}
        user_email_string = str(user_email_dict)  # it will be easier to convert the whole dict to a string first
        user_email_string = user_email_string.replace("'email'", '')  # remove the 'email' substring

        assigned_email_list = re.findall(r"'([^']*)'",
                                         user_email_string)  # gives a list with e.g, ['georgios@gmail.com']

        return assigned_email_list[0]  # returns e.g, georgios@gmail.com
    except Exception as e:
        print("There was an error getting the assigned user's email: %s" % e)


# -----> END OF ASSIGNED_TABLE FUNCTIONS <-----


# -----> FILES LIST PAGES AND FUNCTIONS <-----

# https://www.youtube.com/watch?v=DsgAuceHha4
# List with all the uploads of the specific project
@app.route('/dashboard/<user_email>/projects/<ObjectId:project_id>/uploads')
def upload_table(user_email, project_id):
    try:
        if "active_user" in session:  # checking if active user exist in the session (cookies)
            project = mongo.db.project_table.find_one_or_404({'_id': project_id})
            uploads = mongo.db.upload_table.find({}, {"filename": 1, "project_id": 1})
            return render_template('dashboard/projects/uploads.html', user_email=user_email, project=project,
                                   project_id=project_id, uploads=uploads)
        else:
            error = 'You need to login first'
            session.clear()
            return render_template('login.html', error=error)
    except Exception as e:
        print("There was an error with the loading process of the uploaded files list: %s" % e)


# Add new file in upload_table of the specific project
@app.route('/dashboard/<user_email>/projects/<ObjectId:project_id>/new_file', methods=['POST'])
def upload_new_file(user_email, project_id):
    try:
        if "active_user" in session:  # checking if active user exist in the session (cookies)
            upload_collection = mongo.db.upload_table
            upload = request.files['upload']
            if upload.filename != '':  # avoid to upload empty stuff
                mongo.save_file(upload.filename, upload)  # default BSON size limit 16MB
                upload_collection.insert_one(
                    {
                        'filename': upload.filename,
                        'project_id': project_id
                    }
                )

            return redirect(url_for('upload_table', user_email=user_email, project_id=project_id))
        else:
            error = 'You need to login first'
            session.clear()
            return render_template('login.html', error=error)
    except Exception as e:
        print("There was an error with the upload process of the file: %s" % e)


# Download the file from the upload list
@app.route('/dashboard/<user_email>/projects/<ObjectId:project_id>/uploads/file/<filename>', methods=['GET'])
def download_file(user_email, project_id, filename):
    try:
        if "active_user" in session:  # checking if active user exist in the session (cookies)
            # https://stackoverflow.com/questions/12645505/python-check-if-any-items-of-a-tuple-are-in-a-string
            valid_file_extensions = ".pdf", ".zip", ".rar", ".bmp", ".gif", ".jpg", ".jpeg", ".png"
            if not any(str(filename).endswith(s) for s in valid_file_extensions):

                # where to place the file
                dest_dir = os.path.expanduser('~/Downloads/task-management-tool/')
                # make the directories (recursively)
                try:
                    os.makedirs(dest_dir)
                except OSError:  # ignore errors
                    pass

                # https://www.youtube.com/watch?v=KSB5g8qt9io
                data = mongo.db.fs.files.find_one({'filename': filename})
                file_id = data['_id']
                output_data = fs.get(file_id).read()
                download_location = dest_dir + filename
                output = open(download_location, "wb")
                output.write(output_data)
                output.close()

                return render_template('dashboard/alerts/alertUploadFile.html', user_email=user_email,
                                       project_id=project_id)

            else:
                return mongo.send_file(filename)
        else:
            error = 'You need to login first'
            session.clear()
            return render_template('login.html', error=error)
    except Exception as e:
        print("There was an error with the download process of the uploaded file: %s" % e)


# https://stackoverflow.com/questions/21311540/how-to-delete-an-image-file-from-gridfs-by-file-metadata
@app.route('/dashboard/<user_email>/projects/<ObjectId:project_id>/uploads/delete/<ObjectId:upload_id>',
           methods=['POST'])
def delete_file(user_email, project_id, upload_id):
    try:
        if "active_user" in session:  # checking if active user exist in the session (cookies)
            # upload_table -- use as foreign_key=id to --> fs.files table -- use as foreign_key=filename to--> fs.chunks table
            fs_collection = mongo.db.fs.files  # collect the data of the fs.files table
            upload_collection = mongo.db.upload_table  # collect the data of the upload_table

            upload_result = upload_collection.find_one(
                {"_id": upload_id})  # find the collection of the file which we want to delete based on its id
            files_name = upload_result[
                'filename']  # keep the filename of the file that we want to delete which exist in the upload_table

            fs_result = fs_collection.find_one({
                "filename": files_name})  # use the above filename in order to collect the data of the file which we want to delete and also exist in the fs.file table
            fs_id = fs_result[
                '_id']  # keep the id of the file that we want to delete which it is also exist in the fs.file table

            fs.delete(fs_id)  # delete the file from the fs.files and fs.chunks table
            upload_collection.remove({"_id": upload_id})  # delete the file from the upload_table

            return redirect(url_for('upload_table', user_email=user_email, project_id=project_id))
        else:
            error = 'You need to login first'
            session.clear()
            return render_template('login.html', error=error)
    except Exception as e:
        print("There was an error with the deletion of the uploaded file: %s" % e)


# -----> END OF FILES LIST PAGES AND FUNCTIONS <-----

# -----> CHARTS TAB PAGES AND FUNCTIONS <-----

@app.route('/dashboard/<user_email>/charts')
def charts(user_email):
    try:
        if "active_user" in session:  # checking if active user exist in the session (cookies)
            months = []  # create an empty list
            # Refresh the list by adding the number of project of each month
            for x in range(1, 13):  # 12 months counting from 1
                # Source: https://stackoverflow.com/a/41157529
                # Source: https://docs.mongodb.com/manual/reference/method/db.collection.count/
                # Create a list of data, find and count the projects which belong to a specific month
                # find({..},{..}) --> one condition, find({... , ...}, {..}) --> two conditions
                months.append([mongo.db.project_table.find(
                    {'project_creator_email': user_email,
                     'date': {'$regex': "2021-0" + str(x), '$options': 'i'}}).count()])

            # calculate the sum of all projects which the current user created
            personal_projects_sum = mongo.db.project_table.find({'project_creator_email': user_email}).count()

            # https://stackoverflow.com/questions/41271299/how-can-i-get-the-first-two-digits-of-a-number
            try:
                status = [float(str((mongo.db.project_table.find(
                    {'project_creator_email': user_email,
                     'status': 'Not started'}).count()) / personal_projects_sum * 100)[
                                :4]),
                          float(str((mongo.db.project_table.find(
                              {'project_creator_email': user_email,
                               'status': 'In-progress'}).count()) / personal_projects_sum * 100)[
                                :4]),
                          float(str((mongo.db.project_table.find(
                              {'project_creator_email': user_email,
                               'status': 'Completed'}).count()) / personal_projects_sum * 100)[:4]),
                          float(str((mongo.db.project_table.find(
                              {'project_creator_email': user_email,
                               'status': 'Emergency'}).count()) / personal_projects_sum * 100)[:4])]
            except ZeroDivisionError:
                status = [0, 0, 0, 0]

            # render these data to the charts.html which sending the charts data to base.html
            return render_template('dashboard/charts.html', user_email=user_email, dataMonth=months, dataStatus=status,
                                   project_sum=personal_projects_sum)
        else:
            error = 'You need to login first'
            session.clear()
            return render_template('login.html', error=error)
    except Exception as e:
        print("There was an error with the loading process of the charts: %s" % e)


# -----> END OF CHART TAB PAGES AND FUNCTIONS <-----


# -----> TABLE TAB PAGES AND FUNCTIONS <-----

# https://stackoverflow.com/questions/53425222/python-flask-i-want-to-display-the-data-that-present-in-mongodb-on-a-html-page
@app.route('/dashboard/<user_email>/table')
def table(user_email):
    try:
        if "active_user" in session:  # checking if active user exist in the session (cookies)
            projects = list(mongo.db.project_table.find({}, {"title": 1, "description": 1, "date": 1, "status": 1,
                                                             "project_creator_email": 1}))  # list fixes the assigned_user_list issue
            assigned_users = list(mongo.db.assigned_table.find({}, {"email": 1, "project_id": 1, "_id": 0}))
            # remove duplicates: https://stackoverflow.com/a/9427216
            assigned_users = [dict(t) for t in {tuple(d.items()) for d in assigned_users}]
            return render_template('dashboard/table.html', user_email=user_email, projects=projects,
                                   assigned_users=assigned_users)
        else:
            error = 'You need to login first'
            session.clear()
            return render_template('login.html', error=error)
    except Exception as e:
        print("There was an error with the loading process of the main projects' table: %s" % e)


# Starting project table categories
@app.route('/dashboard/<user_email>/table/not-started')
def table_not_started(user_email):
    try:
        if "active_user" in session:  # checking if active user exist in the session (cookies)
            projects = list(mongo.db.project_table.find({}, {"title": 1, "description": 1, "date": 1, "status": 1,
                                                             "project_creator_email": 1}))
            assigned_users = list(mongo.db.assigned_table.find({}, {"email": 1, "project_id": 1, "_id": 0}))
            # remove duplicates: https://stackoverflow.com/a/9427216
            assigned_users = [dict(t) for t in {tuple(d.items()) for d in assigned_users}]
            return render_template('dashboard/categories/notstarted.html', user_email=user_email, projects=projects,
                                   assigned_users=assigned_users)
        else:
            error = 'You need to login first'
            session.clear()
            return render_template('login.html', error=error)
    except Exception as e:
        print("There was an error with the table of projects type 'Not started': %s" % e)


@app.route('/dashboard/<user_email>/table/in-progress')
def table_in_progress(user_email):
    try:
        if "active_user" in session:  # checking if active user exist in the session (cookies)
            projects = list(mongo.db.project_table.find({}, {"title": 1, "description": 1, "date": 1, "status": 1,
                                                             "project_creator_email": 1}))
            assigned_users = list(mongo.db.assigned_table.find({}, {"email": 1, "project_id": 1, "_id": 0}))
            # remove duplicates: https://stackoverflow.com/a/9427216
            assigned_users = [dict(t) for t in {tuple(d.items()) for d in assigned_users}]
            return render_template('dashboard/categories/inprogress.html', user_email=user_email, projects=projects,
                                   assigned_users=assigned_users)
        error = 'You need to login first'
        session.clear()
        return render_template('login.html', error=error)
    except Exception as e:
        print("There was an error with the table of projects type 'In-progress': %s" % e)


@app.route('/dashboard/<user_email>/table/completed')
def table_completed(user_email):
    try:
        if "active_user" in session:  # checking if active user exist in the session (cookies)
            projects = list(mongo.db.project_table.find({}, {"title": 1, "description": 1, "date": 1, "status": 1,
                                                             "project_creator_email": 1}))
            assigned_users = list(mongo.db.assigned_table.find({}, {"email": 1, "project_id": 1, "_id": 0}))
            # remove duplicates: https://stackoverflow.com/a/9427216
            assigned_users = [dict(t) for t in {tuple(d.items()) for d in assigned_users}]
            return render_template('dashboard/categories/completed.html', user_email=user_email, projects=projects,
                                   assigned_users=assigned_users)
        error = 'You need to login first'
        session.clear()
        return render_template('login.html', error=error)
    except Exception as e:
        print("There was an error with the table of projects type 'Completed': %s" % e)


@app.route('/dashboard/<user_email>/table/emergency')
def table_emergency(user_email):
    try:
        if "active_user" in session:  # checking if active user exist in the session (cookies)
            projects = list(mongo.db.project_table.find({}, {"title": 1, "description": 1, "date": 1, "status": 1,
                                                             "project_creator_email": 1}))
            assigned_users = list(mongo.db.assigned_table.find({}, {"email": 1, "project_id": 1, "_id": 0}))
            # remove duplicates: https://stackoverflow.com/a/9427216
            assigned_users = [dict(t) for t in {tuple(d.items()) for d in assigned_users}]
            return render_template('dashboard/categories/emergency.html', user_email=user_email, projects=projects,
                                   assigned_users=assigned_users)
        else:
            error = 'You need to login first'
            session.clear()
            return render_template('login.html', error=error)
    except Exception as e:
        print("There was an error with the table of projects type 'Emergency': %s" % e)


# -----> END OF TABLE TAB PAGES FUNCTIONS <-----


# https://stackoverflow.com/a/63216793
def main():
    # If the reloader has not yet run - open the browser
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        webbrowser.open_new('http://127.0.0.1:5000/')

    # Otherwise, continue as normal
    app.secret_key = os.urandom(24)  # Keeps the client-side sessions secure by generating random key (output 24 bytes)
    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
