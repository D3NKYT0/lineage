"""
Exemplos de views para demonstrar o uso do S3 no Django
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.conf import settings
import json
import os
from PIL import Image
import io


@login_required
def upload_arquivo_view(request):
    """
    View para upload de arquivo simples
    """
    if request.method == 'POST':
        if 'arquivo' in request.FILES:
            arquivo = request.FILES['arquivo']
            
            # Validação básica
            if arquivo.size > 10 * 1024 * 1024:  # 10MB
                messages.error(request, 'Arquivo muito grande. Máximo 10MB.')
                return redirect('upload_arquivo')
            
            # Salva no S3
            try:
                caminho = default_storage.save(f'uploads/{arquivo.name}', ContentFile(arquivo.read()))
                url = default_storage.url(caminho)
                
                messages.success(request, f'Arquivo enviado com sucesso! URL: {url}')
                return redirect('upload_arquivo')
                
            except Exception as e:
                messages.error(request, f'Erro ao enviar arquivo: {str(e)}')
                return redirect('upload_arquivo')
    
    return render(request, 'upload_arquivo.html')


@csrf_exempt
@require_http_methods(["POST"])
def upload_ajax_view(request):
    """
    View para upload via AJAX
    """
    try:
        if 'arquivo' in request.FILES:
            arquivo = request.FILES['arquivo']
            
            # Validação
            if arquivo.size > 5 * 1024 * 1024:  # 5MB
                return JsonResponse({
                    'success': False,
                    'error': 'Arquivo muito grande. Máximo 5MB.'
                })
            
            # Salva no S3
            caminho = default_storage.save(f'uploads/{arquivo.name}', ContentFile(arquivo.read()))
            url = default_storage.url(caminho)
            
            return JsonResponse({
                'success': True,
                'url': url,
                'caminho': caminho,
                'nome': arquivo.name
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Nenhum arquivo enviado'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def lista_arquivos_view(request):
    """
    View para listar arquivos no S3
    """
    try:
        # Lista arquivos no diretório uploads/
        diretorios, arquivos = default_storage.listdir('uploads/')
        
        arquivos_info = []
        for arquivo in arquivos:
            caminho_completo = f'uploads/{arquivo}'
            url = default_storage.url(caminho_completo)
            tamanho = default_storage.size(caminho_completo)
            
            arquivos_info.append({
                'nome': arquivo,
                'url': url,
                'tamanho': tamanho,
                'tamanho_mb': round(tamanho / (1024 * 1024), 2)
            })
        
        return render(request, 'lista_arquivos.html', {
            'arquivos': arquivos_info
        })
        
    except Exception as e:
        messages.error(request, f'Erro ao listar arquivos: {str(e)}')
        return redirect('home')


@login_required
def deletar_arquivo_view(request, nome_arquivo):
    """
    View para deletar arquivo do S3
    """
    try:
        caminho = f'uploads/{nome_arquivo}'
        
        if default_storage.exists(caminho):
            default_storage.delete(caminho)
            messages.success(request, f'Arquivo {nome_arquivo} deletado com sucesso!')
        else:
            messages.error(request, f'Arquivo {nome_arquivo} não encontrado.')
            
    except Exception as e:
        messages.error(request, f'Erro ao deletar arquivo: {str(e)}')
    
    return redirect('lista_arquivos')


@login_required
def upload_imagem_otimizada_view(request):
    """
    View para upload de imagem com otimização
    """
    if request.method == 'POST':
        if 'imagem' in request.FILES:
            imagem = request.FILES['imagem']
            
            try:
                # Abre a imagem com Pillow
                img = Image.open(imagem)
                
                # Redimensiona se muito grande
                max_size = (800, 600)
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Converte para RGB se necessário
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Salva a imagem otimizada
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85, optimize=True)
                buffer.seek(0)
                
                # Salva no S3
                nome_arquivo = f"imagens_otimizadas/{imagem.name}"
                caminho = default_storage.save(nome_arquivo, ContentFile(buffer.getvalue()))
                url = default_storage.url(caminho)
                
                messages.success(request, f'Imagem otimizada e enviada com sucesso!')
                return redirect('upload_imagem_otimizada')
                
            except Exception as e:
                messages.error(request, f'Erro ao processar imagem: {str(e)}')
                return redirect('upload_imagem_otimizada')
    
    return render(request, 'upload_imagem_otimizada.html')


@login_required
def upload_multiplos_arquivos_view(request):
    """
    View para upload de múltiplos arquivos
    """
    if request.method == 'POST':
        arquivos = request.FILES.getlist('arquivos')
        
        if not arquivos:
            messages.error(request, 'Nenhum arquivo selecionado.')
            return redirect('upload_multiplos')
        
        resultados = []
        for arquivo in arquivos:
            try:
                # Validação
                if arquivo.size > 5 * 1024 * 1024:  # 5MB
                    resultados.append({
                        'nome': arquivo.name,
                        'sucesso': False,
                        'erro': 'Arquivo muito grande'
                    })
                    continue
                
                # Salva no S3
                caminho = default_storage.save(f'uploads/multiplos/{arquivo.name}', ContentFile(arquivo.read()))
                url = default_storage.url(caminho)
                
                resultados.append({
                    'nome': arquivo.name,
                    'sucesso': True,
                    'url': url,
                    'caminho': caminho
                })
                
            except Exception as e:
                resultados.append({
                    'nome': arquivo.name,
                    'sucesso': False,
                    'erro': str(e)
                })
        
        sucessos = sum(1 for r in resultados if r['sucesso'])
        erros = len(resultados) - sucessos
        
        messages.success(request, f'{sucessos} arquivos enviados com sucesso.')
        if erros > 0:
            messages.warning(request, f'{erros} arquivos com erro.')
        
        return render(request, 'upload_multiplos.html', {
            'resultados': resultados
        })
    
    return render(request, 'upload_multiplos.html')


def verificar_s3_view(request):
    """
    View para verificar status do S3
    """
    status = {
        's3_habilitado': getattr(settings, 'USE_S3', False),
        'bucket_name': getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'Não configurado'),
        'region': getattr(settings, 'AWS_S3_REGION_NAME', 'Não configurado'),
        'custom_domain': getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', 'Não configurado'),
    }
    
    # Testa conectividade
    try:
        # Tenta listar arquivos
        default_storage.listdir('')
        status['conectividade'] = 'OK'
    except Exception as e:
        status['conectividade'] = f'Erro: {str(e)}'
    
    return JsonResponse(status)


@login_required
def gerenciar_arquivos_view(request):
    """
    View para gerenciar arquivos (listar, deletar, download)
    """
    try:
        # Lista arquivos
        diretorios, arquivos = default_storage.listdir('uploads/')
        
        arquivos_info = []
        total_size = 0
        
        for arquivo in arquivos:
            caminho = f'uploads/{arquivo}'
            url = default_storage.url(caminho)
            tamanho = default_storage.size(caminho)
            total_size += tamanho
            
            # Determina tipo de arquivo
            extensao = os.path.splitext(arquivo)[1].lower()
            if extensao in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                tipo = 'imagem'
            elif extensao in ['.pdf']:
                tipo = 'pdf'
            elif extensao in ['.doc', '.docx']:
                tipo = 'documento'
            else:
                tipo = 'outro'
            
            arquivos_info.append({
                'nome': arquivo,
                'url': url,
                'tamanho': tamanho,
                'tamanho_mb': round(tamanho / (1024 * 1024), 2),
                'tipo': tipo,
                'caminho': caminho
            })
        
        # Ordena por tamanho (maior primeiro)
        arquivos_info.sort(key=lambda x: x['tamanho'], reverse=True)
        
        return render(request, 'gerenciar_arquivos.html', {
            'arquivos': arquivos_info,
            'total_arquivos': len(arquivos_info),
            'total_size_mb': round(total_size / (1024 * 1024), 2)
        })
        
    except Exception as e:
        messages.error(request, f'Erro ao gerenciar arquivos: {str(e)}')
        return redirect('home')


# Exemplo de template para upload
UPLOAD_TEMPLATE = """
{% extends 'base.html' %}

{% block content %}
<div class="container">
    <h2>Upload de Arquivo</h2>
    
    <form method="post" enctype="multipart/form-data">
        {% csrf_token %}
        <div class="form-group">
            <label for="arquivo">Selecione um arquivo:</label>
            <input type="file" class="form-control-file" id="arquivo" name="arquivo" required>
        </div>
        <button type="submit" class="btn btn-primary">Enviar</button>
    </form>
    
    {% if messages %}
    <div class="mt-3">
        {% for message in messages %}
        <div class="alert alert-{{ message.tags }}">
            {{ message }}
        </div>
        {% endfor %}
    </div>
    {% endif %}
</div>
{% endblock %}
"""

# Exemplo de template para lista de arquivos
LISTA_TEMPLATE = """
{% extends 'base.html' %}

{% block content %}
<div class="container">
    <h2>Arquivos no S3</h2>
    
    <div class="row">
        {% for arquivo in arquivos %}
        <div class="col-md-4 mb-3">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">{{ arquivo.nome }}</h5>
                    <p class="card-text">
                        <strong>Tamanho:</strong> {{ arquivo.tamanho_mb }} MB<br>
                        <strong>URL:</strong> <a href="{{ arquivo.url }}" target="_blank">{{ arquivo.url }}</a>
                    </p>
                    <a href="{{ arquivo.url }}" class="btn btn-primary btn-sm" target="_blank">Ver</a>
                    <a href="{% url 'deletar_arquivo' arquivo.nome %}" class="btn btn-danger btn-sm" 
                       onclick="return confirm('Tem certeza?')">Deletar</a>
                </div>
            </div>
        </div>
        {% empty %}
        <div class="col-12">
            <p>Nenhum arquivo encontrado.</p>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
"""

# Exemplo de JavaScript para upload AJAX
AJAX_UPLOAD_JS = """
function uploadArquivo() {
    const input = document.getElementById('arquivo');
    const file = input.files[0];
    
    if (!file) {
        alert('Selecione um arquivo');
        return;
    }
    
    const formData = new FormData();
    formData.append('arquivo', file);
    
    fetch('/upload-ajax/', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Arquivo enviado com sucesso!');
            document.getElementById('resultado').innerHTML = 
                `<p>URL: <a href="${data.url}" target="_blank">${data.url}</a></p>`;
        } else {
            alert('Erro: ' + data.error);
        }
    })
    .catch(error => {
        alert('Erro na requisição: ' + error);
    });
}
""" 
