# Configuração do Banner Editável

## Visão Geral

O sistema agora permite que o banner do dashboard de contas L2 seja editável através do painel administrativo do Django.

## Como Configurar

### 1. Acesse o Admin

1. Faça login no painel administrativo do Django
2. Navegue até **Lineage > Server > Index Configurations**

### 2. Configure o Banner

1. Se não existir uma configuração, clique em **Add Index Configuration**
2. Se já existir, clique na configuração existente para editá-la
3. No campo **Banner Image**, faça upload da nova imagem
4. Clique em **Save**

### 3. Formatos Suportados

- **Formatos**: JPG, PNG, GIF, WebP
- **Tamanho recomendado**: 800x400 pixels ou proporção similar
- **Tamanho máximo**: 5MB

## Como Funciona

### Template Tag

O sistema usa um template tag personalizado para carregar a imagem do banner:

```django
{% load banner_extras %}

{% get_banner_url as banner_url %}
{% if banner_url %}
  <img src="{{ banner_url }}" alt="Logo Lineage 2" class="img-fluid mb-4">
{% else %}
<<<<<<< HEAD
  <img src="{% static 'assets/img/banner-l2jpremium.png' %}" alt="Logo Lineage 2" class="img-fluid mb-4">
=======
  <img src="{% static 'assets/img/banner-pdl.jpeg' %}" alt="Logo Lineage 2" class="img-fluid mb-4">
>>>>>>> upstream/main
{% endif %}
```

### Fallback

<<<<<<< HEAD
Se nenhuma imagem estiver configurada no admin, o sistema usa a imagem estática padrão (`banner-l2jpremium.png`).
=======
Se nenhuma imagem estiver configurada no admin, o sistema usa a imagem estática padrão (`banner-pdl.jpeg`).
>>>>>>> upstream/main

## Comandos Úteis

### Criar Configuração Inicial

Se você precisar criar a configuração inicial:

```bash
python manage.py create_index_config
```

## Estrutura Técnica

### Modelo

O banner é gerenciado pelo modelo `IndexConfig` no app `apps.lineage.server.models`:

```python
class IndexConfig(BaseModel):
    # ... outros campos ...
    imagem_banner = models.ImageField(upload_to='banners/', blank=True, null=True, verbose_name=_("Banner Image"))
```

### Template Tags

Os template tags estão em `apps.lineage.server.templatetags.banner_extras.py`:

- `get_banner_image()`: Retorna o objeto da imagem
- `get_banner_url()`: Retorna a URL da imagem

### Admin

A configuração está disponível no admin em:
- **List Display**: Mostra o nome do servidor e se há imagem do banner
- **Fieldsets**: Campo organizado em "Configurações de Exibição"

## Uso em Outros Templates

Para usar o banner editável em outros templates:

```django
{% load banner_extras %}

{% get_banner_url as banner_url %}
{% if banner_url %}
  <img src="{{ banner_url }}" alt="Banner">
{% endif %}
```

## Considerações

- Apenas uma configuração pode existir por vez
- As imagens são salvas na pasta `media/banners/`
- O sistema mantém compatibilidade com a imagem estática original 