# 🎉 Sistema de Notificações Flutuantes

> **Última atualização:** 21/02/2026

## ✨ Características Principais

- 🎯 **Notificações flutuantes** no canto superior direito
- ⏰ **Auto-close** após 5 segundos (configurável)
- ❌ **Fechamento manual** com botão X
- 📚 **Empilhamento** de múltiplas notificações
- 🎨 **Animações suaves** de entrada e saída
- 📊 **Barra de progresso** visual
- 🎨 **5 tipos diferentes**: sucesso, erro, aviso, informação, debug
- 📱 **Totalmente responsivo** para dispositivos móveis
- ⏸️ **Pausa no hover** (auto-close pausado)
- 🔧 **API JavaScript** completa para uso programático

## 🚀 Instalação

O sistema já está **100% integrado** ao seu projeto Django! 

### Arquivos Criados/Modificados:

```
✅ templates/includes/floating-notifications.html    (NOVO)
✅ static/css/floating-notifications.css            (NOVO)
✅ static/js/floating-notifications.js              (NOVO)
✅ static/js/floating-notifications-config.js       (NOVO)
✅ templates/includes/notification-examples.html     (NOVO)
✅ docs/SISTEMA_NOTIFICACOES_FLUTUANTES.md          (NOVO)
✅ templates/layouts/base.html                       (MODIFICADO)
✅ templates/includes/head.html                      (MODIFICADO)
✅ templates/includes/scripts.html                   (MODIFICADO)
```

## 🎯 Uso Imediato

### 1. Django Messages (Automático)

```python
from django.contrib import messages

# Funciona automaticamente!
messages.success(request, 'Operação realizada com sucesso!')
messages.error(request, 'Ocorreu um erro na operação.')
messages.warning(request, 'Atenção: dados incompletos.')
messages.info(request, 'Nova atualização disponível.')
```

### 2. JavaScript (Programático)

```javascript
// Métodos simples
window.floatingNotifications.success('Sucesso!');
window.floatingNotifications.error('Erro!');
window.floatingNotifications.warning('Aviso!');
window.floatingNotifications.info('Informação!');

// Método avançado
window.floatingNotifications.addNotification(
    'Mensagem personalizada',
    'info',
    { autoClose: false, autoCloseDelay: 10000 }
);
```

## 🎨 Personalização Fácil

### 1. Cores Personalizadas

Edite `static/js/floating-notifications-config.js`:

```javascript
const FLOATING_NOTIFICATIONS_CONFIG = {
  colors: {
    success: {
      border: '#00d4aa',
      background: 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)',
      icon: '#00d4aa',
      title: '#00d4aa'
    }
  }
};
```

### 2. Configurações Dinâmicas

```javascript
// Configurar para tema escuro
window.FloatingNotificationsConfig.setupCustom();

// Configurar para admin
window.FloatingNotificationsConfig.setupUserSpecific('admin');

// Configuração manual
window.FloatingNotificationsConfig.updateConfig({
  autoCloseDelay: 8000,
  maxNotifications: 8
});
```

## 📱 Responsividade

- **Desktop**: Notificações no canto superior direito
- **Mobile**: Notificações ocupam toda a largura (com margens)
- **Auto-detecta** o tipo de dispositivo

## 🔧 Configurações Avançadas

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
// Global
window.floatingNotifications.setOptions({
  autoCloseDelay: 3000 // 3 segundos
});

// Específico
window.floatingNotifications.success('Mensagem', {
  autoCloseDelay: 10000 // 10 segundos
});
```

## 🎯 Exemplos Práticos

### Formulário de Login

```python
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
function uploadFile() {
    fetch('/upload/', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.floatingNotifications.success('Arquivo enviado!');
        } else {
            window.floatingNotifications.error('Erro: ' + data.error);
        }
    });
}
```

## 🎨 Tipos de Notificação

| Tipo | Cor | Ícone | Uso |
|------|-----|-------|-----|
| `success` | 🟢 Verde | ✓ | Operações bem-sucedidas |
| `error` | 🔴 Vermelho | ⚠ | Erros e falhas |
| `warning` | 🟡 Amarelo | ⚠ | Avisos e alertas |
| `info` | 🔵 Azul | ℹ | Informações gerais |
| `debug` | ⚫ Cinza | 🐛 | Mensagens de debug |

## 🔄 Migração do Sistema Antigo

### ❌ Antes (Sistema Antigo)
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

### ✅ Depois (Sistema Novo)
```html
<!-- Automático - não precisa de código adicional -->
{% include 'includes/floating-notifications.html' %}
```

## 🛠️ Troubleshooting

### Notificações não aparecem?
1. ✅ Verifique se o JavaScript está carregado
2. ✅ Verifique se há mensagens no contexto Django
3. ✅ Verifique o console do navegador

### Estilos não aplicados?
1. ✅ Verifique se o CSS está sendo carregado
2. ✅ Verifique se não há conflitos com outros estilos
3. ✅ Verifique a ordem de carregamento dos arquivos CSS

### Auto-close não funciona?
1. ✅ Verifique se `autoClose: true` está configurado
2. ✅ Verifique se não há JavaScript interferindo
3. ✅ Verifique se o elemento não foi removido do DOM

## 📚 Documentação Completa

Para documentação detalhada, consulte:
- 📖 `docs/SISTEMA_NOTIFICACOES_FLUTUANTES.md` - Documentação completa
- 🎯 `templates/includes/notification-examples.html` - Exemplos práticos

## 🎉 Benefícios

- ✨ **UX Moderna**: Notificações elegantes e profissionais
- 🚀 **Performance**: Animações suaves e otimizadas
- 📱 **Responsivo**: Funciona perfeitamente em todos os dispositivos
- 🔧 **Flexível**: Fácil personalização e configuração
- 🎯 **Compatível**: Totalmente compatível com Bootstrap 5
- 🌍 **Internacionalizado**: Suporte a múltiplos idiomas
- ♿ **Acessível**: Suporte a leitores de tela

## 🎯 Próximos Passos

1. **Teste o sistema** em diferentes páginas
2. **Personalize as cores** conforme sua identidade visual
3. **Configure o tempo** de auto-close conforme necessário
4. **Use programaticamente** em formulários e AJAX
5. **Compartilhe feedback** para melhorias futuras

---

**🎉 Sistema pronto para uso! As notificações agora são modernas, elegantes e profissionais!**

---

[ Voltar ao Índice](../INDEX.md)

