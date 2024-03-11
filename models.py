from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UserCredentials(db.Model):
    username = db.Column(db.String(50), primary_key=True)  # Set username as primary key
    password = db.Column(db.String(255), nullable=False)
    first_login = db.Column(db.Boolean, default=True)
    client_info_id = db.Column(db.Integer, db.ForeignKey('client_information.id'), nullable=True)  # Nullable foreign key reference

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
    client_id = db.Column(db.Integer, db.ForeignKey('client_information.id'), nullable=False)

class States(db.Model):
    state_code = db.Column(db.String(2), primary_key=True)  # Set state_code as primary key
    state_name = db.Column(db.String(50), nullable=False)