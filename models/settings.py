import os
from flask import Flask
from flask_pymongo import pymongo
from app import app

MONGO_URI = os.environ.get('MDB')

client = pymongo.MongoClient(MONGO_URI)
db = client.get_database('mongodbApp')
user_collection = pymongo.collection.Collection(db, 'users')
task_table = db.task_table
