import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data", "safety.csv")

# Load the dataset
df = pd.read_csv(DATA)

# We will use the 'label' column as our target (0 = safe, 1 = unsafe)
# Assuming the labels are already 0/1 or text we can map
X = df['label'].astype(str) # Using label as a proxy for text features in this demo
y = df['kids'].apply(lambda x: 0 if x else 1) # 0 = safe (kids allowed), 1 = unsafe

# Build a simple model
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('clf', LogisticRegression())
])

pipeline.fit(X, y)
joblib.dump(pipeline, os.path.join(HERE, "model", "safety_model.joblib"))
print("Safety model trained and saved!")