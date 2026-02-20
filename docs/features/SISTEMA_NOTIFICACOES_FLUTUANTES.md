# Sistema de Notificações Flutuantes

## Visão Geral

Este sistema substitui o antigo sistema de mensagens do Django por notificações flutuantes modernas e elegantes que aparecem no canto superior direito da tela.

## Características

- ✅ **Notificações flutuantes** no canto superior direito
- ✅ **Auto-close** após 5 segundos (configurável)
- ✅ **Fechamento manual** com botão X
- ✅ **Empilhamento** de múltiplas notificações
- ✅ **Animações suaves** de entrada e saída
- ✅ **Barra de progresso** visual
- ✅ **Diferentes tipos**: sucesso, erro, aviso, informação, debug
- ✅ **Responsivo** para dispositivos móveis
- ✅ **Pausa no hover** (auto-close pausado)
- ✅ **API JavaScript** para uso programático

## Tipos de Notificação

| Tipo | Cor | Ícone | Uso |
|------|-----|-------|-----|
| `success` | Verde | ✓ | Operações bem-sucedidas |
| `error` | Vermelho | ⚠ | Erros e falhas |
| `warning` | Amarelo | ⚠ | Avisos e alertas |
| `info` | Azul | ℹ | Informações gerais |
| `debug` | Cinza | 🐛 | Mensagens de debug |

## Instalação

O sistema já está integrado ao projeto. Os arquivos necessários são:

- `templates/includes/floating-notifications.html` - Template das notificações
- `static/css/floating-notifications.css` - Estilos CSS
- `static/js/floating-notifications.js` - JavaScript funcional
- `templates/layouts/base.html` - Já modificado para usar o novo sistema

## Uso Automático (Django Messages)

O sistema automaticamente exibe todas as mensagens do Django (`messages` framework) como notificações flutuantes.

### No Django (Python)

```python
from django.contrib import messages

# Exemplos de uso
messages.success(request, 'Operação realizada com sucesso!')
messages.error(request, 'Ocorreu um erro na operação.')
messages.warning(request, 'Atenção: dados incompletos.')
messages.info(request, 'Nova atualização disponível.')
messages.debug(request, 'Debug: variável x = 10')
```

## Uso Programático (JavaScript)

### Métodos Básicos

```javascript
// Notificações básicas
window.floatingNotifications.success('Operação realizada com sucesso!');
window.floatingNotifications.error('Ocorreu um erro na operação.');
window.floatingNotifications.warning('Atenção: dados incompletos.');
window.floatingNotifications.info('Nova atualização disponível.');
window.floatingNotifications.debug('Debug: variável x = 10');
```

### Método Avançado

```javascript
window.floatingNotifications.addNotification(
    'Mensagem personalizada',
    'info', // tipo: success, error, warning, info, debug
    {
        autoClose: true,        // fecha automaticamente
        autoCloseDelay: 5000    // tempo em milissegundos
    }
);
```

### Configurações

```javascript
// Configurar opções globais
window.floatingNotifications.setOptions({
    autoClose: true,           // auto-close habilitado
    autoCloseDelay: 5000,      // 5 segundos
    maxNotifications: 5,       // máximo de notificações
    animationDuration: 300     // duração da animação
});
```

### Métodos Utilitários

```javascript
// Fechar todas as notificações
window.floatingNotifications.closeAll();

// Fechar notificação específica
const notification = window.floatingNotifications.success('Teste');
// ... depois ...
window.floatingNotifications.closeNotification(notification);
```

## Personalização

### Cores e Estilos

Edite o arquivo `static/css/floating-notifications.css` para personalizar:

```css
/* Cores de sucesso */
.floating-notification-success {
    border-left-color: #28a745;
    background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
}

/* Cores de erro */
.floating-notification-error {
    border-left-color: #dc3545;
    background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
}
```

### Posicionamento

```css
.floating-notifications-container {
    position: fixed;
    top: 20px;        /* distância do topo */
    right: 20px;      /* distância da direita */
    z-index: 9999;    /* camada */
    max-width: 400px; /* largura máxima */
}
```

### Tempo de Auto-Close

```javascript
// Alterar tempo global
window.floatingNotifications.setOptions({
    autoCloseDelay: 3000 // 3 segundos
});

// Alterar tempo específico
window.floatingNotifications.success('Mensagem', {
    autoCloseDelay: 10000 // 10 segundos
});
```

## Configurações Avançadas

### Notificação Persistente

```javascript
// Notificação que não fecha automaticamente
window.floatingNotifications.addNotification(
    'Esta notificação não fecha automaticamente',
    'info',
    { autoClose: false }
);
```

### Múltiplas Notificações

```javascript
// O sistema automaticamente gerencia múltiplas notificações
window.floatingNotifications.success('Primeira');
window.floatingNotifications.warning('Segunda');
window.floatingNotifications.info('Terceira');
```

### Responsividade

O sistema é automaticamente responsivo:

- **Desktop**: Notificações no canto superior direito
- **Mobile**: Notificações ocupam toda a largura da tela (com margens)

## Compatibilidade

- ✅ **Bootstrap 5** - Totalmente compatível
- ✅ **Bootstrap Icons** - Ícones integrados
- ✅ **Django 3+** - Messages framework
- ✅ **Navegadores modernos** - Chrome, Firefox, Safari, Edge
- ✅ **Dispositivos móveis** - iOS, Android

## Troubleshooting

### Notificações não aparecem

1. Verifique se o JavaScript está carregado
2. Verifique se há mensagens no contexto Django
3. Verifique o console do navegador para erros

### Estilos não aplicados

1. Verifique se o CSS está sendo carregado
2. Verifique se não há conflitos com outros estilos
3. Verifique a ordem de carregamento dos arquivos CSS

### Auto-close não funciona

1. Verifique se `autoClose: true` está configurado
2. Verifique se não há JavaScript interferindo
3. Verifique se o elemento não foi removido do DOM

## Exemplos Práticos

### Formulário de Login

```python
# views.py
def login_view(request):
    if request.method == 'POST':
        user = authenticate(username=username, password=password)
        if user:
            messages.success(request, 'Login realizado com sucesso!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuário ou senha incorretos.')
    
    return render(request, 'login.html')
```

### Upload de Arquivo

```javascript
// JavaScript para upload
function uploadFile() {
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    fetch('/upload/', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.floatingNotifications.success('Arquivo enviado com sucesso!');
        } else {
            window.floatingNotifications.error('Erro ao enviar arquivo: ' + data.error);
        }
    });
}
```

### Validação de Formulário

```javascript
function validateForm() {
    const errors = [];
    
    if (!email.value) {
        errors.push('Email é obrigatório');
    }
    
    if (!password.value) {
        errors.push('Senha é obrigatória');
    }
    
    if (errors.length > 0) {
        errors.forEach(error => {
            window.floatingNotifications.error(error);
        });
        return false;
    }
    
    return true;
}
```

## Migração do Sistema Antigo

O sistema antigo de mensagens foi automaticamente substituído. Se você tinha código personalizado que dependia do antigo sistema, pode ser necessário ajustar:

### Antes (Sistema Antigo)
```html
{% if messages %}
  <div class="container mt-3">
    {% for message in messages %}
      <div class="alert alert-{{ message.tags }}">
        {{ message }}
      </div>
    {% endfor %}
  </div>
{% endif %}
```

### Depois (Sistema Novo)
```html
<!-- Automático - não precisa de código adicional -->
{% include 'includes/floating-notifications.html' %}
```

## Suporte

Para dúvidas ou problemas:

1. Verifique esta documentação
2. Teste com o template de exemplos
3. Verifique o console do navegador
4. Consulte os arquivos de código fonte

---

**Sistema desenvolvido para Django com foco em UX moderna e elegante.**
