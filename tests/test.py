# UNDER CONSTRUCTION
from bson import ObjectId
from mongodb_models import settings_mongo
from flask import Flask
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

test_app = Flask(__name__)
mongo = settings_mongo.config_mongo_db_with_app(test_app)

projects_list = [
    {
        '_id': ObjectId(),
        'title': "Dissertation Part 1",
        'description': "This project is a substantial piece of individual work to solve a problem in computing. It must be performed autonomously. Expected to take 450 hours of work. It is important that you put in this total amount of effort to able to receive a successful outcome",
        'date': "2021-04-12",
        'status': "In-progress",
        'project_creator_email': "georgios@gmail.com",
    },
    {
        '_id': ObjectId(),
        'title': "Dissertation Part 2",
        'description': "This project is a substantial piece of individual work to solve a problem in computing. It must be performed autonomously. Expected to take 450 hours of work. It is important that you put in this total amount of effort to able to receive a successful outcome",
        'date': "2021-04-08",
        'status': "Completed",
        'project_creator_email': "georgios@gmail.com",
    },
    {
        '_id': ObjectId(),
        'title': "Dissertation Part 3",
        'description': "This project is a substantial piece of individual work to solve a problem in computing. It must be performed autonomously. Expected to take 450 hours of work. It is important that you put in this total amount of effort to able to receive a successful outcome",
        'date': "2021-04-14",
        'status': "In-progress",
        'project_creator_email': "georgios@gmail.com",
    },
    {
        '_id': ObjectId(),
        'title': "Dissertation Part 3",
        'description': "This project is a substantial piece of individual work to solve a problem in computing. It must be performed autonomously. Expected to take 450 hours of work. It is important that you put in this total amount of effort to able to receive a successful outcome",
        'date': "2021-04-30",
        'status': "Not started",
        'project_creator_email': "georgios@gmail.com",
    },
    {
        '_id': ObjectId(),
        'title': "Coursework presentation",
        'description': "Prepare a PowerPoint presentation",
        'date': "2021-05-12",
        'status': "Not started",
        'project_creator_email': "georgios@gmail.com",
    },
    {
        '_id': ObjectId('666f6f2d6261722d71757578'),
        'title': "Cloud computing project",
        'description': "The purpose of the project is to develop your own Cloud application. To this end you are required to propose and describe the implementation and architecture of it",
        'date': "2021-05-18",
        'status': "Not started",
        'project_creator_email': "georgios@gmail.com",
    },
    {
        '_id': ObjectId(),
        'title': "Fix Nick's laptop",
        'description': "Nick's laptop seems to be very slow. We need to take a look and fix the problem before the end of the month",
        'date': "2021-05-30",
        'status': "Not started",
        'project_creator_email': "georgios@gmail.com",
    },
    {
        '_id': ObjectId(),
        'title': "Fix Maria's laptop",
        'description': "Maria's laptop seems to be very slow. We need to take a look and fix the problem before the end of the month",
        'date': "2021-05-30",
        'status': "In-progress",
        'project_creator_email': "georgios@gmail.com",
    },
    {
        '_id': ObjectId(),
        'title': "Fix Petro's laptop",
        'description': "Petro's laptop seems to be very slow. We need to take a look and fix the problem before the end of the month",
        'date': "2021-06-30",
        'status': "Emergency",
        'project_creator_email': "georgios@gmail.com",
    },
    {
        '_id': ObjectId(),
        'title': "Fix Richard's laptop",
        'description': "Richard's laptop seems to be very slow. We need to take a look and fix the problem before the end of the month",
        'date': "2021-07-30",
        'status': "Completed",
        'project_creator_email': "georgios@gmail.com",
    },
    {
        '_id': ObjectId(),
        'title': "Fix Nick's laptop",
        'description': "Nick's laptop seems to be very slow. We need to take a look and fix the problem before the end of the month",
        'date': "2021-07-30",
        'status': "Not started",
        'project_creator_email': "georgios@gmail.com",
    },
    {
        '_id': ObjectId(),
        'title': "Fix Georgios's laptop",
        'description': "Georgios's laptop seems to be very slow. We need to take a look and fix the problem before the end of the month",
        'date': "2021-08-30",
        'status': "Completed",
        'project_creator_email': "georgios@gmail.com",
    },
    {
        '_id': ObjectId(),
        'title': "Fix Eleni's laptop",
        'description': "Eleni's laptop seems to be very slow. We need to take a look and fix the problem before the end of the month",
        'date': "2021-08-30",
        'status': "In-progress",
        'project_creator_email': "georgios@gmail.com",
    },
    {
        '_id': ObjectId(),
        'title': "Fix Mike's laptop",
        'description': "Mike's laptop seems to be very slow. We need to take a look and fix the problem before the end of the month",
        'date': "2021-09-30",
        'status': "Not started",
        'project_creator_email': "georgios@gmail.com",
    },
    {
        '_id': ObjectId(),
        'title': "Fix Williams's laptop",
        'description': "Williams's laptop seems to be very slow. We need to take a look and fix the problem before the end of the month",
        'date': "2021-09-30",
        'status': "In-progress",
        'project_creator_email': "georgios@gmail.com",
    },
    {
        '_id': ObjectId(),
        'title': "Fix Mark's laptop",
        'description': "Mark's laptop seems to be very slow. We need to take a look and fix the problem before the end of the month",
        'date': "2021-09-30",
        'status': "Not started",
        'project_creator_email': "georgios@gmail.com",
    },
    {
        '_id': ObjectId(),
        'title': "Fix Emmanuel's laptop",
        'description': "Emmanuel's laptop seems to be very slow. We need to take a look and fix the problem before the end of the month",
        'date': "2021-09-30",
        'status': "Emergency",
        'project_creator_email': "georgios@gmail.com",
    },
    {
        '_id': ObjectId(),
        'title': "Fix Nikol's laptop",
        'description': "Nikol's laptop seems to be very slow. We need to take a look and fix the problem before the end of the month",
        'date': "2021-09-30",
        'status': "Completed",
        'project_creator_email': "georgios@gmail.com",
    },

    {
        '_id': ObjectId(),
        'title': "Fix Alexis laptop",
        'description': "Alexis laptop seems to be very slow. We need to take a look and fix the problem before the end of the month",
        'date': "2021-04-30",
        'status': "Completed",
        'project_creator_email': "georgios@gmail.com",
    },
    {
        '_id': ObjectId(),
        'title': "Fix Dias laptop",
        'description': "Dias laptop seems to be very slow. We need to take a look and fix the problem before the end of the month",
        'date': "2021-04-30",
        'status': "Completed",
        'project_creator_email': "georgios@gmail.com",
    },
    {
        '_id': ObjectId(),
        'title': "Fix Theo laptop",
        'description': "Theo laptop seems to be very slow. We need to take a look and fix the problem before the end of the month",
        'date': "2021-04-30",
        'status': "Completed",
        'project_creator_email': "georgios@gmail.com",
    },
    {
        '_id': ObjectId(),
        'title': "Fix Ioanna laptop",
        'description': "Ioanna laptop seems to be very slow. We need to take a look and fix the problem before the end of the month",
        'date': "2021-04-30",
        'status': "Completed",
        'project_creator_email': "georgios@gmail.com",
    },
    {
        '_id': ObjectId(),
        'title': "Fix Bill laptop",
        'description': "Bill laptop seems to be very slow. We need to take a look and fix the problem before the end of the month",
        'date': "2021-05-30",
        'status': "In-progress",
        'project_creator_email': "georgios@gmail.com",
    },
    {
        '_id': ObjectId(),
        'title': "Fix User1 laptop",
        'description': "User1 laptop seems to be very slow. We need to take a look and fix the problem before the end of the month",
        'date': "2021-05-30",
        'status': "In-progress",
        'project_creator_email': "georgios@gmail.com",
    },
    {
        '_id': ObjectId(),
        'title': "Fix User2 laptop",
        'description': "User2 laptop seems to be very slow. We need to take a look and fix the problem before the end of the month",
        'date': "2021-05-30",
        'status': "In-progress",
        'project_creator_email': "georgios@gmail.com",
    },
    {
        '_id': ObjectId(),
        'title': "Fix User3 laptop",
        'description': "User3 laptop seems to be very slow. We need to take a look and fix the problem before the end of the month",
        'date': "2021-06-30",
        'status': "In-progress",
        'project_creator_email': "georgios@gmail.com",
    },
    {
        '_id': ObjectId(),
        'title': "Fix User4 laptop",
        'description': "User4 laptop seems to be very slow. We need to take a look and fix the problem before the end of the month",
        'date': "2021-06-30",
        'status': "In-progress",
        'project_creator_email': "georgios@gmail.com",
    },
    {
        '_id': ObjectId(),
        'title': "Fix User5 laptop",
        'description': "User5 laptop seems to be very slow. We need to take a look and fix the problem before the end of the month",
        'date': "2021-06-30",
        'status': "Emergency",
        'project_creator_email': "georgios@gmail.com",
    },
    {
        '_id': ObjectId(),
        'title': "Fix User6 laptop",
        'description': "User6 laptop seems to be very slow. We need to take a look and fix the problem before the end of the month",
        'date': "2021-07-30",
        'status': "Emergency",
        'project_creator_email': "georgios@gmail.com",
    },
    {
        '_id': ObjectId(),
        'title': "Fix User7 laptop",
        'description': "User7 laptop seems to be very slow. We need to take a look and fix the problem before the end of the month",
        'date': "2021-07-30",
        'status': "Emergency",
        'project_creator_email': "georgios@gmail.com",
    },
    {
        '_id': ObjectId(),
        'title': "Fix User8 laptop",
        'description': "User8 laptop seems to be very slow. We need to take a look and fix the problem before the end of the month",
        'date': "2021-07-30",
        'status': "Emergency",
        'project_creator_email': "georgios@gmail.com",
    },
    {
        '_id': ObjectId(),
        'title': "Fix User9 laptop",
        'description': "User9 laptop seems to be very slow. We need to take a look and fix the problem before the end of the month",
        'date': "2021-09-30",
        'status': "Emergency",
        'project_creator_email': "georgios@gmail.com",
    },
    {
        '_id': ObjectId(),
        'title': "Fix User10 laptop",
        'description': "User10 laptop seems to be very slow. We need to take a look and fix the problem before the end of the month",
        'date': "2021-09-30",
        'status': "Not started",
        'project_creator_email': "georgios@gmail.com",
    },
    {
        '_id': ObjectId(),
        'title': "Fix User11 laptop",
        'description': "User11 laptop seems to be very slow. We need to take a look and fix the problem before the end of the month",
        'date': "2021-09-30",
        'status': "Not started",
        'project_creator_email': "georgios@gmail.com",
    },
    {
        '_id': ObjectId(),
        'title': "Fix User12 laptop",
        'description': "User12 laptop seems to be very slow. We need to take a look and fix the problem before the end of the month",
        'date': "2021-04-30",
        'status': "Not started",
        'project_creator_email': "georgios@gmail.com",
    },
    {
        '_id': ObjectId(),
        'title': "Fix User13 laptop",
        'description': "User13 laptop seems to be very slow. We need to take a look and fix the problem before the end of the month",
        'date': "2021-04-30",
        'status': "Not started",
        'project_creator_email': "georgios@gmail.com",
    },
    {
        '_id': ObjectId(),
        'title': "Fix User14 laptop",
        'description': "User14 laptop seems to be very slow. We need to take a look and fix the problem before the end of the month",
        'date': "2021-05-30",
        'status': "Not started",
        'project_creator_email': "georgios@gmail.com",
    },
    {
        '_id': ObjectId(),
        'title': "Fix User15 laptop",
        'description': "User15 laptop seems to be very slow. We need to take a look and fix the problem before the end of the month",
        'date': "2021-05-30",
        'status': "Completed",
        'project_creator_email': "georgios@gmail.com",
    },
]

tasks_list = [
    {
        '_id': ObjectId('6076d504c8a4bd3f6594aa91'),
        'title': "Analysis",
        'description': "Identify resources.",
        'date': "2021-03-31",
        'assign_to': "Georgios Karanasios",
        'project_id': ObjectId('666f6f2d6261722d71757578'),  # Cloud computing project
        'status': "Completed",
    },
    {
        '_id': ObjectId('6076d504c8a4bd3f6594aa92'),  # Cloud computing project
        'title': "Design",
        'description': "UML diagrams",
        'date': "2021-04-11",
        'assign_to': "Richard Guaman",
        'project_id': ObjectId('6076d80927a0905c0adac6a5'),  # Cloud computing project
        'status': "Completed",
    },
    {
        '_id': ObjectId('6076d504c8a4bd3f6594aa93'),
        'title': "Implementation",
        'description': "Coding Backend and Frontend",
        'date': "2021-04-25",
        'assign_to': "Georgios Karanasios",
        'project_id': ObjectId('6076d80927a0905c0adac6a5'),  # Cloud computing project
        'status': "In-progress",
    },
    {
        '_id': ObjectId('6076d504c8a4bd3f6594aa94'),
        'title': "Evaluation",
        'description': "Unit and acceptance testing",
        'date': "2021-05-05",
        'assign_to': "Richard Guaman",
        'project_id': ObjectId('6076d80927a0905c0adac6a5'),  # Cloud computing project
        'status': "Not started",
    },
]


def test_create_new_projects():
    mongo.db.project_table.insert_many(projects_list)


def test_create_new_tasks():
    mongo.db.task_table.insert_many(tasks_list)


if __name__ == "__main__":
    test_create_new_projects()
    test_create_new_tasks()
    # mongo.db.project_table.remove()
    # mongo.db.task_table.remove()
    print("Everything passed")
