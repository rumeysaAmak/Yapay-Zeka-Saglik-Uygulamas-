import pandas as pd
data = pd.read_csv(r"C:\Users\Lenovo\Desktop\food_ingredients_and_allergens (1).csv")

categorical_features = ['Main Ingredient', 'Sweetener', 'Fat/Oil', 'Seasoning']

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# web uygulamama uygun olarak Label Encoding tercih ettim.
label_encoders = {}
for feature in categorical_features:
    le = LabelEncoder()
    data[feature] = le.fit_transform(data[feature])
    label_encoders[feature] = le

data['Prediction'] = data['Prediction'].apply(lambda x: 1 if x == 'Contains' else 0)

X = data[categorical_features]
y = data['Prediction']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

from sklearn.ensemble import RandomForestClassifier
import pickle

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
print(f"Accuracy: {accuracy_score(y_test, y_pred)}")
print("Classification Report:")
print(classification_report(y_test, y_pred))
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

with open('model.pickle', 'wb') as file:
    pickle.dump(model, file)

with open('label_encoders.pickle', 'wb') as file:
    pickle.dump(label_encoders, file)