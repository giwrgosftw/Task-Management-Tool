from app import mongo, login, login_manager
from flask_login import UserMixin


class User(UserMixin, mongo.Model):
    def __init__(self, _id, email, fullname):
        self._id = _id
        self.email = email
        self.fullname = fullname

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self._id


@login.user_loader
def load_user(_id):
    user = mongo.db.users.find_one({'_id': _id})
    if not user:
        return None
    return User(user['first_name'], user['last_name'], user['email'], user['_id'])
