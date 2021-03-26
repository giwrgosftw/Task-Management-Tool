import os
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from pathlib import Path  # Python 3.6+ only

# Read more: https://pypi.org/project/python-dotenv/
# Explicitly providing path to '.env'
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

MONGO_URI = os.environ.get('MDB')


def config_mongo_db_with_app(app):
    app.debug = os.environ.get('DEBUG', True)
    app.config["MONGO_URI"] = MONGO_URI
    mongo_db = PyMongo(app)

    return mongo_db
