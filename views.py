from flask import Flask, session, redirect, render_template, request, url_for,flash, jsonify,
from flask.views import MethodView
from models import db, UserCredentials, ClientInformation, FuelQuote
from datetime import datetime

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

# New View for Fuel Quote Form
class FuelQuoteForm(MethodView):
    def get(self):
        # Assuming you might want to pre-fill some data or handle the form in some way
        if 'username' not in session:
            return redirect('/login')
        return render_template('FuelQuoteForm.html')

    def post(self):
        if 'username' not in session:
            flash('You need to be logged in to submit a quote.', 'error')
            return redirect('/login')

        gallons_requested = request.form.get('gallonsRequested', type=int)
        delivery_date = request.form.get('deliveryDate')

        # Validate inputs
        if not gallons_requested or gallons_requested <= 0:
            flash('Invalid number of gallons requested.', 'error')
            return redirect(url_for('fuel_quote'))
        try:
            delivery_date = datetime.strptime(delivery_date, '%Y-%m-%d')
        except ValueError:
            flash('Invalid delivery date format.', 'error')
            return redirect(url_for('fuel_quote'))

        user = UserCredentials.query.filter_by(username=session['username']).first()
        client_info = ClientInformation.query.filter_by(user_id=user.id).first()

        # Example pricing calculation logic
        suggested_price = 2.50  # Placeholder for actual pricing algorithm
        total_amount_due = suggested_price * gallons_requested

        new_quote = FuelQuote(
            user_id=user.id,
            gallons_requested=gallons_requested,
            delivery_address=client_info.address1,
            delivery_date=delivery_date,
            suggested_price=suggested_price,
            total_amount_due=total_amount_due
        )
        db.session.add(new_quote)
        db.session.commit()

        flash('Fuel quote submitted successfully!', 'success')
        return redirect(url_for('fuel_history'))


# Implementing /get_profile_data endpoint
@app.route('/get_profile_data', methods=['GET'])
def get_profile_data():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    user = UserCredentials.query.filter_by(username=session['username']).first()
    client_info = ClientInformation.query.filter_by(user_id=user.id).first()

    if client_info:
        profile_data = {
            "deliveryAddress": client_info.address1
        }
        return jsonify(profile_data)
    else:
        return jsonify({'error': 'Profile data not found'}), 404


# New View for Fuel History
class FuelHistory(MethodView):
    def get(self):
        return render_template('FuelHistory.html')



def add_endpoints(app):
    app.add_url_rule("/register", view_func=Register.as_view("Register"))
    app.add_url_rule("/profile", view_func=Profile.as_view("Profile"))
    app.add_url_rule("/", view_func=Home.as_view("Home"))
    app.add_url_rule("/login", view_func=Login.as_view("Login"))
    app.add_url_rule("/logout", view_func=Logout.as_view("Logout"))
    # Adding new endpoints for fuel quote form and history
    app.add_url_rule("/fuel_quote", view_func=FuelQuoteForm.as_view("fuel_quote"))
    app.add_url_rule("/fuel_history", view_func=FuelHistory.as_view("fuel_history"))

add_endpoints(app)

if __name__ == "__main__":
    app.run(debug=True)
