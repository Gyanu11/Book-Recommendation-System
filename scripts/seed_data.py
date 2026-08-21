import sys
import os
import csv
import requests
import random
import re
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, User, Book, Review, Watchlist

app = create_app()

DATASET_URL = "https://raw.githubusercontent.com/zygmuntz/goodbooks-10k/master/books.csv"
CSV_PATH = os.path.join(os.path.dirname(__file__), 'books.csv')

def download_dataset():
    if os.path.exists(CSV_PATH):
        print(f"Dataset already exists at {CSV_PATH}")
        return

    print(f"Downloading dataset from {DATASET_URL}...")
    try:
        response = requests.get(DATASET_URL)
        response.raise_for_status()
        with open(CSV_PATH, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("Download complete.")
    except Exception as e:
        print(f"Failed to download dataset: {e}")
        sys.exit(1)

def clean_title(title):
    # Remove series info like " (Harry Potter, #1)"
    return re.sub(r'\s*\(.*?\)\s*', '', title).strip()

def seed_data():
    with app.app_context():
        print("--- Resetting Database ---")
        db.drop_all()
        db.create_all()

        # 1. Create Users
        print("--- Creating Users ---")
        users = []
        # Admin
        admin = User(username='admin', email='admin@example.com', is_admin=True)
        admin.set_password('password') # Changed to 'password' for consistency with README
        db.session.add(admin)
        users.append(admin)

        # Standard Users
        for i in range(5):
            u = User(username=f'user{i}', email=f'user{i}@example.com')
            u.set_password('password')
            db.session.add(u)
            users.append(u)
        
        db.session.commit()

        # 2. Download and Import Books
        # Cleaning/Download logic is now in scripts/cleaning.py
        CLEANED_CSV_PATH = os.path.join(os.path.dirname(__file__), 'cleaned_books.csv')
        
        if not os.path.exists(CLEANED_CSV_PATH):
             print("Cleaned dataset not found. Please run 'python scripts/cleaning.py' first.")
             return

        print("--- Importing Books from cleaned dataset ---")
        books_buffer = []
        
        with open(CLEANED_CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            
            for row in reader:
                if count >= 10000: # Increased limit for better recommendations
                    break
                
                try:
                    book = Book(
                        title=row['title'],
                        author=row['authors'],
                        genre=row['genre'], 
                        description=row['description'],
                        cover_url=row['image_url'],
                        price=round(random.uniform(9.99, 29.99), 2),
                        pdf_url="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
                    )
                    books_buffer.append(book)
                    count += 1
                except Exception as e:
                    print(f"Skipping row: {e}")

            db.session.add_all(books_buffer)
            db.session.commit()
            print(f"Imported {len(books_buffer)} books.")

        # 3. Create Reviews & Watchlist
        print("--- Generating Social Proof ---")
        books = Book.query.all()
        for book in books:
            # Random reviews
            if random.random() > 0.5:
                for _ in range(random.randint(1, 3)):
                    user = random.choice(users)
                    review = Review(
                        user_id=user.id,
                        book_id=book.id,
                        rating=random.randint(3, 5),
                        content=random.choice([
                            "Amazing read!", "Couldn't put it down.", "A bit slow but good.", 
                            "Highly recommended.", "The ending was shocking!", "A masterpiece.", "Not my cup of tea."
                        ]),
                        created_at=datetime.utcnow()
                    )
                    db.session.add(review)

            # Random watchlist adds
            if random.random() > 0.7:
                 user = random.choice(users)
                 status = random.choice(['want_to_read', 'reading', 'completed'])
                 entry = Watchlist(user_id=user.id, book_id=book.id, status=status)
                 db.session.add(entry)

        db.session.commit()
        print("--- Seeding Complete! ---")
        print("Login as: admin@example.com / password")

if __name__ == '__main__':
    seed_data()
