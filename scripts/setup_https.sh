#!/bin/bash

# Script pour configurer HTTPS avec nginx + Let's Encrypt

echo "🔐 Configuration HTTPS pour Spoke TTS Server"
echo ""

# Installer nginx et certbot
sudo apt-get update
sudo apt-get install -y nginx certbot python3-certbot-nginx

# Créer la configuration nginx
sudo tee /etc/nginx/sites-available/spoke-tts > /dev/null <<EOF
server {
    listen 80;
    server_name 51.210.165.192;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # CORS headers
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
        add_header Access-Control-Allow-Headers "Content-Type";

        if (\$request_method = OPTIONS) {
            return 204;
        }
    }
}
EOF

# Activer le site
sudo ln -sf /etc/nginx/sites-available/spoke-tts /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

echo ""
echo "✅ Nginx configuré!"
echo "⚠️  Pour HTTPS, vous devez avoir un nom de domaine (pas une IP)"
echo ""
echo "Si vous avez un domaine, lancez:"
echo "  sudo certbot --nginx -d votre-domaine.com"
