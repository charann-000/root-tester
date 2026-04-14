# METATRON on Oracle Cloud (FREE Forever)

## Why Oracle Cloud?
- 2 CPUs + 1GB RAM (Ampere A1) - ALWAYS FREE
- Free Autonomous Database - ALWAYS FREE
- No credit card required after signup

---

## Step 1: Sign Up for Oracle Cloud

1. Go to: https://www.oracle.com/cloud/free/
2. Click "Start for free"
3. Create account (requires email verification)
4. **Don't add payment** - select "Always Free" tier

---

## Step 2: Create Free Instance

1. After login, go to **Compute** → **Instances**
2. Click **Create Instance**
3. Configure:
   - **Name**: metatron-server
   - **Image**: Oracle Linux 9 (or Ubuntu 22.04)
   - **Shape**: Ampere (should be selected by default - free!)
   - **Networking**: Create new VCN or use existing
   - **Add public IP**: Yes (required)
4. Click **Create**

5. Wait 2-3 minutes for provisioning
6. Copy the **Public IP address**

---

## Step 3: SSH Into Server

Open Terminal (Linux/Mac) or PowerShell (Windows):

```bash
ssh opc@YOUR_PUBLIC_IP
```

Replace `YOUR_PUBLIC_IP` with your instance's IP.

---

## Step 4: Install METATRON

Run these commands one by one:

```bash
# Update system
sudo dnf update -y

# Install security tools
sudo dnf install -y nmap curl bind-utils whois git

# Install Python
sudo dnf install -y python3 python3-pip python3-venv

# Create app directory
sudo mkdir -p /opt/metatron
sudo chown -R opc:opc /opt/metatron

# Clone your code (upload first or use this template)
cd /opt/metatron
git clone https://github.com/YOUR_USERNAME/metatron-web.git .

# Install Python dependencies
cd /opt/metatron/backend
pip3 install -r requirements.txt --break-system-packages

# Create .env file
cp .env .env.backup
nano .env
```

Edit `.env` with:
```env
# Database (we'll get this from Oracle)
DB_HOST=
DB_PORT=3306
DB_USER=metatron
DB_PASSWORD=your-secure-password
DB_NAME=metatron_db

SECRET_KEY=generate-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

LLM_PROVIDER=groq
GROQ_API_KEY=your-groq-api-key
LLM_MODEL=llama-3.3-70b-versatile

CORS_ORIGINS=http://YOUR_PUBLIC_IP:5173
```

---

## Step 5: Set Up Free Database

1. Go to Oracle Cloud Console → **Autonomous Transaction Processing**
2. Click **Create Database**
3. Configure:
   - **Display name**: metatron-db
   - **Workload type**: Transaction Processing
   - **Deployment type**: Shared Infrastructure (FREE!)
   - **Database version**: 23c (or 19c)
   - **CPU count**: 0 (free tier)
   - **Storage**: 20GB (free tier)
4. Click **Create**

5. Wait 5 minutes for provisioning
6. Go to **Database Details** → **Copy SQL Developer Web**
7. Run this SQL to create user:
```sql
CREATE USER metatron IDENTIFIED BY "your-password";
GRANT CONNECT, RESOURCE TO metatron;
GRANT UNLIMITED TABLESPACE TO metatron;
CREATE DATABASE metatron_db;
GRANT ALL ON metatron_db.* TO metatron;
```

8. Get connection string from **Connection Strings** tab
9. Update `.env` with DB_HOST (from the connection string)

---

## Step 6: Initialize Database

```bash
cd /opt/metatron/backend
python3 -c "from db import init_db; init_db()"
```

---

## Step 7: Start Backend

```bash
# Create service file
sudo nano /etc/systemd/system/metatron.service
```

Paste:
```ini
[Unit]
Description=METATRON Backend
After=network.target

[Service]
Type=simple
User=opc
WorkingDirectory=/opt/metatron/backend
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable metatron
sudo systemctl start metatron
```

Check status:
```bash
sudo systemctl status metatron
```

---

## Step 8: Open Firewall

```bash
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

---

## Access Your App

- **Backend API**: `http://YOUR_PUBLIC_IP:8000`
- **Health Check**: `http://YOUR_PUBLIC_IP:8000/health`

---

## Optional: Add Domain (Free)

Use **Cloudflare** (free DNS):
1. Sign up at cloudflare.com
2. Add your domain
3. Update nameservers at your domain registrar

---

## Cost: $0 Forever