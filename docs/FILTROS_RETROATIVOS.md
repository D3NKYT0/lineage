# 🔄 Sistema de Filtros Retroativos

## Visão Geral

O sistema de filtros retroativos permite aplicar as regras de moderação atuais a todo o conteúdo já existente no sistema, garantindo que posts e comentários criados antes da implementação dos filtros também sejam verificados e moderados adequadamente.

## ✨ Características Principais

### 🎯 **Aplicação Inteligente**
- **Processamento em Lotes**: Evita sobrecarga do sistema
- **Filtros Específicos**: Pode aplicar um filtro específico ou todos
- **Tipos de Conteúdo**: Posts, comentários ou ambos
- **Modo Simulação**: Teste antes de aplicar mudanças

### 📊 **Interface Completa**
- **Dashboard Integrado**: Acesso direto do painel de moderação
- **Estatísticas em Tempo Real**: Progresso e resultados
- **Configuração Flexível**: Múltiplas opções de execução
- **Logs Detalhados**: Acompanhamento completo das ações

### ⚡ **Performance Otimizada**
- **Processamento Assíncrono**: Não bloqueia a interface
- **Limite de Segurança**: Proteção contra timeouts
- **Transações Atômicas**: Consistência dos dados
- **Recuperação de Erros**: Falhas não interrompem o processo

## 🚀 Como Usar

### 1. **Via Interface Web**

#### Acessar:
```
Dashboard de Moderação → Filtros Retroativos
/social/moderation/apply-retroactive/
```

#### Configurar:
- **Tipo de Conteúdo**: Posts, comentários ou ambos
- **Filtro Específico**: Um filtro ou todos (opcional)
- **Modo Simulação**: Recomendado para primeira execução

#### Executar:
1. **Simular** primeiro para ver impacto
2. **Aplicar** após confirmar resultados
3. **Acompanhar** logs e estatísticas

### 2. **Via Linha de Comando**

#### Comando Básico:
```bash
python manage.py apply_filters_retroactive
```

#### Opções Disponíveis:
```bash
# Simulação (dry-run)
python manage.py apply_filters_retroactive --dry-run

# Apenas posts
python manage.py apply_filters_retroactive --content-type posts

# Apenas comentários  
python manage.py apply_filters_retroactive --content-type comments

# Filtro específico
python manage.py apply_filters_retroactive --filter-id 5

# Tamanho do lote customizado
python manage.py apply_filters_retroactive --batch-size 200

# Combinação de opções
python manage.py apply_filters_retroactive --content-type posts --filter-id 3 --dry-run
```

## 📋 Parâmetros de Configuração

### Interface Web
| Parâmetro | Opções | Descrição |
|-----------|--------|-----------|
| **Tipo de Conteúdo** | all, posts, comments | Define que tipo de conteúdo será processado |
| **Filtro Específico** | ID do filtro ou vazio | Aplica apenas um filtro ou todos |
| **Modo Simulação** | checkbox | Executa sem aplicar mudanças reais |

### Linha de Comando
| Argumento | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `--dry-run` | flag | False | Modo simulação |
| `--batch-size` | int | 100 | Itens processados por lote |
| `--filter-id` | int | None | ID específico do filtro |
| `--content-type` | choice | all | posts/comments/all |

## 🔧 Funcionamento Técnico

### Processo de Execução
1. **Validação**: Verifica filtros ativos e permissões
2. **Preparação**: Conta itens e estima tempo
3. **Processamento**: Executa em lotes configuráveis
4. **Aplicação**: Executa ações baseadas no tipo de filtro
5. **Logging**: Registra todas as ações e resultados

### Ações por Tipo de Filtro
| Ação | Comportamento Retroativo |
|------|-------------------------|
| **🏴 Flag** | Cria denúncia automática |
| **👁️ Auto Hide** | Oculta posts (is_public=False) |
| **🗑️ Auto Delete** | Remove conteúdo permanentemente |
| **📧 Notify Moderator** | Cria denúncia de alta prioridade |

### Proteções Implementadas
- **Duplicação**: Não cria denúncias duplicadas
- **Performance**: Lotes configuráveis
- **Atomicidade**: Transações por item
- **Logs**: Registro completo de ações
- **Permissões**: Verificação de acesso

## 📊 Logs e Auditoria

### Logs Criados
Cada aplicação de filtro gera:
```
Moderador: Sistema (null)
Ação: filter_triggered
Tipo: post/comment
Descrição: "Filtro retroativo aplicado: [Nome do Filtro]"
Detalhes: Conteúdo truncado e padrão detectado
```

### Denúncias Geradas
Para ações `flag` e `notify_moderator`:
```
Reporter: Sistema (null)
Tipo: spam/inappropriate
Status: pending
Prioridade: medium/high
Descrição: "Conteúdo filtrado retroativamente: [Nome do Filtro]"
```

### Estatísticas Atualizadas
- **matches_count**: Incrementado para cada match
- **last_matched**: Atualizado com timestamp atual

## ⚠️ Considerações Importantes

### Performance
- **Tempo de Execução**: Proporcional ao volume de conteúdo
- **Recursos**: Pode consumir CPU/memória durante execução
- **Banco de Dados**: Gera várias transações

### Impacto no Sistema
- **Conteúdo Deletado**: Ação irreversível
- **Denúncias**: Pode gerar muitos itens para moderação
- **Usuários**: Conteúdo pode desaparecer retroativamente

### Recomendações
1. **Sempre simular primeiro** com `--dry-run`
2. **Executar fora do horário de pico**
3. **Monitorar logs durante execução**
4. **Fazer backup antes de execuções grandes**
5. **Testar com lotes menores primeiro**

## 🛡️ Segurança e Permissões

### Permissões Necessárias
```python
'social.can_take_moderation_actions'
```

### Limitações de Segurança
- **Interface Web**: Lotes de 50 itens (performance)
- **Linha de Comando**: Lotes de 100 itens (padrão)
- **Timeout**: 5 minutos máximo por execução web
- **Logs**: Todas as ações são auditadas

## 📈 Casos de Uso

### 1. **Nova Implementação**
Cenário: Sistema implementado sem filtros
```bash
# 1. Criar filtros padrão
python manage.py setup_moderation

# 2. Simular aplicação
python manage.py apply_filters_retroactive --dry-run

# 3. Aplicar a todo conteúdo
python manage.py apply_filters_retroactive
```

### 2. **Novo Filtro Criado**
Cenário: Adicionado filtro específico
```bash
# Aplicar apenas o novo filtro
python manage.py apply_filters_retroactive --filter-id 15
```

### 3. **Auditoria de Conteúdo**
Cenário: Verificação periódica
```bash
# Verificar apenas posts dos últimos 30 dias
# (implementar filtro de data se necessário)
python manage.py apply_filters_retroactive --content-type posts --dry-run
```

### 4. **Limpeza de Spam**
Cenário: Onda de spam detectada
```bash
# Aplicar filtros anti-spam específicos
python manage.py apply_filters_retroactive --filter-id 8 --filter-id 12
```

## 🔗 Integrações

### Sistema de Moderação
- **Filtros**: Usa filtros ativos do ContentFilter
- **Denúncias**: Integra com sistema de Report
- **Logs**: Registra em ModerationLog
- **Ações**: Reutiliza lógica de ModerationAction

### Interface de Administração
- **Dashboard**: Link direto na seção "Ações Rápidas"
- **Filtros**: Mostra filtros disponíveis
- **Logs**: Resultados visíveis nos logs de moderação

### API (Futuro)
```python
# Endpoint planejado
POST /api/v1/moderation/apply-retroactive/
{
    "content_type": "posts",
    "filter_id": 5,
    "dry_run": true
}
```

## 📚 Exemplos Práticos

### Exemplo 1: Primeira Execução
```bash
# Verificar filtros disponíveis
python manage.py shell -c "
from apps.main.social.models import ContentFilter
for f in ContentFilter.objects.filter(is_active=True):
    print(f'{f.id}: {f.name} - {f.get_action_display()}')
"

# Simular aplicação
python manage.py apply_filters_retroactive --dry-run

# Aplicar se resultados estiverem OK
python manage.py apply_filters_retroactive
```

### Exemplo 2: Filtro Específico
```bash
# Aplicar apenas filtro de palavrões
python manage.py apply_filters_retroactive --filter-id 3 --content-type posts
```

### Exemplo 3: Verificação Mensal
```bash
# Script para execução mensal
#!/bin/bash
echo "Iniciando verificação mensal de conteúdo..."
python manage.py apply_filters_retroactive --dry-run > /tmp/moderation_check.log
echo "Resultados salvos em /tmp/moderation_check.log"
```

---

**Última atualização**: Dezembro 2024  
**Versão**: 1.0  
**Compatibilidade**: Django 4.0+
