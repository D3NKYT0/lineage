# Configuração do AWS S3 no Django

> **Última atualização:** 21/02/2026

Este projeto está configurado para usar o Amazon S3 para armazenamento de arquivos estáticos e de mídia.

## 🚀 Configuração Rápida

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

Adicione ao seu arquivo `.env`:

```env
# AWS S3 Configuration
USE_S3=True
AWS_ACCESS_KEY_ID=sua_access_key_id
AWS_SECRET_ACCESS_KEY=sua_secret_access_key
AWS_STORAGE_BUCKET_NAME=seu-bucket-name
AWS_S3_REGION_NAME=us-east-1
AWS_S3_CUSTOM_DOMAIN=seu-bucket-name.s3.amazonaws.com
```

### 3. Criar Bucket S3

1. Acesse o [Console AWS S3](https://console.aws.amazon.com/s3/)
2. Crie um novo bucket
3. Configure as permissões para acesso público (se necessário)
4. Configure CORS se precisar de uploads diretos

### 4. Configurar IAM

1. Crie um usuário IAM
2. Anexe a política `AmazonS3FullAccess` ou crie uma política personalizada
3. Gere Access Keys

### 5. Testar Configuração

```bash
python manage.py shell
```

```python
>>> from django.conf import settings
>>> print(settings.USE_S3)
>>> print(settings.AWS_STORAGE_BUCKET_NAME)
```

## 📁 Estrutura de Arquivos

O projeto está configurado para usar S3 para:

- **Arquivos Estáticos**: CSS, JS, imagens estáticas
- **Arquivos de Mídia**: Uploads de usuários, imagens de produtos, etc.

### Modelos que usam S3:

- `IndexConfig.imagem_banner` - Banner do servidor
- `Apoiador.imagem` - Imagens dos apoiadores
- `Prize.image` - Imagens dos prêmios
- `Item.image` - Imagens dos itens
- `SiteLogo.image` - Logos do site
- `Conquista.icone` - Ícones das conquistas
- `CustomItem.imagem` - Imagens de itens customizados
- `BackgroundSetting.image` - Imagens de fundo
- `Roadmap.image` - Imagens dos roadmaps
- `News.image` - Imagens das notícias
- `SolicitationHistory.image` - Imagens do histórico

## 🔄 Migração de Arquivos

### Migrar arquivos existentes para S3:

```bash
# Modo de teste (não faz alterações)
python manage.py migrate_to_s3 --dry-run

# Migrar todos os arquivos
python manage.py migrate_to_s3

# Migrar apenas um modelo específico
python manage.py migrate_to_s3 --model apps.lineage.server.models.IndexConfig

# Migrar apenas um campo específico
python manage.py migrate_to_s3 --field imagem_banner
```

### Script de exemplo:

```bash
python utils/s3_migration_example.py
```

## 💻 Uso no Código

### Upload de Arquivo

```python
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

# Upload direto
arquivo = request.FILES['arquivo']
caminho = default_storage.save(f'uploads/{arquivo.name}', ContentFile(arquivo.read()))

# URL do arquivo
url = default_storage.url(caminho)
```

### Em Modelos

```python
from django.db import models

class MinhaImagem(models.Model):
    titulo = models.CharField(max_length=100)
    imagem = models.ImageField(upload_to='imagens/')
    
    def __str__(self):
        return self.titulo
```

### Em Templates

```html
<!-- Exibir imagem -->
<img src="{{ objeto.imagem.url }}" alt="{{ objeto.titulo }}">

<!-- Link para download -->
<a href="{{ objeto.arquivo.url }}" download>Download</a>
```

## ⚙️ Configurações Avançadas

### Storage Personalizado

Crie um arquivo `storages.py`:

```python
from storages.backends.s3boto3 import S3Boto3Storage

class MediaStorage(S3Boto3Storage):
    location = 'media'
    file_overwrite = False

class StaticStorage(S3Boto3Storage):
    location = 'static'
    file_overwrite = True
```

### Configurações de Cache

```python
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
    'Expires': 'Thu, 31 Dec 2099 20:00:00 GMT',
}
```

## 🔧 Comandos Úteis

### Coletar Arquivos Estáticos

```bash
python manage.py collectstatic
```

### Verificar Configuração

```bash
python manage.py shell
```

```python
>>> from django.conf import settings
>>> print(settings.USE_S3)
>>> print(settings.AWS_STORAGE_BUCKET_NAME)
>>> print(settings.AWS_S3_CUSTOM_DOMAIN)
```

## 🚨 Troubleshooting

### Erro de Permissão

```
botocore.exceptions.ClientError: An error occurred (AccessDenied)
```

**Solução**: Verifique as permissões do usuário IAM e do bucket.

### Erro de Região

```
botocore.exceptions.NoSuchBucket
```

**Solução**: Verifique se o nome do bucket e a região estão corretos.

### Arquivos não aparecem

**Solução**: 
1. Verifique se o bucket tem permissões públicas
2. Verifique se os arquivos foram enviados corretamente
3. Verifique a URL do arquivo no console S3

## 📊 Monitoramento

### CloudWatch

Configure alertas para:
- Uso de armazenamento
- Número de requisições
- Erros de acesso

### Logs

Ative logs de acesso do bucket para monitorar uso.

## 🔒 Segurança

### Política IAM Restritiva

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::seu-bucket-name",
                "arn:aws:s3:::seu-bucket-name/*"
            ]
        }
    ]
}
```

### Configurações de CORS

```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "POST", "PUT", "DELETE"],
        "AllowedOrigins": ["*"],
        "ExposeHeaders": ["ETag"]
    }
]
```

## 📈 Performance

### CDN (CloudFront)

Para melhor performance, configure o CloudFront:

1. Crie uma distribuição CloudFront
2. Configure o S3 como origem
3. Atualize `AWS_S3_CUSTOM_DOMAIN` com o domínio do CloudFront

### Cache

```python
# Cache de URLs
from django.core.cache import cache

def get_cached_url(arquivo_path, timeout=3600):
    cache_key = f"s3_url_{arquivo_path}"
    url = cache.get(cache_key)
    
    if not url:
        url = default_storage.url(arquivo_path)
        cache.set(cache_key, url, timeout)
    
    return url
```

## 📚 Documentação Completa

Para mais detalhes, consulte:
- [docs/AWS_S3_SETUP.md](docs/AWS_S3_SETUP.md) - Guia completo de configuração
- [Documentação django-storages](https://django-storages.readthedocs.io/)
- [Documentação boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

## 🤝 Contribuição

Para contribuir com melhorias no sistema S3:

1. Teste suas mudanças em ambiente de desenvolvimento
2. Verifique se os arquivos estão sendo servidos corretamente
3. Execute os testes de migração
4. Documente as mudanças

## 📞 Suporte

Se encontrar problemas:

1. Verifique as configurações no `settings.py`
2. Teste a conectividade com o S3
3. Verifique os logs do Django
4. Consulte a documentação da AWS 

---

[ Voltar ao Índice](../INDEX.md)

