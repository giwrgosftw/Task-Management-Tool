import os
from flask_pymongo import PyMongo
from dotenv import load_dotenv

# Read more: https://pypi.org/project/python-dotenv/
load_dotenv()
MONGO_URI = os.environ.get('MDB')


def config_mongo_db_with_app(app):
    app.debug = os.environ.get('DEBUG', True)
    app.config["MONGO_URI"] = MONGO_URI
    mongo_db = PyMongo(app)

    return mongo_db
