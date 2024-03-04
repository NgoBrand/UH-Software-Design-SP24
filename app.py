from flask import Flask, render_template
app = Flask(__name__)

@app.route('/login')
def home():

    return render_template('Login.html')

@app.route('/register')
def register():
    return render_template('Register.html')

if __name__ == '__main__':
    app.run(debug=True)
