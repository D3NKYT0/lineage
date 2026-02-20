# Integração Bot Discord - PDL

Este documento descreve a integração do bot Discord global com as instâncias do site PDL.

## 📋 Visão Geral

O bot Discord é um bot global que pode se conectar a qualquer instância do site PDL. Ele usa MongoDB para gerenciar seus próprios dados e se comunica com os sites via API REST.

## 🏗️ Arquitetura

### Bot Discord (Separado)
- **Localização**: `bot/`
- **Banco de Dados**: MongoDB
- **Tecnologias**: discord.py, motor (MongoDB async), aiohttp

### Site Django
- **Modelo**: `apps.api.models.DiscordServer`
- **Endpoints**: `/api/v1/discord/server/`
- **Admin**: Painel administrativo para cadastrar servidores

## 🔧 Configuração no Site

### 1. Cadastrar Servidor Discord

No painel administrativo do Django (`/admin/api/discordserver/`):

1. Clique em "Adicionar Servidor Discord"
2. Preencha os campos:
   - **ID do Servidor Discord**: ID numérico do servidor (ex: 1101010101100)
   - **Domínio do Site**: Domínio desta instância (ex: pdl.denky.dev.br)
   - **Nome do Servidor**: Nome do servidor Discord (opcional)
   - **Ativo**: Marque como ativo
3. Salve

### 2. Exemplo de Cadastro

```
ID do Servidor Discord: 1101010101100
Domínio do Site: pdl.denky.dev.br
Nome do Servidor: L2Iron Server
Ativo: ✅
```

## 🔌 Endpoints da API

### GET `/api/v1/discord/server/?discord_guild_id={id}`

Retorna informações do servidor Discord cadastrado.

**Parâmetros:**
- `discord_guild_id` (obrigatório): ID do servidor Discord

**Resposta (200):**
```json
{
  "uuid": "123e4567-e89b-12d3-a456-426614174000",
  "discord_guild_id": 1101010101100,
  "site_domain": "pdl.denky.dev.br",
  "server_name": "L2Iron Server",
  "is_active": true,
  "notes": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Resposta (404):**
```json
{
  "error": "Servidor Discord não encontrado"
}
```

### GET `/api/v1/discord/server/by-domain/`

Retorna informações do servidor Discord cadastrado para o domínio atual.

**Resposta (200):**
```json
{
  "uuid": "123e4567-e89b-12d3-a456-426614174000",
  "discord_guild_id": 1101010101100,
  "site_domain": "pdl.denky.dev.br",
  "server_name": "L2Iron Server",
  "is_active": true
}
```

**Resposta (404):**
```json
{
  "error": "Nenhum servidor Discord cadastrado para este domínio"
}
```

## 🤖 Como o Bot Funciona

### 1. Detecção de Servidor

Quando o bot entra em um servidor Discord:

1. O bot verifica no MongoDB se o servidor está registrado
2. Se não estiver, o bot aguarda o comando `/register`
3. Se estiver, o bot pode usar os comandos imediatamente

### 2. Registro Manual

No servidor Discord, um administrador pode usar:

```
/register pdl.denky.dev.br
```

Isso registra o servidor no MongoDB do bot.

### 3. Consulta à API

Quando o bot precisa de dados do servidor:

1. O bot busca o domínio no MongoDB
2. O bot faz requisição à API do site: `https://{domain}/api/v1/...`
3. O bot exibe os dados no Discord

## 📊 Modelo de Dados

### Django (DiscordServer)

```python
class DiscordServer(BaseModel):
    discord_guild_id = BigIntegerField(unique=True)
    site_domain = CharField(max_length=255, db_index=True)
    server_name = CharField(max_length=255, null=True, blank=True)
    is_active = BooleanField(default=True)
    notes = TextField(null=True, blank=True)
```

### MongoDB (Bot)

```javascript
{
  discord_guild_id: "1101010101100",
  site_domain: "pdl.denky.dev.br",
  server_name: "L2Iron Server",
  is_active: true,
  created_at: ISODate("2024-01-01T00:00:00Z")
}
```

## 🔄 Fluxo de Integração

```
┌─────────────────┐
│  Servidor       │
│  Discord        │
└────────┬────────┘
         │
         │ Bot entra no servidor
         ▼
┌─────────────────┐
│  Bot MongoDB    │
│  Verifica       │
│  registro       │
└────────┬────────┘
         │
         │ Não encontrado
         ▼
┌─────────────────┐
│  Admin usa      │
│  /register      │
└────────┬────────┘
         │
         │ Registra no MongoDB
         ▼
┌─────────────────┐
│  Bot consulta   │
│  API do site    │
│  via domínio    │
└────────┬────────┘
         │
         │ Retorna dados
         ▼
┌─────────────────┐
│  Bot exibe      │
│  no Discord     │
└─────────────────┘
```

## 🛡️ Segurança

- Os endpoints são públicos (AllowAny) para permitir que o bot acesse
- Rate limiting aplicado (30 requisições/minuto)
- Validação de domínio no modelo
- Normalização automática de domínios

## 📝 Notas

- O bot pode estar em múltiplos servidores Discord
- Cada servidor Discord pode estar vinculado a apenas um domínio
- O mesmo domínio pode ter múltiplos servidores Discord (se necessário)
- O bot funciona de forma independente do Django

## 🐛 Troubleshooting

### Bot não encontra servidor

1. Verifique se o servidor está cadastrado no Django admin
2. Verifique se `is_active=True`
3. Verifique se o domínio está correto (sem http://, www, etc)

### API retorna 404

1. Verifique se o endpoint está correto
2. Verifique se a API está habilitada no site
3. Verifique CORS se necessário

### Domínio não normalizado

O sistema normaliza automaticamente:
- Remove `http://` e `https://`
- Remove `www.`
- Remove barras finais
- Converte para minúsculas
