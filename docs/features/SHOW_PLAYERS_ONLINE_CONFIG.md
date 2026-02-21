# Configuração de Exibição de Jogadores Online na Página Inicial

> **Última atualização:** 21/02/2026

## Visão Geral

Esta funcionalidade permite controlar se a quantidade de jogadores online é exibida na página inicial (index) do painel.

## Configuração

### Variável de Ambiente

Adicione a seguinte variável ao seu arquivo `.env`:

```bash
# Exibir quantidade de jogadores online na página inicial
# True = mostrar quantidade de jogadores online
# False = ocultar quantidade de jogadores online
CONFIG_SHOW_PLAYERS_ONLINE=True
```

### Valores Possíveis

- **`True`** (padrão): Exibe a quantidade de jogadores online na seção de estatísticas
- **`False`**: Oculta a quantidade de jogadores online da seção de estatísticas

## Como Funciona

### Com `CONFIG_SHOW_PLAYERS_ONLINE=True`
```
┌─────────────────────────────────────┐
│ 📊 Estatísticas                     │
├─────────────────────────────────────┤
│ 150        │ 25        │ 24/7      │
│ Online     │ Clãs      │ Uptime    │
└─────────────────────────────────────┘
```

### Com `CONFIG_SHOW_PLAYERS_ONLINE=False`
```
┌─────────────────────────────────────┐
│ 📊 Estatísticas                     │
├─────────────────────────────────────┤
│ 25         │ 24/7      │ 🟢 Online │
│ Clãs       │ Uptime    │ Servidor  │
└─────────────────────────────────────┘
```

## Implementação Técnica

A configuração é implementada no arquivo `core/settings.py`:

```python
# Configuração para exibir quantidade de jogadores online na página inicial
SHOW_PLAYERS_ONLINE = os.getenv("CONFIG_SHOW_PLAYERS_ONLINE", "True").lower() in ['true', '1', 'yes']
```

E utilizada na view `apps/main/home/views/views.py`:

```python
# Verificar se deve mostrar jogadores online
show_players_online = getattr(settings, 'SHOW_PLAYERS_ONLINE', True)

context = {
    # ... outros dados ...
    'show_players_online': show_players_online,
    # ... outros dados ...
}
```

E no template `templates/public/index.html`:

```html
{% if show_players_online %}
<div class="stat-item">
    <div class="stat-number">{{ online|default:"0" }}</div>
    <div class="stat-label">{% trans "Online" %}</div>
</div>
{% endif %}
```

## Benefícios

1. **Flexibilidade**: Administradores podem escolher se querem mostrar ou não a quantidade de jogadores
2. **Performance**: Reduz a carga no banco de dados quando não é necessário buscar essa informação
3. **Privacidade**: Alguns servidores preferem não mostrar a quantidade de jogadores por questões estratégicas
4. **Customização**: Cada servidor pode configurar conforme suas necessidades
5. **Compatibilidade**: Mantém compatibilidade com configurações existentes

## Exemplo de Uso

### Para ocultar jogadores online:
```bash
CONFIG_SHOW_PLAYERS_ONLINE=False
```

### Para mostrar jogadores online (padrão):
```bash
CONFIG_SHOW_PLAYERS_ONLINE=True
```

## Notas

- A configuração padrão é `True` (mostrar jogadores online)
- A mudança é aplicada imediatamente após reiniciar o servidor
- A configuração afeta apenas a exibição na página inicial
- Outras funcionalidades que usam dados de jogadores online (como API) não são afetadas
- A contagem de jogadores online continua sendo calculada internamente, apenas não é exibida

## Localização

A funcionalidade afeta especificamente a seção de estatísticas na página inicial (`/`).

## Relacionado

Esta configuração trabalha em conjunto com outras configurações relacionadas a jogadores online:
- `FAKE_PLAYERS_FACTOR`: Multiplicador de jogadores online
- `FAKE_PLAYERS_MIN`: Valor mínimo de jogadores online
- `FAKE_PLAYERS_MAX`: Valor máximo de jogadores online 
---

[ Voltar ao Índice](../INDEX.md)

