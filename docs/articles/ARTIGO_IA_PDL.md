# Assistente Virtual com IA do PDL: Como Funciona

## Da Explicação Simples à Implementação Técnica

---

> **Autor:** Equipe PDL (Painel Definitivo Lineage)
> **Data:** Dezembro de 2025
> **Versão:** 1.0

---

## Índice

1. [Introdução](#introdução)
2. [Explicação para Leigos](#explicação-para-leigos---como-funciona-a-ia-do-pdl)
3. [Explicação Técnica](#explicação-técnica---arquitetura-e-implementação)
4. [Exemplos em PHP](#exemplos-em-php)
5. [Limitações do PHP vs Python](#limitações-do-php-e-por-que-python-é-melhor)
6. [Conclusão](#conclusão)

---

## Introdução

O **PDL (Painel Definitivo Lineage)** possui um sistema de assistente virtual com inteligência artificial que oferece suporte automatizado aos usuários. Neste artigo, vamos explicar como esse sistema funciona de forma simples e depois mergulhar nos detalhes técnicos, além de mostrar como você poderia implementar algo similar em PHP e por que escolhemos Python.

---

## Explicação para Leigos - Como Funciona a IA do PDL

### O que é a IA do PDL?

Imagine que você tem uma dúvida sobre como funciona a loja do servidor, como comprar coins ou verificar seu inventário. Antigamente, você teria que criar um ticket de suporte e esperar alguém responder. Com a IA do PDL, você pode **conversar diretamente com um assistente virtual** que responde suas perguntas instantaneamente, 24 horas por dia!

### Como funciona na prática?

1. **Você faz uma pergunta:** "Como compro coins?"
2. **A IA pensa:** Ela consulta uma base de conhecimento com perguntas frequentes (FAQs), analisa o contexto e entende o que você precisa
3. **Você recebe a resposta:** Em segundos, a IA explica como fazer a compra

### O que a IA consegue fazer?

- ✅ **Responder dúvidas comuns** sobre o painel, loja, carteira, etc.
- ✅ **Guiar você** em processos como cadastro, compras e transferências
- ✅ **Sugerir ações** quando necessário
- ✅ **Encaminhar para suporte humano** quando a dúvida é muito complexa

### Como ela "aprende"?

A IA do PDL não é mágica! Ela usa serviços de inteligência artificial poderosos (como Claude da Anthropic, Gemini do Google ou Grok da xAI) combinados com a **base de conhecimento do próprio PDL** (FAQs, documentação, etc.). 

Pense assim: a IA é como um funcionário muito bem treinado que decorou todo o manual do sistema e consegue responder rapidamente consultando suas "anotações".

### Diagrama Simples

```
┌─────────────────────────────────────────────────────────────┐
│                        VOCÊ (Usuário)                       │
│                    "Como compro coins?"                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    CHAT DO PDL (Interface)                  │
│                 Envia sua pergunta via WebSocket            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     SERVIÇO DE IA DO PDL                    │
│   1. Busca FAQs relacionadas                                │
│   2. Monta o contexto (perguntas anteriores + FAQs)         │
│   3. Envia para a IA (Claude/Gemini/Grok)                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   IA EXTERNA (Anthropic, etc)               │
│     Processa e gera uma resposta inteligente                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      RESPOSTA PARA VOCÊ                     │
│  "Para comprar coins, acesse a Loja > Adicionar Saldo..."   │
└─────────────────────────────────────────────────────────────┘
```

---

## Explicação Técnica - Arquitetura e Implementação

### Visão Geral da Arquitetura

O sistema de IA do PDL é composto por várias camadas:

```
┌──────────────────────────────────────────────────────────────────────┐
│                          FRONTEND (JavaScript)                        │
│  - Interface de chat responsiva                                       │
│  - Cliente WebSocket (chatbot.js)                                     │
│  - Indicadores de digitação (typing)                                  │
└──────────────────────────────────────────────────────────────────────┘
                                    │
                         WebSocket (ws://...)
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     DJANGO CHANNELS (Python)                          │
│  - ChatBotConsumer (consumers.py)                                     │
│  - Gerenciamento de conexões assíncronas                              │
│  - Autenticação via AuthMiddlewareStack                               │
└──────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    AIAssistantService (services.py)                   │
│  - Montagem de prompts com contexto (FAQs)                            │
│  - Multi-provider: Anthropic, Gemini, Grok                            │
│  - Extração de sugestões e metadados                                  │
│  - Fallback automático entre modelos                                  │
└──────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
            ┌───────────┐   ┌───────────┐   ┌───────────┐
            │ Anthropic │   │  Google   │   │    xAI    │
            │  Claude   │   │  Gemini   │   │   Grok    │
            └───────────┘   └───────────┘   └───────────┘
```

### Componentes Principais

#### 1. Modelos de Dados (models.py)

```python
# Configuração do provedor de IA
class AIProviderConfig(BaseModel):
    PROVIDER_CHOICES = [
        ('anthropic', 'Anthropic (Claude)'),
        ('gemini', 'Google Gemini'),
        ('grok', 'xAI Grok'),
    ]
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    is_active = models.BooleanField(default=True)

# Sessão de conversa
class ChatSession(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    solicitation = models.ForeignKey(Solicitation, null=True, blank=True)

# Mensagem individual
class ChatMessage(BaseModel):
    ROLE_CHOICES = [('user', 'Usuário'), ('assistant', 'Assistente'), ('system', 'Sistema')]
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    metadata = models.JSONField(default=dict)  # Sugestões, tokens, etc.
    tokens_used = models.IntegerField(default=0)
```

#### 2. Serviço de IA (services.py)

O coração do sistema. Responsável por:

- **Carregar contexto das FAQs** do banco de dados
- **Montar o prompt do sistema** com instruções e conhecimento
- **Chamar a API** do provedor configurado (Claude, Gemini ou Grok)
- **Processar a resposta** e extrair metadados (sugestões, categorias)

```python
class AIAssistantService:
    def __init__(self):
        # Detecta qual provedor está ativo
        self.provider = AIProviderConfig.get_active_provider()
        
        # Inicializa o cliente apropriado
        if self.provider == 'anthropic':
            self.anthropic_client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
        elif self.provider == 'gemini':
            genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
        elif self.provider == 'grok':
            self.grok_client = openai.OpenAI(
                api_key=os.environ.get('XAI_API_KEY'),
                base_url="https://api.x.ai/v1"
            )

    def get_faq_context(self, language='pt'):
        """Busca FAQs públicas e internas para contexto"""
        faqs = FAQ.objects.filter(Q(is_public=True) | Q(show_in_internal=True))
        context_parts = []
        for faq in faqs[:80]:
            translation = faq.translations.filter(language=language).first()
            if translation:
                context_parts.append(f"P: {translation.question}\nR: {translation.answer}")
        return "\n".join(context_parts)

    def create_system_prompt(self, language='pt'):
        """Cria o prompt do sistema com instruções e FAQs"""
        faq_context = self.get_faq_context(language)
        return f"""Você é um assistente virtual do PDL...
        
FAQs Disponíveis:
{faq_context}

INSTRUÇÕES:
1. Responda usando as FAQs quando possível
2. Só sugira criar solicitação em casos complexos
..."""

    def generate_response(self, user_message, conversation_history, language='pt'):
        """Gera resposta da IA"""
        system_prompt = self.create_system_prompt(language)
        
        if self.provider == 'anthropic':
            return self._generate_anthropic_response(user_message, conversation_history, system_prompt)
        elif self.provider == 'gemini':
            return self._generate_gemini_response(...)
        elif self.provider == 'grok':
            return self._generate_grok_response(...)
```

#### 3. WebSocket Consumer (consumers.py)

Gerencia a comunicação em tempo real usando **Django Channels**:

```python
class ChatBotConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Conexão estabelecida"""
        if self.scope["user"].is_anonymous:
            raise DenyConnection("Usuário não autenticado")
        
        self.user = self.scope["user"]
        await self.accept()
        
        # Mensagem de boas-vindas
        await self.send(json.dumps({
            "type": "welcome",
            "message": "Olá! Sou o assistente virtual do PDL..."
        }))

    async def receive(self, text_data):
        """Recebe mensagem do usuário"""
        data = json.loads(text_data)
        
        if data.get('type') == 'message':
            await self.handle_user_message(data)

    async def handle_user_message(self, data):
        """Processa mensagem e gera resposta"""
        message_content = data.get('message')
        
        # Indicador de digitação
        await self.send(json.dumps({"type": "typing", "status": True}))
        
        # Gerar resposta (chamada assíncrona)
        def generate_response():
            service = AIAssistantService()
            return service.generate_response(message_content, history, language)
        
        response_text, metadata = await database_sync_to_async(generate_response)()
        
        # Enviar resposta
        await self.send(json.dumps({
            "type": "message",
            "message": {"role": "assistant", "content": response_text}
        }))
```

### Fluxo de Funcionamento Detalhado

```
1. Usuário conecta ao WebSocket
   └── Consumer verifica autenticação
   └── Cria/recupera sessão de chat

2. Usuário envia mensagem
   └── Consumer recebe via WebSocket
   └── Salva mensagem no banco (ChatMessage)
   └── Envia indicador "typing"

3. Processamento da IA
   └── AIAssistantService instanciado
   └── Busca FAQs relevantes do banco
   └── Monta prompt com contexto + histórico
   └── Chama API externa (Claude/Gemini/Grok)
   └── Processa resposta e extrai metadados

4. Resposta enviada
   └── Salva resposta no banco
   └── Envia via WebSocket ao usuário
   └── Remove indicador "typing"
```

---

## Exemplos em PHP

### Como você faria isso em PHP?

#### Exemplo 1: Chamada Simples à API da Anthropic

```php
<?php
/**
 * Exemplo básico de chamada à API da Anthropic (Claude)
 * Requer: composer require guzzlehttp/guzzle
 */

require 'vendor/autoload.php';

use GuzzleHttp\Client;

class AIAssistantPHP
{
    private $client;
    private $apiKey;
    
    public function __construct($apiKey)
    {
        $this->apiKey = $apiKey;
        $this->client = new Client([
            'base_uri' => 'https://api.anthropic.com/',
            'timeout' => 30.0,
        ]);
    }
    
    public function generateResponse($userMessage, $systemPrompt = '')
    {
        try {
            $response = $this->client->post('v1/messages', [
                'headers' => [
                    'Content-Type' => 'application/json',
                    'x-api-key' => $this->apiKey,
                    'anthropic-version' => '2023-06-01',
                ],
                'json' => [
                    'model' => 'claude-3-5-sonnet-20241022',
                    'max_tokens' => 1024,
                    'system' => $systemPrompt ?: 'Você é um assistente útil.',
                    'messages' => [
                        ['role' => 'user', 'content' => $userMessage]
                    ]
                ]
            ]);
            
            $body = json_decode($response->getBody(), true);
            return [
                'success' => true,
                'message' => $body['content'][0]['text'],
                'tokens' => $body['usage']['input_tokens'] + $body['usage']['output_tokens']
            ];
            
        } catch (\Exception $e) {
            return [
                'success' => false,
                'error' => $e->getMessage()
            ];
        }
    }
}

// Uso
$assistant = new AIAssistantPHP('sua-api-key-aqui');
$result = $assistant->generateResponse('Como compro coins no servidor?');

if ($result['success']) {
    echo "Resposta: " . $result['message'];
} else {
    echo "Erro: " . $result['error'];
}
```

#### Exemplo 2: Com Contexto de FAQs

```php
<?php
/**
 * Assistente com contexto de FAQs
 */

class AIAssistantWithContext
{
    private $client;
    private $apiKey;
    private $pdo;
    
    public function __construct($apiKey, $pdo)
    {
        $this->apiKey = $apiKey;
        $this->pdo = $pdo;
        $this->client = new \GuzzleHttp\Client([
            'base_uri' => 'https://api.anthropic.com/',
        ]);
    }
    
    /**
     * Busca FAQs do banco de dados
     */
    private function getFaqContext($language = 'pt')
    {
        $stmt = $this->pdo->prepare("
            SELECT f.id, ft.question, ft.answer 
            FROM faqs f
            JOIN faq_translations ft ON f.id = ft.faq_id
            WHERE f.is_public = 1 AND ft.language = ?
            ORDER BY f.order_position
            LIMIT 50
        ");
        $stmt->execute([$language]);
        
        $context = [];
        while ($row = $stmt->fetch()) {
            $context[] = "P: {$row['question']}\nR: {$row['answer']}";
        }
        
        return implode("\n\n", $context);
    }
    
    /**
     * Cria o prompt do sistema
     */
    private function createSystemPrompt($language = 'pt')
    {
        $faqContext = $this->getFaqContext($language);
        
        return <<<PROMPT
Você é um assistente virtual para um servidor de Lineage 2.
Sua função é responder perguntas usando as FAQs abaixo.

FAQs Disponíveis:
{$faqContext}

INSTRUÇÕES:
- Responda de forma clara e objetiva
- Use as FAQs como base para suas respostas
- Se não souber, admita e sugira contato com o suporte
PROMPT;
    }
    
    /**
     * Gera resposta com contexto
     */
    public function chat($userMessage, $conversationHistory = [])
    {
        $messages = [];
        
        // Adiciona histórico
        foreach ($conversationHistory as $msg) {
            $messages[] = [
                'role' => $msg['role'],
                'content' => $msg['content']
            ];
        }
        
        // Adiciona mensagem atual
        $messages[] = ['role' => 'user', 'content' => $userMessage];
        
        try {
            $response = $this->client->post('v1/messages', [
                'headers' => [
                    'Content-Type' => 'application/json',
                    'x-api-key' => $this->apiKey,
                    'anthropic-version' => '2023-06-01',
                ],
                'json' => [
                    'model' => 'claude-3-5-sonnet-20241022',
                    'max_tokens' => 1024,
                    'system' => $this->createSystemPrompt(),
                    'messages' => $messages
                ]
            ]);
            
            $body = json_decode($response->getBody(), true);
            
            return [
                'success' => true,
                'message' => $body['content'][0]['text'],
                'tokens_used' => $body['usage']['input_tokens'] + $body['usage']['output_tokens']
            ];
            
        } catch (\Exception $e) {
            return [
                'success' => false,
                'error' => $e->getMessage()
            ];
        }
    }
}
```

#### Exemplo 3: WebSocket com Ratchet (PHP)

```php
<?php
/**
 * WebSocket Server com Ratchet
 * composer require cboden/ratchet
 * 
 * ATENÇÃO: Este é um exemplo simplificado.
 * Em produção, você precisaria de muito mais código.
 */

use Ratchet\MessageComponentInterface;
use Ratchet\ConnectionInterface;

class ChatServer implements MessageComponentInterface
{
    protected $clients;
    protected $aiService;
    
    public function __construct()
    {
        $this->clients = new \SplObjectStorage;
        $this->aiService = new AIAssistantPHP(getenv('ANTHROPIC_API_KEY'));
    }
    
    public function onOpen(ConnectionInterface $conn)
    {
        $this->clients->attach($conn);
        
        // Mensagem de boas-vindas
        $conn->send(json_encode([
            'type' => 'welcome',
            'message' => 'Olá! Sou o assistente virtual. Como posso ajudar?'
        ]));
    }
    
    public function onMessage(ConnectionInterface $from, $msg)
    {
        $data = json_decode($msg, true);
        
        if ($data['type'] === 'message') {
            // Indicador de digitação
            $from->send(json_encode(['type' => 'typing', 'status' => true]));
            
            // PROBLEMA: Esta chamada é SÍNCRONA!
            // O servidor TRAVA enquanto espera a resposta da IA
            $response = $this->aiService->generateResponse($data['message']);
            
            // Envia resposta
            $from->send(json_encode([
                'type' => 'message',
                'message' => $response['message']
            ]));
            
            // Remove indicador
            $from->send(json_encode(['type' => 'typing', 'status' => false]));
        }
    }
    
    public function onClose(ConnectionInterface $conn)
    {
        $this->clients->detach($conn);
    }
    
    public function onError(ConnectionInterface $conn, \Exception $e)
    {
        $conn->close();
    }
}

// Para rodar o servidor:
// php -r "require 'vendor/autoload.php'; 
//         $server = \Ratchet\Server\IoServer::factory(
//             new \Ratchet\Http\HttpServer(
//                 new \Ratchet\WebSocket\WsServer(new ChatServer())
//             ), 8080
//         ); 
//         $server->run();"
```

---

## Limitações do PHP e Por Que Python é Melhor

### 1. Programação Assíncrona

#### O Problema em PHP

PHP foi projetado para o modelo **request-response**: recebe uma requisição, processa, responde e morre. Isso é péssimo para:

- **WebSockets**: Conexões que precisam ficar abertas
- **Chamadas de API lentas**: Enquanto espera a IA responder, o servidor trava

```php
// PHP - SÍNCRONO (bloqueante)
$response = $client->post('api/ai'); // ← Servidor TRAVA aqui por 2-5 segundos
// Nenhum outro usuário pode ser atendido enquanto isso!
```

#### A Solução em Python

Python com **asyncio** permite processamento verdadeiramente assíncrono:

```python
# Python - ASSÍNCRONO (não-bloqueante)
response = await client.post('api/ai')  # ← Servidor continua atendendo outros
# Enquanto espera, outras requisições são processadas!
```

### 2. Django Channels vs Ratchet

| Aspecto | Django Channels (Python) | Ratchet (PHP) |
|---------|-------------------------|---------------|
| **Async Nativo** | ✅ Sim, completo | ❌ Parcial, gambiarras |
| **Integração com ORM** | ✅ database_sync_to_async | ❌ Complexo, propenso a erros |
| **Autenticação** | ✅ AuthMiddlewareStack integrado | ❌ Implementação manual |
| **Escalabilidade** | ✅ Redis, múltiplos workers | ❌ Limitado |
| **Documentação** | ✅ Excelente | ⚠️ Básica |

### 3. Ecossistema de IA

#### Bibliotecas Oficiais

| Provedor | Python | PHP |
|----------|--------|-----|
| **Anthropic (Claude)** | ✅ `anthropic` (oficial) | ❌ Não oficial |
| **Google Gemini** | ✅ `google-generativeai` (oficial) | ❌ Não oficial |
| **OpenAI/Grok** | ✅ `openai` (oficial) | ⚠️ Comunidade |

Python tem **SDKs oficiais** de todos os principais provedores de IA. Em PHP, você precisa:
- Usar bibliotecas da comunidade (menos atualizadas)
- Ou fazer chamadas HTTP manuais (mais trabalho, mais bugs)

### 4. Exemplo Comparativo Real

#### Fallback entre Modelos em Python

```python
# Python - Elegante e simples
model_names = [
    'claude-3-5-sonnet-20241022',
    'claude-3-haiku-20240307',
]

for model_name in model_names:
    try:
        response = await self.client.messages.create(
            model=model_name,
            max_tokens=1024,
            messages=messages
        )
        break  # Sucesso!
    except NotFoundError:
        continue  # Tenta próximo modelo
```

#### Mesmo código em PHP

```php
// PHP - Verbose e complexo
$modelNames = [
    'claude-3-5-sonnet-20241022',
    'claude-3-haiku-20240307',
];

$response = null;
$lastError = null;

foreach ($modelNames as $modelName) {
    try {
        $response = $this->client->post('v1/messages', [
            'json' => [
                'model' => $modelName,
                'max_tokens' => 1024,
                'messages' => $messages
            ]
        ]);
        break;
    } catch (\GuzzleHttp\Exception\ClientException $e) {
        $statusCode = $e->getResponse()->getStatusCode();
        if ($statusCode === 404) {
            $lastError = $e;
            continue;
        }
        throw $e;
    }
}

if ($response === null) {
    throw $lastError ?? new \Exception('Nenhum modelo disponível');
}
```

### 5. Performance e Concorrência

#### Cenário: 100 usuários simultâneos no chat

**PHP (Ratchet/ReactPHP):**
- Cada chamada de IA (2-5s) **bloqueia o event loop**
- Mesmo com workers, escala mal
- Precisa de arquitetura complexa (filas, workers separados)

**Python (Django Channels + asyncio):**
- Chamadas são **não-bloqueantes**
- Um único processo atende centenas de conexões
- Escala horizontalmente com Redis

### 6. Resumo: Por Que Escolhemos Python

| Critério | PHP | Python |
|----------|-----|--------|
| **Async/Await Nativo** | ❌ | ✅ |
| **WebSockets Integrado** | ❌ | ✅ |
| **SDKs de IA Oficiais** | ❌ | ✅ |
| **ORM Assíncrono** | ❌ | ✅ |
| **Comunidade de IA** | ⚠️ | ✅ |
| **Manutenibilidade** | ⚠️ | ✅ |
| **Performance em Tempo Real** | ❌ | ✅ |

### Quando PHP Ainda Faz Sentido?

- ✅ APIs REST simples (sem tempo real)
- ✅ Sistemas CRUD tradicionais
- ✅ Quando sua equipe só conhece PHP
- ✅ Integração com sistemas legados em PHP

### Quando Python é a Escolha Certa?

- ✅ **Qualquer coisa com IA** (chatbots, ML, processamento)
- ✅ **WebSockets e tempo real**
- ✅ **Alta concorrência** (muitos usuários simultâneos)
- ✅ **Processamento assíncrono** (filas, background tasks)

---

## Conclusão

A implementação de um assistente virtual com IA no PDL demonstra a importância de escolher as ferramentas certas para cada trabalho:

1. **Python + Django Channels** nos permite ter WebSockets eficientes com async/await nativo
2. **Multi-provider** (Claude, Gemini, Grok) garante disponibilidade e flexibilidade
3. **Integração com FAQs** personaliza as respostas para o contexto do servidor
4. **Armazenamento de sessões** permite histórico e análise

Enquanto PHP continua sendo uma excelente escolha para muitos cenários web, **sistemas de IA em tempo real** se beneficiam enormemente das capacidades assíncronas nativas do Python.

Se você está pensando em implementar algo similar em seu servidor, considere:
- Começar com chamadas REST simples (funciona em qualquer linguagem)
- Migrar para WebSockets quando precisar de tempo real
- Avaliar Python se precisar de performance e escalabilidade

---

## Links Úteis

- **PDL Demo**: https://pdl.denky.dev.br
- **Documentação Anthropic**: https://docs.anthropic.com
- **Django Channels**: https://channels.readthedocs.io
- **Google Gemini**: https://ai.google.dev
- **xAI Grok**: https://x.ai

---

*Dúvidas? Deixe seu comentário no L2JBrasil!*

**PDL - Painel Definitivo Lineage**
*Transformando a gestão de servidores Lineage 2*
