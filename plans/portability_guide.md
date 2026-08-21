# Codebase Portability Analysis & Migration Guide

## Current Machine-Specific Issues Identified

### 1. Database Configuration
- **config.py** (line 8): Hardcoded MySQL connection string
  ```python
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:password@localhost/bookrecommendation_db'
  ```
- **instance/db.sqlite3**: SQLite database file is machine-specific
- **.env**: Contains `DATABASE_URL=sqlite:///db.sqlite3` - path-dependent

### 2. Virtual Environment
- **venv/** folder: Contains machine-specific compiled Python packages
- **pyvenv.cfg**: References absolute paths

### 3. Environment Variables
- **.env file**: Contains secrets that should not be committed
  - SECRET_KEY
  - DATABASE_URL
  - STRIPE keys (test placeholders)
  - ADMIN_CODE

### 4. Data Files
- **scripts/books.csv** (3.2MB): Downloaded dataset
- **scripts/cleaned_books.csv** (3MB): Processed data
- **instance/db.sqlite3** (212KB): SQLite database with seeded data

### 5. Hardcoded Paths
- Scripts reference absolute paths using `os.path.dirname(__file__)`

### 6. Missing Files
- **run_app.bat**: Referenced in README but doesn't exist

---

## Migration Strategy

### Files to EXCLUDE from Version Control (.gitignore)
```
venv/
instance/
__pycache__/
*.pyc
.env
*.log
.DS_Store
```

### Files to INCLUDE in Distribution
```
# Core application
app.py
config.py
forms.py
models.py
routes.py
recommendation.py

# Configuration
requirements.txt

# Templates & Static
templates/
static/

# Scripts (without large CSV files)
scripts/seed_data.py
scripts/import_csv.py
scripts/cleaning.py
scripts/check_db.py

# Documentation
README.md
PLANS/ (this file)
```

---

## Step-by-Step Migration Guide

### Step 1: Prepare for Transfer
1. Create a `.gitignore` file excluding machine-specific files
2. Document all required environment variables
3. Create a setup script for new machines

### Step 2: On the New Machine
1. Install Python 3.8+
2. Create virtual environment
3. Install dependencies
4. Configure environment variables
5. Run database setup
6. Start the application

### Step 3: Database Options
- **Option A (Recommended)**: Use SQLite (no setup required)
- **Option B**: Use MySQL (requires MySQL server)
- **Option C**: Use PostgreSQL (requires PostgreSQL server)

---

## Recommended Environment Setup

### Create .env File
```env
# Required
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///instance/db.sqlite3

# Optional (for payments)
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Admin
ADMIN_CODE=your-admin-code
```

### Create requirements.txt (already exists, verify contents)
```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Flask-WTF==1.2.1
email-validator==2.1.0.post1
PyMySQL==1.1.0
Stripe
Werkzeug==3.0.1
pandas==2.1.4
scikit-learn==1.3.2
numpy==1.26.2
python-dotenv==1.0.0
requests==2.31.0
```

---

## Quick Start Script (setup.bat)

```batch
@echo off
REM Book Library Setup Script for Windows

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Setup complete!
echo.
echo Next steps:
echo 1. Copy .env file with your configuration
echo 2. Run: python scripts\seed_data.py
echo 3. Run: python app.py
echo.
pause
```

---

## Docker Containerization (Optional)

For maximum portability, create a Dockerfile:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app.py
ENV FLASK_ENV=development

EXPOSE 5000

CMD ["python", "app.py"]
```

And docker-compose.yml:

```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./instance:/app/instance
    environment:
      - DATABASE_URL=sqlite:///instance/db.sqlite3
      - SECRET_KEY=dev-secret-key
```

---

## Summary

To make this codebase portable:
1. **Do NOT transfer**: venv/, instance/, .env
2. **Do transfer**: All .py files, templates/, static/, requirements.txt, README.md
3. **On new machine**: Create venv, install deps, configure .env, run seed_data.py
