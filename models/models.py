from flask_pymongo import PyMongo
from flask import Flask, jsonify, request, session, redirect

mongoDB = PyMongo()


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
