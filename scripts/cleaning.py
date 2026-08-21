import pandas as pd
import requests
import os
import random
import re

DATASET_URL = "https://raw.githubusercontent.com/zygmuntz/goodbooks-10k/master/books.csv"
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'cleaned_books.csv')

def download_data():
    print(f"Downloading dataset from {DATASET_URL}...")
    try:
        df = pd.read_csv(DATASET_URL)
        return df
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        return None

def clean_data(df):
    print("Cleaning data...")
    
    # 1. Fill NaN
    df.fillna('', inplace=True)
    
    # 2. Clean Titles (remove series info in brackets)
    def clean_title(title):
        return re.sub(r'\s*\(.*?\)\s*', '', str(title)).strip()
    
    df['clean_title'] = df['original_title'].fillna(df['title']).apply(clean_title)
    
    # 3. Enrich with Genres (Simulated)
    print("Enriching with genres...")
    genres = ["Fiction", "Fantasy", "Science Fiction", "Mystery", "Thriller", "Romance", "History", "Biography", "Business"]
    
    def assign_genre(row):
        # Very basic keyword matching, otherwise random
        title_lower = str(row['clean_title']).lower()
        if 'harry potter' in title_lower: return "Fantasy"
        if 'history' in title_lower: return "History"
        return random.choice(genres)

    df['genre'] = df.apply(assign_genre, axis=1)

    # 4. Generate Descriptions
    print("Generating descriptions...")
    def generate_description(row):
        return f"A compelling {row['genre']} novel by {row['authors']}. '{row['clean_title']}' has captivated readers with its engaging narrative and deep character development. Rated {row['average_rating']} stars on Goodreads."

    df['description'] = df.apply(generate_description, axis=1)

    # 5. Fix Image URLs (Goodreads images in csv might be small or missing)
    def fix_image(url):
        if not url or 'nophoto' in str(url):
            return "https://placehold.co/400x600?text=No+Cover"
        return url
        
    df['image_url'] = df['image_url'].apply(fix_image)
    
    return df

def main():
    df = download_data()
    if df is not None:
        cleaned_df = clean_data(df)
        
        # Select relevant columns
        final_df = cleaned_df[['clean_title', 'authors', 'genre', 'description', 'image_url', 'average_rating']]
        final_df.rename(columns={'clean_title': 'title', 'average_rating': 'rating'}, inplace=True)
        
        # Save
        final_df.to_csv(OUTPUT_PATH, index=False, encoding='utf-8')
        print(f"Successfully saved cleaned data to {OUTPUT_PATH}")
        print(final_df.head())

if __name__ == "__main__":
    main()
