import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
import pickle

# Sample data
data = {
    'area': [1000, 1200, 1500, 1800],
    'bedrooms': [2, 2, 3, 4],
    'bathrooms': [1, 2, 2, 3],
    'price': [3000000, 4000000, 5000000, 6500000]
}

df = pd.DataFrame(data)

# Features and target
X = df[['area', 'bedrooms', 'bathrooms']]
y = df['price']
# test and train split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Train model
model = LinearRegression()
model.fit(X, y)

#accurences
score = r2_score(y, model.predict(X))

print (score)
# Save model
pickle.dump(model, open('model.pkl', 'wb'))

print("Model saved successfully")
