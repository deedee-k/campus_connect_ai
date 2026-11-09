import os
import random
import kagglehub
from supabase import create_client

# ─── CONFIGURATION ──────────────────────────────────────────────

URL = "https://hdrdzwjdojmxvmftdckd.supabase.co"
KEY = os.environ.get("SUPABASE_KEY", "PASTE_YOUR_SECRET_KEY_HERE" )
SELLER_ID = "03715e1e-e0fe-4452-a428-7604fbd1046e"

# ────────────────────────────────────────────────────────────────

supabase = create_client(URL, KEY)

# 1. Download Dataset via Kagglehub
print("Downloading dataset from Kaggle...")
path = kagglehub.dataset_download("gustavofadel/clothes-dataset")
print(f"Dataset downloaded to: {path}")

# 2. Get Seller ID
seller = supabase.table("profiles").select("id, name").eq("email", SELLER_EMAIL).single().execute()
if not seller.data:
    print(f"Error: Could not find seller {SELLER_EMAIL}")
    exit()
    
seller_id = seller.data["id"]
seller_name = seller.data["name"]

# 3. Find all images in the downloaded folder
valid_exts = ('.jpg', '.jpeg', '.png')
image_paths = []

for root, dirs, files in os.walk(path):
    for file in files:
        if file.lower().endswith(valid_exts):
            image_paths.append(os.path.join(root, file))

print(f"Found {len(image_paths)} images in the dataset.")

# Limit to 50 images for the demo
image_paths = image_paths[:50]

CLOTHES_ITEMS = ['T-Shirt', 'Jacket', 'Jeans', 'Dress', 'Hoodie', 'Sweater', 'Shorts', 'Skirt']
inserted_count = 0

# 4. Upload and Insert
for file_path in image_paths:
    filename = os.path.basename(file_path)
    
    # Upload to Supabase Storage
    storage_path = f"clothing/{filename}"
    try:
        with open(file_path, 'rb') as f:
            supabase.storage.from_('listings').upload(storage_path, f)
    except Exception as e:
        # Ignore if file already exists
        if "Duplicate" not in str(e) and "already exists" not in str(e):
            print(f"Failed to upload {filename}: {e}")
            continue

    # Get Public URL
    public_url = supabase.storage.from_('listings').get_public_url(storage_path)
    
    # Generate Listing Data
    item_type = random.choice(CLOTHES_ITEMS)
    price = round(random.uniform(100, 600), 2) # Random price between M100 and M600
    
    listing = {
        "title": f"{item_type} - {filename.split('.')[0].title()[:15]}",
        "description": f"Stylish {item_type.lower()} in great condition. Perfect for campus life.",
        "price": price,
        "category": "Clothing",
        "condition": random.choice(["New", "Like new", "Good"]),
        "image_url": public_url,
        "seller_id": seller_id,
        "seller_name": seller_name,
        "status": "active",
        "stock": 10,
        "views": 0,
        "risk_score": 0
    }
    
    # Insert into Database
    try:
        supabase.table("listings").insert(listing).execute()
        inserted_count += 1
        print(f"✅ Added: {listing['title']}")
    except Exception as e:
        print(f"Failed to insert {filename}: {e}")

print(f"\n🎉 Done! Inserted {inserted_count} clothing items.")