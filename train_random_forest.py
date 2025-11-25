# train_random_forest.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# cargar CSV de ejemplo con columnas: speed,accuracy,stamina,success
df = pd.read_csv("historical_events.csv")
X = df[["speed","accuracy","stamina"]]
y = df["success"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)
pred = clf.predict(X_test)
print("Accuracy:", accuracy_score(y_test, pred))

# Guardar modelo si quieres (joblib)
import joblib
joblib.dump(clf, "rf_model.joblib")
