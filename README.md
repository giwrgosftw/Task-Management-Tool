# CloudComputing-Coursework
This web application is a Task Management Tool for the IN3046 module

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
