#!/bin/bash

# Verifica se está rodando como root
if [ "$EUID" -ne 0 ]; then 
    echo "Por favor, execute este script como root (sudo)"
    exit 1
fi

# Função para garantir que a linha de include esteja presente no nginx.conf
configure_nginx_conf() {
    NGINX_CONF="/etc/nginx/nginx.conf"
    INCLUDE_LINE="    include /etc/nginx/sites-enabled/*;"

    # Cria backup
    cp "$NGINX_CONF" "${NGINX_CONF}.bak"

    if ! grep -qF "$INCLUDE_LINE" "$NGINX_CONF"; then
        # Insere o include dentro do bloco http
        sed -i "/http {/{
            :a
            n
            /}/!ba
            i\\
$INCLUDE_LINE
        }" "$NGINX_CONF"
        echo "Linha para incluir sites-enabled adicionada no nginx.conf"
    else
        echo "Linha para incluir sites-enabled já presente no nginx.conf"
    fi
}

# Instala o Nginx se não estiver instalado
if ! command -v nginx &> /dev/null; then
    echo "Instalando Nginx..."
    apt-get update
    apt-get install -y nginx
fi

# Garante que os diretórios existam
mkdir -p /etc/nginx/sites-available
mkdir -p /etc/nginx/sites-enabled

# Configura o nginx.conf para incluir sites-enabled
configure_nginx_conf

# Instala o Certbot para SSL
if ! command -v certbot &> /dev/null; then
    echo "Instalando Certbot..."
    apt-get install -y certbot python3-certbot-nginx
fi

# Cria a configuração do Nginx para proxy reverso
cat > /etc/nginx/sites-available/lineage-proxy << 'EOL'
server {
    listen 80;
    server_name seu-dominio.com;  # Domínio atualizado
    
    # Redirect all HTTP traffic to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name seu-dominio.com;  # Domínio atualizado

    # SSL configuration will be added by certbot
    # ssl_certificate /etc/letsencrypt/live/seu-dominio.com/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/seu-dominio.com/privkey.pem;

    location / {
        proxy_pass http://localhost:6085;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOL

# Cria link simbólico para habilitar o site
ln -sf /etc/nginx/sites-available/lineage-proxy /etc/nginx/sites-enabled/

# Remove a configuração padrão do Nginx, se existir
rm -f /etc/nginx/sites-enabled/default

# Testa a configuração do Nginx
nginx -t

# Reinicia o Nginx
systemctl restart nginx

echo "Configuração do Nginx concluída!"
echo "Para configurar o SSL, execute:"
echo "sudo certbot --nginx -d seu-dominio.com"
echo ""
echo "Lembre-se de substituir 'seu-dominio.com' pelo seu domínio real"
