from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Association table for Order Items
order_items = db.Table('order_items',
    db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True),
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True)
)

# Association table for User's Purchased Books (Library)
user_library = db.Table('user_library',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    avatar_id = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    watchlist = db.relationship('Watchlist', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    cart_items = db.relationship('CartItem', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    library = db.relationship('Book', secondary=user_library, lazy='dynamic', backref=db.backref('owners', lazy='dynamic'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(100))
    description = db.Column(db.Text)
    cover_url = db.Column(db.String(500)) # URL to image
    price = db.Column(db.Float, default=0.0)
    pdf_url = db.Column(db.String(500)) # URL to download PDF
    is_featured = db.Column(db.Boolean, default=False) # Featured book for homepage
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    reviews = db.relationship('Review', backref='book', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'genre': self.genre,
            'cover_url': self.cover_url,
            'price': self.price,
            'description': self.description,
            'is_featured': self.is_featured,
            'java_script_void': 0
        }

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False) # 1-5
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Watchlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    status = db.Column(db.String(20), default='want_to_read') # want_to_read, reading, completed
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    book = db.relationship('Book')

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    book = db.relationship('Book')

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending') # pending, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    books = db.relationship('Book', secondary=order_items, lazy='subquery', backref=db.backref('orders', lazy=True))
