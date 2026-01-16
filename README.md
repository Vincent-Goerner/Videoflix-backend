# Videoflix

## 🔍 Overview
Videoflix is a Django-based, video streaming platform developed as part of the Developer Akademie program. It allows registered users to stream videos with HLS support from different categories and change video resolution.

## ✨ Features

### User Authentication
- E-mail verification based registration
- Login based on JWT authentication
- Logout functionality
- Password reset function

### Video Managment
- Video Upload and management (Only superusers can upload videos via the admin panel)
- Video categorization
- different resolution options
- HLS streaming support
- Video thumbnail support

## ⚙️ Installation

### Prerequisites
- Python 3.13+
- Django 4.0+
- Django REST Framework
- Django-Cors-Headers
- SimpleJWT
- FFmpeg
- redis

Full list: requirements.txt (Installation guide see below)

### Local Setup
```bash
# 1. Clone the repository

git clone https://github.com/Vincent-Goerner/Videoflix-backend.git
cd Videoflix-backend

# 2. Create .env using the 'git bash' console

cd Videoflix-backend

  # Windows
  copy .env.template .env

  # Linux/Mac
  cp .env.template .env    

# 3. Create and enter virtual environment

python -m venv env

  #Mac and Linux:
    source env/bin/activate

  # On Windows:
    env\Scripts\activate

# 4. Install dependencies

pip install -r requirements.txt

# 5. Run migrations

python manage.py makemigrations
python manage.py migrate

# 6. create superuser

python manage.py createsuperuser

# 7. Start development server

python manage.py runserver
```

### Docker Installation
```bash
# 1. Clone the repository

git clone https://github.com/Vincent-Goerner/Videoflix-backend.git
cd Videoflix-backend

# 2. Create .env using the 'git bash' console

cd Videoflix-backend

  # Windows
  copy .env.template .env

  # Linux/Mac
  cp .env.template .env

# 3. Docker setup
```
