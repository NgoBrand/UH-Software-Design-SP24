from flask import Flask, redirect, render_template
from flask.views import MethodView
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydatabase.db"
db = SQLAlchemy(app)

class UserCredentials(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Encrypted password

class ClientInformation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(50), nullable=False)
    address1 = db.Column(db.String(100), nullable=False)
    address2 = db.Column(db.String(100))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(2), nullable=False)  # State code (e.g., "TX")
    zipcode = db.Column(db.String(9), nullable=False)

class FuelQuote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gallons_requested = db.Column(db.Float, nullable=False)
    delivery_address = db.Column(db.String(100), nullable=False)
    delivery_date = db.Column(db.Date, nullable=False)
    suggested_price_per_gallon = db.Column(db.Float, nullable=False)
    total_amount_due = db.Column(db.Float, nullable=False)

class States(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state_code = db.Column(db.String(2), unique=True, nullable=False)
    state_name = db.Column(db.String(50), nullable=False)

@app.route('/')
def home():
    return redirect('/login')

class Login(MethodView):
    init_every_request = False

    def get(self):
        return render_template('Login.html')

    def post(self):
        # Log the client in and award them a session cookie given all the conditions are correct
        return "", 200

class Register(MethodView):
    init_every_request = False

    def get(self):
        return render_template('Register.html')

    def post(self):
        # Add new client to database given all the conditions are correct
        return "", 200

if __name__ == '__main__':
    app.add_url_rule("/register", view_func=Register.as_view("Register"))
    app.add_url_rule("/login", view_func=Login.as_view("Login"))
    app.run(debug=True)
