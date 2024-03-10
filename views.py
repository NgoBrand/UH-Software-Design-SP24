from flask import session, redirect, render_template, request
from flask.views import MethodView
from models import db, UserCredentials

class Login(MethodView):
    init_every_request = False

    def get(self):
        return render_template('Login.html')

    def post(self):
        username = request.form.get('username')
        password = request.form.get('password')

        user = UserCredentials.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username # This is stored as a signed browser cookie
            return "Welcome!"
        else:
            # Invalid credentials, render the login page again with an error message
            return render_template('Login.html', error="Invalid username or password")

class Register(MethodView):
    init_every_request = False

    def get(self):
        return render_template('Register.html')

    def post(self):
        # Get form data from the POST request
        username = request.form.get('username')
        password = request.form.get('password')
        password_confirm = request.form.get('passwordConfirm')

        if password != password_confirm:
            return render_template('Register.html', error="Passwords do not match")

        # Check if the username or email already exists in the database
        existing_client = UserCredentials.query.filter_by(username=username).first()
        if existing_client:
            return render_template('Register.html', error="Username already exists")

        # Create a new client and add it to the database
        new_client = UserCredentials()
        new_client.username = username
        new_client.password = password
        db.session.add(new_client)
        db.session.commit()

        # Registration successful, redirect the user to the login page
        return redirect("/login")

class Logout(MethodView):
    def get(self):
        session.clear()
        return redirect('/login')

    def post(self):
        session.clear()
        return redirect('/login')

def add_endpoints(app):
    app.add_url_rule("/register", view_func=Register.as_view("Register"))
    app.add_url_rule("/login", view_func=Login.as_view("Login"))
    app.add_url_rule("/logout", view_func=Logout.as_view("Logout"))