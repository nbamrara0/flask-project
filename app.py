from dotenv import load_dotenv
load_dotenv()
from flask import Flask, render_template, request, session, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
import pickle
import os

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")
database_url = os.getenv("DATABASE_URL")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "connect_args": {"sslmode": "require"}
}

db = SQLAlchemy(app)
# ---------------- LOAD MODEL ----------------
model = pickle.load(open('model.pkl', 'rb'))

# Database Table
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(100), nullable=False)

    password = db.Column(db.String(100), nullable=False)
    def __repr__(self):
        return f"{self.id} - {self.username} - {self.email}"
# Create Database
with app.app_context():
    db.create_all()


# Login Page First
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")

        email = request.form.get("email")

        password = request.form.get("password")

        # Save Data
        user = User(
            username=username,
            email=email,
            password=password
        )

        db.session.add(user)

        db.session.commit()

        # Go To Home Page
        return redirect(url_for("home"))

    return render_template("login.html")


# ---------------- HOME PAGE ----------------
@app.route('/home')
def home():
    all_data = Prediction.query.all()
    return render_template('index.html', all_data=all_data)


# ---------------- DATABASE TABLE ----------------
class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.Float, nullable=False)
    bedrooms = db.Column(db.Integer, nullable=False)
    bathrooms = db.Column(db.Integer, nullable=False)
    predicted_price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"{self.id} - {self.predicted_price}"

# Create DB
with app.app_context():
    try:
        db.create_all()
        print("Database connected successfully!")
    except Exception as e:
        print(f"Database error: {e}")

# ---------------- PREDICT ----------------
@app.route('/predict', methods=['POST'])
def predict():

    area = float(request.form['area'])
    bedrooms = int(request.form['bedrooms'])
    bathrooms = int(request.form['bathrooms'])

    features = [[area, bedrooms, bathrooms]]

    prediction = model.predict(features)
    output = float(round(prediction[0], 2))

    # SAVE TO DATABASE (FIXED)
    data = Prediction(
        area=area,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        predicted_price=output
    )

    db.session.add(data)
    db.session.commit()

    prediction_text = f"Predicted Price: ₹ {output:,.2f}"

    all_data = Prediction.query.all()

    return render_template(
        "index.html",
        prediction_text=prediction_text,
        all_data=all_data
    )
# Admin credentials — environment se lo
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@gmail.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")


# Admin login route
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('show_data'))
        else:
            return render_template('admin_login.html', error="Wrong credentials!")
    return render_template('admin_login.html')

@app.route('/show-data')
def show_data():
    if not session.get('admin'):
        return redirect (url_for('admin_login'))
    entries = Prediction.query.all()
    result = []
    for e in entries:
        result.append({
            'id': e.id,
            'area': e.area,
            'bedrooms': e.bedrooms,
            'bathrooms': e.bathrooms,
            'price': e.predicted_price
        })
        entries = Prediction.query.all()
        # Login Users Data
        users = User.query.all()
    return render_template('show_data.html',  entries=entries)
# ---------------- RUN APP ----------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    # https://flask-project-1-foev.onrender.com url