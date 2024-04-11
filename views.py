from flask import session, redirect, render_template, request, flash, url_for
from flask.views import MethodView
from models import db, UserCredentials, ClientInformation, FuelQuote
from datetime import datetime
import decimal
import bcrypt

# Source: https://stackoverflow.com/questions/77897298/storing-and-retrieving-hashed-password-in-postgres
def get_password_hash(password):
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    string_password = hashed_password.decode('utf8')
    return string_password

def verify_password(plain_password, hashed_password):
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_byte_enc, hashed_password)

class Login(MethodView):
    init_every_request = False

    def get(self):
        return render_template('Login.html')

    def post(self):
        username = request.form.get('username')
        password = request.form.get('password')

        password_hashed = get_password_hash(password)

        user = UserCredentials.query.filter_by(username=username).first()

        if user and verify_password(password,user.password):
            session['username'] = username  # This is stored as a signed browser cookie

            client_info = ClientInformation.query.filter_by(user_id=user.id).first()

            if not client_info:
                # Redirect to the profile management page
                return redirect('/profile')
            else:
                # Redirect to the home page
                return redirect('/')
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
        new_client.password = get_password_hash(password)
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


class Profile(MethodView):
    init_every_request = False

    def get(self):
        return render_template('ProfileManage.html')

    def post(self):
        if 'username' in session:
            user = UserCredentials.query.filter_by(username=session['username']).first()
            full_name = request.form.get('fullName')
            address1 = request.form.get('address1')
            address2 = request.form.get('address2')
            city = request.form.get('city')
            state = request.form.get('state')
            zipcode = request.form.get('zipcode')

            client_info = ClientInformation.query.filter_by(user_id=user.id).first()
            if not client_info:
                new_profile = ClientInformation()
                new_profile.user_id = user.id
                new_profile.full_name = full_name
                new_profile.address1 = address1
                new_profile.address2 = address2
                new_profile.city = city
                new_profile.state = state
                new_profile.zipcode = zipcode
                db.session.add(new_profile)
                db.session.commit()
            else:
                client_info.full_name = full_name
                client_info.address1 = address1
                client_info.address2 = address2
                client_info.city = city
                client_info.state = state
                client_info.zipcode = zipcode
                db.session.commit()
            return redirect('/')
        else:
            return redirect('/login')


class Home(MethodView):
    init_every_request = False

    def get(self):
        if 'username' in session:
            # Get the logged-in user's username
            user_credentials = UserCredentials.query.filter_by(username=session['username']).first()

            if user_credentials:

                # Query the ClientInformation table based on the client_info_id
                client_info = ClientInformation.query.filter_by(user_id=user_credentials.id).first()

                if client_info:
                    # Assuming ClientInformation has fields like 'full_name', 'address1', 'state', 'zipcode'
                    name = client_info.full_name
                    address1 = client_info.address1
                    address2 = client_info.address2 or ""  # Use empty string if address2 is None
                    state = client_info.state
                    zip_code = client_info.zipcode

                    # Render the template with user information
                    return render_template('Home.html', name=name, address1=address1, address2 = address2, state=state, zip_code=zip_code)
                else:
                    # Handle case where client information is not found
                    return "Client information not found."
            else:
                # Handle case where user credentials are not found
                return "User credentials not found."
        else:
            return redirect('/login')




class FuelQuoteForm(MethodView):
    init_every_request = False

    def get(self):
        username = session.get('username')

        if not username:
            flash('User not logged in. Please log in to access the Fuel Quote Form.', 'error')
            return redirect(url_for('Login'))

        user = UserCredentials.query.filter_by(username=username).first()

        if not user:
            flash('User session not found. Please log in again.', 'error')
            return redirect(url_for('Login'))

        client_info = ClientInformation.query.filter_by(user_id=user.id).first()

        if client_info and client_info.address1:
            delivery_address = client_info.address1
            state = client_info.state
            fuel_quote = FuelQuote.query.filter_by(user_id=user.id).order_by(FuelQuote.delivery_date).first()
            if fuel_quote:
                history = "1"
            else:
                history = "0"


        else:
            flash('Delivery address not found in your profile. Please update your profile.', 'error')
            return redirect(url_for('Profile'))
        

        return render_template('FuelQuoteForm.html', delivery_address=delivery_address, state = state, history = history)

    def post(self):
        username = session.get('username')
        if not username:
            flash('Please log in to submit a fuel quote.', 'error')
            return redirect(url_for('Login'))

        user = UserCredentials.query.filter_by(username=username).first()
        if not user:
            flash('User session expired.', 'error')
            return redirect(url_for('Login'))

        # Assuming you have a method to calculate these or they are being set somehow
        suggested_price_per_gallon = request.form.get('suggestedPrice', '0')
        total_amount_due = request.form.get('totalAmountDue', '0')
        gallons_requested = request.form.get('gallonsRequested', '0')

        # Convert to float, or handle the case where the conversion fails
        try:
            suggested_price_per_gallon = float(suggested_price_per_gallon) if suggested_price_per_gallon else 0.0
            gallons_requested = float(gallons_requested) if gallons_requested else 0.0
            total_amount_due = float(suggested_price_per_gallon*gallons_requested) if total_amount_due else 0.0
        except ValueError:
            flash('Invalid input for price or total amount.', 'error')
            return redirect(url_for('FuelQuoteForm'))

        delivery_date = datetime.strptime(request.form['deliveryDate'], '%Y-%m-%d')
        new_quote = FuelQuote(
            gallons_requested=gallons_requested,
            delivery_address=request.form['deliveryAddress'],
            delivery_date=delivery_date,
            suggested_price_per_gallon=decimal.Decimal(suggested_price_per_gallon),
            total_amount_due=decimal.Decimal(total_amount_due),
            user_id=user.id
        )
        db.session.add(new_quote)
        db.session.commit()
        flash('Fuel quote submitted successfully.', 'success')
        return redirect(url_for('FuelQuoteForm'))


class History(MethodView):
    init_every_request = False

    def get(self):
        if 'username' in session:
            user_credentials = UserCredentials.query.filter_by(username=session['username']).first()
            if user_credentials:
                fuel_quotes = FuelQuote.query.filter_by(user_id=user_credentials.id).order_by(FuelQuote.delivery_date).all()

                # Prepare the data for rendering
                quotes_data = [{
                    'gallonsRequested': quote.gallons_requested,
                    'deliveryAddress': quote.delivery_address,
                    'deliveryDate': quote.delivery_date.strftime('%Y-%m-%d'),  # Format date for display
                    'pricePerGallon': "{:.2f}".format(quote.suggested_price_per_gallon),
                    'total': "{:.2f}".format(quote.total_amount_due)
                } for quote in fuel_quotes]

                return render_template('FuelHistory.html', quotes_data=quotes_data)
            else:
                flash('User credentials not found.', 'error')
                return redirect('/login')
        else:
            flash('Please log in to view fuel history.', 'error')
            return redirect('/login')



def add_endpoints(app):
    app.add_url_rule("/register", view_func=Register.as_view("Register"))
    app.add_url_rule("/profile", view_func=Profile.as_view("Profile"))
    app.add_url_rule("/", view_func=Home.as_view("Home"))
    app.add_url_rule("/login", view_func=Login.as_view("Login"))
    app.add_url_rule("/logout", view_func=Logout.as_view("Logout"))
    app.add_url_rule("/history", view_func=History.as_view("History"))
    app.add_url_rule("/fuel_quote_form", view_func=FuelQuoteForm.as_view("FuelQuoteForm"))