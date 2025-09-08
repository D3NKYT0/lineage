"""
Script de exemplo para migração de arquivos para S3
Este script demonstra como migrar arquivos existentes do sistema de arquivos local para o S3
"""

import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from apps.lineage.server.models import IndexConfig, Apoiador
from apps.lineage.games.models import Prize, Item
from apps.main.home.models import SiteLogo, Conquista
from apps.lineage.inventory.models import CustomItem
from apps.main.administrator.models import BackgroundSetting
from apps.lineage.roadmap.models import Roadmap
from apps.main.news.models import News
from apps.main.solicitation.models import SolicitationHistory


def migrar_arquivos_para_s3():
    """
    Função para migrar todos os arquivos existentes para o S3
    """
    print("Iniciando migração de arquivos para S3...")
    
    # Lista de modelos que contêm arquivos
    modelos_com_arquivos = [
        (IndexConfig, 'imagem_banner'),
        (Apoiador, 'imagem'),
        (Prize, 'image'),
        (Item, 'image'),
        (SiteLogo, 'image'),
        (Conquista, 'icone'),
        (CustomItem, 'imagem'),
        (BackgroundSetting, 'image'),
        (Roadmap, 'image'),
        (News, 'image'),
        (SolicitationHistory, 'image'),
    ]
    
    total_migrados = 0
    total_erros = 0
    
    for modelo, campo_arquivo in modelos_com_arquivos:
        print(f"\nMigrando arquivos do modelo: {modelo.__name__}")
        
        # Busca todos os objetos que têm arquivos
        objetos = modelo.objects.exclude(**{f"{campo_arquivo}__isnull": True}).exclude(**{campo_arquivo: ""})
        
        for obj in objetos:
            try:
                arquivo_atual = getattr(obj, campo_arquivo)
                
                if arquivo_atual and arquivo_atual.name:
                    # Verifica se o arquivo já está no S3
                    if arquivo_atual.url.startswith('http'):
                        print(f"  ✓ {obj} - Arquivo já está no S3")
                        continue
                    
                    # Verifica se o arquivo existe localmente
                    if not os.path.exists(arquivo_atual.path):
                        print(f"  ⚠ {obj} - Arquivo local não encontrado: {arquivo_atual.path}")
                        continue
                    
                    # Lê o arquivo local
                    with open(arquivo_atual.path, 'rb') as f:
                        conteudo = f.read()
                    
                    # Salva no S3
                    novo_caminho = arquivo_atual.name
                    arquivo_s3 = default_storage.save(novo_caminho, ContentFile(conteudo))
                    
                    # Atualiza o objeto com o novo caminho
                    setattr(obj, campo_arquivo, arquivo_s3)
                    obj.save(update_fields=[campo_arquivo])
                    
                    print(f"  ✓ {obj} - Migrado com sucesso: {arquivo_s3}")
                    total_migrados += 1
                    
            except Exception as e:
                print(f"  ✗ {obj} - Erro na migração: {str(e)}")
                total_erros += 1
    
    print(f"\nMigração concluída!")
    print(f"Total de arquivos migrados: {total_migrados}")
    print(f"Total de erros: {total_erros}")


def verificar_arquivos_s3():
    """
    Função para verificar se os arquivos estão sendo servidos pelo S3
    """
    print("Verificando arquivos no S3...")
    
    # Lista de modelos que contêm arquivos
    modelos_com_arquivos = [
        (IndexConfig, 'imagem_banner'),
        (Apoiador, 'imagem'),
        (Prize, 'image'),
        (Item, 'image'),
        (SiteLogo, 'image'),
        (Conquista, 'icone'),
        (CustomItem, 'imagem'),
        (BackgroundSetting, 'image'),
        (Roadmap, 'image'),
        (News, 'image'),
        (SolicitationHistory, 'image'),
    ]
    
    for modelo, campo_arquivo in modelos_com_arquivos:
        print(f"\nVerificando {modelo.__name__}:")
        
        objetos = modelo.objects.exclude(**{f"{campo_arquivo}__isnull": True}).exclude(**{campo_arquivo: ""})
        
        for obj in objetos:
            arquivo = getattr(obj, campo_arquivo)
            if arquivo:
                url = arquivo.url
                print(f"  {obj}: {url}")
                
                # Verifica se a URL é do S3
                if 's3.amazonaws.com' in url or 'amazonaws.com' in url:
                    print(f"    ✓ Servido pelo S3")
                else:
                    print(f"    ⚠ Servido localmente")


def exemplo_upload_arquivo():
    """
    Exemplo de como fazer upload de um arquivo para o S3
    """
    print("Exemplo de upload de arquivo para S3...")
    
    # Exemplo 1: Upload direto usando default_storage
    from django.core.files.base import ContentFile
    
    # Simula um arquivo
    conteudo_arquivo = b"Conteudo do arquivo de exemplo"
    nome_arquivo = "exemplo.txt"
    
    # Salva no S3
    caminho_s3 = default_storage.save(f"uploads/{nome_arquivo}", ContentFile(conteudo_arquivo))
    print(f"Arquivo salvo em: {caminho_s3}")
    
    # Obtém a URL
    url_arquivo = default_storage.url(caminho_s3)
    print(f"URL do arquivo: {url_arquivo}")
    
    # Exemplo 2: Upload usando um modelo
    from apps.lineage.server.models import IndexConfig
    
    # Cria uma instância do modelo
    config = IndexConfig.objects.first()
    if config:
        # Simula um upload de arquivo
        arquivo_simulado = ContentFile(b"conteudo da imagem", name="banner.jpg")
        config.imagem_banner.save("banner.jpg", arquivo_simulado, save=True)
        print(f"Banner salvo: {config.imagem_banner.url}")


def exemplo_manipulacao_arquivos():
    """
    Exemplo de como manipular arquivos no S3
    """
    print("Exemplos de manipulação de arquivos no S3...")
    
    # Listar arquivos em um diretório
    diretorio = "uploads/"
    arquivos = default_storage.listdir(diretorio)
    print(f"Arquivos em {diretorio}: {arquivos}")
    
    # Verificar se um arquivo existe
    arquivo_teste = "uploads/exemplo.txt"
    existe = default_storage.exists(arquivo_teste)
    print(f"Arquivo {arquivo_teste} existe: {existe}")
    
    # Obter informações do arquivo
    if existe:
        tamanho = default_storage.size(arquivo_teste)
        url = default_storage.url(arquivo_teste)
        print(f"Tamanho: {tamanho} bytes")
        print(f"URL: {url}")
    
    # Deletar arquivo
    # default_storage.delete(arquivo_teste)
    # print(f"Arquivo {arquivo_teste} deletado")


def exemplo_otimizacao():
    """
    Exemplo de otimizações para uso do S3
    """
    print("Exemplos de otimização para S3...")
    
    # 1. Usar cache para URLs
    from django.core.cache import cache
    
    def get_cached_url(arquivo_path, timeout=3600):
        """Obtém a URL do arquivo com cache"""
        cache_key = f"s3_url_{arquivo_path}"
        url = cache.get(cache_key)
        
        if not url:
            url = default_storage.url(arquivo_path)
            cache.set(cache_key, url, timeout)
        
        return url
    
    # 2. Upload em lotes
    def upload_lote_arquivos(arquivos_info):
        """Upload de múltiplos arquivos"""
        resultados = []
        
        for nome, conteudo in arquivos_info:
            try:
                caminho = default_storage.save(f"uploads/{nome}", ContentFile(conteudo))
                resultados.append({"nome": nome, "caminho": caminho, "sucesso": True})
            except Exception as e:
                resultados.append({"nome": nome, "erro": str(e), "sucesso": False})
        
        return resultados
    
    # 3. Verificar espaço usado
    def calcular_espaco_usado():
        """Calcula o espaço usado no S3"""
        total_bytes = 0
        arquivos = default_storage.listdir("")[1]  # Lista todos os arquivos
        
        for arquivo in arquivos:
            total_bytes += default_storage.size(arquivo)
        
        return total_bytes
    
    print("Funções de otimização criadas!")


if __name__ == "__main__":
    # Descomente as funções que deseja executar
    
    # Migrar arquivos existentes para S3
    # migrar_arquivos_para_s3()
    
    # Verificar arquivos no S3
    # verificar_arquivos_s3()
    
    # Exemplo de upload
    # exemplo_upload_arquivo()
    
    # Exemplo de manipulação
    # exemplo_manipulacao_arquivos()
    
    # Exemplo de otimização
    # exemplo_otimizacao()
    
    print("Script de exemplo do S3 carregado!")
    print("Descomente as funções que deseja executar.") 
    