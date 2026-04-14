#!/bin/bash
# METATRON Quick Deploy Script for Oracle Cloud / VPS
# Run: bash setup.sh

set -e

echo "=========================================="
echo "  METATRON Server Setup"
echo "=========================================="

# Check if root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root: sudo bash setup.sh"
  exit 1
fi

echo "[1/7] Updating system..."
dnf update -y

echo "[2/7] Installing security tools..."
dnf install -y nmap curl bind-utils whois git python3 python3-pip psmisc

echo "[3/7] Installing Python tools..."
pip3 install -r requirements.txt --break-system-packages 2>/dev/null || \
pip3 install fastapi uvicorn sqlalchemy pymysql python-jose passlib --break-system-packages

echo "[4/7] Creating metatron user..."
useradd -m -s /bin/bash metatron 2>/dev/null || true
mkdir -p /opt/metatron
chown -R metatron:metatron /opt/metatron

echo "[5/7] Setting up service..."
cat > /etc/systemd/system/metatron.service << 'EOF'
[Unit]
Description=METATRON Backend API
After=network.target

[Service]
Type=simple
User=metatron
WorkingDirectory=/opt/metatron/backend
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable metatron

echo "[6/7] Configuring firewall..."
firewall-cmd --permanent --add-port=8000/tcp 2>/dev/null || true
firewall-cmd --reload 2>/dev/null || true

echo "[7/7] Done!"
echo ""
echo "=========================================="
echo "  Next Steps:"
echo "=========================================="
echo "1. Upload your code to /opt/metatron"
echo "2. Configure .env with your database"
echo "3. Run: systemctl start metatron"
echo "4. Check: curl http://localhost:8000/health"
echo ""
echo "Your public IP: $(curl -s ifconfig.me)"
echo "=========================================="