"""Convert the device dataset into CampusConnect listing rows."""
import os, pandas as pd
from datetime import datetime, timedelta
import random

HERE = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(HERE, "data", "data.csv"))

# Drop rows without price
df = df.dropna(subset=["normalized_used_price"])
df = df[df["normalized_used_price"] > 0].copy()

# Sample 60 rows
random.seed(42)
df = df.sample(n=min(100, len(df)), random_state=42).reset_index(drop=True)

# Build listing rows
CATEGORY = "Electronics"
rows = []
for _, r in df.iterrows():
    brand = str(r.get("device_brand", "Device")).title()
    os_ = str(r.get("os", "Android"))
    storage = int(float(r.get("internal_memory", 128) or 128))
    ram = int(float(r.get("ram", 6) or 6))
    year = int(float(r.get("release_year", 2022) or 2022))
    days = int(float(r.get("days_used", 365) or 365))
    battery = int(float(r.get("battery", 5000) or 5000))
    screen = float(r.get("screen_size", 6.5) or 6.5)
    price = float(r["normalized_used_price"]) * 2500

    title = f"{brand} {storage}GB Smartphone ({year})"
    description = (
        f"Used {brand} smartphone running {os_}. "
        f"{storage}GB storage, {ram}GB RAM, {screen}\" screen, {battery}mAh battery. "
        f"Released in {year}, used for approximately {days} days. "
        f"Good working condition, minor wear."
    )

    rows.append({
        "title": title,
        "description": description,
        "price": round(price, 2),
        "category": CATEGORY,
        "condition": "Good" if days > 365 else "Like new",
        "image_url": f"https://picsum.photos/seed/{brand}-{year}-{storage}/600/450",
        "days_used": days,
        "device_brand": brand,
        "os": os_,
        "internal_memory": storage,
        "ram": ram,
        "release_year": year,
    })

out = pd.DataFrame(rows)
out.to_csv(os.path.join(HERE, "data", "listings_seed.csv"), index=False)
print(f"Wrote {len(out)} rows to data/listings_seed.csv")