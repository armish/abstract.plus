# Production Deployment Guide

This guide explains how to run the Conference Abstract Annotator in production mode.

## Quick Start

### Development Mode (Not Recommended for Production)
```bash
# This will show warnings about using development server
python conference-webapp.py
```

### Production Mode with Gunicorn (Recommended)
```bash
# Install dependencies including gunicorn
pip install -r requirements.txt

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 300 conference-webapp:app
```

## Why Not Use Flask's Built-in Server?

The warnings you see when running `python conference-webapp.py` are because:

1. **Not designed for production** - Flask's built-in server is single-threaded and not optimized for handling multiple concurrent requests
2. **Security concerns** - Missing security features needed for production
3. **Performance** - Cannot handle high load or multiple users efficiently
4. **Stability** - Not as robust as production WSGI servers

## Production Setup Options

### Option 1: Gunicorn (Recommended)

Gunicorn is a Python WSGI HTTP server that's production-ready.

**Installation:**
```bash
pip install gunicorn  # Already in requirements.txt
```

**Basic Usage:**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 conference-webapp:app
```

**With All Recommended Options:**
```bash
gunicorn \
  -w 4 \
  -b 0.0.0.0:5000 \
  --timeout 300 \
  --access-logfile - \
  --error-logfile - \
  --log-level info \
  conference-webapp:app
```

**Parameters Explained:**
- `-w 4`: Number of worker processes (adjust based on CPU cores)
- `-b 0.0.0.0:5000`: Bind to all network interfaces on port 5000
- `--timeout 300`: 5-minute timeout for long annotation requests
- `--access-logfile -`: Log access requests to stdout
- `--error-logfile -`: Log errors to stdout
- `--log-level info`: Logging verbosity
- `conference-webapp:app`: Python module and Flask app object

**Worker Recommendations:**
- CPU-bound tasks: workers = (2 × num_cores) + 1
- I/O-bound tasks (like this app): workers = (4 × num_cores)
- Start with 4 workers and adjust based on load

### Option 2: uWSGI

Alternative to Gunicorn, also production-ready.

**Installation:**
```bash
pip install uwsgi
```

**Usage:**
```bash
uwsgi --http 0.0.0.0:5000 --wsgi-file conference-webapp.py --callable app --processes 4 --threads 2
```

### Option 3: Waitress (Windows-friendly)

Good option for Windows servers.

**Installation:**
```bash
pip install waitress
```

**Usage:**
Create a file `serve.py`:
```python
from waitress import serve
from conference_webapp import app

serve(app, host='0.0.0.0', port=5000, threads=4)
```

Then run:
```bash
python serve.py
```

## Environment Variables

Set these before starting the server:

```bash
# Required for annotation
export OPENAI_API_KEY='sk-your-api-key'

# Optional configuration
export HOST='0.0.0.0'
export PORT='5000'
export FLASK_DEBUG='False'  # Always False in production
```

## Using systemd (Linux)

For automatic startup and process management.

### 1. Create Service File

Create `/etc/systemd/system/conference-annotator.service`:

```ini
[Unit]
Description=ESMO 2025 Conference Abstract Annotator
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/conference-webapp/2025-ESMO
Environment="OPENAI_API_KEY=sk-your-api-key-here"
Environment="PATH=/var/www/conference-webapp/venv/bin"
ExecStart=/var/www/conference-webapp/venv/bin/gunicorn \
    -w 4 \
    -b 0.0.0.0:5000 \
    --timeout 300 \
    --access-logfile /var/log/conference-annotator/access.log \
    --error-logfile /var/log/conference-annotator/error.log \
    conference-webapp:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always

[Install]
WantedBy=multi-user.target
```

### 2. Enable and Start

```bash
# Create log directory
sudo mkdir -p /var/log/conference-annotator
sudo chown www-data:www-data /var/log/conference-annotator

# Reload systemd
sudo systemctl daemon-reload

# Enable autostart
sudo systemctl enable conference-annotator

# Start service
sudo systemctl start conference-annotator

# Check status
sudo systemctl status conference-annotator

# View logs
sudo journalctl -u conference-annotator -f
```

### 3. Manage Service

```bash
# Stop
sudo systemctl stop conference-annotator

# Restart
sudo systemctl restart conference-annotator

# Reload (graceful restart)
sudo systemctl reload conference-annotator

# Disable autostart
sudo systemctl disable conference-annotator
```

## Reverse Proxy with Nginx

For HTTPS and better performance, put nginx in front of Gunicorn.

### 1. Install Nginx

```bash
sudo apt install nginx  # Ubuntu/Debian
sudo yum install nginx  # CentOS/RHEL
```

### 2. Configure Nginx

Create `/etc/nginx/sites-available/conference-annotator`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL configuration
    ssl_certificate /etc/ssl/certs/your-cert.pem;
    ssl_certificate_key /etc/ssl/private/your-key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Increase timeouts for long annotation requests
    proxy_connect_timeout 300;
    proxy_send_timeout 300;
    proxy_read_timeout 300;
    send_timeout 300;

    # Max upload size
    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Static file caching (if you extract static assets)
    location /static {
        alias /var/www/conference-webapp/2025-ESMO/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### 3. Enable Site

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/conference-annotator /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

## SSL/TLS Certificates

### Option 1: Let's Encrypt (Free)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is set up automatically
# Test renewal
sudo certbot renew --dry-run
```

### Option 2: Self-Signed (Development/Testing)

```bash
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/self-signed.key \
  -out /etc/ssl/certs/self-signed.crt
```

## Monitoring and Logging

### View Gunicorn Logs

```bash
# If using systemd
sudo journalctl -u conference-annotator -f

# If running manually
tail -f /var/log/conference-annotator/access.log
tail -f /var/log/conference-annotator/error.log
```

### Monitor Resource Usage

```bash
# Watch process
ps aux | grep gunicorn

# Monitor in real-time
htop  # or top
```

## Security Checklist

- [ ] Use HTTPS (SSL/TLS certificates)
- [ ] Set `FLASK_DEBUG=False`
- [ ] Use strong API keys
- [ ] Configure firewall (allow only ports 80/443)
- [ ] Run as non-root user (e.g., www-data)
- [ ] Keep dependencies updated
- [ ] Set proper file permissions
- [ ] Use environment variables for secrets
- [ ] Enable access logging
- [ ] Configure rate limiting (if needed)
- [ ] Regular security updates

## Performance Tuning

### Gunicorn Workers

```bash
# Calculate optimal workers
python -c "import multiprocessing; print(2 * multiprocessing.cpu_count() + 1)"

# Use result in gunicorn command
gunicorn -w CALCULATED_NUMBER ...
```

### Database Optimization

This app loads data into memory, so ensure sufficient RAM:
- Small datasets (<10K rows): 1-2 GB RAM
- Medium datasets (10K-100K rows): 4-8 GB RAM
- Large datasets (>100K rows): 16+ GB RAM

### Timeout Settings

For annotation jobs processing many abstracts:
```bash
gunicorn --timeout 600 ...  # 10 minutes
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 5000
sudo lsof -i :5000

# Kill process
sudo kill -9 PID
```

### Permission Denied
```bash
# Fix ownership
sudo chown -R www-data:www-data /var/www/conference-webapp

# Fix permissions
sudo chmod -R 755 /var/www/conference-webapp
```

### Out of Memory
```bash
# Check memory usage
free -h

# Add swap if needed
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## Quick Commands Reference

```bash
# Development
python conference-webapp.py

# Production (basic)
gunicorn -w 4 -b 0.0.0.0:5000 conference-webapp:app

# Production (recommended)
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 300 \
  --access-logfile - --error-logfile - conference-webapp:app

# With environment variables
OPENAI_API_KEY='sk-key' gunicorn -w 4 -b 0.0.0.0:5000 conference-webapp:app

# Background process
gunicorn -w 4 -b 0.0.0.0:5000 conference-webapp:app --daemon

# systemd
sudo systemctl start conference-annotator
sudo systemctl status conference-annotator
sudo systemctl stop conference-annotator
```

## Support

For production deployment issues:
1. Check logs: `sudo journalctl -u conference-annotator -f`
2. Verify configuration: `gunicorn --check-config conference-webapp:app`
3. Test network: `curl http://localhost:5000/api/stats`
