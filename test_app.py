from app import app
from models import db, UserCredentials, FuelQuote, ClientInformation
from views import add_endpoints, get_password_hash
from datetime import datetime, date
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
    response = client.get('/profile', follow_redirects=True)

    assert b'Profile' in response.data

# Test when username is not in session
def test_get_without_username(client):
    response = client.get('/')
    assert response.status_code == 302
    assert response.location == '/login'


def test_profile_post(client):
    # Create a user in the database for the test
    with client.application.app_context():
        test_user = UserCredentials(username='testuser', password=get_password_hash('testpass'))
        db.session.add(test_user)
        db.session.commit()

        # Now, within the same app context, perform the rest of the test
        # Simulate a user being logged in
        with client.session_transaction() as session:
            session['username'] = 'testuser'

        # Simulate form data for updating the profile
        form_data = {
            'fullName': 'Test User',
            'address1': '123 Test St',
            'address2': '',
            'city': 'Testville',
            'state': 'TS',
            'zipcode': '12345'
        }

        # Send a POST request with the form data
        response = client.post('/profile', data=form_data, follow_redirects=True)

        # Check if the client was redirected to the home page
        assert response.request.path == '/'

        # Retrieve the updated profile from the database
        updated_profile = ClientInformation.query.filter_by(user_id=test_user.id).first()

        # Verify that the profile was updated with the form data
        assert updated_profile.full_name == form_data['fullName']
        assert updated_profile.address1 == form_data['address1']
        assert updated_profile.address2 == form_data['address2']
        assert updated_profile.city == form_data['city']
        assert updated_profile.state == form_data['state']
        assert updated_profile.zipcode == form_data['zipcode']


def test_login_success_existing_profile(client):
    # Create a test user
    test_user = UserCredentials(username='testuser', password=get_password_hash('testpass'))

    with app.app_context():
        db.session.add(test_user)
        db.session.commit()
        test_profile = ClientInformation(user_id=test_user.id, full_name='Test User', 
                                        address1='123 Test St', city='Testville', 
                                        state='TS', zipcode='12345')
        # Add and commit test_profile to the database
        with app.app_context():
            db.session.add(test_profile)
            db.session.commit()
        # Perform login request
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass'
        }, follow_redirects=True)

        # Check if login was successful
        assert response.request.path == '/'

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
    test_user.password = password=get_password_hash('testpassword')
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
    # Setup: Create a user and a profile in the database
    with app.app_context():
        user = UserCredentials(username='testuser', password='testpassword')
        db.session.add(user)
        db.session.commit()
        # Assuming a profile is needed to access the Fuel Quote Form
        profile = ClientInformation(user_id=user.id, full_name='Test User', address1='123 Test Address', city='Test City', state='TS', zipcode='12345')
        db.session.add(profile)
        db.session.commit()
    with client.session_transaction() as session:
        session['username'] = 'testuser'
    # Make the request to the Fuel Quote Form page
    response = client.get('/fuel_quote_form', follow_redirects=True)
    assert b'Gallons Requested' in response.data, "Fuel Quote Form content not found."




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

def test_history_get(client):
    with app.app_context():
        user = UserCredentials(username='testuser', password='testpassword')
        db.session.add(user)
        db.session.commit()
        userHistory = FuelQuote(user_id=user.id, 
                                gallons_requested= 10.0,
                                delivery_address= '123 Test', 
                                delivery_date=date(2023, 1, 1), 
                                suggested_price_per_gallon = 10.0, 
                                total_amount_due = 100.0)
        db.session.add(userHistory)
        db.session.commit()
    with client.session_transaction() as session:
        session['username'] = 'testuser'
    response = client.get('/history', follow_redirects=True)
    assert b'History' in response.data

