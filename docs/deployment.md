# Deployment Guide — KrushiSetu (कृषिसेतु)

## 1. Local Development Setup

### Prerequisites
- Python 3.9+ installed
- Git installed
- MongoDB (optional; defaults to embedded mock DB for standalone local development)

### Step 1: Clone Repository
```bash
git clone https://github.com/your-username/KrushiSetu.git
cd KrushiSetu
```

### Step 2: Configure Environment Variables
```bash
cp .env.example .env
```
*(Review `.env` and set `JWT_SECRET` and `SECRET_KEY`)*

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run Application
```bash
python backend/app.py
```
Open browser and navigate to `http://127.0.0.1:5000`.

---

## 2. Production Deployment (Linux / Docker / Gunicorn / NGINX)

### Production Gunicorn Server
Run the Flask application behind Gunicorn WSGI server:
```bash
pip install gunicorn
gunicorn --workers 4 --bind 0.0.0.0:5000 "backend.app:create_app()"
```

### NGINX Configuration Sample
```nginx
server {
    listen 80;
    server_name krushisetu.example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name krushisetu.example.com;

    ssl_certificate /etc/letsencrypt/live/krushisetu.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/krushisetu.example.com/privkey.pem;

    # Security Headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options SAMEORIGIN;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Static Frontend Assets
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Uploads directory
    location /uploads/ {
        alias /var/www/krushisetu/uploads/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
}
```

---

## 3. MongoDB Atlas Connection

1. Create a free cluster on [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
2. Create a Database User with read/write access.
3. Whitelist your server IP address (or `0.0.0.0/0` with secure credentials).
4. Set `MONGODB_URI` in `.env`:
   ```env
   MONGODB_URI=mongodb+srv://<username>:<password>@cluster0.abcde.mongodb.net/krushisetu_db?retryWrites=true&w=majority
   DB_NAME=krushisetu_db
   ```
