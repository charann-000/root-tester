# METATRON Cloud Deployment Guide

## Architecture

```
[Users] → [Nginx (SSL)] → [Frontend] → [Backend (Python)]
                              ↓
                    [MariaDB Managed (Cloud DB)]
```

## Option 1: DigitalOcean (Recommended)

### 1. Create MariaDB Managed Database
1. Go to DigitalOcean → Managed Databases
2. Create new database:
   - **Name**: metatron-db
   - **Engine**: MariaDB
   - **Size**: DB-s-1vcpu-1gb ($15/mo)
   - **Region**: Choose closest to users
3. Get connection details from "Connection Details" tab:
   - Host: `10.104.0.2` (example)
   - Port: `3306`
   - User: `metatron`
   - Password: `your-password`
   - Database: `metatron_db`

### 2. Create Droplet (Server)
1. Go to Droplets → Create
2. Choose:
   - **Image**: Ubuntu 22.04
   - **Size**: s-2vcpu-2gb ($12/mo)
   - **Region**: Same as DB
3. Add SSH key or create password

### 3. Deploy to Droplet

SSH into your droplet:
```bash
ssh root@YOUR_DROPLET_IP
```

Install METATRON:
```bash
# Install git
apt update && apt install -y git

# Clone your repository
git clone https://github.com/YOUR_USERNAME/metatron-web.git
cd metatron-web/backend

# Install tools
apt install -y nmap curl dnsutils whois nikto whatweb gobuster

# Install Python
apt install -y python3-pip python3-venv
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit with your DB credentials and API keys

# Run database migrations
python3 -c "from db import init_db; init_db()"

# Start backend
nohup uvicorn main:app --host 0.0.0.0 --port 8000 &
```

### 4. Nginx + SSL

```bash
# Install nginx
apt install -y nginx certbot python3-certbot-nginx

# Create nginx config
nano /etc/nginx/sites-available/metatron
```

Paste:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5173;
        proxy_set_header Host $host;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Enable SSL:
```bash
# Link config
ln -s /etc/nginx/sites-available/metatron /etc/nginx/sites-enabled/

# Get SSL (replace with your email)
certbot --nginx -d your-domain.com --email your@email.com

# Restart nginx
systemctl restart nginx
```

### 5. Point Domain
1. Go to your domain registrar
2. Create A record: `@ → YOUR_DROPLET_IP`


## Option 2: AWS

### 1. RDS MariaDB (Free Tier)
1. AWS Console → RDS → Create database
2. Choose: **MariaDB**, **Free tier**
3. Username: `metatron`
4. Password: Create strong password

### 2. EC2 Instance
1. EC2 → Launch Instance
2. Choose: **t2.micro** (Free tier)
3. Security Group: Add rules for HTTP(80), HTTPS(443), SSH(22)

### 3. Deploy Same as DigitalOcean


## Environment Variables for Cloud

Create `.env` file:
```env
# Database (from cloud provider)
DB_HOST=your-cloud-db-ip
DB_PORT=3306
DB_USER=metatron
DB_PASSWORD=your-secure-password
DB_NAME=metatron_db

# JWT
SECRET_KEY=generate-random-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# LLM
LLM_PROVIDER=groq
GROQ_API_KEY=your-groq-api-key
LLM_MODEL=llama-3.3-70b-versatile

# App
CORS_ORIGINS=https://your-domain.com
```


## Starting the Service

After deployment, check status:
```bash
# Check backend
curl http://localhost:8000/health

# Check frontend
curl http://localhost:5173
```

View logs:
```bash
tail -f nohup.out
```