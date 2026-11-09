import os
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, cross_val_score, learning_curve
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.impute import SimpleImputer

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data", "data.csv")
MODEL_DIR = os.path.join(HERE, "model")
os.makedirs(MODEL_DIR, exist_ok=True)

# ─── 1. Load ──────────────────────────────────────────────────────────
print("Loading dataset…")
df = pd.read_csv(DATA)
print(f"  rows: {len(df):,}   columns: {len(df.columns)}")

# ─── 2. Clean target ──────────────────────────────────────────────────
target = "normalized_used_price"
if target not in df.columns:
    raise SystemExit(f"Target column '{target}' not found. "
                     f"Columns: {list(df.columns)}")

before = len(df)
df = df.dropna(subset=[target])
df = df[df[target] > 0]
df = df.reset_index(drop=True)
print(f"  dropped {before - len(df)} rows with missing/invalid price "
      f"({len(df):,} remain)")

# Rescale normalized price (~0-1) to a plausible "M" range
df["price_m"] = df[target] * 2500

# ─── 3. Coerce numeric columns ────────────────────────────────────────
# Any column that might come in as text like "4500 mAh" gets its digits
# extracted. Anything that ends up mostly NaN is dropped from numeric.
numeric_candidates = [
    "screen_size", "rear_camera_mp", "front_camera_mp",
    "internal_memory", "ram", "battery", "weight",
    "release_year", "days_used",
]

for col in numeric_candidates:
    if col in df.columns:
        # Extract first number found in each value (handles "6.5 inches", "4500mAh")
        df[col] = pd.to_numeric(
            df[col].astype(str).str.extract(r"(-?\d+\.?\d*)")[0],
            errors="coerce",
        )

# Only keep numeric columns with enough real values
numeric = [c for c in numeric_candidates
           if c in df.columns and df[c].notna().sum() > len(df) * 0.5]

# Categorical: strings + yes/no flags
categorical = [c for c in ["device_brand", "os", "4g", "5g"]
               if c in df.columns]

print(f"  categorical: {categorical}")
print(f"  numeric:     {numeric}")

X = df[categorical + numeric]
y = df["price_m"]

# ─── 4. Pipeline ──────────────────────────────────────────────────────
preprocessor = ColumnTransformer(
    transformers=[
        ("cat", Pipeline([
            ("imp", SimpleImputer(strategy="most_frequent")),
            ("ohe", OneHotEncoder(handle_unknown="ignore")),
        ]), categorical),
        ("num", Pipeline([
            ("imp", SimpleImputer(strategy="median")),
            ("sc",  StandardScaler()),
        ]), numeric),
    ],
    remainder="drop",
)

pipeline = Pipeline([
    ("prep", preprocessor),
    ("rf", RandomForestRegressor(
        n_estimators=200,
        max_depth=15,
        min_samples_leaf=4,
        random_state=42,
        n_jobs=-1,
    )),
])

# ─── 5. Split + Train ─────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"\nTraining on {len(X_train):,} samples, testing on {len(X_test):,}…")
pipeline.fit(X_train, y_train)

# ─── 6. Evaluate ──────────────────────────────────────────────────────
pred_train = pipeline.predict(X_train)
pred_test  = pipeline.predict(X_test)

metrics = {
    "n_total":    int(len(df)),
    "n_train":    int(len(X_train)),
    "n_test":     int(len(X_test)),
    "n_features": int(len(categorical) + len(numeric)),
    "mae_train":  float(mean_absolute_error(y_train, pred_train)),
    "mae":        float(mean_absolute_error(y_test, pred_test)),
    "rmse":       float(np.sqrt(mean_squared_error(y_test, pred_test))),
    "r2_train":   float(r2_score(y_train, pred_train)),
    "r2":         float(r2_score(y_test, pred_test)),
}

print("\n─── Metrics ───")
for k, v in metrics.items():
    print(f"  {k:12s} {v}")

# Cross-validation
print("\n5-fold cross-validation…")
cv_r2 = cross_val_score(pipeline, X, y, cv=5, scoring="r2", n_jobs=-1)
metrics["cv_r2_mean"] = float(cv_r2.mean())
metrics["cv_r2_std"]  = float(cv_r2.std())
print(f"  cv R² = {cv_r2.mean():.3f} ± {cv_r2.std():.3f}")

# ─── 7. Save model ────────────────────────────────────────────────────
model_path = os.path.join(MODEL_DIR, "price_model.joblib")
joblib.dump(pipeline, model_path)
print(f"\nSaved model → {model_path}")

# ─── 8. Learning curve ────────────────────────────────────────────────
print("\nGenerating learning curve…")
train_sizes, train_scores, val_scores = learning_curve(
    pipeline, X, y,
    train_sizes=np.linspace(0.1, 1.0, 8),
    cv=3, scoring="r2", n_jobs=-1,
)

train_mean = train_scores.mean(axis=1)
val_mean   = val_scores.mean(axis=1)
val_std    = val_scores.std(axis=1)

plt.figure(figsize=(9, 5))
plt.plot(train_sizes, train_mean, "o-", label="Training R²", color="#7c3aed")
plt.plot(train_sizes, val_mean,   "s-", label="Validation R²", color="#f59e0b")
plt.fill_between(train_sizes, val_mean - val_std, val_mean + val_std,
                 alpha=0.15, color="#f59e0b")
plt.xlabel("Training samples")
plt.ylabel("R² score")
plt.title("Learning curve — where does more data stop helping?")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(HERE, "learning_curve.png"), dpi=120)
print("Saved → learning_curve.png")

# ─── 9. Saturation summary ────────────────────────────────────────────
deltas = np.diff(val_mean)
last_three_gain = float(deltas[-3:].mean())
metrics["last_three_gain"] = last_three_gain
metrics["saturated"] = bool(abs(last_three_gain) < 0.005)

with open(os.path.join(HERE, "metrics.json"), "w") as f:
    json.dump(metrics, f, indent=2)
print("Saved → metrics.json")

print(f"\nSaturation: last-3 average R² gain = {last_three_gain:+.4f}")
print(f"  → {'SATURATED' if metrics['saturated'] else 'still improving'}")

print("\n✓ Training complete.")