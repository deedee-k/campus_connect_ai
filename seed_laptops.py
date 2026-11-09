import os
import pandas as pd
from supabase import create_client

URL = "https://hdrdzwjdojmxvmftdckd.supabase.co"
KEY = os.environ.get("SUPABASE_KEY", "PASTE_YOUR_SECRET_KEY_HERE" )
SELLER_ID = "03715e1e-e0fe-4452-a428-7604fbd1046e"

supabase = create_client(URL, KEY)
HERE = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(HERE, "data", "laptops_seed.csv"))


seller = supabase.table("profiles").select("id, name").eq("email", "tiisetsolerotha@gmail.com").single().execute()
seller_id = seller.data["id"]
seller_name = seller.data["name"]

records = df.to_dict(orient="records")
for r in records:
    r["seller_id"] = seller_id
    r["seller_name"] = seller_name
    r["status"] = "active"
    r["views"] = 0
    r["risk_score"] = 0

print(f"Inserting {len(records)} laptops for {seller_name}...")
result = supabase.table("listings").insert(records).execute()
print(f"Inserted {len(result.data)} laptops")