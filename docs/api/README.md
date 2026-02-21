# 📚 API - Lineage 2 PDL

> **Última atualização:** 21/02/2026

Bem-vindo à documentação da API REST do servidor Lineage 2 PDL. Esta API fornece acesso programático aos dados em tempo real do servidor, incluindo status, rankings, estatísticas corporativas, dados da Olimpíada, informações financeiras do mercado e configurações da conta do usuário.

A API foi projetada seguindo padrões RESTful para ser o mais previsível e orientada a desenvolvedores possível.

---

## 📑 Índice da Documentação

A documentação da API está dividida em guias focados:

1. **[Referência da API (`API_REFERENCE.md`)](API_REFERENCE.md)**
   A referência completa e exaustiva técnica de **todos** os endpoints disponíveis na API, seus métodos HTTP recomendados, esquemas de payload JSON (Request/Response) e autenticação necessária.

2. **[Casos e Exemplos de Uso (`API_USE_CASES.md`)](API_USE_CASES.md)**
   Um guia passo a passo com exemplos práticos, mostrando como interagir com a API no mundo real. Ideal para aprender os fluxos complexos como Autenticação, Link de Contas e Status do Jogo.

---

## 🌐 Informações Base

### Base URL Server
Todas as requisições para a Game API principal devem ser feitas para a seguinte base URL:
```text
https://seu-dominio.com/api/v1/
```

Para chamadas referentes à gestão de Contas Lineage (registro, link, senhas), a base URL é:
```text
https://seu-dominio.com/api/accounts/
```

### Formato de Transmissão
A API opera exclusivamente com o formato **JSON**.
Certifique-se de configurar o header `Content-Type: application/json` nas requisições cujo método requer envio de corpo (ex: `POST`, `PUT`, `PATCH`).

---

## 🔐 Autenticação (Fluxo JWT)

Alguns recursos sensíveis exigem que o cliente se autentique antes de receber o payload requisitado.

A autenticação é gerida via **JSON Web Tokens (JWT)**. Para acessar endpoints protegidos (identificados por 🔒 na Referência), inclua seu Token de Acesso (Access Token) no HTTP Header da sua requisição:

```http
Authorization: Bearer <seu_access_token>
```

### Obtendo o Token
1. Faça um `POST` para o endpoint `/api/v1/auth/login/` com seu `username` e `password`.
2. Em caso de sucesso, você receberá dois tokens na resposta: `access` (curta duração) e `refresh` (longa duração).
3. Utilize o token `access` para as chamadas subsequentes.
4. Quando o `access` expirar, envie o `refresh` token para `/api/v1/auth/refresh/` para emitir um novo par de tokens.

---

## 🚦 Rate Limiting (Limitação de Taxa)

Para proteger a integridade do servidor e evitar sobrecargas (DDoS/Spam), a API utiliza limitação rigorosa de requisições:

- **Usuários Anônimos (Sem Token):** Máximo de **30 requisições por minuto** por IP.
- **Usuários Autenticados (Com Token válido):** Máximo de **100 requisições por minuto** por usuário logado.

*Se o limite for ultrapassado, O servidor responderá com o HTTP Status `429 Too Many Requests`.*

---

## ⚡ Caching
Buscando alta performance para as consultas públicas altamente acessadas, algumas respostas da API são cacheadas em memória pelo Servidor Web (Redis):

| Endpoint Principal | Tempo de Cache |
| :--- | :--- |
| **Jogadores Online e Status** | 30 Segundos |
| **Rankings Gerais** | 1 Minuto |
| **Bosses / Grand Bosses Status** | 1 Minuto |
| **Dados da Olimpíada** | 5 Minutos |
| **Cercos (Sieges)** | 5 Minutos |

---

## 📖 Swagger e OpenAPI (Documentação Interativa)

Caso você prefira visualizar, iterar e explorar os Endpoints em tempo real através da UI do Swagger gerada via `drf-spectacular`, os seguintes portais estão disponíveis no seu servidor:

- **API Gateway Dashboard**: `https://seu-dominio.com/api/`
- **Swagger UI**: `https://seu-dominio.com/api/v1/schema/swagger/`
- **ReDoc UI**: `https://seu-dominio.com/api/v1/schema/redoc/`
- **Arquivo Schema Nativo OpenAPI V3**: `https://seu-dominio.com/api/v1/schema/`

---

## 📞 Suporte e Contato

Em caso de dúvidas a respeito das funcionalidades, relatar anomalias (bugs), ou conversar sobre viabilidade técnica de novas requisições programáticas, entre em contato através das canais oficiais em nosso Discord ou verifique as `Issues` no repositório do Github.

---

[ Voltar ao Índice](../INDEX.md)

