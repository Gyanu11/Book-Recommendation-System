from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app, send_file
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Book, Watchlist, Review, CartItem, Order
from forms import LoginForm, RegistrationForm, SearchForm, BookForm, ReviewForm, ProfileForm
from sqlalchemy import func
import os

main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)
admin_bp = Blueprint('admin', __name__)

# --- Helper ---
def admin_required(f):
    from functools import wraps
    from flask import request
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('admin.login', next=request.full_path))
        if not current_user.is_admin:
            flash('You need admin privileges to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

# --- Auth Routes ---
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Welcome back! Logged in successfully.', 'success')
            
            # Redirect admins to admin dashboard
            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            
            # Secure Redirect: Prevent Open Redirect Vulnerabilities
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/') or next_page.startswith('//'):
                next_page = url_for('main.index')
            return redirect(next_page)
        else:
            flash('Invalid email or password. Please try again.', 'danger')
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Strip whitespace from inputs
        username = form.username.data.strip()
        email = form.email.data.strip()
        
        # Check for existing email
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please use a different email.', 'warning')
            return render_template('auth/register.html', form=form)
            
        # Check for existing username (FIX for IntegrityError)
        if User.query.filter_by(username=username).first():
            flash('Username already taken. Please choose another one.', 'warning')
            return render_template('auth/register.html', form=form)
        
        user = User(username=username, email=email)
        user.set_password(form.password.data)
        
        # Admin Logic: Only FIRST admin can be created
        admin_code = os.environ.get('ADMIN_CODE', 'ADMIN')
        if form.admin_code.data and form.admin_code.data.strip() == admin_code:
            # Check if ANY admin already exists
            existing_admin = User.query.filter_by(is_admin=True).first()
            if existing_admin:
                flash('An admin account already exists. Only one admin is allowed.', 'warning')
                user.is_admin = False 
            else:
                user.is_admin = True
                flash('Admin privileges granted!', 'success')
            
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Registration successful! Welcome to Bookify.', 'success')
        
        # Redirect admins to admin dashboard
        if user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth_bp.route('/reset-admin', methods=['GET', 'POST'])
def reset_admin():
    from forms import ResetAdminForm
    form = ResetAdminForm()
    if form.validate_on_submit():
        admin_code = os.environ.get('ADMIN_CODE', 'ADMIN')
        if form.admin_code.data.strip() == admin_code:
            admin_user = User.query.filter_by(is_admin=True).first()
            if admin_user:
                db.session.delete(admin_user)
                db.session.commit()
                flash('Current admin account has been deleted. You can now register a new admin.', 'success')
                return redirect(url_for('auth.register'))
            else:
                flash('No admin account found to delete.', 'info')
                return redirect(url_for('auth.register'))
        else:
            flash('Invalid Admin Code. Deletion denied.', 'danger')
    
    return render_template('auth/reset_admin.html', form=form)

# --- Main Routes ---
@main_bp.route('/')
def index():
    # Redirect admins to admin dashboard
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    
    page = request.args.get('page', 1, type=int)
    # Show random books with pagination
    books = Book.query.order_by(func.random()).paginate(page=page, per_page=12, error_out=False)
    
    # Get featured books (ordered by most recent first)
    featured_books = Book.query.filter_by(is_featured=True).order_by(Book.created_at.desc()).limit(6).all()
    
    # Get all genres for filter
    genres = db.session.query(Book.genre, func.count(Book.id)).group_by(Book.genre).order_by(func.count(Book.id).desc()).limit(10).all()
    
    return render_template('main/index.html', books=books, genres=genres, featured_books=featured_books)

@main_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    genre = request.args.get('genre', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort = request.args.get('sort', 'relevance')
    page = request.args.get('page', 1, type=int)
    
    books_query = Book.query
    
    if query:
        books_query = books_query.filter(
            (Book.title.ilike(f'%{query}%')) | 
            (Book.author.ilike(f'%{query}%')) |
            (Book.genre.ilike(f'%{query}%'))
        )
    if genre:
        books_query = books_query.filter(Book.genre.ilike(genre))
    if min_price is not None:
        books_query = books_query.filter(Book.price >= min_price)
    if max_price is not None:
        books_query = books_query.filter(Book.price <= max_price)
    
    # Sorting
    if sort == 'price_asc':
        books_query = books_query.order_by(Book.price.asc())
    elif sort == 'price_desc':
        books_query = books_query.order_by(Book.price.desc())
    elif sort == 'newest':
        books_query = books_query.order_by(Book.created_at.desc())
    elif sort == 'title':
        books_query = books_query.order_by(Book.title.asc())
    
    books = books_query.paginate(page=page, per_page=12, error_out=False)
    
    # Get all genres for filter dropdown
    genres = db.session.query(Book.genre).distinct().all()
    genres = [g[0] for g in genres if g[0]]
    
    # Get recommendations based on first result
    recommendations = []
    if books.items:
        from recommendation import get_recommendations
        recommendations = get_recommendations(books.items[0].id, num_recommendations=4)
    
    return render_template('main/search_results.html', books=books, query=query, recommendations=recommendations, genres=genres, selected_genre=genre, min_price=min_price, max_price=max_price, sort=sort)

@main_bp.route('/book/<int:book_id>')
def book_details(book_id):
    book = Book.query.get_or_404(book_id)
    reviews = Review.query.filter_by(book_id=book_id).order_by(Review.created_at.desc()).all()
    
    has_purchased = False
    in_watchlist = False
    in_cart = False
    
    if current_user.is_authenticated:
        # Check if user owns the book
        if current_user.library.filter_by(id=book.id).first():
            has_purchased = True
        # Check if in watchlist
        if Watchlist.query.filter_by(user_id=current_user.id, book_id=book_id).first():
            in_watchlist = True
        # Check if in cart
        if CartItem.query.filter_by(user_id=current_user.id, book_id=book_id).first():
            in_cart = True
            
    # Get Recommendations
    from recommendation import get_recommendations
    recommendations = get_recommendations(book.id)
    
    # Calculate average rating
    avg_rating = 0
    if reviews:
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
    
    return render_template('main/book_detail.html', book=book, reviews=reviews, has_purchased=has_purchased, recommendations=recommendations, in_watchlist=in_watchlist, in_cart=in_cart, avg_rating=avg_rating)

# --- Library (Purchased Books) ---
@main_bp.route('/library')
@login_required
def library():
    # Redirect admins to admin dashboard
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    library_books = current_user.library.all()
    return render_template('main/library.html', books=library_books)

# --- Watchlist (Want to Read) ---
@main_bp.route('/watchlist')
@login_required
def watchlist():
    # Redirect admins to admin dashboard
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    watchlist_items = Watchlist.query.filter_by(user_id=current_user.id).order_by(Watchlist.added_at.desc()).all()
    return render_template('main/watchlist.html', items=watchlist_items)

@main_bp.route('/watchlist/add/<int:book_id>', methods=['POST'])
@login_required
def add_to_watchlist(book_id):
    book = Book.query.get_or_404(book_id)
    if Watchlist.query.filter_by(user_id=current_user.id, book_id=book_id).first():
        flash('Already in watchlist', 'info')
    else:
        item = Watchlist(user_id=current_user.id, book_id=book_id)
        db.session.add(item)
        db.session.commit()
        flash('Added to watchlist', 'success')
    return redirect(url_for('main.book_details', book_id=book_id))

@main_bp.route('/watchlist/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_watchlist(item_id):
    item = Watchlist.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        abort(403)
    db.session.delete(item)
    db.session.commit()
    flash('Removed from watchlist', 'success')
    return redirect(url_for('main.watchlist'))

@main_bp.route('/watchlist/status/<int:item_id>', methods=['POST'])
@login_required
def update_watchlist_status(item_id):
    item = Watchlist.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        abort(403)
    new_status = request.form.get('status', 'want_to_read')
    item.status = new_status
    db.session.commit()
    flash('Status updated', 'success')
    return redirect(url_for('main.watchlist'))

# --- Reviews ---
@main_bp.route('/book/<int:book_id>/review', methods=['POST'])
@login_required
def add_review(book_id):
    book = Book.query.get_or_404(book_id)
    
    # Check if already reviewed
    existing = Review.query.filter_by(user_id=current_user.id, book_id=book_id).first()
    if existing:
        flash('You have already reviewed this book', 'warning')
        return redirect(url_for('main.book_details', book_id=book_id))
    
    rating = int(request.form.get('rating', 5))
    content = request.form.get('content', '')
    
    if rating < 1 or rating > 5:
        flash('Rating must be between 1 and 5', 'danger')
        return redirect(url_for('main.book_details', book_id=book_id))
    
    review = Review(user_id=current_user.id, book_id=book_id, rating=rating, content=content)
    db.session.add(review)
    db.session.commit()
    flash('Review submitted successfully!', 'success')
    return redirect(url_for('main.book_details', book_id=book_id))

@main_bp.route('/review/<int:review_id>/delete', methods=['POST'])
@login_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    if review.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    book_id = review.book_id
    db.session.delete(review)
    db.session.commit()
    flash('Review deleted', 'success')
    return redirect(url_for('main.book_details', book_id=book_id))

# --- Genre Browsing ---
@main_bp.route('/genre/<genre>')
def books_by_genre(genre):
    page = request.args.get('page', 1, type=int)
    books = Book.query.filter(Book.genre.ilike(genre)).paginate(page=page, per_page=12, error_out=False)
    return render_template('main/genre.html', books=books, genre=genre)

@main_bp.route('/genres')
def all_genres():
    genres = db.session.query(Book.genre, func.count(Book.id).label('count')).group_by(Book.genre).order_by(func.count(Book.id).desc()).all()
    return render_template('main/genres.html', genres=genres)

# --- Orders ---
@main_bp.route('/orders')
@login_required
def orders():
    # Redirect admins to admin dashboard
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('main/orders.html', orders=orders)

@main_bp.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    return render_template('main/order_detail.html', order=order)

# --- Profile ---
@main_bp.route('/profile')
@login_required
def profile():
    # Redirect admins to admin dashboard
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    
    library_count = current_user.library.count()
    review_count = current_user.reviews.count()
    order_count = current_user.orders.count()
    watchlist_count = Watchlist.query.filter_by(user_id=current_user.id).count()
    
    # Recent activity
    recent_reviews = Review.query.filter_by(user_id=current_user.id).order_by(Review.created_at.desc()).limit(3).all()
    recent_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).limit(3).all()
    
    return render_template('main/profile.html', 
                         library_count=library_count,
                         review_count=review_count,
                         order_count=order_count,
                         watchlist_count=watchlist_count,
                         recent_reviews=recent_reviews,
                         recent_orders=recent_orders)

@main_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm(obj=current_user)
    form._user_id = current_user.id  # For validation
    
    if form.validate_on_submit():
        current_user.username = form.username.data.strip()
        current_user.email = form.email.data.strip().lower()
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.profile'))
    
    return render_template('main/edit_profile.html', form=form)

@main_bp.route('/profile/avatar', methods=['POST'])
@login_required
def update_avatar():
    avatar_id = request.form.get('avatar_id', type=int)
    if avatar_id and 1 <= avatar_id <= 8:
        current_user.avatar_id = avatar_id
        db.session.commit()
        flash('Avatar updated successfully!', 'success')
    else:
        flash('Invalid avatar selection.', 'danger')
    return redirect(url_for('main.edit_profile'))

@main_bp.route('/profile/delete', methods=['POST'])
@login_required
def delete_account():
    user = User.query.get(current_user.id)
    username = user.username
    logout_user()
    db.session.delete(user)
    db.session.commit()
    flash(f'Account "{username}" has been permanently deleted.', 'success')
    return redirect(url_for('auth.login'))

# --- Cart & Purchase ---
@main_bp.route('/cart')
@login_required
def cart():
    # Redirect admins to admin dashboard
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    cart_items = current_user.cart_items.all()
    total = sum(item.book.price for item in cart_items)
    return render_template('main/cart.html', cart_items=cart_items, total=total)

@main_bp.route('/cart/add/<int:book_id>', methods=['POST'])
@login_required
def add_to_cart(book_id):
    book = Book.query.get_or_404(book_id)
    
    # Check if already purchased
    if current_user.library.filter_by(id=book.id).first():
        flash('You already own this book', 'info')
        return redirect(url_for('main.book_details', book_id=book_id))
    
    # Check if already in cart
    if CartItem.query.filter_by(user_id=current_user.id, book_id=book_id).first():
        flash('Item already in cart', 'info')
    else:
        item = CartItem(user_id=current_user.id, book_id=book_id)
        db.session.add(item)
        db.session.commit()
        flash('Added to cart', 'success')
    return redirect(url_for('main.book_details', book_id=book_id))

@main_bp.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        abort(403)
    db.session.delete(item)
    db.session.commit()
    flash('Removed from cart', 'success')
    return redirect(url_for('main.cart'))

@main_bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    item_ids = request.form.getlist('selected_items')
    
    if not item_ids:
        flash('No items selected for checkout', 'warning')
        return redirect(url_for('main.cart'))
        
    cart_items = CartItem.query.filter(CartItem.id.in_(item_ids), CartItem.user_id == current_user.id).all()
    
    if not cart_items:
        flash('Selected items are not available', 'warning')
        return redirect(url_for('main.cart'))
    
    total = sum(item.book.price for item in cart_items)
    # Pass item_ids to payment template to preserve selection
    return render_template('main/payment.html', total=total, cart_items=cart_items, item_ids=item_ids)

@main_bp.route('/process_payment', methods=['POST'])
@login_required
def process_payment():
    # Mock Payment Processing
    item_ids = request.form.getlist('item_ids')
    
    if not item_ids:
        flash('Session expired or no items selected.', 'warning')
        return redirect(url_for('main.cart'))
        
    cart_items = CartItem.query.filter(CartItem.id.in_(item_ids), CartItem.user_id == current_user.id).all()
    
    if not cart_items:
        flash('Nothing to process.', 'warning')
        return redirect(url_for('main.index'))
    
    total = sum(item.book.price for item in cart_items)
    
    # Create Order
    order = Order(user_id=current_user.id, total_amount=total, status='completed')
    
    for item in cart_items:
        order.books.append(item.book)
        # Add to user library
        if not current_user.library.filter_by(id=item.book.id).first():
            current_user.library.append(item.book)
        db.session.delete(item) # Clear selected items from cart
        
    db.session.add(order)
    db.session.commit()
    
    flash(f'Payment of ${total:.2f} successful! Your library has been updated.', 'success')
    return redirect(url_for('main.library'))

@main_bp.route('/recommendations')
@login_required
def recommendations_page():
    # Redirect admins to admin dashboard
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    
    from recommendation import get_recommendations
    import random
    
    query = request.args.get('q', '').strip()
    source_book = None
    rec_books = []
    
    if query:
        # Search for book by title or author
        search_book = Book.query.filter(
            (Book.title.ilike(f'%{query}%')) | (Book.author.ilike(f'%{query}%'))
        ).first()
        
        if search_book:
            source_book = search_book
            rec_books = get_recommendations(search_book.id, num_recommendations=12)
    else:
        # Default: get recommendations based on user's library or random book
        if current_user.library.count() > 0:
            source_book = current_user.library.first()
        else:
            all_books = Book.query.limit(50).all()
            if all_books:
                source_book = random.choice(all_books)
        
        if source_book:
            rec_books = get_recommendations(source_book.id, num_recommendations=12)
    
    return render_template('main/recommendations.html', books=rec_books, source_book=source_book, query=query)

@main_bp.route('/download/<int:book_id>')
@login_required
def download_pdf(book_id):
    book = Book.query.get_or_404(book_id)
    if not current_user.library.filter_by(id=book.id).first() and not current_user.is_admin:
         flash('You must purchase this book to download it.', 'danger')
         return redirect(url_for('main.book_details', book_id=book_id))
    
    # In a real app, serve securely. Here we redirect to the URL.
    if book.pdf_url:
        return redirect(book.pdf_url)
    flash('PDF not available for this book.', 'warning')
    return redirect(url_for('main.book_details', book_id=book_id))


# --- Admin Routes ---
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email, is_admin=True).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Admin Logged in successfully', 'success')
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/') or next_page.startswith('//'):
                next_page = url_for('admin.dashboard')
            return redirect(next_page)
        else:
            flash('Invalid admin credentials.', 'danger')
            
    return render_template('admin/login.html')

@admin_bp.route('/')
@admin_required
def admin_root():
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    from collections import Counter
    
    total_books = Book.query.count()
    total_users = User.query.count()
    total_orders = Order.query.count()
    total_revenue = db.session.query(func.sum(Order.total_amount)).filter(Order.status == 'completed').scalar() or 0
    featured_count = Book.query.filter_by(is_featured=True).count()
    recent_books = Book.query.order_by(Book.created_at.desc()).limit(5).all()
    
    # Genre statistics for chart
    books = Book.query.all()
    genres = [book.genre for book in books if book.genre]
    genre_counter = Counter(genres)
    genre_stats = genre_counter.most_common(8)  # Top 8 genres
    
    # Sample recommendations - REMOVED for performance
    # Recommendation logs are pre-recorded activity, so they are fast to display
    from recommendation import recommendation_logs
    
    return render_template('admin/dashboard.html', 
        total_books=total_books, 
        total_users=total_users, 
        total_orders=total_orders, 
        total_revenue=total_revenue, 
        featured_count=featured_count,
        recent_books=recent_books,
        genre_stats=genre_stats,
        recommendation_logs=recommendation_logs)

@admin_bp.route('/book/add', methods=['GET', 'POST'])
@admin_required
def add_book():
    form = BookForm()
    if form.validate_on_submit():
        book = Book(
            title=form.title.data,
            author=form.author.data,
            genre=form.genre.data,
            description=form.description.data,
            cover_url=form.cover_url.data,
            price=form.price.data,
            pdf_url=form.pdf_url.data,
            is_featured=form.is_featured.data
        )
        db.session.add(book)
        db.session.commit()
        flash('Book added successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/add_book.html', form=form)

@admin_bp.route('/book/<int:book_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    
    if request.method == 'POST':
        book.cover_url = request.form.get('cover_url', book.cover_url)
        book.price = float(request.form.get('price', book.price))
        book.pdf_url = request.form.get('pdf_url') or None
        book.is_featured = request.form.get('is_featured') == '1'
        db.session.commit()
        flash('Book updated successfully!', 'success')
        # Redirect to the page the user came from, or dashboard as fallback
        redirect_url = request.referrer or url_for('admin.dashboard')
        return redirect(redirect_url)
    
    return render_template('admin/edit_book.html', book=book)

@admin_bp.route('/book/delete/<int:book_id>', methods=['POST'])
@admin_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted.', 'success')
    # Redirect to the page the user came from, or dashboard as fallback
    redirect_url = request.referrer or url_for('admin.dashboard')
    return redirect(redirect_url)

@admin_bp.route('/book/<int:book_id>/feature', methods=['POST'])
@admin_required
def toggle_featured(book_id):
    book = Book.query.get_or_404(book_id)
    book.is_featured = not book.is_featured
    db.session.commit()
    status = 'featured' if book.is_featured else 'unfeatured'
    flash(f'Book "{book.title}" is now {status}.', 'success')
    # Redirect to the page the user came from, or dashboard as fallback
    redirect_url = request.referrer or url_for('admin.dashboard')
    return redirect(redirect_url)

@admin_bp.route('/featured')
@admin_required
def featured_books():
    featured = Book.query.filter_by(is_featured=True).order_by(Book.created_at.desc()).all()
    all_books = Book.query.order_by(Book.is_featured.desc(), Book.title.asc()).all()
    return render_template('admin/featured.html', books=featured, all_books=all_books)

@admin_bp.route('/users')
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/users.html', users=users)

@admin_bp.route('/user/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot delete your own account from here.', 'danger')
        return redirect(url_for('admin.users'))
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.username} has been deleted.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/recommendations')
@admin_required
def recommendations_dashboard():
    from recommendation import get_recommendations
    from collections import Counter
    import random
    
    # Get all books and genre stats
    all_books = Book.query.all()
    total_books = len(all_books)
    featured_count = Book.query.filter_by(is_featured=True).count()
    
    # Genre statistics
    genres = [book.genre for book in all_books]
    genre_counter = Counter(genres)
    genre_stats = dict(genre_counter.most_common())
    popular_genre = genre_counter.most_common(1)[0][0] if genre_counter else "N/A"
    
    # Sample recommendations
    sample_book = random.choice(all_books) if all_books else None
    sample_recommendations = []
    if sample_book:
        sample_recommendations = get_recommendations(sample_book.id, num_recommendations=6)
    
    return render_template('admin/recommendations.html', 
                         genres=list(set(genres)),
                         popular_genre=popular_genre,
                         total_books=total_books,
                         featured_count=featured_count,
                         genre_stats=genre_stats,
                         sample_book=sample_book,
                         sample_recommendations=sample_recommendations)
