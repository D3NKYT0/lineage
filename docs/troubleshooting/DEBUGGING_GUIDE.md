# 🔧 Guia Geral de Debugging e Troubleshooting

> **Última atualização:** 21/02/2026

Este documento contém os passos recomendados para diagnosticar e resolver problemas comuns na plataforma PDL, abrangendo desde anomalias no client-side (Frontend) até rastreamento de fluxos dinâmicos no server-side (Django).

---

## 1. Troubleshooting de Frontend (Client-side)

Problemas estruturais, de botões que não respondem, formulários que não enviam requisições ou componentes que não atualizam a tela geralmente originam-se no frontend.

### A. Console do Navegador
1. Abra as Ferramentas de Desenvolvedor (F12) e acesse a aba **Console**.
2. Interaja com o elemento problemático.
3. Observe mensagens de erro no JavaScript (ex: `ReferenceError`, `TypeError`) ou falhas graves bloqueando o event-loop.

### B. Inspecionando a Rede (Network Tab)
1. Na aba **Network**, limpe o log antes da execução e repita a ação que causou a falha.
2. Verifique se a request está sendo enviada para a URL correta com o verbo HTTP esperado (`GET`, `POST`, `PUT`).
3. Avalie o **Response Payload** (os dados devolvidos) na requisição, ele quase sempre revela mensagens silenciosas que validaram as recusas sem apresentar alertas diretos para o cliente.

### C. Event Listeners e Templates
- Confirme se os handlers de eventos (listeners como `onclick`, `onsubmit`) estao sendo adicionados de forma assíncrona antes do DOM ser completamente renderizado (verifique concorrência).
- Garanta que as varíaveis do ecossistema do template (quando fora do formato PWA), derivadas do Django (ex: variáveis interpoladas como `{{ user.id }}`) foram impressas corretamente nos scripts nativos.

---

## 2. Troubleshooting de Backend (Django)

Falhas de processamento interno, retornos severos `500 Internal Server Error`, exclusões silenciadas ou impedimentos não identificáveis.

### A. Verificação de Roteamento e URLs
Sempre certifique que seus dados em submit alcançam a View mapeada nos arquivos de `urls.py`. 
- Caso os argumentos passem despercebidos, verifique o match com as `regex` e os parâmetros obrigatórios da tipagem nas rotas (como `<int:user_id>`).

### B. Exame Atento de Views e Decorators
Erros de premissões exclusivas em telas que antes passavam batido (ex: `403 Forbidden` e redirecionamentos para login) são bloqueios de View. Inspecione na view específica se as restrições são compatíveis:
- Checagem primária de Sessão (`@login_required`)
- Validações de Tokens (CSRF Middleware Token faltantes no corpo do POST)
- Travas de Segurança Secundária (`@conditional_otp_required` em setores mais críticos).

*Dica Dev:* Ao isolar bugs persistentes em ambiente local, remova provisoriamente (via comentários de código) o decorator do fluxo da view para verificar se o bug habita a restrição e não a renderização, inserindo tudo de volta após averiguação funcional.

### C. Rastreamento e Leitura de Logs
O núcleo PDL conta com loggers estruturados com `X-Request-ID`. Use essa vantagem para filtrar a cadeia:
- Execute `tail -f logs/django.log` ao rodar a plataforma de modo persistente.
- Compare cada request ao banco combinando a saída de query com a request da sessão original filtrando o ID de contexto associado à requisição capturada outrora pelo middleware.

---

## 3. Comandos Úteis

Isolamento de partes específicas podem ser facilmente feitos por linha de comando para evitar a interface.

```bash
# Consultar mapa de links da Plataforma, exemplo com rota de mensagem:
python manage.py show_urls | grep message

# Validando rotas nativamente pela compilação Reversa da shell do Django
python manage.py shell
>>> from django.urls import reverse
>>> reverse('app_name:view_name', kwargs={'id': 1})
```

Caso aplicável, você pode usar a pasta `/test/` para construir pequenos módulos autônomos para imitar chamadas do front sem acoplamentos das engines visuais.

---

[ Voltar ao Índice](../INDEX.md)

