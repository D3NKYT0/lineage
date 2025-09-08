from django.db import models
from core.models import BaseModel
from apps.main.home.models import User
from django.core.exceptions import ValidationError
import zipfile, os, json, shutil, re
from django.conf import settings
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class ChatGroup(BaseModel):
    group_name = models.CharField(max_length=255, verbose_name=_("Nome do Grupo"))
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Remetente"))
    message = models.TextField(verbose_name=_("Mensagem"))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("Data de Envio"))

    def __str__(self):
        return f"{self.sender.username}: {self.message[:20]}"

    class Meta:
        verbose_name = _('Histórico de Atendimentos')
        verbose_name_plural = _('Históricos de Atendimentos')


class Theme(BaseModel):
    nome = models.CharField(max_length=100, unique=True, verbose_name=_("Nome"))
    slug = models.SlugField(unique=True, verbose_name=_("Slug"))
    descricao = models.TextField(blank=True, verbose_name=_("Descrição"))
    ativo = models.BooleanField(default=False, verbose_name=_("Ativo"))

    version = models.CharField(max_length=50, blank=True, verbose_name=_("Versão"))
    author = models.CharField(max_length=100, blank=True, verbose_name=_("Autor"))

    upload = models.FileField(upload_to='themes/', verbose_name=_("Upload de Arquivo"))

    criado_em = models.DateTimeField(auto_now_add=True, verbose_name=_("Criado em"))
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name=_("Atualizado em"))

    class Meta:
        verbose_name = _("Tema")
        verbose_name_plural = _("Temas")

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        # Se ativado, desativa os outros
        if self.ativo:
            Theme.objects.exclude(pk=self.pk).update(ativo=False)

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Remove o arquivo ZIP
        try:
            if self.upload and os.path.isfile(self.upload.path):
                os.remove(self.upload.path)
        except Exception as e:
            print(f"Erro ao remover o arquivo: {e}")

        # Remove a pasta extraída
        try:
            if self.slug:
                theme_folder_path = os.path.join(settings.BASE_DIR, 'themes/installed', self.slug)
                if os.path.isdir(theme_folder_path):
                    shutil.rmtree(theme_folder_path)
        except Exception as e:
            print(f"Erro ao remover a pasta: {e}")

        super().delete(*args, **kwargs)

    def clean_upload(self):
        file = self.upload
        if file:
            if file.size > 50 * 1024 * 1024:
                raise ValidationError(_("O arquivo é muito grande. Tente um arquivo menor que 50MB."))
            if not zipfile.is_zipfile(file):
                raise ValidationError(_("O arquivo não é um ZIP válido."))
        return file

    def processar_upload(self):
        if not self.upload:
            return

        upload_file = self.upload.file

        if not zipfile.is_zipfile(upload_file):
            raise ValidationError(_("O arquivo não é um ZIP válido."))

        with zipfile.ZipFile(upload_file, 'r') as zip_ref:
            file_names = zip_ref.namelist()

            extensoes_permitidas = [
                # Arquivos de marcação e dados
                '.html', '.htm', '.json',

                # Estilos
                '.css', '.scss', '.sass', '.less',

                # Scripts
                '.js', '.ts', '.map', '.mjs', '.cjs',

                # Imagens
                '.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico', '.bmp', '.tiff', '.gif',

                # Fontes
                '.woff', '.woff2', '.ttf', '.otf', '.eot',

                # Multimídia (menos comum em temas, mas possível)
                '.mp4', '.webm', '.mp3', '.ogg',

                # Outros arquivos úteis
                '.md', '.txt', '.pdf',
            ]

            for member in zip_ref.infolist():
                ext = os.path.splitext(member.filename)[1].lower()
                if ext and ext not in extensoes_permitidas:
                    raise ValidationError(_("Arquivo com extensão não permitida: %s") % ext)

                extracted_path = os.path.join(settings.BASE_DIR, 'themes/installed', self.slug, member.filename)
                if not os.path.realpath(extracted_path).startswith(
                    os.path.realpath(os.path.join(settings.BASE_DIR, 'themes/installed', self.slug))
                ):
                    raise ValidationError(_("O tema contém arquivos em caminhos não permitidos."))

            # Procurando theme.json
            theme_json_path = next((f for f in file_names if f.lower().endswith('theme.json')), None)
            if not theme_json_path:
                raise ValidationError(_("O arquivo 'theme.json' não foi encontrado."))

            try:
                with zip_ref.open(theme_json_path) as f:
                    meta = json.load(f)

                obrigatorios = ['name', 'slug']
                for campo in obrigatorios:
                    if campo not in meta:
                        raise ValidationError(_("O campo obrigatório '%s' está ausente no theme.json.") % campo)

                self.nome = meta.get('name', self.nome)
                self.slug = slugify(meta.get('slug', self.slug))
                self.version = meta.get('version', '')
                self.author = meta.get('author', '')
                self.descricao = meta.get('description', '')

                # Depois de extrair os arquivos e carregar o meta
                variables = meta.get('variables', [])

                for var in variables:
                    nome_original = var.get('name')
                    if not nome_original:
                        continue  # Ignora se não tem nome
                    
                    nome_final = f"{self.slug}_{slugify(nome_original)}".replace("-", "_")

                    tipo = var.get('tipo', 'string')  # Default para string
                    valor_pt = var.get('valor_pt', '')
                    valor_en = var.get('valor_en', '')
                    valor_es = var.get('valor_es', '')

                    variable_obj, created = ThemeVariable.objects.update_or_create(
                        nome=nome_final,
                        defaults={
                            'tipo': tipo,
                            'valor_pt': valor_pt,
                            'valor_en': valor_en,
                            'valor_es': valor_es,
                        }
                    )

                theme_folder_path = os.path.join(settings.BASE_DIR, 'themes/installed', self.slug)

                if os.path.exists(theme_folder_path):
                    shutil.rmtree(theme_folder_path)

                os.makedirs(theme_folder_path, exist_ok=False)
                zip_ref.extractall(theme_folder_path)

            except json.JSONDecodeError:
                raise ValidationError(_("Erro ao interpretar o arquivo theme.json. Verifique se o JSON está bem formado."))
            
            except Exception as e:
                raise ValidationError(_("Erro ao processar o arquivo do tema: %s") % str(e))


class BackgroundSetting(BaseModel):
    name = models.CharField(max_length=100, help_text=_("Nome de referência para o background"), verbose_name=_("Nome"))
    image = models.ImageField(upload_to='backgrounds/', help_text=_("Imagem de fundo"), verbose_name=_("Imagem"))
    is_active = models.BooleanField(default=False, help_text=_("Define se este background está ativo"), verbose_name=_("Ativo"))

    class Meta:
        verbose_name = _("Configuração de Background")
        verbose_name_plural = _("Configurações de Background")

    def __str__(self):
        return self.name

    @classmethod
    def get_active(cls):
        """Pega o background ativo"""
        return cls.objects.filter(is_active=True).first()


class ThemeVariable(BaseModel):
    nome = models.CharField(max_length=100, unique=True, verbose_name=_("Nome"))
    valor_pt = models.TextField(verbose_name=_("Valor em Português"), blank=True, default="")
    valor_en = models.TextField(verbose_name=_("Valor em Inglês"), blank=True, default="")
    valor_es = models.TextField(verbose_name=_("Valor em Espanhol"), blank=True, default="")
    
    tipo = models.CharField(
        max_length=50,
        choices=(
            ('string', _('Texto')),
            ('int', _('Número')),
            ('boolean', _('Booleano')),
        ),
        default='string',
        verbose_name=_("Tipo")
    )

    criado_em = models.DateTimeField(auto_now_add=True, verbose_name=_("Criado em"))
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name=_("Atualizado em"))

    class Meta:
        verbose_name = _("Variável de Tema")
        verbose_name_plural = _("Variáveis de Tema")

    def clean(self):
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', self.nome):
            raise ValidationError(
                _("O nome da variável só pode conter letras, números e underscores (_) "
                  "e deve começar com uma letra ou underscore.")
            )

    def get_valor_convertido(self, lang_code='pt'):
        """Retorna o valor no idioma atual e converte baseado no tipo"""
        valor = getattr(self, f"valor_{lang_code}", None) or self.valor_pt

        if self.tipo == 'int':
            try:
                return float(valor)
            except (ValueError, TypeError):
                return 0
        elif self.tipo == 'boolean':
            return str(valor).lower() in ['true', '1', 'yes', 'sim']
        
        return valor

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome
