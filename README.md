<<<<<<< HEAD
# Book-Recommendation-System
=======
# 📚 BookVerse — Intelligent Book Recommendation & E-Commerce Platform


**BookVerse** is a modern, full-stack Web Application that seamlessly combines a **Content-Based Book Recommendation Engine** with a feature-complete **E-Commerce Platform**. Users can discover tailored book suggestions based on mathematical text similarity algorithms, read reviews, maintain reading watchlists, purchase digital books securely via Stripe, and download PDFs straight to their personal digital library.

---

## 🌟 Key Features

### 🧠 1. Intelligent Recommendation Engine
* **Content-Based Filtering**: Recommends books based on text content extracted from book titles, genres, and descriptions.
* **Jaccard Similarity Algorithm**: Computes exact percentage match scores between books using tokenized set intersections and unions.
* **Token Caching Layer**: Pre-computes and caches text tokens in memory for optimal server response times.
* **Real-time Admin Analytics**: Logs recommendation requests and score breakdowns for administrator audit.

### 🛒 2. E-Commerce & Digital Shopping
* **Interactive Shopping Cart**: Add, update, and clear books seamlessly before purchase.
* **Stripe Checkout Integration**: Secure credit card payment processing via Stripe Payment Links / Webhooks.
* **Personal Digital Library**: Purchased titles automatically unlock instant PDF downloads and permanent ownership in the user's library.
* **Order Tracking & Receipts**: View order histories with itemized breakdowns and transaction statuses.

### 👤 3. Rich User Experience & Account Management
* **Authentication System**: Secure signup, login, and session persistence powered by Flask-Login and Werkzeug password hashing.
* **Interactive UI Enhancements**: Show/Hide password visibility toggle, client-side validation, and smooth micro-animations.
* **Customizable User Profile**: Choose custom avatar presets, update email/username, and view account stats.
* **Reading Watchlist & Tracker**: Organize reading habits into categories: *Want to Read*, *Currently Reading*, and *Completed*.
* **Reviews & Rating System**: Submit star ratings and detailed community book reviews.

### 🛡️ 4. Comprehensive Admin Control Panel
* **Protected Admin Dashboard**: Restricted route accessibility reserved for administrator accounts.
* **Book Inventory Management (CRUD)**: Easily add new books, edit details, set prices, upload cover image URLs, and PDF download links.
* **Homepage Feature Manager**: Toggle featured highlights to display custom curated books on the main landing page carousel.
* **User Management**: Monitor registered users, inspect permissions, and grant administrative privileges.
* **Live Recommendation Metrics**: Monitor recent recommendation queries and algorithm similarity scores in real-time.

---

## 🛠️ Technology Stack

| Domain | Technologies Used |
| :--- | :--- |
| **Backend Framework** | Python 3.10+, Flask 3.0, Flask-SQLAlchemy, Flask-Login, Flask-WTF |
| **Frontend UI** | HTML5, Modern CSS3 (Glassmorphism, Dark/Light Themes), JavaScript (ES6+), Jinja2 |
| **Data Processing & ML** | NumPy, Pandas, Scikit-Learn, Custom Jaccard Similarity Model |
| **Database** | MySQL (via PyMySQL connector) |
| **Payment Processor** | Stripe API Integration |
| **Form Validation & Security** | WTForms, CSRF Protection, Email-Validator |

---

## 📐 Recommendation Algorithm Explained

The core recommendation engine relies on **Jaccard Similarity** calculated over tokenized attributes:

$$\text{Jaccard Similarity}(A, B) = \frac{|A \cap B|}{|A \cup B|}$$

1. **Tokenization**: Combines the book's Title, Genre, and Description into a unified text string, normalized to lowercase and split into distinct sets of word tokens.
2. **Set Operations**: Calculates the intersection $|A \cap B|$ (common keywords) divided by union $|A \cup B|$ (all unique keywords).
3. **Similarity Score**: Generates a normalized score between `0.0` (0%) and `1.0` (100%).
4. **Ranking & Filtering**: Sorts candidates in descending order to present the top matching recommendations to the reader.

---

## 📁 Repository Structure

```gcode
Book Recomendation Project/
│
├── app.py                  # Application entry point & factory function (Flask app initialization)
├── config.py               # Application configuration & environment variables settings
├── models.py               # SQLAlchemy Database Models (User, Book, Review, Order, Watchlist, Cart)
├── forms.py                # WTForms schemas for User Login, Registration, Book creation & Profile edits
├── recommendation.py       # Recommendation Engine implementation (Jaccard algorithm & token cache)
├── routes.py               # Blueprint route handlers (Main, Auth, Admin)
├── requirements.txt        # Python package dependencies list
├── .env.example            # Sample environment variables template
│
├── scripts/                # Database utilities & data ingestion scripts
│   ├── seed_data.py        # Seed script for populating initial database books & admin user
│   ├── import_csv.py       # Utility to parse and import CSV datasets into MySQL
│   └── cleaned_books.csv   # Preprocessed dataset of books
│
├── static/                 # Static assets (CSS stylesheets, images, JS scripts, icons)
│   ├── css/
│   ├── js/
│   └── images/
│
└── templates/              # Jinja2 HTML Templates
    ├── base.html           # Main website layout frame
    ├── admin_base.html     # Admin dashboard master template
    ├── auth_base.html      # Authentication layout template
    ├── admin/              # Admin view pages (Dashboard, Manage Books, Users, Featured)
    ├── auth/               # User account pages (Login, Register)
    ├── components/         # Reusable Jinja2 partials (Navbar, Footer, Book Cards)
    └── main/               # Public pages (Index, Book Detail, Cart, Library, Watchlist, Search)
```

---

## 🚀 Getting Started

Follow these steps to set up and run **BookVerse** locally on your machine.

### 1. Prerequisites
* **Python**: 3.10 or higher
* **MySQL Database Server**: MySQL 8.0+ or MariaDB running locally or remotely

### 2. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/book-recommendation-project.git
cd book-recommendation-project
```

### 3. Create & Activate a Virtual Environment
* **On Windows (PowerShell)**:
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate
  ```
* **On macOS / Linux**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Create a `.env` file in the root directory (or copy from `.env.example`):

```env
SECRET_KEY=your_super_secret_key_here
DATABASE_URL=mysql+pymysql://root:your_password@localhost/bookrecommendation_db
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### 6. Set Up the Database & Seed Initial Data
Create the MySQL database manually if it doesn't exist:
```sql
CREATE DATABASE bookrecommendation_db;
```
Then run the seed script to automatically create tables and populate initial book data:
```bash
python scripts/seed_data.py
```

### 7. Run the Application
```bash
python app.py
```
Open your browser and navigate to: **`http://127.0.0.1:5000`**

---

## 📸 Key Application Screens

| Screen | Description |
| :--- | :--- |
| **Homepage Showcase** | Hero banner with featured book carousels, genre quick-links, and trending books. |
| **Book Detail & Recommendations** | Comprehensive overview of book details, star ratings, reviews, and algorithm recommendations. |
| **Shopping Cart & Checkout** | Seamless cart management with integrated Stripe payment processing. |
| **User Library** | Instant digital access and direct PDF download links for purchased titles. |
| **Admin Control Panel** | Real-time system monitoring, book CRUD management, and user permissions control. |

---

## 🤝 Contributing

Contributions are welcome! If you'd like to improve the recommendation algorithm, add new payment gateways, or enhance the UI:

1. Fork the Repository
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** - see the `LICENSE` file for details.
>>>>>>> 3ff6f9a (initial commit)
