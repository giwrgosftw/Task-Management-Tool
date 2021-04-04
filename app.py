import os
import webbrowser
import bcrypt
import gridfs
from flask import Flask, render_template, request, url_for, session, redirect, flash
from mongodb_models import settings_mongo
from bson import ObjectId

app = Flask(__name__)
mongo = settings_mongo.config_mongo_db_with_app(app)
fs = gridfs.GridFS(mongo.db)  # create GridFS instance


# # -----> OUTSIDE DASHBOARD PAGES & FUNCTIONS <-----

@app.route('/')
def welcome_login():
    return render_template('login.html')  # welcome and login page are one page (need to add new background)


# Check if the given credentials are successful
@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.user_table  # connect to the db from the settings module and then rendering the users table
    login_user = users.find_one({'email': request.form['email']})  # true/false if the e-mail exists
    # if e-mail exist, check if the password is correct, if correct, navigate me to the dashboard page
    if login_user:
        if bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['password']) != login_user['password']:
            error = 'Invalid credentials'
            # session['active_user'] = request.form['email']
            # flash('You were successfully logged in')
            # return redirect(url_for('dashboard'))
        else:
            session['active_user'] = request.form['email']
            # flash('You were successfully logged in')
            return redirect(url_for('dashboard'))
            # error = 'Invalid credentials'
            # flash('You test d in')
    else:
        error = 'Account not found, please create one'
    return render_template('login.html', error=error)


# Registration process (+ checking if the account already exists)
# Source: https://www.youtube.com/watch?v=vVx1737auSE&list=PLXmMXHVSvS-Db9KK1LA7lifcyZm4c-rwj&index=5
@app.route('/register', methods=['POST', 'GET'])
def register():
    error = None
    if request.method == 'POST':
        users = mongo.db.user_table
        existing_user = users.find_one({'email': request.form['email']})
        if existing_user is None:
            hash_pass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            users.insert_one(
                {'fullname': request.form['fullname'], 'email': request.form['email'],
                 'password': hash_pass})
            session['active_session'] = request.form['email']
            return redirect(url_for('welcome_login'))  # account created successfully navigate me to the login page
        else:
            error = 'This account already exists!'
    return render_template('register.html', error=error)


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
        active_user = session["active_user"]
        print(active_user)  # use this variable to check the email who is loged in during a session (remove the comment)
        projects = mongo.db.project_table.find({}, {"title": 1, "description": 1, "date": 1, "status": 1})
        return render_template('dashboard/home.html', projects=projects)  # https://startbootstrap.com/template/sb-admin
    else:
        error = 'Invalid credentials'
        print(error)
        session.clear()
        flash(u'You need to login', 'error')
        return render_template('login.html', error=error)


# -----> END DASHBOARD PAGES <-----

# -----> PROJECTS PAGES AND FUNCTIONS <-----
@app.route('/dashboard/projects/new_project', methods=['POST', 'GET'])
def create_new_project():
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
                                           })
            # As soon as the project is created, the next step will be to add a new empty task to avoid the 404 issue
            # this will be deleted when the user adds the first task
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

    # Collect all the variables which we want to display in the project page
    tasks = mongo.db.task_table.find({}, {"title": 1, "description": 1, "date": 1, "assign_to": 1, "project_id": 1,
                                          "status": 1})
    users = mongo.db.user_table.find({}, {"fullname": 1})

    return render_template('dashboard/projects/view.html', project=project, task=task, tasks=tasks, users=users)


# Update Project details
@app.route('/dashboard/projects/update/<ObjectId:project_id>', methods=['POST'])
def update_project(project_id):
    project_collection = mongo.db.project_table
    project_collection.find_one_and_update({"_id": project_id},
                                           {"$set": {
                                               "title": request.form.get('title'),
                                               "description": request.form.get('description'),
                                               "date": request.form.get('date'),
                                               'status': request.form.get('status')
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
            "assign_to": "",
            "status": ""
        }
    )

    return redirect(url_for('view_project', project_id=project_id))


# -----> END OF PROJECTS PAGES AND FUNCTIONS<-----

# Add new task in the project's table
@app.route('/dashboard/projects/<ObjectId:project_id>/new_task', methods=['POST', 'GET'])
def create_new_task(project_id):
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
        task_collection.remove(
            {'project_id': project_id, 'title': ""})  # delete now the auto-created empty task of this project

        return redirect(url_for('view_project', project_id=project_id, task_id=task_id))

    return render_template('dashboard/tasks/new.html', project=project, users=users)


# View a project's task
@app.route('/dashboard/projects/<ObjectId:project_id>/<ObjectId:task_id>', methods=['GET'])
def view_task(project_id, task_id):
    # Check if the project and task exists in the db table based on the id
    project = mongo.db.project_table.find_one_or_404({'_id': project_id})
    task = mongo.db.task_table.find_one_or_404({'_id': task_id})

    tasks = mongo.db.task_table.find({}, {"title": 1, "description": 1, "date": 1, "assign_to": 1, "status": 1})
    users = mongo.db.user_table.find({}, {"fullname": 1})

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
                                            "assign_to": request.form.get('assign_to'),
                                            'status': request.form.get('status')
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
                                                "assign_to": "",
                                                "status": ""
                                            }
                                            })
    else:
        task_collection.remove({"_id": task_id})

    return redirect(url_for('view_project', project_id=project_id, task_id=task_id))


# -----> END OF TASKS PAGES AND FUNCTIONS <-----

# -----> FILES LIST PAGES AND FUNCTIONS <-----

# https://www.youtube.com/watch?v=DsgAuceHha4
# List with all the uploads of the specific project
@app.route('/dashboard/projects/<ObjectId:project_id>/uploads')
def upload_table(project_id):
    project = mongo.db.project_table.find_one_or_404({'_id': project_id})
    uploads = mongo.db.upload_table.find({}, {"filename": 1, "project_id": 1})
    return render_template('dashboard/projects/uploads.html', project=project, project_id=project_id, uploads=uploads)


# Add new file in upload_table of the specific project
@app.route('/dashboard/projects/<ObjectId:project_id>/new_file', methods=['POST'])
def upload_new_file(project_id):
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

    return redirect(url_for('upload_table', project_id=project_id))


# Get the file from the upload list
@app.route('/dashboard/projects/<ObjectId:project_id>/uploads/file/<filename>', methods=['GET'])
def download_file(project_id, filename):
    # https://stackoverflow.com/questions/12645505/python-check-if-any-items-of-a-tuple-are-in-a-string
    valid_file_extensions = ".txt", ".pdf", ".zip", ".rar", ".bmp", ".gif", ".jpg", ".jpeg", ".png"
    if not any(s in str(filename) for s in valid_file_extensions):

        dest_dir = os.path.expandvars('%userprofile%/Downloads/task-management-tool/')  # where to put it

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

        return render_template('dashboard/alert.html', project_id=project_id)

    else:
        return mongo.send_file(filename)


# https://stackoverflow.com/questions/21311540/how-to-delete-an-image-file-from-gridfs-by-file-metadata
@app.route('/dashboard/projects/<ObjectId:project_id>/uploads/delete/<ObjectId:upload_id>', methods=['POST'])
def delete_file(project_id, upload_id):
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

    return redirect(url_for('upload_table', project_id=project_id))


# -----> END OF FILES LIST PAGES AND FUNCTIONS <-----


# -----> TABLE TAB PAGES AND FUNCTIONS <-----

# https://stackoverflow.com/questions/53425222/python-flask-i-want-to-display-the-data-that-present-in-mongodb-on-a-html-page
@app.route('/dashboard/table')
def table():
    projects = mongo.db.project_table.find({}, {"title": 1, "description": 1, "date": 1, "status": 1})
    return render_template('dashboard/table.html', projects=projects)


# Start project table categories
@app.route('/dashboard/table/not-started')
def table_not_started():
    projects = mongo.db.project_table.find({}, {"title": 1, "description": 1, "date": 1, "status": 1})
    return render_template('dashboard/categories/notstarted.html', projects=projects)


@app.route('/dashboard/table/in-progress')
def table_in_progress():
    projects = mongo.db.project_table.find({}, {"title": 1, "description": 1, "date": 1, "status": 1})
    return render_template('dashboard/categories/inprogress.html', projects=projects)


@app.route('/dashboard/table/completed')
def table_completed():
    projects = mongo.db.project_table.find({}, {"title": 1, "description": 1, "date": 1, "status": 1})
    return render_template('dashboard/categories/completed.html', projects=projects)


@app.route('/dashboard/table/emergency')
def table_emergency():
    projects = mongo.db.project_table.find({}, {"title": 1, "description": 1, "date": 1, "status": 1})
    return render_template('dashboard/categories/emergency.html', projects=projects)


# -----> END OF TABLE TAB PAGES FUNCTIONS <-----


# https://stackoverflow.com/a/63216793
def main():
    # The reloader has not yet run - open the browser
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        webbrowser.open_new('http://127.0.0.1:5000/')

    # Otherwise, continue as normal
    app.secret_key = os.urandom(24)  # Keeps the client-side sessions secure by generating random key (output 24 bytes)
    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
