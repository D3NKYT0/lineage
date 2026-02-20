# Configuração do AWS S3 no Django

Este guia explica como configurar e usar o Amazon S3 para armazenamento de arquivos estáticos e de mídia no Django.

## Pré-requisitos

1. Conta na AWS
2. Bucket S3 criado
3. Usuário IAM com permissões para S3
4. Python e Django instalados

## 1. Instalação das Dependências

As dependências já estão incluídas no `requirements.txt`:

```bash
pip install django-storages boto3
```

## 2. Configuração do Bucket S3

### 2.1 Criar um Bucket S3

1. Acesse o console da AWS
2. Vá para o serviço S3
3. Clique em "Create bucket"
4. Configure:
   - **Bucket name**: nome único global (ex: `meu-projeto-django`)
   - **Region**: escolha a região mais próxima
   - **Block Public Access**: desmarque se quiser arquivos públicos
   - **Bucket Versioning**: opcional
   - **Tags**: opcional

### 2.2 Configurar Permissões do Bucket

Crie uma política de bucket para permitir acesso público aos arquivos:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::seu-bucket-name/*"
        }
    ]
}
```

### 2.3 Configurar CORS (se necessário)

Se você precisar fazer uploads diretos do frontend:

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

## 3. Configuração do IAM

### 3.1 Criar Usuário IAM

1. Vá para IAM no console da AWS
2. Crie um novo usuário
3. Anexe a política `AmazonS3FullAccess` ou crie uma política personalizada:

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

### 3.2 Gerar Access Keys

1. No usuário IAM criado, vá para "Security credentials"
2. Clique em "Create access key"
3. Salve o Access Key ID e Secret Access Key

## 4. Configuração do Django

### 4.1 Variáveis de Ambiente

Adicione as seguintes variáveis ao seu arquivo `.env`:

```env
# AWS S3 Configuration
USE_S3=True
AWS_ACCESS_KEY_ID=sua_access_key_id
AWS_SECRET_ACCESS_KEY=sua_secret_access_key
AWS_STORAGE_BUCKET_NAME=seu-bucket-name
AWS_S3_REGION_NAME=us-east-1
AWS_S3_CUSTOM_DOMAIN=seu-bucket-name.s3.amazonaws.com
```

### 4.2 Configurações no settings.py

As configurações já estão incluídas no `core/settings.py`. O sistema automaticamente usa S3 quando `USE_S3=True`.

## 5. Uso no Django

### 5.1 Upload de Arquivos

```python
from django.db import models

class MinhaImagem(models.Model):
    titulo = models.CharField(max_length=100)
    imagem = models.ImageField(upload_to='imagens/')
    arquivo = models.FileField(upload_to='documentos/')
    
    def __str__(self):
        return self.titulo
```

### 5.2 Em Views

```python
from django.shortcuts import render
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

def upload_arquivo(request):
    if request.method == 'POST' and request.FILES['arquivo']:
        arquivo = request.FILES['arquivo']
        # Salva no S3 automaticamente
        path = default_storage.save(f'uploads/{arquivo.name}', ContentFile(arquivo.read()))
        return JsonResponse({'path': path})
    return render(request, 'upload.html')
```

### 5.3 Em Templates

```html
<!-- Exibir imagem -->
<img src="{{ objeto.imagem.url }}" alt="{{ objeto.titulo }}">

<!-- Link para download -->
<a href="{{ objeto.arquivo.url }}" download>Download</a>
```

## 6. Comandos Úteis

### 6.1 Coletar Arquivos Estáticos

```bash
python manage.py collectstatic
```

### 6.2 Verificar Configuração

```python
# No shell do Django
python manage.py shell

>>> from django.conf import settings
>>> print(settings.USE_S3)
>>> print(settings.AWS_STORAGE_BUCKET_NAME)
```

## 7. Configurações Avançadas

### 7.1 Storage Personalizado

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

### 7.2 Configuração no settings.py

```python
if USE_S3:
    DEFAULT_FILE_STORAGE = 'path.to.MediaStorage'
    STATICFILES_STORAGE = 'path.to.StaticStorage'
```

### 7.3 Configurações de Cache

```python
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
    'Expires': 'Thu, 31 Dec 2099 20:00:00 GMT',
}
```

## 8. Troubleshooting

### 8.1 Erro de Permissão

```
botocore.exceptions.ClientError: An error occurred (AccessDenied)
```

**Solução**: Verifique as permissões do usuário IAM e do bucket.

### 8.2 Erro de Região

```
botocore.exceptions.NoSuchBucket
```

**Solução**: Verifique se o nome do bucket e a região estão corretos.

### 8.3 Arquivos não aparecem

**Solução**: 
1. Verifique se o bucket tem permissões públicas
2. Verifique se os arquivos foram enviados corretamente
3. Verifique a URL do arquivo no console S3

## 9. Boas Práticas

1. **Segurança**: Use políticas IAM restritivas
2. **Performance**: Configure CDN (CloudFront) para melhor performance
3. **Custos**: Monitore o uso do S3 para controlar custos
4. **Backup**: Configure versionamento do bucket
5. **Organização**: Use prefixos para organizar arquivos

## 10. Monitoramento

### 10.1 CloudWatch

Configure alertas no CloudWatch para:
- Uso de armazenamento
- Número de requisições
- Erros de acesso

### 10.2 Logs

Ative logs de acesso do bucket para monitorar uso.

## 11. Exemplo Completo

### 11.1 Modelo

```python
# models.py
from django.db import models

class Documento(models.Model):
    titulo = models.CharField(max_length=200)
    arquivo = models.FileField(upload_to='documentos/%Y/%m/%d/')
    data_upload = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-data_upload']
    
    def __str__(self):
        return self.titulo
    
    def get_filename(self):
        return self.arquivo.name.split('/')[-1]
```

### 11.2 View

```python
# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Documento
from .forms import DocumentoForm

def upload_documento(request):
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Documento enviado com sucesso!')
            return redirect('lista_documentos')
    else:
        form = DocumentoForm()
    
    return render(request, 'upload_documento.html', {'form': form})
```

### 11.3 Template

```html
<!-- upload_documento.html -->
<form method="post" enctype="multipart/form-data">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Enviar</button>
</form>

<!-- lista_documentos.html -->
{% for documento in documentos %}
    <div>
        <h3>{{ documento.titulo }}</h3>
        <p>Arquivo: <a href="{{ documento.arquivo.url }}" target="_blank">{{ documento.get_filename }}</a></p>
        <p>Data: {{ documento.data_upload }}</p>
    </div>
{% endfor %}
```

## 12. Recursos Adicionais

- [Documentação oficial do django-storages](https://django-storages.readthedocs.io/)
- [Documentação do boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [Guia AWS S3](https://docs.aws.amazon.com/s3/)
- [Melhores práticas S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/best-practices.html) 
