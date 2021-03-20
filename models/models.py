from flask_pymongo import PyMongo
from flask import Flask, jsonify, request, session, redirect

mongoDB = PyMongo()


def create_app(config_object='models.settings'):
    app = Flask(__name__)

    app.config.from_object(config_object)

    mongoDB.init_app(app)


class User():
    #
    def signup(self):

        user = {
            '_id': '',
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'password': request.form.get('password')
        }
        return jsonify(user), 200
