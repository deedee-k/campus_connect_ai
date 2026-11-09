import os, random
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(
    os.path.join(HERE, "data", "books.csv"),
    sep=";",
    encoding="latin-1",
    on_bad_lines="skip",
)

df = df.dropna(subset=["Book-Title", "Book-Author"])
df = df[df["Year-Of-Publication"].astype(str).str.isdigit()]
df = df.sample(n=min(2000, len(df)), random_state=42).reset_index(drop=True)

rows = []
for _, r in df.iterrows():
    title = str(r["Book-Title"])[:120]
    author = str(r["Book-Author"])[:80]
    year = int(r["Year-Of-Publication"])
    publisher = str(r.get("Publisher", "Unknown"))[:80]
    image = str(r.get("Image-URL-M", ""))

    age = max(0, 2025 - year)
    base = 400 - age * 3
    price = max(80, min(800, base + random.randint(-60, 60)))

    rows.append({
        "title": title,
        "description": f"By {author}. Published by {publisher} in {year}. Used but in good condition.",
        "price": round(price, 2),
        "category": "Textbooks",
        "condition": random.choice(["Good", "Like new", "Fair"]),
        "image_url": image if image.startswith("http") else f"https://picsum.photos/seed/book{random.randint(1, 999)}/600/450",
    })

out = pd.DataFrame(rows)
out.to_csv(os.path.join(HERE, "data", "books_seed.csv"), index=False)
print(f"Wrote {len(out)} book listings to data/books_seed.csv")