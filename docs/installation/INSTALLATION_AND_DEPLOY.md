# Guia de Instalação e Implantação

> **Última atualização:** 21/02/2026

## Pré-requisitos
- **Python** 3.10+ (recomendado 3.14)
- **Docker** e **Docker Compose**
- **Node.js** (opcional, para frontend)
- **Git**

## Instalação Rápida (Recomendado)

O PDL possui o script `install.sh` que automatiza todo o processo:

```bash
git clone https://github.com/D3NKYT0/lineage.git
cd lineage
chmod +x install.sh
./install.sh
```

O script irá:
- Verificar pré-requisitos
- Instalar Docker e Docker Compose (se necessário)
- Configurar ambiente
- Gerar arquivo `.env` interativamente
- Fazer build e iniciar os containers
- Aplicar migrações do banco

Acesse em: `http://localhost:6085`

## Instalação Local (sem Docker)

1. Clone o repositório:
   ```bash
   git clone <url-do-repositorio>
   cd lineage
   ```

2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv .venv
   # Linux/macOS:
   source .venv/bin/activate
   # Windows:
   .venv\Scripts\activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure as variáveis de ambiente:
   - Copie `env.sample` para `.env` e ajuste conforme necessário

5. Execute as migrações e crie um superusuário:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. Inicie o servidor:
   ```bash
   python manage.py runserver
   ```

## Instalação com Docker

1. Configure o arquivo `.env` (use `./install.sh generate-env` para gerar)

2. Execute:
   ```bash
   docker compose up --build -d
   ```
   Ou use o install.sh:
   ```bash
   ./install.sh build
   ```

3. Acesse o sistema em `http://localhost:6085`

## Implantação em Produção

- Use **Docker Compose** com volumes persistentes
- Configure **Nginx** com HTTPS (Let's Encrypt) — use `./install.sh nginx-proxy`
- Ajuste variáveis de ambiente para produção
- Configure backup regular: `./install.sh backup` (ex.: via cron às 3h)

## Comandos Úteis

```bash
# Ver logs
docker compose logs -f

# Acessar container Django
docker compose exec site_http bash

# Reiniciar containers
docker compose restart

# Atualizar projeto
./install.sh update
```

## Documentação Relacionada
- [Guia Completo do install.sh](../installation/INSTALL_SH_GUIDE.md)
- [Variáveis de Ambiente](../installation/VARIABLES_ENVIRONMENT.md)

---

[ Voltar ao Índice](../INDEX.md)

