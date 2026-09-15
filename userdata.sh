#!/bin/bash
set -e

# -----------------------------
# 1. Setup directory
# -----------------------------
export APP_DIR=/opt/defect-app
rm -rf $APP_DIR
mkdir -p $APP_DIR
cd $APP_DIR

# -----------------------------
# 2. Install system packages
# -----------------------------
apt update -y
apt install -y git python3 python3-venv python3-pip nginx libgomp1

# -----------------------------
# 3. Clone your project (HTTPS + PAT)
# -----------------------------
git clone https://github.com/Jelilololad/Defect_Detection.git .

# -----------------------------
# 4. Create virtual environment
# -----------------------------
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip

# -----------------------------
# 5. Install Python dependencies
# -----------------------------
pip install numpy pandas scikit-learn==1.4.2 xgboost lightgbm fastapi pydantic imbalanced-learn uvicorn

# -----------------------------
# 6. Train your model (if needed)
# -----------------------------
python3 models.py

# -----------------------------
# 7. Create Uvicorn systemd service
# -----------------------------
cat >/etc/systemd/system/defect_uvicorn.service <<'EOF'
[Unit]
Description=Uvicorn FastAPI server for Defect Detection
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/defect-app
Environment="PATH=/opt/defect-app/.venv/bin"
ExecStart=/opt/defect-app/.venv/bin/uvicorn app:app --host=127.0.0.1 --port=8001
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# -----------------------------
# 8. Configure Nginx reverse proxy
# -----------------------------
cat >/etc/nginx/conf.d/defect_app.conf <<'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_connect_timeout 60s;
        proxy_read_timeout 120s;
    }
}
EOF

rm -f /etc/nginx/sites-enabled/default || true

# -----------------------------
# 9. Start & enable services
# -----------------------------
systemctl daemon-reload
systemctl enable defect_uvicorn
systemctl start defect_uvicorn
systemctl enable nginx
systemctl restart nginx
