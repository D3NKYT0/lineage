# Configuração de Exibição de Tempo dos Grand Bosses

## Visão Geral

Esta funcionalidade permite controlar como o tempo de respawn dos Grand Bosses é exibido na página `/app/server/status/grandboss/`.

## Configuração

### Variável de Ambiente

Adicione a seguinte variável ao seu arquivo `.env`:

```bash
# Exibir data e hora ou apenas data no status dos Grand Bosses
# True = mostra data e hora (ex: 25/12/2024 14:30)
# False = mostra apenas data (ex: 25/12/2024)
CONFIG_GRANDBOSS_SHOW_TIME=True
```

### Valores Possíveis

- **`True`** (padrão): Exibe data e hora no formato `dd/mm/aaaa hh:mm`
- **`False`**: Exibe apenas a data no formato `dd/mm/aaaa`

## Como Funciona

### Com `CONFIG_GRANDBOSS_SHOW_TIME=True`
```
Nome do Boss    | Nível | Respawn        | Status
----------------|-------|----------------|--------
Boss Exemplo    | 80    | 25/12/2024 14:30 | Morto
```

### Com `CONFIG_GRANDBOSS_SHOW_TIME=False`
```
Nome do Boss    | Nível | Respawn    | Status
----------------|-------|------------|--------
Boss Exemplo    | 80    | 25/12/2024 | Morto
```

## Implementação Técnica

A configuração é implementada no arquivo `core/settings.py`:

```python
# Configuração para exibir data e hora ou apenas data no status dos Grand Bosses
GRANDBOSS_SHOW_TIME = os.getenv("CONFIG_GRANDBOSS_SHOW_TIME", "True").lower() in ['true', '1', 'yes']
```

E utilizada na view `apps/lineage/server/views/status_views.py`:

```python
# Usar configuração para decidir se mostra data e hora ou apenas data
if getattr(settings, 'GRANDBOSS_SHOW_TIME', True):
    boss['respawn_human'] = respawn_datetime.strftime('%d/%m/%Y %H:%M')
else:
    boss['respawn_human'] = respawn_datetime.strftime('%d/%m/%Y')
```

## Benefícios

1. **Flexibilidade**: Administradores podem escolher o nível de detalhe desejado
2. **Performance**: Menos informações podem melhorar a legibilidade em dispositivos móveis
3. **Customização**: Cada servidor pode configurar conforme suas necessidades
4. **Compatibilidade**: Mantém compatibilidade com configurações existentes

## Exemplo de Uso

### Para mostrar apenas data:
```bash
CONFIG_GRANDBOSS_SHOW_TIME=False
```

### Para mostrar data e hora (padrão):
```bash
CONFIG_GRANDBOSS_SHOW_TIME=True
```

## Notas

- A configuração padrão é `True` (mostrar data e hora)
- A mudança é aplicada imediatamente após reiniciar o servidor
- A configuração afeta apenas a exibição, não os dados armazenados
- O formato de data segue o padrão brasileiro (dd/mm/aaaa) 