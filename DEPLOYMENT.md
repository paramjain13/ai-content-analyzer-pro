# Deployment Guide

This guide covers various deployment options for AI Content Analyzer Pro.

## Table of Contents
- [Local Development](#local-development)
- [Production Deployment](#production-deployment)
- [Docker Deployment](#docker-deployment)
- [Cloud Platforms](#cloud-platforms)
- [Environment Variables](#environment-variables)
- [Database Setup](#database-setup)

## Local Development

### Prerequisites
- Python 3.8+
- pip
- Virtual environment tool

### Steps
1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate: `source venv/bin/activate` (Unix) or `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Set up `.env` file
6. Initialize database: Run the initialization commands in README
7. Run: `python app.py`

## Production Deployment

### Using Gunicorn (Recommended for Linux)

1. Install Gunicorn:
```bash
pip install gunicorn
```

2. Create a systemd service file `/etc/systemd/system/content-analyzer.service`:
```ini
[Unit]
Description=AI Content Analyzer Pro
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/ai-content-analyzer-pro
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:8000 app:app

[Install]
WantedBy=multi-user.target
```

3. Enable and start:
```bash
sudo systemctl enable content-analyzer
sudo systemctl start content-analyzer
```

### Using Nginx (Reverse Proxy)

1. Install Nginx: `sudo apt install nginx`

2. Create Nginx config `/etc/nginx/sites-available/content-analyzer`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /path/to/ai-content-analyzer-pro/static;
    }
}
```

3. Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/content-analyzer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Docker Deployment

### Dockerfile (Create this)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy application
COPY . .

# Create necessary directories
RUN mkdir -p uploads instance

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
```

### docker-compose.yml (Create this)

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./uploads:/app/uploads
      - ./instance:/app/instance
      - ./chroma_db:/app/chroma_db
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - web
    restart: unless-stopped
```

### Build and Run

```bash
docker-compose up -d
```

## Cloud Platforms

### Heroku

1. Create `Procfile`:
```
web: gunicorn app:app
```

2. Create `runtime.txt`:
```
python-3.11.0
```

3. Deploy:
```bash
heroku create your-app-name
git push heroku main
heroku config:set OPENAI_API_KEY=your_key
heroku config:set GOOGLE_API_KEY=your_key
```

### AWS (EC2)

1. Launch an EC2 instance (Ubuntu 22.04)
2. SSH into instance
3. Install dependencies:
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx
```
4. Clone repository and follow production deployment steps
5. Configure security groups to allow HTTP/HTTPS

### DigitalOcean

1. Create a Droplet (Ubuntu)
2. Follow the same steps as AWS EC2
3. Optionally use DigitalOcean's App Platform for easier deployment

### Google Cloud Platform

1. Create a new project
2. Enable Cloud Run
3. Build and deploy:
```bash
gcloud builds submit --tag gcr.io/your-project/content-analyzer
gcloud run deploy --image gcr.io/your-project/content-analyzer --platform managed
```

## Environment Variables

### Required Variables
- `OPENAI_API_KEY`: OpenAI API key
- `GOOGLE_API_KEY`: Google Gemini API key
- `SECRET_KEY`: Flask secret key (generate with `python -c "import secrets; print(secrets.token_hex(32))"`)

### Optional Variables
- `DATABASE_URL`: Database connection string (default: SQLite)
- `MAX_FILE_SIZE_MB`: Maximum upload size (default: 10)
- `TESSERACT_PATH`: Path to Tesseract OCR binary

## Database Setup

### SQLite (Development)
Default configuration - no setup needed.

### PostgreSQL (Production)

1. Install PostgreSQL
2. Create database:
```sql
CREATE DATABASE content_analyzer;
CREATE USER analyzer_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE content_analyzer TO analyzer_user;
```

3. Update `.env`:
```
DATABASE_URL=postgresql://analyzer_user:your_password@localhost/content_analyzer
```

4. Update `app.py`:
```python
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///content_analyzer.db")
```

## Performance Optimization

### Production Settings

1. Enable production mode:
```python
app.config["DEBUG"] = False
app.config["TESTING"] = False
```

2. Use a production-grade web server (Gunicorn, uWSGI)
3. Set up caching (Redis, Memcached)
4. Use a CDN for static files
5. Enable compression
6. Configure proper logging

### Scaling

1. Use multiple Gunicorn workers: `--workers 4`
2. Implement load balancing with Nginx
3. Use PostgreSQL instead of SQLite
4. Consider Redis for session management
5. Implement celery for async tasks

## Security Checklist

- [ ] Change SECRET_KEY to a strong random value
- [ ] Use HTTPS (SSL certificate)
- [ ] Set up firewall rules
- [ ] Regular security updates
- [ ] Rate limiting
- [ ] Input validation
- [ ] SQL injection prevention (using ORM)
- [ ] XSS protection
- [ ] CSRF protection
- [ ] Secure file uploads

## Monitoring

### Logs
```bash
# View systemd logs
sudo journalctl -u content-analyzer -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Health Checks
Create a health check endpoint:
```python
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200
```

## Backup

### Database Backup
```bash
# SQLite
cp instance/content_analyzer.db backups/content_analyzer_$(date +%Y%m%d).db

# PostgreSQL
pg_dump content_analyzer > backups/content_analyzer_$(date +%Y%m%d).sql
```

### File Backup
```bash
tar -czf backups/uploads_$(date +%Y%m%d).tar.gz uploads/
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   - Check with: `sudo lsof -i :5000`
   - Kill process: `kill -9 PID`

2. **Permission errors**
   - Fix ownership: `sudo chown -R www-data:www-data /path/to/app`

3. **Database errors**
   - Delete and recreate: `rm instance/content_analyzer.db`
   - Initialize again

4. **Module not found**
   - Reinstall dependencies: `pip install -r requirements.txt`

## Support

For deployment issues:
- Check application logs
- Review Nginx/Gunicorn logs
- Open an issue on GitHub
- Contact: your.email@example.com
