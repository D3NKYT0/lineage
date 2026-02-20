# Troubleshooting - Botões não funcionam

## Problema
Os botões na página de amigos não estão funcionando quando clicados.

## Possíveis Causas e Soluções

### 1. Verificar Console do Navegador
1. Abra o console do navegador (F12)
2. Clique em um botão
3. Verifique se há mensagens de log ou erros

**Logs esperados:**
```
Enviando solicitação de amizade para usuário: 123
URL: /app/message/send-friend-request/123/
```

### 2. Verificar URLs
As URLs devem estar corretas no arquivo `apps/main/message/urls.py`:

```python
urlpatterns = [
    path('send-friend-request/<int:user_id>/', send_friend_request, name='send_friend_request'),
    path('accept-friend-request/<int:friendship_id>/', accept_friend_request, name='accept_friend_request'),
    path('reject-friend-request/<int:friendship_id>/', reject_friend_request, name='reject_friend_request'),
    path('remove-friend/<int:friendship_id>/', remove_friend, name='remove_friend'),
    # ...
]
```

### 3. Verificar Views
As views devem existir em `apps/main/message/views.py`:

```python
@conditional_otp_required
def send_friend_request(request, user_id):
    # ...

@conditional_otp_required
def accept_friend_request(request, friendship_id):
    # ...

@conditional_otp_required
def reject_friend_request(request, friendship_id):
    # ...

@conditional_otp_required
def remove_friend(request, friendship_id):
    # ...
```

### 4. Verificar Decorator OTP
O decorator `@conditional_otp_required` pode estar bloqueando as requisições.

**Solução temporária:** Remover o decorator para teste:
```python
# Comentar temporariamente para teste
# @conditional_otp_required
def send_friend_request(request, user_id):
    # ...
```

### 5. Verificar JavaScript
O JavaScript pode estar com problemas. Verificar:

1. **Funções definidas:**
```javascript
function sendFriendRequest(userId) {
    console.log('Enviando solicitação de amizade para usuário:', userId);
    // ...
}
```

2. **Eventos onclick:**
```html
<button onclick="sendFriendRequest({{ user.id }})">
```

### 6. Verificar Permissões
O usuário pode não ter permissões para acessar as views.

**Solução:** Verificar se o usuário está logado e tem as permissões necessárias.

### 7. Verificar CSRF Token
Se as requisições são POST, pode ser necessário CSRF token.

**Solução:** Adicionar CSRF token ou usar GET requests.

### 8. Teste Manual
Testar manualmente as URLs:

1. Acesse diretamente: `/app/message/send-friend-request/1/`
2. Verifique se redireciona corretamente
3. Verifique se não há erros 404 ou 500

### 9. Logs do Django
Verificar os logs do Django para erros:

```bash
python manage.py runserver
# Clique nos botões e observe os logs
```

### 10. Debug com Python
Executar o script de debug:

```bash
python test/test_buttons_debug.py
```

## Soluções Implementadas

### 1. JavaScript Melhorado
- Adicionado tratamento de erros
- Logs de debug
- URLs construídas de forma mais robusta

### 2. Verificação de Elementos
- Verificação se elementos existem antes de adicionar event listeners
- Tratamento de erros para elementos não encontrados

### 3. URLs Corrigidas
- Uso correto das URLs do Django
- Substituição adequada de parâmetros

## Próximos Passos

1. **Testar no navegador:**
   - Abrir console (F12)
   - Clicar nos botões
   - Verificar logs e erros

2. **Verificar URLs:**
   - Confirmar que as URLs estão corretas
   - Testar acesso direto às URLs

3. **Verificar Views:**
   - Confirmar que as views existem
   - Verificar se não há erros nas views

4. **Verificar Permissões:**
   - Confirmar que o usuário tem acesso
   - Verificar decorators de autenticação

## Comandos Úteis

```bash
# Verificar URLs
python manage.py show_urls | grep message

# Testar views
python manage.py shell
>>> from django.urls import reverse
>>> reverse('message:send_friend_request', kwargs={'user_id': 1})

# Verificar logs
tail -f logs/django.log
``` 