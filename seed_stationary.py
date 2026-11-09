import os
import random
from supabase import create_client

# ─── CONFIGURATION ──────────────────────────────────────────────

URL = "https://hdrdzwjdojmxvmftdckd.supabase.co"
KEY = os.environ.get("SUPABASE_KEY", "PASTE_YOUR_SECRET_KEY_HERE" )
SELLER_ID = "03715e1e-e0fe-4452-a428-7604fbd1046e"


DATASET_FOLDER = r"C:\Users\Rosalie\Downloads\archive\Stationary Dataset\test\images"
SELLER_EMAIL = "majaramasupha221@gmail.com" 
# ────────────────────────────────────────────────────────────────

supabase = create_client(URL, KEY)

# 1. Get Seller ID
seller = supabase.table("profiles").select("id, name").eq("email", SELLER_EMAIL).single().execute()
if not seller.data:
    print(f"Error: Could not find seller {SELLER_EMAIL}")
    exit()
    
seller_id = seller.data["id"]
seller_name = seller.data["name"]
print(f"Found Seller: {seller_name}")

# 2. Get list of images
valid_exts = ('.jpg', '.jpeg', '.png')
images = [f for f in os.listdir(DATASET_FOLDER) if f.lower().endswith(valid_exts)]
print(f"Found {len(images)} images in folder.")

# 3. Process each image
STATIONERY_ITEMS = ['Pen', 'Notebook', 'Calculator', 'Highlighter', 'Folder', 'Stapler', 'Ruler', 'Pencil Case']
inserted_count = 0

for filename in images[:40]: # Limit to 40 items so it doesn't take too long
    file_path = os.path.join(DATASET_FOLDER, filename)
    
    # Upload to Supabase Storage
    storage_path = f"stationery/{filename}"
    try:
        with open(file_path, 'rb') as f:
            supabase.storage.from_('listings').upload(storage_path, f)
    except Exception as e:
        # If the file is already uploaded, ignore the error and continue
        if "Duplicate" not in str(e) and "already exists" not in str(e):
            print(f"Failed to upload {filename}: {e}")
            continue

    # Get Public URL
    public_url = supabase.storage.from_('listings').get_public_url(storage_path)
    
    # Generate Listing Data
    item_type = random.choice(STATIONERY_ITEMS)
    # Make up a price between M 20 and M 250
    price = round(random.uniform(20, 250), 2)
    
    listing = {
        "title": f"{item_type} - {filename.split('.')[0].title()}",
        "description": f"Brand new {item_type.lower()} for campus use. Perfect for lectures and exams.",
        "price": price,
        "category": "Stationery",
        "condition": random.choice(["New", "Like new", "Good"]),
        "image_url": public_url,
        "seller_id": seller_id,
        "seller_name": seller_name,
        "status": "active",
        "stock": 20,
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

print(f"\n🎉 Done! Inserted {inserted_count} stationery items.")