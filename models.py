from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UserCredentials(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(255), nullable=False)
    first_login = db.Column(db.Boolean, default=True)

class ClientInformation(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user_credentials.id'), primary_key=True)
    full_name = db.Column(db.String(50), nullable=False)
    address1 = db.Column(db.String(100), nullable=False)
    address2 = db.Column(db.String(100), nullable=True)
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
    user_id = db.Column(db.Integer, db.ForeignKey('user_credentials.id'), nullable=False)

class States(db.Model):
    state_code = db.Column(db.String(2), primary_key=True)  # Set state_code as primary key
    state_name = db.Column(db.String(50), nullable=False)