# Task Management Tool - Cloud Computing Project
This web application is a Task Management Tool which aids to assist teams or individuals in managing multiple projects at once. Specifically:
1. Register/Login account & Manage user account details 
2. Create/Edit/Delete projects (add a subject, deadline, status etc.)
3. Create/Edit/Delete project's tasks for each project
4. Assign specific users to specific project's tasks
5. Upload/Download and share files of a specific project with multiple users
6. Monitor your project's progress analysis through various charts
7. Split your projects' list into categories based on their status (not started, in-progress, completed, emergency)

It is written in Python-Flask for the backend, Bootstrap for the frontend, and used Jinja to transfer values from the backend to the frontend. Also, MongoDB Atlas was used for data storage.

# How to run it
1. Using Python39 (recommended)
2. Using your (IDE's) terminal, go to project's directory and run "pip install -r requirements.txt"
3. Using your (IDE's) terminal, go to project's directory and run "python app.py" to start the app

# How to run using Docker
1. Download docker desktop
2. Open a terminal and go the project's directory and run the following comands
    - docker-compose build
    - docker-compose up
# Notes
My virtualenv (venv) folder is not uploaded. So, BEFORE install the "requirements.txt", create a virtual environment using pyCharm on your production server (check here how: https://www.jetbrains.com/help/pycharm/creating-virtual-environment.html)

Also, as soon as you have installed new dependencies, please, update the "requirements.txt" file by typing in the console "pip freeze > requirements.txt".

# Video link
https://www.youtube.com/watch?v=vWzpESVf4gs
