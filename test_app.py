from unittest.mock import patch, Mock
from app import app
from models import db, UserCredentials, FuelQuote, ClientInformation
from views import add_endpoints
from datetime import datetime, date
import pytest
from flask import session, template_rendered
from contextlib import contextmanager

started = False
@contextmanager
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    global started
    if not started:
        add_endpoints(app)
        db.init_app(app)
        started = True
    client = app.test_client()

    # Set up the database
    with app.app_context():
        db.create_all()

    yield client

    # Teardown: drop the database and remove the session
    with app.app_context():
        db.drop_all()

def test_login_get(client):
    # Perform login request
    response = client.get('/login', follow_redirects=True)

    # Check if login page was requested
    assert b'Login' in response.data

def test_register_get(client):
    # Perform login request
    response = client.get('/register', follow_redirects=True)

    # Check if login page was requested
    assert b'Register' in response.data

def test_profile_get(client):
    response = client.get('/profile', follow_redirects=True)

    assert b'Profile' in response.data

def test_history_get(client):
    # Perform history request
    response = client.get('/history', follow_redirects=True)

    # Check if history page was requested
    assert b'History' in response.data

@pytest.fixture
def user_credentials():
    user = UserCredentials(username='testuser', password='testpass')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def client_info(user_credentials):
    info = ClientInformation(user_id=user_credentials.id, full_name='Test User', address1='123 Test St', city='Testville', state='TX', zipcode='12345')
    db.session.add(info)
    db.session.commit()
    return info

def test_home_get_with_user_logged_in(client, user_credentials, client_info):
    with client:
        with captured_templates(app) as templates:
            session['username'] = user_credentials.username
            response = client.get('/home')
            assert response.status_code == 200
            assert len(templates) == 1
            template, context = templates[0]
            assert template.name == 'Home.html'
            assert context['name'] == client_info.full_name
            assert context['address1'] == client_info.address1
            assert context['city'] == client_info.city
            assert context['state'] == client_info.state
            assert context['zipcode'] == client_info.zipcode



# Test when username is not in session
def test_get_without_username(client):
    response = client.get('/')
    assert response.status_code == 302
    assert response.location == '/login'


def test_profile_post(client):
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['username'] = 'testuser'

        form_data = {
            'full_name': 'John Doe',
            'address1': '123 Main St',
            'address2': 'Apt 4B',
            'city': 'Springfield',
            'state': 'IL',
            'zipcode': '12345'
        }

        with patch('myapp.UserCredentials.query.filter_by') as mock_filter_by:
            mock_filter_by.return_value.first.return_value = None

            response = client.post('/profile', data=form_data, follow_redirects=True)

            # Assertions
            assert response.status_code == 200
            assert b'Entered New Profile' in response.data


def test_login_success(client):
    # Create a test user
    test_user = UserCredentials()
    test_user.username = 'testuser'
    test_user.password = 'testpassword'
    with app.app_context():
        db.session.add(test_user)
        db.session.commit()

    # Perform login request
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    }, follow_redirects=True)

    # Check if login was successful
    assert b'Welcome' in response.data

def test_login_failure(client):
    # Perform login request with incorrect credentials
    response = client.post('/login', data={
        'username': 'nonexistentuser',
        'password': 'wrongpassword'
    }, follow_redirects=True)

    # Check if login failed and the login page is rendered again with an error message
    assert b'Invalid username or password' in response.data

def test_login_wrong_password(client):
    # Create a test user
    test_user = UserCredentials()
    test_user.username = 'testuser'
    test_user.password = 'testpassword'
    with app.app_context():
        db.session.add(test_user)
        db.session.commit()

    # Perform login request with existing username but wrong password
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'wrongpassword'
    }, follow_redirects=True)

    # Check if login failed and the login page is rendered again with an error message
    assert b'Invalid username or password' in response.data

def test_registration_success(client):
    # Perform registration request with valid credentials
    response = client.post('/register', data={
        'username': 'newuser',
        'password': 'newpassword',
        'passwordConfirm': 'newpassword'
    }, follow_redirects=True)

    # Check if registration was successful and user is redirected to the login page
    assert b'Login' in response.data

def test_registration_failure(client):
    # Create a test user with the same username as the one we're trying to register
    test_user = UserCredentials()
    test_user.username = 'existinguser'
    test_user.password = 'existingpassword'
    with app.app_context():
        db.session.add(test_user)
        db.session.commit()

    # Perform registration request with username that already exists
    response = client.post('/register', data={
        'username': 'existinguser',
        'password': 'newpassword',
        'passwordConfirm': 'newpassword'
    }, follow_redirects=True)

    # Check if registration failed and the registration page is rendered again with an error message
    assert b'Username already exists' in response.data

def test_registration_mismatching_passwords(client):
    # Perform registration request with passwords not matching
    response = client.post('/register', data={
        'username': 'existinguser',
        'password': 'newpassword',
        'passwordConfirm': 'newpassword0'
    }, follow_redirects=True)

    # Check if registration failed and the registration page is rendered again with an error message
    assert b'Passwords do not match' in response.data

def test_logout(client):
    # Perform logout request
    response = client.get('/logout', follow_redirects=True)
    response2 = client.post('/logout', follow_redirects=True)

    # Check if logout was successful and user is redirected to the login page
    assert b'Login' in response.data and b'Login' in response2.data


def test_fuel_quote_form_get(client):
    response = client.get('/fuel_quote_form', follow_redirects=True)
    assert b'Fuel Quote Form' in response.data, "The Fuel Quote Form content was not found in the response."


def test_direct_fuel_quote_insertion(client):
    with app.app_context():
        user = UserCredentials(username='testuser', password='testpassword')
        db.session.add(user)
        db.session.commit()
        user_id = user.id

        new_quote = FuelQuote(
            gallons_requested=100,
            delivery_address='123 Test St',
            delivery_date=date(2023, 1, 1),
            suggested_price_per_gallon=2.5,
            total_amount_due=250.00,
            user_id=user_id
        )
        db.session.add(new_quote)
        db.session.commit()

        assert FuelQuote.query.count() == 1, "Fuel quote was not inserted successfully."



def test_fuel_quote_form_post_success(client):
    # Setup user and login
    with app.app_context():
        user = UserCredentials(username='testuser', password='testpassword')
        db.session.add(user)
        db.session.commit()

    with client.session_transaction() as session:
        session['username'] = 'testuser'

    form_data = {
        'gallonsRequested': '100',
        'deliveryAddress': '123 Main St',
        'deliveryDate': datetime.now().strftime('%Y-%m-%d'),
        'suggestedPrice': '2.5',
        'totalAmountDue': '250',
    }

    client.post('/fuel_quote_form', data=form_data, follow_redirects=True)
    with app.app_context():
        assert FuelQuote.query.count() == 1, "FuelQuote record was not created"







