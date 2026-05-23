from dotenv import load_dotenv
load_dotenv()
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import pickle
import os

app = Flask(__name__)


database_url = os.getenv("DATABASE_URL")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "connect_args": {"sslmode": "require"}
}

db = SQLAlchemy(app)
# ---------------- LOAD MODEL ----------------
model = pickle.load(open('model.pkl', 'rb'))

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

# ---------------- HOME PAGE ----------------
@app.route('/')
def home():
    all_data = Prediction.query.all()
    return render_template('index.html', all_data=all_data)

# ---------------- PREDICT ----------------
@app.route('/predict', methods=['POST'])
def predict():

    area = float(request.form['area'])
    bedrooms = int(request.form['bedrooms'])
    bathrooms = int(request.form['bathrooms'])

    features = [[area, bedrooms, bathrooms]]

    prediction = model.predict(features)
    output = float(round(prediction[0], 2))

    # ✅ SAVE TO DATABASE (FIXED)
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

@app.route('/show-data')
def show_data():
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
    return render_template('show_data.html',  entries=entries)
# ---------------- RUN APP ----------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    # https://flask-project-1-foev.onrender.com url