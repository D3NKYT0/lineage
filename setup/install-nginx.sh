#!/bin/bash

# Verifica se está rodando como root
if [ "$EUID" -ne 0 ]; then 
    echo "Por favor, execute este script como root (sudo)"
    exit 1
fi

# Detecta a versão do Ubuntu
UBUNTU_VERSION=$(lsb_release -rs)

echo "Detectada versão do Ubuntu: $UBUNTU_VERSION"

# Instala dependências necessárias
apt-get update
apt-get install -y curl gnupg2 ca-certificates lsb-release ubuntu-keyring

# Importa a chave de assinatura do Nginx
curl https://nginx.org/keys/nginx_signing.key | gpg --dearmor | tee /usr/share/keyrings/nginx-archive-keyring.gpg >/dev/null

# Adiciona o repositório oficial do Nginx
echo "deb [signed-by=/usr/share/keyrings/nginx-archive-keyring.gpg] https://nginx.org/packages/mainline/ubuntu $(lsb_release -cs) nginx" | tee /etc/apt/sources.list.d/nginx.list

# Atualiza a lista de pacotes
apt-get update

# Remove versão antiga do Nginx se existir
apt-get remove -y nginx nginx-common nginx-full nginx-core

# Instala o Nginx
apt-get install -y nginx

# Cria as pastas sites-available e sites-enabled caso não existam
mkdir -p /etc/nginx/sites-available
mkdir -p /etc/nginx/sites-enabled

# Cria diretório para verificação do Certbot
mkdir -p /var/www/html/.well-known/acme-challenge
chown -R www-data:www-data /var/www/html/.well-known
chmod -R 755 /var/www/html/.well-known

# Ajusta o nginx.conf para incluir sites-enabled, se ainda não estiver incluído
NGINX_CONF="/etc/nginx/nginx.conf"
INCLUDE_LINE="    include /etc/nginx/sites-enabled/*;"

if ! grep -qF "$INCLUDE_LINE" "$NGINX_CONF"; then
    # Insere o include dentro do bloco http
    # Faz um backup antes
    cp "$NGINX_CONF" "${NGINX_CONF}.bak"

    # Usa sed para inserir antes da última linha do bloco http (antes da última chave '}')
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

# Copia e habilita a configuração de negação de acesso por IP
cp "$(dirname "$0")/nginx-default-deny.conf" /etc/nginx/sites-available/default-deny
ln -sf /etc/nginx/sites-available/default-deny /etc/nginx/sites-enabled/default-deny

# Verifica a instalação
nginx -v

# Habilita e inicia o serviço
systemctl enable nginx
systemctl restart nginx

# Verifica o status
systemctl status nginx --no-pager

echo "Nginx instalado e configurado com sucesso!"
echo "Para verificar a versão instalada: nginx -v"
echo "Para iniciar: systemctl start nginx"
echo "Para parar: systemctl stop nginx"
echo "Para reiniciar: systemctl restart nginx"
