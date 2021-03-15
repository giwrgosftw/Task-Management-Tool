from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def login():
    return render_template('login.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/password')
def forgot_password():
    return render_template('password.html')


@app.route('/dashboard')
def dashboard():
    return render_template('index.html')  # https://startbootstrap.com/template/sb-admin


@app.route('/dashboard/charts')
def charts():
    return render_template('charts.html')


@app.route('/dashboard/tables')
def tables():
    return render_template('tables.html')


@app.route('/logout')
def logout():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
