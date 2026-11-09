import pandas as pd
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# 1. Load your laptop dataset (Make sure the file is named laptops.csv and is in the data folder)
df = pd.read_csv(os.path.join(HERE, "data", "laptop.csv"))

df = df.head(500).copy()

rows = []
for _, r in df.iterrows():
    brand = str(r.get("Brand", "Laptop")).title()
    name = str(r.get("Name", "Model")).title()
    price = float(r.get("Price", 5000))
    
    # Extract specs for the description
    processor = f"{r.get('Processor_Brand', '')} {r.get('Processor_Name', '')}".strip()
    ram = f"{r.get('RAM', '8')}GB {r.get('RAM_TYPE', 'DDR4')}"
    storage = f"{r.get('SSD', '256')}GB SSD"
    display = f"{r.get('Display', '15.6')} inch {r.get('Display_type', 'IPS')}"
    
    description = f"Used {brand} laptop. Specs: {processor}, {ram} RAM, {storage}, {display} display."
    
    rows.append({
        "title": f"{brand} {name}",
        "description": description,
        "price": round(price, 2),
        "category": "Electronics",
        "condition": "Good",
        "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800", # Nice laptop image
    })

out = pd.DataFrame(rows)
out.to_csv(os.path.join(HERE, "data", "laptops_seed.csv"), index=False)
print(f"Wrote {len(out)} laptop listings to data/laptops_seed.csv")