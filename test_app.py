from unittest.mock import patch
from app import app
from models import db, UserCredentials
from views import add_endpoints
import pytest

started = False

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
    # Perform profile request
    response = client.get('/profile', follow_redirects=True)

    # Check if profile page was requested
    assert b'Profile' in response.data

def test_history_get(client):
    # Perform profile request
    response = client.get('/history', follow_redirects=True)

    # Check if profile page was requested
    assert b'Profile' in response.data

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