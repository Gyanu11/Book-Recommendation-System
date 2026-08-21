import csv
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, Book

app = create_app()

def import_books(csv_path):
    with app.app_context():
        if not os.path.exists(csv_path):
            print(f"File not found: {csv_path}")
            return

        print(f"Importing from {csv_path}...")
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                # Adjust column names based on the actual Kaggle CSV structure
                # Typically: bookID, title, authors, average_rating, isbn, language_code, num_pages, ratings_count, text_reviews_count, publication_date, publisher
                
                try:
                    title = row.get('title')
                    authors = row.get('authors')
                    # Simple heuristic for genre or description if missing
                    
                    if title and authors:
                        book = Book(
                            title=title,
                            author=authors,
                            genre="General", # Placeholder
                            description=f"A book by {authors}",
                            cover_url="https://placehold.co/400x600?text=No+Cover",
                            price=19.99,
                            buy_link=f"https://www.amazon.com/s?k={title.replace(' ', '+')}"
                        )
                        db.session.add(book)
                        count += 1
                        
                        if count % 100 == 0:
                            db.session.commit()
                            print(f"Imported {count} books...")
                except Exception as e:
                    print(f"Skipping row due to error: {e}")
            
            db.session.commit()
            print(f"Successfully imported {count} books.")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        import_books(sys.argv[1])
    else:
        print("Usage: python import_csv.py <path_to_goodreads_books.csv>")
