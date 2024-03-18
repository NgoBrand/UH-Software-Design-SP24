from flask import session, redirect, render_template, request
from flask.views import MethodView
from models import db, UserCredentials, ClientInformation

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
            if user.first_login:
                # Redirect to the profile management page
                return redirect('/profile')
            else:
                # Redirect to the home page
                return redirect('/home')
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
            full_name = request.form.get('full_name')
            address1 = request.form.get('address1')
            address2 = request.form.get('address2')
            city = request.form.get('city')
            state = request.form.get('state')
            zipcode = request.form.get('zipcode')
            user.first_login = False

            new_profile = ClientInformation()
            new_profile.full_name = full_name
            new_profile.address1 = address1
            new_profile.address2 = address2
            new_profile.city = city
            new_profile.state = state
            new_profile.zipcode = zipcode
            db.session.add(new_profile)
            user.client_info_id = new_profile.id 
            db.session.commit()
            return redirect('/home')
        else:
            return redirect('/login')

class Home(MethodView):
    init_every_request = False

    def get(self):
        if 'username' in session:
            # Get the logged-in user's username
            user_credentials = UserCredentials.query.filter_by(username=session['username']).first()

            if user_credentials:
                # Get the associated client_info_id
                client_info_id = user_credentials.client_info_id

                # Query the ClientInformation table based on the client_info_id
                client_info = ClientInformation.query.filter_by(id=client_info_id).first()

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

def add_endpoints(app):
    app.add_url_rule("/register", view_func=Register.as_view("Register"))
    app.add_url_rule("/profile", view_func=Profile.as_view("Profile"))
    app.add_url_rule("/home", view_func=Home.as_view("Home"))
    app.add_url_rule("/login", view_func=Login.as_view("Login"))
    app.add_url_rule("/logout", view_func=Logout.as_view("Logout"))