from flask import Flask, render_template, request
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import pickle
import numpy as np
import os


app = Flask(__name__)

# ---------------- DATABASE CONFIG ----------------

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------- LOAD ML MODEL ----------------

model = pickle.load(open('model.pkl', 'rb'))

# ---------------- DATABASE TABLE ----------------

class Prediction(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    area = db.Column(db.Float, nullable=False)

    bedrooms = db.Column(db.Integer, nullable=False)

    bathrooms = db.Column(db.Integer, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    predicted_price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"{self.id} - {self.predicted_price}"


# Create database
with app.app_context():
    db.create_all()

# ---------------- HOME PAGE ----------------

@app.route('/')
def home():

    all_data = Prediction.query.all()

    return render_template(
        'index.html',
        all_data=all_data
    )

# ---------------- PREDICTION ----------------

@app.route('/predict', methods=['POST'])
def predict():

    # Get form data
    area = float(request.form['area'])

    bedrooms = int(request.form['bedrooms'])

    bathrooms = int(request.form['bathrooms'])

    # Convert into numpy array
    features = np.array([[area, bedrooms, bathrooms]])

    # Predict price

    prediction = model.predict(features)
    # prediction_text = f"Predicted Price: ₹ {prediction[0]:,.2f}"

    output = round(prediction[0], 2)

    # Save into database
    data = Prediction(
        area=area,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        # datetime=datetime.now(),
        predicted_price=output
    )

    db.session.add(data)
    db.session.commit()

    all_data = Prediction.query.all()

    prediction_text = f"Predicted Price: ₹ {prediction[0]:,.2f}"
    return render_template("index.html", prediction_text=prediction_text)

# ---------------- DELETE ----------------
#
# @app.route('/delete/<int:id>')
# def delete(id):
#
#     data = Prediction.query.filter_by(id=id).first()
#
#     db.session.delete(data)
#
#     db.session.commit()
#
#     return home()

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# deploy url https://flask-project-1-foev.onrender.com