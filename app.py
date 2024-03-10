from flask import Flask
from models import db
from views import add_endpoints

app = Flask(__name__)
app.secret_key = 'your_secret_key'

if __name__ == '__main__':
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydatabase.db"
    db.init_app(app)
    with app.app_context():
        db.create_all()
        add_endpoints(app)
    app.run(debug=True)