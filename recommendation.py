from models import Book

# Global list to store the most recent recommendation logs for the admin dashboard
recommendation_logs = []

# Simple cache for book tokens to improve performance
token_cache = {}

def get_recommendations(book_id, num_recommendations=4):
    """
    Returns a list of Book objects similar to the given book_id.
    Uses Jaccard Similarity on Title + Genre + Description.
    Prints similarity scores to the console.
    """
    books = Book.query.all()
    if not books:
        return []

    # Find the target book
    target_book = None
    for b in books:
        if b.id == book_id:
            target_book = b
            break
            
    if not target_book:
        return []

    def get_tokens(book):
        # Combine title, genre, and description for content matching
        content = f"{book.title} {book.genre} {book.description}"
        # Tokenize and remove small words/punctuation could be better, 
        # but simple split is common for Jaccard examples
        return set(content.lower().split())

    target_tokens = get_tokens(target_book)
    
    sim_scores = []
    # Optimization: Use token cache and pre-calculate target tokens
    for book in books:
        if book.id == book_id:
            continue
        
        # Get tokens from cache or calculate
        if book.id in token_cache:
            book_tokens = token_cache[book.id]
        else:
            book_content = f"{book.title} {book.genre} {book.description}"
            book_tokens = set(book_content.lower().split())
            token_cache[book.id] = book_tokens
        
        intersection = len(target_tokens.intersection(book_tokens))
        union = len(target_tokens.union(book_tokens))
        score = intersection / union if union > 0 else 0
        sim_scores.append((book, score))

    # Sort by score descending
    sim_scores.sort(key=lambda x: x[1], reverse=True)

    # Get top N
    top_recommendations = sim_scores[:num_recommendations]

    # Print Jaccard Similarity Percentage to console (Server-side)
    print(f"\n[Jaccard Similarity] Recommendations for: \"{target_book.title}\"")
    print("-" * 60)
    for i, (book, score) in enumerate(top_recommendations, 1):
        print(f"{i}. {book.title:<40} | Score: {score:.4f} ({score*100:.2f}%)")
        # Attach score to book object
        book.jaccard_score = score

    # Store in global logs for Admin Panel
    from datetime import datetime
    log_entry = {
        'timestamp': datetime.now().strftime("%H:%M:%S"),
        'target_book': target_book.title,
        'recommendations': [
            {'title': b.title, 'score': s} for b, s in top_recommendations
        ]
    }
    recommendation_logs.insert(0, log_entry)
    if len(recommendation_logs) > 10:
        recommendation_logs.pop()

    print("-" * 60 + "\n")

    return [item[0] for item in top_recommendations]
