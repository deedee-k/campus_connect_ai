import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(HERE, "data", "data.csv"))
df = df.dropna(subset=["normalized_used_price"])
df["price_m"] = df["normalized_used_price"] * 2500


plt.figure(figsize=(9, 4))
plt.hist(df["price_m"], bins=40, color="#7c3aed", edgecolor="white")
plt.xlabel("Price (M)")
plt.ylabel("Listings")
plt.title("Distribution of used-device prices in the dataset")
plt.tight_layout()
plt.savefig(os.path.join(HERE, "price_distribution.png"), dpi=120)
plt.close()


if "device_brand" in df.columns:
    top_brands = df["device_brand"].value_counts().nlargest(8).index
    subset = df[df["device_brand"].isin(top_brands)]
    plt.figure(figsize=(10, 5))
    subset.boxplot(column="price_m", by="device_brand", grid=False, color="#7c3aed")
    plt.suptitle("")
    plt.title("Price by device brand")
    plt.ylabel("Price (M)")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(os.path.join(HERE, "price_by_brand.png"), dpi=120)
    plt.close()


if "days_used" in df.columns:
    df["days_used_num"] = pd.to_numeric(
        df["days_used"].astype(str).str.extract(r"(-?\d+\.?\d*)")[0],
        errors="coerce",
    )
    plt.figure(figsize=(9, 4))
    plt.scatter(df["days_used_num"], df["price_m"], alpha=0.3, color="#f59e0b", s=10)
    plt.xlabel("Days used")
    plt.ylabel("Price (M)")
    plt.title("Price decreases with usage")
    plt.tight_layout()
    plt.savefig(os.path.join(HERE, "price_vs_age.png"), dpi=120)
    plt.close()

print("Saved 3 plots to the ai-service folder:")
print("  price_distribution.png")
print("  price_by_brand.png")
print("  price_vs_age.png")