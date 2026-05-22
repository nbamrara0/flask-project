from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import pickle
import numpy as np
import os

app = Flask(__name__)

# DATABASE URL
database_url = os.environ.get("DATABASE_URL")

# Local or Render Database
if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://naveen:9jlCrOzliDSz0lfMLF3AoI8c6byumTIG@dpg-d8836pgg4nts73eogpmg-a.oregon-postgres.render.com/house_db_bqk1'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
    db.create_all()

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

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    # https://flask-project-1-foev.onrender.com url