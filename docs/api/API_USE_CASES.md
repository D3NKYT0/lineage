# 🛠️ Casos de Uso e Exemplos Práticos da API

> **Última atualização:** 21/02/2026

Nesta seção, agrupamos os endpoints documentados na [Referência (API_REFERENCE)](API_REFERENCE.md) em problemas reais que o desenvolvedor web ou o criador de bots podem querer solucionar utilizando nosso servidor. 

---

## Caso de Uso 1: Fluxo Completo de Senha e Dashboard

Seu objetivo é permitir que o usuário faça Login no site, guarde sua autenticação e acesse os painéis do seu "User Dashboard".

### Passo 1: Solicitar os Tokens
Você fará a comunicação de login.

```javascript
// Obtendo o Token na tela de login
const response = await fetch('https://seu-dominio.com/api/v1/auth/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        username: 'john_l2',
        password: 'password123'
    })
});

const data = await response.json();
if (data.access) {
    // É recomendado salvar `access` e `refresh` em LocalStorage ou Cookies seguros.
    localStorage.setItem('accessToken', data.access);
    localStorage.setItem('refreshToken', data.refresh);
    
    // Sucesso no login, prosseguir.
}
```

### Passo 2: Recuperar o Front-end/Dashboard Base
Com o Token Access, agora nós disparamos as rotas do painel que contêm o `Bearer` no Header.

```javascript
const token = localStorage.getItem('accessToken');

const dashResponse = await fetch('https://seu-dominio.com/api/v1/user/dashboard/', {
    method: 'GET',
    headers: {
        'Authorization': `Bearer ${token}`
    }
});

const dashData = await dashResponse.json();
// Renderize a tela usando `dashData` para saudar o user, mostrar chars, etc.
console.log(`Olá, ${dashData.user_info.username}! Seus chars logados somam ${dashData.game_stats.characters}.`);
```

---

## Caso de Uso 2: Integrando as Informações do Servidor na Home do seu Site (Público)

Você quer mostrar de forma dinâmica e leve quantos Players estão Online e mostrar o TOP Ranking PvP. Esses Endpoints não exigem login.

```javascript
// Função autoinvocada para rodar ao carregar a index.html
(async function loadServerStatus() {
    try {
        // 1. Buscando contagem de players
        const playerRes = await fetch('https://seu-dominio.com/api/v1/server/players-online/');
        const playerData = await playerRes.json();
        
        document.getElementById('online-count').innerText = playerData.real_players;

        // 2. Trazendo o TOP 5 de Pvp. Limitando para 5 para economizar rede/interface.
        const pvpRes = await fetch('https://seu-dominio.com/api/v1/server/top-pvp/?limit=5');
        const pvpData = await pvpRes.json();
        
        const listDiv = document.getElementById('pvp-ranking-list');
        pvpData.forEach((player, index) => {
             const div = document.createElement('div');
             div.innerText = `#${index + 1} - ${player.char_name} (${player.pvp_count} PvPs) - Nível ${player.level}`;
             listDiv.appendChild(div);
        });

    } catch (error) {
        console.error('Falha ao obter status do servidor:', error);
    }
})();
```

---

## Caso de Uso 3: Criando um Bot de Discord de "Raid/Grand Boss Alert"

O servidor do discord deverá notificar seus usuários do status atual dos grandes Bosses (Ex: Antharas, Valakas, Baium).

**Linguagem Simbolizada:** `Python / requests`

```python
import requests
import json
import time

API_URL = "https://seu-dominio.com/api/v1/server/grandboss-status/"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/SUA_WEBHOOK_AQUI"

def check_boss_status():
    try:
        response = requests.get(API_URL)
        bosses = response.json()
        
        for boss in bosses:
            # Boss Name, Is Alive, Respawn Time
            if boss.get('is_alive'):
               # Montando a Payload do Discord Action
               payload = {
                   "content": f"🚨 **ALERTA Boss!** O incrível {boss['boss_name']} ({boss['location']}) está **VIVO** neste exato momento e pronto para raid!"
               }
               requests.post(DISCORD_WEBHOOK_URL, json=payload)

    except Exception as e:
        print("Erro de conexao API", e)

# Um loop na nuvem do Cloud Bot que roda a cada exatos 5 minutos
while True:
    check_boss_status()
    time.sleep(300) 
```

---

## Caso de Uso 4: Trabalhando com Linkagem de Contas In-Game e Painel Web

Sua conta web e a do servidor do jogo de Lineage (DB Ingame) precisam ser sincronizadas usando seu Token.

```javascript
async function linkMyGameAccount(gameId, emailTokenValidado) {
    const webToken = localStorage.getItem('accessToken');
    
    // Você vai bater no /api/accounts/link_by_token/
    const response = await fetch('https://seu-dominio.com/api/accounts/link_by_token/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${webToken}`
        },
        body: JSON.stringify({
            game_account_id: gameId,
            verification_token: emailTokenValidado
        })
    });
    
    if (response.ok) {
       alert('Sua conta do JOGO foi ligada a sua conta do SITE com sucesso!');
       // Redirecionar para dashboard de Contas
       window.location.href = "/conta/dashboard";
    }
}
```

---

[ Voltar ao Índice](../INDEX.md)

