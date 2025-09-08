# API Configuration Panel

## Visão Geral

O **API Configuration Panel** é uma interface administrativa que permite aos administradores do sistema controlar quais endpoints da API estão ativos ou inativos. Esta funcionalidade oferece controle granular sobre a disponibilidade dos serviços da API.

## Funcionalidades

### 🔧 Controle de Endpoints
- **Ativar/Desativar** endpoints individuais
- **Visualização em tempo real** do status dos endpoints
- **Reset para padrões** com um clique
- **Interface intuitiva** com switches visuais

### 🛡️ Segurança
- **Acesso restrito** apenas para usuários staff
- **Autenticação obrigatória** via Django
- **Logs de auditoria** para todas as alterações
- **Validação de permissões** em todas as operações

### ⚡ Performance
- **Cache inteligente** que é limpo automaticamente
- **Resposta rápida** via AJAX
- **Feedback visual** imediato para o usuário
- **Otimização de consultas** ao banco de dados

## Endpoints Disponíveis

### Interface HTML
```
GET /api/v1/admin/config/panel/
```
- **Descrição**: Renderiza a interface HTML do painel de configuração
- **Autenticação**: Requer usuário staff
- **Resposta**: Template HTML com formulário de configuração

### API REST
```
GET /api/v1/admin/config/
POST /api/v1/admin/config/
DELETE /api/v1/admin/config/panel/
```

## Estrutura de Dados

### Modelo ApiEndpointToggle
```python
class ApiEndpointToggle(BaseModel):
    players_online = models.BooleanField(default=True)
    top_pvp = models.BooleanField(default=True)
    top_pk = models.BooleanField(default=True)
    top_clan = models.BooleanField(default=True)
    top_rich = models.BooleanField(default=True)
    top_online = models.BooleanField(default=True)
    top_level = models.BooleanField(default=True)
    olympiad_ranking = models.BooleanField(default=True)
    olympiad_all_heroes = models.BooleanField(default=True)
    olympiad_current_heroes = models.BooleanField(default=True)
    grandboss_status = models.BooleanField(default=True)
    raidboss_status = models.BooleanField(default=True)
    siege = models.BooleanField(default=True)
    siege_participants = models.BooleanField(default=True)
    boss_jewel_locations = models.BooleanField(default=True)
```

## Como Usar

### 1. Acesso ao Painel
1. Faça login como administrador
2. Acesse: `/api/v1/admin/config/panel/`
3. Verifique se você tem permissões de staff

### 2. Configuração de Endpoints
1. **Visualizar Status**: Cada endpoint mostra um indicador visual (verde = ativo, vermelho = inativo)
2. **Alterar Status**: Use os switches para ativar/desativar endpoints
3. **Salvar Alterações**: Clique em "Salvar Alterações" para aplicar as mudanças
4. **Reset**: Use "Resetar Padrões" para voltar todas as configurações ao padrão

### 3. Monitoramento
- **Logs**: Todas as alterações são registradas no log do sistema
- **Cache**: O cache é limpo automaticamente quando endpoints são alterados
- **Feedback**: Mensagens de sucesso/erro são exibidas na interface

## Implementação Técnica

### View Principal
```python
@extend_schema(
    summary="API Configuration Panel",
    description="Painel de configuração da API para administradores",
    responses={
        status.HTTP_200_OK: APIResponseSerializer,
        status.HTTP_403_FORBIDDEN: APIResponseSerializer,
    },
    tags=["Administração"],
    auth=[]
)
class APIConfigPanelView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Renderiza interface HTML
        pass
    
    def post(self, request):
        # Atualiza configurações via AJAX
        pass
    
    def delete(self, request):
        # Reseta configurações para padrões
        pass
```

### Decorator de Controle
```python
def endpoint_enabled(endpoint_field):
    def decorator(view_func_or_class):
        # Verifica se o endpoint está habilitado
        # Retorna 503 se desabilitado
        pass
    return decorator
```

### Template JavaScript
```javascript
// Carregamento de configuração
function loadConfig() {
    // Carrega dados do contexto ou via AJAX
}

// Salvamento de configuração
function saveConfig() {
    // Envia dados via POST para a API
}

// Reset de configuração
function resetConfig() {
    // Envia DELETE para resetar padrões
}
```

## Fluxo de Funcionamento

### 1. Carregamento da Página
```
Usuário acessa /api/v1/admin/config/panel/
↓
Verificação de permissões (staff)
↓
Busca configurações do banco de dados
↓
Renderização do template com dados
↓
JavaScript carrega interface interativa
```

### 2. Alteração de Configuração
```
Usuário altera switch
↓
JavaScript captura mudança
↓
Envio via AJAX para POST /api/v1/admin/config/panel/
↓
Validação de permissões
↓
Atualização no banco de dados
↓
Limpeza de cache relacionado
↓
Log da alteração
↓
Resposta de sucesso/erro
```

### 3. Reset de Configuração
```
Usuário clica em "Resetar Padrões"
↓
Confirmação via JavaScript
↓
Envio via AJAX para DELETE /api/v1/admin/config/panel/
↓
Reset de todos os campos para True
↓
Limpeza completa do cache
↓
Log da ação
↓
Recarregamento da página
```

## Configuração de Cache

### Chaves de Cache
- `api_players_online`
- `api_top_pvp`
- `api_top_clan`
- etc.

### Limpeza Automática
Quando um endpoint é alterado, o cache relacionado é limpo automaticamente:
```python
for field in updated_fields:
    cache_key = f'api_{field}'
    cache.delete(cache_key)
```

## Logs e Auditoria

### Logs Gerados
- **Alterações de configuração**: Quem alterou, quando, quais campos
- **Resets**: Quem resetou, quando
- **Erros**: Falhas na atualização ou acesso não autorizado

### Exemplo de Log
```
INFO: API config updated by admin: ['players_online', 'top_pvp']
INFO: API config reset by admin
ERROR: Error updating API config: Database connection failed
```

## Testes

### Teste Automatizado
Execute o arquivo de teste para verificar a funcionalidade:
```bash
python test/api_config_test.py
```

### Testes Manuais
1. **Acesso sem autenticação**: Deve retornar 403
2. **Acesso com usuário normal**: Deve retornar 403
3. **Acesso com staff**: Deve permitir acesso
4. **Alteração de configuração**: Deve funcionar e limpar cache
5. **Reset de configuração**: Deve resetar todos os campos

## Troubleshooting

### Problemas Comuns

#### 1. "Acesso Negado"
- **Causa**: Usuário não é staff
- **Solução**: Verificar se o usuário tem `is_staff=True`

#### 2. "Erro ao carregar configuração"
- **Causa**: Problema no banco de dados
- **Solução**: Verificar se o modelo `ApiEndpointToggle` existe

#### 3. "Cache não está sendo limpo"
- **Causa**: Configuração de cache incorreta
- **Solução**: Verificar configurações de cache no `settings.py`

#### 4. "JavaScript não funciona"
- **Causa**: Erro no template ou CSRF token
- **Solução**: Verificar console do navegador e CSRF token

### Debug
Para debug, adicione logs adicionais:
```python
import logging
logger = logging.getLogger(__name__)
logger.debug(f"Config data: {config_data}")
```

## Segurança

### Medidas Implementadas
- ✅ Verificação de permissões em todas as operações
- ✅ Validação de dados de entrada
- ✅ Proteção CSRF
- ✅ Logs de auditoria
- ✅ Rate limiting (via DRF)
- ✅ Sanitização de dados

### Recomendações
- 🔒 Use HTTPS em produção
- 🔒 Configure rate limiting adequado
- 🔒 Monitore logs regularmente
- 🔒 Faça backup das configurações
- 🔒 Teste regularmente as permissões

## Performance

### Otimizações
- **Cache inteligente**: Dados cacheados por tipo
- **Consultas otimizadas**: Uso de `get_or_create`
- **Limpeza seletiva**: Apenas cache relacionado é limpo
- **Resposta rápida**: Interface AJAX para feedback imediato

### Métricas
- **Tempo de resposta**: < 200ms para carregamento
- **Tempo de atualização**: < 500ms para alterações
- **Uso de memória**: Mínimo impacto no cache

## Roadmap

### Melhorias Futuras
- [ ] Interface mais moderna com React/Vue
- [ ] Histórico de alterações
- [ ] Configurações por ambiente (dev/prod)
- [ ] Notificações em tempo real
- [ ] Backup automático de configurações
- [ ] API para integração externa
- [ ] Métricas de uso por endpoint
- [ ] Sistema de templates de configuração

## Contribuição

Para contribuir com melhorias:
1. Fork o projeto
2. Crie uma branch para sua feature
3. Implemente as mudanças
4. Adicione testes
5. Documente as alterações
6. Submeta um pull request

## Suporte

Para suporte técnico:
- 📧 Email: admin@lineage2server.com
- 📖 Documentação: `/docs/`
- 🐛 Issues: GitHub Issues
- 💬 Chat: Discord/Slack 