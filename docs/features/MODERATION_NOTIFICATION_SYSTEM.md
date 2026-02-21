# Sistema de Notificação de Moderação

> **Última atualização:** 21/02/2026

## 📋 Visão Geral

O sistema de notificação de moderação permite que moderadores enviem notificações automáticas aos usuários quando uma ação de moderação é aplicada. Isso melhora a transparência e comunicação entre moderadores e usuários.

## 🎯 Funcionalidades

### ✅ Implementado

1. **Flag "Notificar Usuário"**: Checkbox no formulário de ação de moderação
2. **Campo de Mensagem Personalizada**: Textarea para mensagem customizada
3. **Notificação Automática**: Envio automático quando ação é aplicada
4. **Mensagens Padrão**: Mensagens automáticas baseadas no tipo de ação
5. **Links Contextuais**: Links para o conteúdo afetado
6. **Tratamento de Erros**: Sistema robusto que não quebra a ação principal

## 🔧 Como Funciona

### 1. Interface do Moderador

No formulário de ação de moderação (`/social/moderation/reports/55/`):

```html
<div class="form-check">
  {{ action_form.notify_user }}
  {{ action_form.notify_user.label_tag }}
</div>

<div class="mb-3" id="notification-message-field" style="display: none;">
  {{ action_form.notification_message.label_tag }}
  {{ action_form.notification_message }}
</div>
```

### 2. JavaScript de Controle

O campo de mensagem aparece/desaparece baseado no checkbox:

```javascript
function toggleNotificationField() {
    if (notifyUserCheckbox && notificationMessageField) {
        if (notifyUserCheckbox.checked) {
            notificationMessageField.style.display = 'block';
        } else {
            notificationMessageField.style.display = 'none';
        }
    }
}
```

### 3. Lógica de Notificação

Quando uma ação é aplicada, o método `apply_action()` verifica:

```python
# Enviar notificação ao usuário se solicitado
if success and self.notify_user and self.target_user:
    try:
        self._send_notification_to_user()
    except Exception as notification_error:
        # Não propagar o erro da notificação
        logger.error(f'Erro ao enviar notificação: {notification_error}')
```

## 📝 Tipos de Mensagens

### Mensagens Padrão por Tipo de Ação

| Ação | Mensagem Padrão |
|------|-----------------|
| `warn` | "Você recebeu uma advertência da moderação." |
| `hide_content` | "Seu conteúdo foi ocultado pela moderação." |
| `delete_content` | "Seu conteúdo foi removido pela moderação." |
| `suspend_user` | "Sua conta foi suspensa temporariamente." |
| `ban_user` | "Sua conta foi banida permanentemente." |
| `restrict_user` | "Suas permissões foram restringidas." |
| `approve_content` | "Seu conteúdo foi aprovado pela moderação." |
| `feature_content` | "Seu conteúdo foi destacado pela moderação." |

### Mensagem Personalizada

Se o moderador preencher o campo "Mensagem de Notificação", ela será usada no lugar da mensagem padrão.

### Adição do Motivo

Se houver um motivo na ação, ele será adicionado à mensagem:

```
Mensagem + " Motivo: [motivo da ação]"
```

## 🔗 Links Contextuais

O sistema automaticamente gera links para o conteúdo afetado:

- **Post**: `/social/post/{post_id}/`
- **Comentário**: `/social/post/{post_id}/#comment-{comment_id}`

## 🛡️ Tratamento de Erros

### Robustez

1. **Não Quebra a Ação Principal**: Erros de notificação não impedem a aplicação da ação
2. **Logs Detalhados**: Todos os erros são registrados no log
3. **Validação de Usuário**: Verifica se o usuário alvo existe antes de enviar
4. **Fallbacks**: Usa mensagens padrão se a personalizada falhar

### Exemplo de Tratamento

```python
try:
    self._send_notification_to_user()
except Exception as notification_error:
    # Não propagar o erro para não quebrar a ação principal
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f'Erro ao enviar notificação ao usuário: {notification_error}')
```

## 🧪 Testando o Sistema

### Script de Teste

Execute o script de teste para verificar se tudo está funcionando:

```bash
python test_notification_system.py
```

### Teste Manual

1. Acesse `/social/moderation/reports/55/`
2. Selecione uma ação de moderação
3. Marque "Notificar Usuário"
4. Opcionalmente, adicione uma mensagem personalizada
5. Aplique a ação
6. Verifique se a notificação foi criada no painel do usuário

## 📊 Estrutura do Banco de Dados

### Campos no ModerationAction

```python
notify_user = models.BooleanField(
    default=True,
    verbose_name=_('Notificar Usuário')
)
notification_message = models.TextField(
    blank=True,
    null=True,
    verbose_name=_('Mensagem de Notificação')
)
```

### Notificação Criada

```python
Notification.objects.create(
    user=target_user,
    notification_type='user',
    message=message,
    created_by=moderator,
    link=link
)
```

## 🎨 Personalização

### Cores e Estilos

As notificações usam o sistema de notificações flutuantes já implementado, com:

- **Sucesso**: Verde
- **Aviso**: Amarelo  
- **Erro**: Vermelho
- **Info**: Azul

### Mensagens Customizadas

Moderadores podem:

1. **Usar mensagem padrão**: Deixar o campo vazio
2. **Mensagem personalizada**: Preencher o campo de texto
3. **Combinar**: Mensagem personalizada + motivo automático

## 🔄 Fluxo Completo

```
1. Moderador acessa /social/moderation/reports/55/
2. Seleciona ação de moderação
3. Marca "Notificar Usuário" (opcional)
4. Adiciona mensagem personalizada (opcional)
5. Aplica a ação
6. Sistema executa apply_action()
7. Se notify_user=True e target_user existe:
   - Cria mensagem (padrão ou personalizada)
   - Gera link contextual
   - Envia notificação via send_notification()
8. Usuário recebe notificação flutuante
```

## 🚀 Benefícios

1. **Transparência**: Usuários sabem quando ações são tomadas
2. **Comunicação**: Moderadores podem explicar decisões
3. **Educação**: Usuários aprendem sobre as regras
4. **Redução de Recursos**: Menos tickets de suporte
5. **Melhor Experiência**: Comunicação clara e profissional

## 🔧 Manutenção

### Logs

Monitore os logs para erros de notificação:

```python
logger.error(f'Erro ao enviar notificação ao usuário: {notification_error}')
```

### Estatísticas

Para acompanhar o uso:

```python
# Notificações enviadas por moderador
ModerationAction.objects.filter(notify_user=True).count()

# Notificações por tipo de ação
ModerationAction.objects.filter(notify_user=True).values('action_type').annotate(count=Count('id'))
```

## 📝 Próximos Passos

### Melhorias Futuras

1. **Templates de Mensagem**: Mensagens pré-definidas para casos comuns
2. **Notificações por Email**: Envio de emails além de notificações in-app
3. **Histórico de Notificações**: Página para moderadores verem notificações enviadas
4. **Configurações Globais**: Permitir desabilitar notificações por tipo de ação
5. **Múltiplos Idiomas**: Suporte a diferentes idiomas nas mensagens

---

**Status**: ✅ Implementado e Funcionando  
**Versão**: 1.0  
**Última Atualização**: Dezembro 2024

---

[ Voltar ao Índice](../INDEX.md)

