import os, random
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))

path = os.path.join(HERE, "data", "mobile_sales_data.csv")
try:
    df = pd.read_csv(path, sep="\t", encoding="utf-8", on_bad_lines="skip")
    if len(df.columns) < 3:
        raise ValueError("tab parse produced too few columns")
except Exception:
    df = pd.read_csv(path, sep=",", encoding="utf-8", on_bad_lines="skip")

print(f"Loaded {len(df)} rows, columns: {list(df.columns)}")

if "Product" not in df.columns:
    raise SystemExit(f"'Product' column not found. Columns are: {list(df.columns)}")

df = df.dropna(subset=["Product"]).drop_duplicates(subset=["Product"]).reset_index(drop=True)
print(f"Unique products: {len(df)}")

df = df.sample(n=min(1000, len(df)), random_state=42).reset_index(drop=True)

rows = []
for _, r in df.iterrows():
    product = str(r["Product"])[:120]
    brand = str(r.get("Brand", "")).strip()
    spec = str(r.get("Product Specification", "") or "")
    core = str(r.get("Core Specification", "") or "")
    processor = str(r.get("Processor Specification", "") or "")

    try:
        price = float(str(r["Price"]).replace(",", "").strip())
    except Exception:
        price = None

    if price is None or price <= 0:
        price = round(random.uniform(1500, 8000), 2)

    if price > 20000:
        price = round(price / 10, 2)

    description_parts = [p for p in [spec, core, processor] if p and p != "nan"]
    description = " ".join(description_parts)[:400] or f"{brand} device in working condition."
    if len(description) < 20:
        description = f"{brand} {product} — used but in good working condition."

    # Use a stable image per product
    seed = abs(hash(product)) % 9999

    rows.append({
        "title": f"{brand} {product}".strip()[:120] if brand else product,
        "description": description,
        "price": price,
        "category": "Electronics",
        "condition": random.choice(["Good", "Like new", "Fair"]),
        "image_url": f"https://picsum.photos/seed/mobile{seed}/600/450",
    })

out = pd.DataFrame(rows)
out.to_csv(os.path.join(HERE, "data", "mobiles_seed.csv"), index=False)
print(f"Wrote {len(out)} mobile listings to data/mobiles_seed.csv")