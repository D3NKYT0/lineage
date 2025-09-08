from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel
from utils.media_validators import (
    validate_social_media_image, validate_social_media_video, 
    validate_avatar_image, process_image_for_social_media,
    process_avatar_image, create_image_thumbnail
)
import os

User = get_user_model()


class Post(BaseModel):
    """Modelo para posts da rede social"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='social_posts',
        verbose_name=_('Autor')
    )
    content = models.TextField(
        verbose_name=_('Conteúdo'),
        help_text=_('Conteúdo do post')
    )
    image = models.ImageField(
        upload_to='social/posts/',
        blank=True,
        null=True,
        verbose_name=_('Imagem'),
        help_text=_('Imagem opcional para o post (máx. 10MB, 1920x1080px)'),
        validators=[validate_social_media_image]
    )
    # Novos campos para melhorar a rede social
    video = models.FileField(
        upload_to='social/videos/',
        blank=True,
        null=True,
        verbose_name=_('Vídeo'),
        help_text=_('Vídeo opcional para o post (máx. 100MB, 5min, MP4/MOV/AVI/WEBM)'),
        validators=[validate_social_media_video]
    )
    link = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('Link'),
        help_text=_('Link opcional para o post')
    )
    link_title = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Título do link'),
        help_text=_('Título para o link compartilhado')
    )
    link_description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Descrição do link'),
        help_text=_('Descrição para o link compartilhado')
    )
    link_image = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('Imagem do link'),
        help_text=_('URL da imagem do link compartilhado')
    )
    # Campos de engajamento
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Número de visualizações')
    )
    shares_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Número de compartilhamentos')
    )
    # Campos de privacidade e moderação
    is_public = models.BooleanField(
        default=True,
        verbose_name=_('Público'),
        help_text=_('Se marcado, o post será visível para todos')
    )
    is_pinned = models.BooleanField(
        default=False,
        verbose_name=_('Fixado'),
        help_text=_('Se marcado, o post ficará fixado no topo do perfil')
    )
    is_edited = models.BooleanField(
        default=False,
        verbose_name=_('Editado'),
        help_text=_('Indica se o post foi editado')
    )
    edited_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Data da última edição')
    )
    # Contadores
    likes_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Número de curtidas')
    )
    comments_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Número de comentários')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de criação')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Data de atualização')
    )

    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return f"Post de {self.author.username} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"

    def update_counts(self):
        """Atualiza contadores de likes, comentários e compartilhamentos"""
        self.likes_count = self.likes.count()
        self.comments_count = self.comments.count()
        self.shares_count = self.shares.count()
        self.save(update_fields=['likes_count', 'comments_count', 'shares_count'])

    def increment_views(self):
        """Incrementa o contador de visualizações"""
        self.views_count += 1
        self.save(update_fields=['views_count'])

    def mark_as_edited(self):
        """Marca o post como editado"""
        self.is_edited = True
        self.edited_at = timezone.now()
        self.save(update_fields=['is_edited', 'edited_at'])

    @property
    def engagement_rate(self):
        """Calcula a taxa de engajamento do post"""
        total_interactions = self.likes_count + self.comments_count + self.shares_count
        if self.views_count > 0:
            return (total_interactions / self.views_count) * 100
        return 0

    @property
    def has_media(self):
        """Verifica se o post tem mídia (imagem ou vídeo)"""
        return bool(self.image or self.video)

    @property
    def has_link(self):
        """Verifica se o post tem link"""
        return bool(self.link)
    
    def is_liked_by(self, user):
        """Verifica se um usuário específico deu like no post"""
        if not user or not user.is_authenticated:
            return False
        return self.likes.filter(user=user).exists()
    
    def extract_hashtags_from_content(self):
        """Extrai hashtags do conteúdo do post"""
        import re
        if not self.content:
            return []
        
        # Padrão para encontrar hashtags no conteúdo
        hashtag_pattern = r'#([a-zA-Z0-9_]+)'
        hashtags = re.findall(hashtag_pattern, self.content)
        
        # Retornar hashtags únicas em minúsculas
        return list(set([tag.lower() for tag in hashtags]))
    
    def save(self, *args, **kwargs):
        """Override save para processar mídia automaticamente"""
        # Processar imagem se foi alterada
        if self.image and hasattr(self.image, 'file'):
            try:
                # Processar imagem para otimização
                processed_path = process_image_for_social_media(
                    self.image.path if hasattr(self.image, 'path') else self.image.file,
                    max_width=1920,
                    max_height=1080,
                    quality=85
                )
            except Exception:
                pass  # Se falhar, manter imagem original
        
        super().save(*args, **kwargs)


class Comment(BaseModel):
    """Modelo para comentários nos posts"""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('Post')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='social_comments',
        verbose_name=_('Autor')
    )
    content = models.TextField(
        verbose_name=_('Conteúdo'),
        help_text=_('Conteúdo do comentário')
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='replies',
        verbose_name=_('Comentário pai'),
        help_text=_('Para respostas a outros comentários')
    )
    # Novos campos para comentários
    image = models.ImageField(
        upload_to='social/comments/',
        blank=True,
        null=True,
        verbose_name=_('Imagem'),
        help_text=_('Imagem opcional no comentário (máx. 5MB)'),
        validators=[validate_social_media_image]
    )
    likes_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Número de curtidas')
    )
    is_edited = models.BooleanField(
        default=False,
        verbose_name=_('Editado')
    )
    edited_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Data da edição')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de criação')
    )

    class Meta:
        verbose_name = _('Comentário')
        verbose_name_plural = _('Comentários')
        ordering = ['created_at']

    def __str__(self):
        return f"Comentário de {self.author.username} em {self.post}"

    def update_likes_count(self):
        """Atualiza contador de likes do comentário"""
        self.likes_count = self.comment_likes.count()
        self.save(update_fields=['likes_count'])

    def mark_as_edited(self):
        """Marca o comentário como editado"""
        self.is_edited = True
        self.edited_at = timezone.now()
        self.save(update_fields=['is_edited', 'edited_at'])
    
    def is_liked_by(self, user):
        """Verifica se um usuário específico deu like no comentário"""
        if not user or not user.is_authenticated:
            return False
        return self.comment_likes.filter(user=user).exists()
    
    def get_level(self):
        """Retorna o nível de aninhamento do comentário (0 = comentário principal)"""
        level = 0
        current = self
        while current.parent:
            level += 1
            current = current.parent
        return level
    
    def get_all_replies(self):
        """Retorna todas as respostas aninhadas do comentário"""
        replies = []
        for reply in self.replies.all():
            replies.append(reply)
            replies.extend(reply.get_all_replies())
        return replies
    
    def get_reply_count(self):
        """Retorna o número total de respostas (incluindo respostas de respostas)"""
        return len(self.get_all_replies())


class CommentLike(BaseModel):
    """Modelo para curtidas nos comentários"""
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='comment_likes',
        verbose_name=_('Comentário')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='social_comment_likes',
        verbose_name=_('Usuário')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de criação')
    )

    class Meta:
        verbose_name = _('Curtida de Comentário')
        verbose_name_plural = _('Curtidas de Comentários')
        unique_together = ['comment', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"Curtida de {self.user.username} em comentário de {self.comment.author.username}"


class Like(BaseModel):
    """Modelo para curtidas nos posts"""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name=_('Post')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='social_likes',
        verbose_name=_('Usuário')
    )
    # Novo campo para tipos de reação
    reaction_type = models.CharField(
        max_length=20,
        choices=[
            ('like', '👍 Curtir'),
            ('love', '❤️ Amar'),
            ('haha', '😂 Haha'),
            ('wow', '😮 Uau'),
            ('sad', '😢 Triste'),
            ('angry', '😠 Bravo'),
        ],
        default='like',
        verbose_name=_('Tipo de reação')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de criação')
    )

    class Meta:
        verbose_name = _('Curtida')
        verbose_name_plural = _('Curtidas')
        unique_together = ['post', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_reaction_type_display()} de {self.user.username} em {self.post}"


class Share(BaseModel):
    """Modelo para compartilhamentos de posts"""
    original_post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='shares',
        verbose_name=_('Post original')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='social_shares',
        verbose_name=_('Usuário que compartilhou')
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Comentário no compartilhamento'),
        help_text=_('Comentário opcional ao compartilhar')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de criação')
    )

    class Meta:
        verbose_name = _('Compartilhamento')
        verbose_name_plural = _('Compartilhamentos')
        ordering = ['-created_at']

    def __str__(self):
        return f"Compartilhamento de {self.user.username} do post de {self.original_post.author.username}"


class Follow(BaseModel):
    """Modelo para seguir usuários"""
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name=_('Seguidor')
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name=_('Seguindo')
    )
    # Novo campo para notificações
    notifications_enabled = models.BooleanField(
        default=True,
        verbose_name=_('Notificações ativadas'),
        help_text=_('Receber notificações de posts deste usuário')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de criação')
    )

    class Meta:
        verbose_name = _('Seguir')
        verbose_name_plural = _('Seguir')
        unique_together = ['follower', 'following']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.follower.username} segue {self.following.username}"


class UserProfile(BaseModel):
    """Perfil estendido do usuário para rede social"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='social_profile',
        verbose_name=_('Usuário')
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        verbose_name=_('Biografia'),
        help_text=_('Breve descrição sobre você')
    )
    avatar = models.ImageField(
        upload_to='social/avatars/',
        blank=True,
        null=True,
        verbose_name=_('Avatar'),
        help_text=_('Foto de perfil (máx. 5MB, será redimensionada para 400x400px)'),
        validators=[validate_avatar_image]
    )
    cover_image = models.ImageField(
        upload_to='social/covers/',
        blank=True,
        null=True,
        verbose_name=_('Imagem de capa'),
        help_text=_('Imagem de capa do perfil (máx. 10MB, recomendado: 1200x400px)'),
        validators=[validate_social_media_image]
    )
    website = models.URLField(
        blank=True,
        verbose_name=_('Website'),
        help_text=_('Link para seu site pessoal')
    )
    location = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Localização'),
        help_text=_('Sua cidade/país')
    )
    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Data de nascimento')
    )
    # Novos campos para melhorar o perfil
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Telefone'),
        help_text=_('Seu número de telefone')
    )
    gender = models.CharField(
        max_length=10,
        choices=[
            ('M', 'Masculino'),
            ('F', 'Feminino'),
            ('O', 'Outro'),
            ('P', 'Prefiro não informar'),
        ],
        blank=True,
        verbose_name=_('Gênero')
    )
    interests = models.TextField(
        blank=True,
        verbose_name=_('Interesses'),
        help_text=_('Seus hobbies e interesses')
    )
    social_links = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Links sociais'),
        help_text=_('Links para redes sociais (JSON)')
    )
    # Configurações de privacidade
    is_private = models.BooleanField(
        default=False,
        verbose_name=_('Perfil privado'),
        help_text=_('Se marcado, apenas seguidores aprovados podem ver seus posts')
    )
    show_email = models.BooleanField(
        default=False,
        verbose_name=_('Mostrar email'),
        help_text=_('Se marcado, seu email será visível no perfil')
    )
    show_phone = models.BooleanField(
        default=False,
        verbose_name=_('Mostrar telefone'),
        help_text=_('Se marcado, seu telefone será visível no perfil')
    )
    allow_messages = models.BooleanField(
        default=True,
        verbose_name=_('Permitir mensagens'),
        help_text=_('Se marcado, outros usuários podem te enviar mensagens')
    )
    # Estatísticas
    total_posts = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Total de posts')
    )
    total_likes_received = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Total de curtidas recebidas')
    )
    total_comments_received = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Total de comentários recebidos')
    )

    class Meta:
        verbose_name = _('Perfil Social')
        verbose_name_plural = _('Perfis Sociais')

    def __str__(self):
        return f"Perfil de {self.user.username}"

    @property
    def followers_count(self):
        return self.user.followers.count()

    @property
    def following_count(self):
        return self.user.following.count()

    @property
    def posts_count(self):
        return self.user.social_posts.count()


    def update_statistics(self):
        """Atualiza estatísticas do perfil"""
        self.total_posts = self.user.social_posts.count()
        self.total_likes_received = sum(post.likes_count for post in self.user.social_posts.all())
        self.total_comments_received = sum(post.comments_count for post in self.user.social_posts.all())
        self.save(update_fields=['total_posts', 'total_likes_received', 'total_comments_received'])
    
    def save(self, *args, **kwargs):
        """Override save para processar mídia automaticamente"""
        # Processar avatar se foi alterado
        if self.avatar and hasattr(self.avatar, 'file'):
            try:
                processed_path = process_avatar_image(
                    self.avatar.path if hasattr(self.avatar, 'path') else self.avatar.file,
                    size=400
                )
            except Exception:
                pass  # Se falhar, manter avatar original
        
        # Processar imagem de capa se foi alterada
        if self.cover_image and hasattr(self.cover_image, 'file'):
            try:
                processed_path = process_image_for_social_media(
                    self.cover_image.path if hasattr(self.cover_image, 'path') else self.cover_image.file,
                    max_width=1200,
                    max_height=400,
                    quality=90
                )
            except Exception:
                pass  # Se falhar, manter imagem original
        
        super().save(*args, **kwargs)


class Hashtag(BaseModel):
    """Modelo para hashtags nos posts"""
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('Nome'),
        help_text=_('Nome da hashtag (sem #)')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Descrição'),
        help_text=_('Descrição da hashtag')
    )
    posts_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Número de posts')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de criação')
    )

    class Meta:
        verbose_name = _('Hashtag')
        verbose_name_plural = _('Hashtags')
        ordering = ['-posts_count', '-created_at']

    def __str__(self):
        return f"#{self.name}"

    def update_posts_count(self):
        """Atualiza contador de posts da hashtag"""
        self.posts_count = self.posts.count()
        self.save(update_fields=['posts_count'])


class PostHashtag(BaseModel):
    """Modelo para relacionar posts com hashtags"""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='hashtags',
        verbose_name=_('Post')
    )
    hashtag = models.ForeignKey(
        Hashtag,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name=_('Hashtag')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de criação')
    )

    class Meta:
        verbose_name = _('Hashtag do Post')
        verbose_name_plural = _('Hashtags dos Posts')
        unique_together = ['post', 'hashtag']
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.hashtag.name} em {self.post}"


# ============================================================================
# SISTEMA DE MODERAÇÃO
# ============================================================================

class Report(BaseModel):
    """Modelo para denúncias de conteúdo ou usuários"""
    REPORT_TYPES = [
        ('spam', _('Spam')),
        ('inappropriate', _('Conteúdo Inapropriado')),
        ('harassment', _('Assédio')),
        ('violence', _('Violência')),
        ('hate_speech', _('Discurso de Ódio')),
        ('fake_news', _('Fake News')),
        ('copyright', _('Violação de Direitos Autorais')),
        ('other', _('Outro')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pendente')),
        ('reviewing', _('Em Revisão')),
        ('resolved', _('Resolvido')),
        ('dismissed', _('Descartado')),
    ]
    
    reporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='reports_made',
        verbose_name=_('Denunciante'),
        help_text=_('Deixe em branco para denúncias geradas pelo sistema')
    )
    report_type = models.CharField(
        max_length=20,
        choices=REPORT_TYPES,
        verbose_name=_('Tipo de Denúncia')
    )
    description = models.TextField(
        verbose_name=_('Descrição'),
        help_text=_('Detalhes sobre a denúncia')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status')
    )
    
    # Conteúdo reportado (pode ser post, comentário ou usuário)
    reported_post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='reports',
        verbose_name=_('Post Reportado')
    )
    reported_comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='reports',
        verbose_name=_('Comentário Reportado')
    )
    reported_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='reports_received',
        verbose_name=_('Usuário Reportado')
    )
    
    # Campos de moderação
    assigned_moderator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='reports_assigned',
        verbose_name=_('Moderador Responsável')
    )
    moderator_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Notas do Moderador')
    )
    resolved_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Data de Resolução')
    )
    
    # Prioridade baseada no tipo e quantidade de denúncias
    priority = models.CharField(
        max_length=10,
        choices=[
            ('low', _('Baixa')),
            ('medium', _('Média')),
            ('high', _('Alta')),
            ('urgent', _('Urgente')),
        ],
        default='medium',
        verbose_name=_('Prioridade')
    )
    
    # Contadores
    similar_reports_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Denúncias Similares')
    )
    
    # Contador de denúncias do mesmo usuário para o mesmo post
    user_report_count = models.PositiveIntegerField(
        default=1,
        verbose_name=_('Contador de Denúncias do Usuário'),
        help_text=_('Número de vezes que este usuário denunciou este conteúdo')
    )
    
    class Meta:
        verbose_name = _('Denúncia')
        verbose_name_plural = _('Denúncias')
        ordering = ['-priority', '-created_at']
        permissions = [
            ("can_moderate_reports", _("Pode moderar denúncias")),
            ("can_view_reports", _("Pode visualizar denúncias")),
        ]

    def __str__(self):
        content = self.get_reported_content()
        return f"{self.get_report_type_display()} - {content}"

    def get_reported_content(self):
        """Retorna uma descrição do conteúdo reportado"""
        if self.reported_post:
            return f"Post: {self.reported_post.content[:50]}..."
        elif self.reported_comment:
            return f"Comentário: {self.reported_comment.content[:50]}..."
        elif self.reported_user:
            return f"Usuário: {self.reported_user.username}"
        return "Conteúdo não especificado"

    def save(self, *args, **kwargs):
        # Atualizar prioridade baseada no tipo de denúncia
        if self.report_type in ['violence', 'hate_speech']:
            self.priority = 'urgent'
        elif self.report_type in ['harassment', 'inappropriate']:
            self.priority = 'high'
        elif self.report_type == 'spam':
            self.priority = 'medium'
        else:
            self.priority = 'low'
        
        # Salvar primeiro para ter o ID
        super().save(*args, **kwargs)
        
        # Atualizar o contador de denúncias do usuário
        if self.reporter:
            self.update_user_report_count()

    def resolve(self, moderator, action_taken, notes=""):
        """Resolve a denúncia"""
        self.status = 'resolved'
        
        # Verificar se moderator é válido antes de atribuir
        if moderator and hasattr(moderator, 'id'):
            try:
                User.objects.get(id=moderator.id)
                self.assigned_moderator = moderator
            except User.DoesNotExist:
                self.assigned_moderator = None
        else:
            self.assigned_moderator = None
            
        self.moderator_notes = notes
        self.resolved_at = timezone.now()
        
        # Verificar se os objetos referenciados ainda existem antes de salvar
        if self.reported_post:
            try:
                Post.objects.get(id=self.reported_post.id)
            except Post.DoesNotExist:
                self.reported_post = None
        
        if self.reported_comment:
            try:
                Comment.objects.get(id=self.reported_comment.id)
            except Comment.DoesNotExist:
                self.reported_comment = None
        
        if self.reported_user:
            try:
                User.objects.get(id=self.reported_user.id)
            except User.DoesNotExist:
                self.reported_user = None
        
        self.save()
        
        # Criar log da ação
        # Verificar se moderator é válido
        moderator_id = None
        if moderator and hasattr(moderator, 'id'):
            moderator_id = moderator.id
            try:
                User.objects.get(id=moderator_id)
            except User.DoesNotExist:
                moderator_id = None
        
        ModerationLog.objects.create(
            moderator_id=moderator_id,
            action_type='resolve_report',
            target_type='report',
            target_id=self.id,
            description=f"Denúncia resolvida: {action_taken}",
            details=notes
        )
    
    def get_triggered_filters(self):
        """Retorna lista de filtros que acionaram este report"""
        return [flag.content_filter for flag in self.filter_flags.all()]
    
    def get_filter_flags_summary(self):
        """Retorna resumo das flags dos filtros"""
        flags = self.filter_flags.select_related('content_filter').order_by('-confidence_score')
        summary = []
        for flag in flags:
            summary.append({
                'filter_name': flag.content_filter.name,
                'filter_type': flag.content_filter.get_filter_type_display(),
                'action': flag.content_filter.get_action_display(),
                'confidence': flag.confidence_score,
                'pattern': flag.matched_pattern[:50] + '...' if flag.matched_pattern and len(flag.matched_pattern) > 50 else flag.matched_pattern
            })
        return summary
    
    def add_filter_flag(self, content_filter, matched_pattern=None, confidence=1.0):
        """Adiciona uma flag de filtro a este report"""
        flag, created = ReportFilterFlag.objects.get_or_create(
            report=self,
            content_filter=content_filter,
            defaults={
                'matched_pattern': matched_pattern,
                'confidence_score': confidence
            }
        )
        if not created and matched_pattern:
            # Atualizar padrão se foi fornecido um novo
            flag.matched_pattern = matched_pattern
            flag.confidence_score = max(flag.confidence_score, confidence)
            flag.save()
        return flag

    @classmethod
    def get_user_report_count_for_content(cls, user, content_type, content_id):
        """
        Retorna o número total de denúncias que um usuário fez para um conteúdo específico
        (incluindo denúncias resolvidas/descartadas)
        """
        if not user or not content_type or not content_id:
            return 0
            
        filter_kwargs = {'reporter': user}
        
        if content_type == 'post':
            filter_kwargs['reported_post_id'] = content_id
        elif content_type == 'comment':
            filter_kwargs['reported_comment_id'] = content_id
        elif content_type == 'user':
            filter_kwargs['reported_user_id'] = content_id
        else:
            return 0
            
        return cls.objects.filter(**filter_kwargs).count()

    @classmethod
    def can_user_report_content(cls, user, content_type, content_id, max_reports=3):
        """
        Verifica se um usuário pode denunciar um conteúdo específico
        baseado no limite máximo de denúncias permitidas
        """
        if not user or not content_type or not content_id:
            return False, 0
            
        current_count = cls.get_user_report_count_for_content(user, content_type, content_id)
        return current_count < max_reports, current_count

    def update_user_report_count(self):
        """
        Atualiza o contador de denúncias do usuário para este conteúdo
        """
        if not self.reporter:
            return
            
        # Contar todas as denúncias deste usuário para este conteúdo
        count = 1  # Começa com 1 (esta denúncia)
        
        if self.reported_post:
            count += Report.objects.filter(
                reporter=self.reporter,
                reported_post=self.reported_post
            ).exclude(id=self.id).count()
        elif self.reported_comment:
            count += Report.objects.filter(
                reporter=self.reporter,
                reported_comment=self.reported_comment
            ).exclude(id=self.id).count()
        elif self.reported_user:
            count += Report.objects.filter(
                reporter=self.reporter,
                reported_user=self.reported_user
            ).exclude(id=self.id).count()
            
        # Usar update() para evitar recursão no save()
        Report.objects.filter(id=self.id).update(user_report_count=count)
        # Atualizar o atributo local também
        self.user_report_count = count


class ReportFilterFlag(BaseModel):
    """Modelo para flags de filtros que acionaram um report"""
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='filter_flags',
        verbose_name=_('Report')
    )
    content_filter = models.ForeignKey(
        'ContentFilter',
        on_delete=models.CASCADE,
        related_name='report_flags',
        verbose_name=_('Filtro de Conteúdo')
    )
    matched_pattern = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Padrão Detectado'),
        help_text=_('Parte do conteúdo que acionou o filtro')
    )
    confidence_score = models.FloatField(
        default=1.0,
        verbose_name=_('Nível de Confiança'),
        help_text=_('Quão confiante o filtro está na detecção (0.0 a 1.0)')
    )
    
    class Meta:
        verbose_name = _('Flag de Filtro')
        verbose_name_plural = _('Flags de Filtros')
        unique_together = ['report', 'content_filter']
        ordering = ['-confidence_score', '-created_at']
    
    def __str__(self):
        return f"{self.content_filter.name} → {self.report}"


class ModerationAction(BaseModel):
    """Modelo para ações de moderação tomadas"""
    ACTION_TYPES = [
        ('warn', _('Advertência')),
        ('hide_content', _('Ocultar Conteúdo')),
        ('delete_content', _('Deletar Conteúdo')),
        ('suspend_user', _('Suspender Usuário')),
        ('ban_user', _('Banir Usuário')),
        ('restrict_user', _('Restringir Usuário')),
        ('approve_content', _('Aprovar Conteúdo')),
        ('feature_content', _('Destacar Conteúdo')),
    ]
    
    SUSPENSION_TYPES = [
        ('temporary', _('Temporária')),
        ('permanent', _('Permanente')),
    ]
    
    moderator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='moderation_actions',
        verbose_name=_('Moderador')
    )
    action_type = models.CharField(
        max_length=20,
        choices=ACTION_TYPES,
        verbose_name=_('Tipo de Ação')
    )
    reason = models.TextField(
        verbose_name=_('Motivo'),
        help_text=_('Justificativa para a ação')
    )
    
    # Conteúdo ou usuário alvo da ação
    target_post = models.ForeignKey(
        Post,
        on_delete=models.SET_NULL,  # Manter registro mesmo se post for deletado
        blank=True,
        null=True,
        related_name='moderation_actions',
        verbose_name=_('Post Alvo')
    )
    target_comment = models.ForeignKey(
        Comment,
        on_delete=models.SET_NULL,  # Manter registro mesmo se comentário for deletado
        blank=True,
        null=True,
        related_name='moderation_actions',
        verbose_name=_('Comentário Alvo')
    )
    
    # Campos para manter informações quando conteúdo é deletado
    target_post_id_backup = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_('ID do Post (Backup)')
    )
    target_comment_id_backup = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_('ID do Comentário (Backup)')
    )
    target_content_backup = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Conteúdo Original (Backup)'),
        help_text=_('Backup do conteúdo para casos de deleção')
    )
    target_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='moderation_actions_received',
        verbose_name=_('Usuário Alvo')
    )
    
    # Campos específicos para suspensões
    suspension_duration = models.DurationField(
        blank=True,
        null=True,
        verbose_name=_('Duração da Suspensão')
    )
    suspension_type = models.CharField(
        max_length=20,
        choices=SUSPENSION_TYPES,
        blank=True,
        null=True,
        verbose_name=_('Tipo de Suspensão')
    )
    suspension_end_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Data de Fim da Suspensão')
    )
    
    # Campos de controle
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Ativa'),
        help_text=_('Se a ação ainda está em vigor')
    )
    expires_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Data de Expiração')
    )
    
    # Notificação ao usuário
    notify_user = models.BooleanField(
        default=True,
        verbose_name=_('Notificar Usuário')
    )
    notification_message = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Mensagem de Notificação')
    )

    class Meta:
        verbose_name = _('Ação de Moderação')
        verbose_name_plural = _('Ações de Moderação')
        ordering = ['-created_at']
        permissions = [
            ("can_take_moderation_actions", _("Pode tomar ações de moderação")),
            ("can_view_moderation_actions", _("Pode visualizar ações de moderação")),
        ]

    def __str__(self):
        target = self.get_target_description()
        return f"{self.get_action_type_display()} - {target}"

    def get_target_description(self):
        """Retorna descrição do alvo da ação (robusta para conteúdo deletado)"""
        if self.target_post:
            return f"Post: {self.target_post.content[:50]}..."
        elif self.target_comment:
            return f"Comentário: {self.target_comment.content[:50]}..."
        elif self.target_user:
            return f"Usuário: {self.target_user.username}"
        elif self.target_content_backup:
            # Usar backup se conteúdo foi deletado
            content_type = "Post" if self.target_post_id_backup else "Comentário" if self.target_comment_id_backup else "Conteúdo"
            backup_id = self.target_post_id_backup or self.target_comment_id_backup
            return f"{content_type} (DELETADO) #{backup_id}: {self.target_content_backup[:50]}..."
        return "Alvo não especificado"

    def save(self, *args, **kwargs):
        # Definir data de expiração para ações temporárias
        if self.action_type in ['suspend_user', 'restrict_user'] and self.suspension_duration:
            self.suspension_end_date = timezone.now() + self.suspension_duration
            self.expires_at = self.suspension_end_date
        
        super().save(*args, **kwargs)

    def apply_action(self):
        """Aplica a ação de moderação de forma robusta"""
        try:
            success = False
            error_msg = None
            
            if self.action_type == 'hide_content':
                success = self._hide_content()
            elif self.action_type == 'delete_content':
                success = self._delete_content()
            elif self.action_type == 'approve_content':
                success = self._approve_content()
            elif self.action_type in ['suspend_user', 'ban_user']:
                success = self._suspend_or_ban_user()
            elif self.action_type == 'restrict_user':
                success = self._restrict_user()
            elif self.action_type == 'warn':
                success = self._warn_user()
            elif self.action_type == 'feature_content':
                success = self._feature_content()
            else:
                error_msg = f"Tipo de ação não implementado: {self.action_type}"
            
            # Criar log da ação
            status = 'success' if success else 'failed'
            description = f"Ação aplicada: {self.get_action_type_display()}"
            if error_msg:
                description += f" - ERRO: {error_msg}"
            
            # Garantir que a instância foi salva antes de criar log
            if not self.pk:
                self.save()
                
            # Verificar se moderator é válido antes de criar log
            moderator_id = None
            if self.moderator and hasattr(self.moderator, 'id'):
                moderator_id = self.moderator.id
                # Verificar se o usuário ainda existe no banco
                try:
                    User.objects.get(id=moderator_id)
                except User.DoesNotExist:
                    moderator_id = None
            
            try:
                ModerationLog.objects.create(
                    moderator_id=moderator_id,
                    action_type=self.action_type,
                    target_type=self.get_target_type(),
                    target_id=self.get_target_id(),
                    description=description,
                    details=self.reason + (f"\nErro: {error_msg}" if error_msg else "") + (f"\nStatus: {status}" if status else "")
                )
            except Exception as log_error:
                # Não propagar o erro para não quebrar a ação principal
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Erro ao criar log de moderação: {log_error}')
            
            # Enviar notificação ao usuário se solicitado
            if success and self.notify_user and self.target_user:
                try:
                    self._send_notification_to_user()
                except Exception as notification_error:
                    # Não propagar o erro da notificação para não quebrar a ação principal
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f'Erro ao enviar notificação ao usuário: {notification_error}')
            
            return success
            
        except Exception as e:
            # Garantir que a instância foi salva antes de criar log de erro
            if not self.pk:
                try:
                    self.save()
                except:
                    pass  # Se não conseguir salvar, continuar com log
                    
            # Log de erro detalhado
            # Verificar se moderator é válido antes de criar log de erro
            moderator_id = None
            if self.moderator and hasattr(self.moderator, 'id'):
                moderator_id = self.moderator.id
                try:
                    User.objects.get(id=moderator_id)
                except User.DoesNotExist:
                    moderator_id = None
            
            try:
                ModerationLog.objects.create(
                    moderator_id=moderator_id,
                    action_type=self.action_type,
                    target_type=self.get_target_type(),
                    target_id=self.get_target_id(),
                    description=f"ERRO ao aplicar ação: {self.get_action_type_display()}",
                    details=f"Erro: {str(e)}\nRazão original: {self.reason}\nStatus: error\nException: {str(e)}"
                )
            except Exception as log_error:
                # Silenciosamente falha para não quebrar ainda mais
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Erro ao criar log de erro de moderação: {log_error}')
            return False
    
    def _hide_content(self):
        """Oculta conteúdo"""
        try:
            if self.target_post and self.target_post.is_public:
                self.target_post.is_public = False
                self.target_post.save(update_fields=['is_public'])
                return True
            elif self.target_comment:
                # Implementar campo is_hidden se necessário
                # Por enquanto, deletar comentário
                self.target_comment.delete()
                return True
            return False
        except Exception:
            return False
    
    def _delete_content(self):
        """Deleta conteúdo"""
        try:
            # Fazer backup antes de deletar
            if self.target_post:
                self.target_post_id_backup = self.target_post.id
                self.target_content_backup = self.target_post.content[:500]
                self.target_post.delete()
                return True
            elif self.target_comment:
                self.target_comment_id_backup = self.target_comment.id
                self.target_content_backup = self.target_comment.content[:500]
                self.target_comment.delete()
                return True
            return False
        except Exception:
            return False
    
    def _approve_content(self):
        """Aprova conteúdo (torna público)"""
        try:
            if self.target_post and not self.target_post.is_public:
                self.target_post.is_public = True
                self.target_post.save(update_fields=['is_public'])
                return True
            return True  # Se já estiver público, considerar como sucesso
        except Exception:
            return False
    
    def _suspend_or_ban_user(self):
        """Suspende ou bane usuário"""
        try:
            if self.target_user and self.target_user.is_active:
                self.target_user.is_active = False
                self.target_user.save(update_fields=['is_active'])
                
                # Se for suspensão temporária, criar task para reativar
                if self.action_type == 'suspend_user' and self.suspension_end_date:
                    # TODO: Implementar task celery para reativar usuário
                    pass
                
                return True
            return False
        except Exception:
            return False
    
    def _restrict_user(self):
        """Restringe usuário (implementar conforme necessário)"""
        try:
            if self.target_user:
                # Implementar lógica de restrição
                # Por exemplo: não pode criar posts, apenas comentar
                return True
            return False
        except Exception:
            return False
    
    def _warn_user(self):
        """Envia advertência ao usuário"""
        try:
            if self.target_user:
                # Implementar sistema de notificações de advertência
                # Por enquanto, apenas registrar no log
                return True
            return False
        except Exception:
            return False
    
    def _feature_content(self):
        """Destaca conteúdo"""
        try:
            if self.target_post:
                self.target_post.is_pinned = True
                self.target_post.save(update_fields=['is_pinned'])
                return True
            return False
        except Exception:
            return False

    def _send_notification_to_user(self):
        """Envia notificação ao usuário sobre a ação de moderação"""
        from utils.notifications import send_notification
        from django.utils.translation import gettext as _
        
        # Determinar o tipo de ação para a mensagem
        action_display = self.get_action_type_display()
        
        # Criar mensagem base
        if self.notification_message:
            # Usar mensagem personalizada se fornecida
            message = self.notification_message
        else:
            # Criar mensagem padrão baseada no tipo de ação
            if self.action_type == 'warn':
                message = _('Você recebeu uma advertência da moderação.')
            elif self.action_type == 'hide_content':
                message = _('Seu conteúdo foi ocultado pela moderação.')
            elif self.action_type == 'delete_content':
                message = _('Seu conteúdo foi removido pela moderação.')
            elif self.action_type == 'suspend_user':
                message = _('Sua conta foi suspensa temporariamente.')
            elif self.action_type == 'ban_user':
                message = _('Sua conta foi banida permanentemente.')
            elif self.action_type == 'restrict_user':
                message = _('Suas permissões foram restringidas.')
            elif self.action_type == 'approve_content':
                message = _('Seu conteúdo foi aprovado pela moderação.')
            elif self.action_type == 'feature_content':
                message = _('Seu conteúdo foi destacado pela moderação.')
            else:
                message = _('Uma ação de moderação foi aplicada ao seu conteúdo.')
            
            # Adicionar motivo se disponível
            if self.reason:
                message += f" {_('Motivo')}: {self.reason}"
        
        # Criar link para a notificação (opcional)
        link = None
        if self.target_post:
            link = f"/social/post/{self.target_post.id}/"
        elif self.target_comment:
            link = f"/social/post/{self.target_comment.post.id}/#comment-{self.target_comment.id}"
        
        # Enviar notificação
        send_notification(
            user=self.target_user,
            notification_type='user',
            message=message,
            created_by=self.moderator,
            link=link
        )

    def get_target_type(self):
        """Retorna o tipo do alvo"""
        if self.target_post:
            return 'post'
        elif self.target_comment:
            return 'comment'
        elif self.target_user:
            return 'user'
        elif self.target_post_id_backup:
            return 'post'
        elif self.target_comment_id_backup:
            return 'comment'
        return 'action'

    def get_target_id(self):
        """Retorna o ID do alvo (robusta para conteúdo deletado)"""
        # Tentar obter ID dos objetos principais (se existem e têm ID válido)
        if self.target_post and getattr(self.target_post, 'id', None) is not None:
            return self.target_post.id
        elif self.target_comment and getattr(self.target_comment, 'id', None) is not None:
            return self.target_comment.id
        elif self.target_user and getattr(self.target_user, 'id', None) is not None:
            return self.target_user.id
            
        # Usar campos de backup se objetos principais não têm ID válido
        if self.target_post_id_backup:
            return self.target_post_id_backup
        elif self.target_comment_id_backup:
            return self.target_comment_id_backup
        
        # Se não há nenhum alvo, usar o ID desta própria ação como fallback
        if self.pk:
            return self.pk
        else:
            # Se nem mesmo tem pk, usar um ID padrão que não quebre FK
            return 1


class ContentFilter(BaseModel):
    """Modelo para filtros automáticos de conteúdo"""
    FILTER_TYPES = [
        ('keyword', _('Palavra-chave')),
        ('regex', _('Expressão Regular')),
        ('spam_pattern', _('Padrão de Spam')),
        ('url_pattern', _('Padrão de URL')),
    ]
    
    ACTION_CHOICES = [
        ('flag', _('Marcar para Revisão')),
        ('auto_hide', _('Ocultar Automaticamente')),
        ('auto_delete', _('Deletar Automaticamente')),
        ('notify_moderator', _('Notificar Moderador')),
    ]
    
    name = models.CharField(
        max_length=100,
        verbose_name=_('Nome do Filtro')
    )
    filter_type = models.CharField(
        max_length=20,
        choices=FILTER_TYPES,
        verbose_name=_('Tipo de Filtro')
    )
    pattern = models.TextField(
        verbose_name=_('Padrão'),
        help_text=_('Palavra-chave, regex ou padrão a ser filtrado')
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name=_('Ação')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Ativo')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Descrição')
    )
    
    # Campos de controle
    case_sensitive = models.BooleanField(
        default=False,
        verbose_name=_('Sensível a Maiúsculas/Minúsculas')
    )
    apply_to_posts = models.BooleanField(
        default=True,
        verbose_name=_('Aplicar a Posts')
    )
    apply_to_comments = models.BooleanField(
        default=True,
        verbose_name=_('Aplicar a Comentários')
    )
    apply_to_usernames = models.BooleanField(
        default=False,
        verbose_name=_('Aplicar a Nomes de Usuário')
    )
    
    # Estatísticas
    matches_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Número de Correspondências')
    )
    last_matched = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Última Correspondência')
    )

    class Meta:
        verbose_name = _('Filtro de Conteúdo')
        verbose_name_plural = _('Filtros de Conteúdo')
        ordering = ['-is_active', 'name']

        def __str__(self):
            return f"{self.name} ({self.get_filter_type_display()})"

    def matches_content(self, content):
        """Verifica se o conteúdo corresponde ao filtro"""
        if not self.is_active:
            return False
        
        if not content:
            return False
        
        if self.case_sensitive:
            text = content
            pattern = self.pattern
        else:
            text = content.lower()
            pattern = self.pattern.lower()
        
        if self.filter_type == 'keyword':
            # Para keywords, dividir o padrão em palavras individuais
            keywords = pattern.split()
            for keyword in keywords:
                if keyword.strip() in text:
                    return True
            return False
        elif self.filter_type == 'regex':
            import re
            try:
                # Para regex, usar o padrão original (case sensitivity é controlada pelo regex)
                regex_pattern = self.pattern
                flags = 0 if self.case_sensitive else re.IGNORECASE
                return bool(re.search(regex_pattern, content, flags))
            except re.error:
                return False
        elif self.filter_type == 'spam_pattern':
            # Padrões comuns de spam em português e inglês
            spam_patterns = [
                # Palavras de ganho fácil (português e inglês)
                r'\b(ganhe|ganhar|dinheiro|fácil|rápido|grátis|free|money|earn|easy|rich)\b',
                r'\b(clique|click|here|aqui|agora|now|urgente|urgent)\b',
                
                # Frases comuns de spam
                r'ganhe? dinheiro',
                r'dinheiro fácil',
                r'renda extra',
                r'trabalhe em casa',
                r'oportunidade única',
                r'limited time',
                r'act now',
                r'click here',
                r'clique aqui',
                
                # Padrões originais em inglês
                r'\b(buy|sell|cheap|discount|business|opportunity)\b',
                r'\b(viagra|cialis|casino|poker|lottery)\b',
                r'http[s]?://[^\s<>"{}|\\^`\[\]]{1,2000}',
                
                # Múltiplos sinais de exclamação ou interrogação
                r'[!]{3,}',
                r'[?]{3,}',
                
                # Caps excessivo
                r'[A-Z]{10,}',
            ]
            import re
            for spam_pattern in spam_patterns:
                try:
                    if re.search(spam_pattern, text, re.IGNORECASE):
                        return True
                except Exception:
                    # Em caso de erro na regex, continuar para o próximo padrão
                    continue
            return False
        
        return False

    def apply_action_to_content(self, content, content_type, content_id):
        """Aplica a ação do filtro ao conteúdo"""
        if self.action == 'flag':
            # Criar denúncia automática
            Report.objects.create(
                reporter=None,  # Sistema
                report_type='spam' if self.filter_type == 'spam_pattern' else 'inappropriate',
                description=f"Conteúdo filtrado automaticamente: {self.name}",
                status='pending',
                priority='medium'
            )
        
        elif self.action == 'auto_hide':
            if content_type == 'post':
                post = Post.objects.get(id=content_id)
                post.is_public = False
                post.save()
            elif content_type == 'comment':
                comment = Comment.objects.get(id=content_id)
                # Marcar como oculto (implementar se necessário)
                pass
        
        elif self.action == 'auto_delete':
            if content_type == 'post':
                Post.objects.filter(id=content_id).delete()
            elif content_type == 'comment':
                Comment.objects.filter(id=content_id).delete()
        
        # Atualizar estatísticas
        self.matches_count += 1
        self.last_matched = timezone.now()
        self.save()


class ModerationLog(BaseModel):
    """Modelo para logs de ações de moderação"""
    LOG_TYPES = [
        ('report_created', _('Denúncia Criada')),
        ('report_resolved', _('Denúncia Resolvida')),
        ('report_status_changed', _('Status da Denúncia Alterado')),
        ('report_assigned', _('Denúncia Atribuída')),
        ('resolve_report', _('Resolver Denúncia')),
        ('content_hidden', _('Conteúdo Ocultado')),
        ('content_deleted', _('Conteúdo Deletado')),
        ('user_suspended', _('Usuário Suspenso')),
        ('user_banned', _('Usuário Banido')),
        ('filter_triggered', _('Filtro Acionado')),
        ('filter_deleted', _('Filtro Deletado')),
        ('warning_sent', _('Advertência Enviada')),
        ('bulk_action_error', _('Erro em Ação em Massa')),
        ('bulk_action_success', _('Ação em Massa Executada')),
        # Ações específicas dos ModerationAction
        ('hide_content', _('Ocultar Conteúdo')),
        ('delete_content', _('Deletar Conteúdo')),
        ('approve_content', _('Aprovar Conteúdo')),
        ('restrict_user', _('Restringir Usuário')),
        ('warn', _('Advertir Usuário')),
        ('feature_content', _('Destacar Conteúdo')),
    ]
    
    moderator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='moderation_logs',
        verbose_name=_('Moderador')
    )
    action_type = models.CharField(
        max_length=30,
        choices=LOG_TYPES,
        verbose_name=_('Tipo de Ação')
    )
    target_type = models.CharField(
        max_length=20,
        verbose_name=_('Tipo do Alvo'),
        help_text=_('post, comment, user, report, etc.')
    )
    target_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_('ID do Alvo')
    )
    description = models.TextField(
        verbose_name=_('Descrição')
    )
    details = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Detalhes Adicionais')
    )
    
    # Campos de contexto
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name=_('Endereço IP')
    )
    user_agent = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('User Agent')
    )

    class Meta:
        verbose_name = _('Log de Moderação')
        verbose_name_plural = _('Logs de Moderação')
        ordering = ['-created_at']
        permissions = [
            ("can_view_moderation_logs", _("Pode visualizar logs de moderação")),
        ]

    def __str__(self):
        return f"{self.get_action_type_display()} - {self.description[:50]}"

    @classmethod
    def log_action(cls, moderator, action_type, target_type, target_id, description, details=None, request=None):
        """Método de classe para facilitar a criação de logs"""
        # Validar campos obrigatórios
        if not action_type:
            raise ValueError('action_type é obrigatório')
        if not target_type:
            raise ValueError('target_type é obrigatório')
        if target_id is None:
            raise ValueError('target_id é obrigatório')
        if not description:
            raise ValueError('description é obrigatório')
        
        # Verificar se action_type é válido
        valid_types = [choice[0] for choice in cls.LOG_TYPES]
        if action_type not in valid_types:
            raise ValueError(f'Tipo de ação inválido: {action_type}. Tipos válidos: {valid_types}')
        
        try:
            log = cls.objects.create(
                moderator=moderator,
                action_type=action_type,
                target_type=target_type,
                target_id=target_id,
                description=description,
                details=details
            )
            
            if request:
                log.ip_address = request.META.get('REMOTE_ADDR')
                log.user_agent = request.META.get('HTTP_USER_AGENT')
                log.save()
            
            return log
        except Exception as e:
            # Em caso de erro, não propagar a exceção para não quebrar o fluxo principal
            # Log do erro em outra forma se necessário
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Erro ao criar log de moderação: {e}')
            return None


class VerificationRequest(BaseModel):
    """Modelo para solicitações de verificação de conta"""
    
    STATUS_CHOICES = [
        ('pending', _('Pendente')),
        ('approved', _('Aprovada')),
        ('rejected', _('Rejeitada')),
        ('cancelled', _('Cancelada')),
    ]
    
    REJECTION_REASONS = [
        ('incomplete_profile', _('Perfil incompleto')),
        ('invalid_cpf', _('CPF inválido ou não fornecido')),
        ('email_not_verified', _('E-mail não verificado')),
        ('2fa_not_enabled', _('2FA não habilitado')),
        ('insufficient_activity', _('Atividade insuficiente na plataforma')),
        ('policy_violation', _('Violação das políticas da comunidade')),
        ('fake_account', _('Conta falsa ou duplicada')),
        ('other', _('Outro motivo')),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='verification_requests',
        verbose_name=_('Usuário')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status')
    )
    
    # Campos obrigatórios para verificação
    cpf = models.CharField(
        max_length=14,
        verbose_name=_('CPF'),
        help_text=_('CPF válido (será validado)')
    )
    
    # Documentos de identificação
    identity_document = models.ImageField(
        upload_to='verification/documents/',
        verbose_name=_('Documento de Identificação'),
        help_text=_('RG, CNH ou outro documento oficial com foto (máx. 5MB)')
    )
    
    # Informações adicionais
    full_name = models.CharField(
        max_length=200,
        verbose_name=_('Nome Completo'),
        help_text=_('Nome completo como aparece no documento')
    )
    
    birth_date = models.DateField(
        verbose_name=_('Data de Nascimento'),
        help_text=_('Data de nascimento')
    )
    
    phone_number = models.CharField(
        max_length=20,
        verbose_name=_('Telefone'),
        help_text=_('Número de telefone para contato')
    )
    
    # Motivo da solicitação
    reason = models.TextField(
        verbose_name=_('Motivo da Solicitação'),
        help_text=_('Explique por que você deseja ter sua conta verificada'),
        max_length=1000
    )
    
    # Campos de resposta da administração
    rejection_reason = models.CharField(
        max_length=50,
        choices=REJECTION_REASONS,
        blank=True,
        null=True,
        verbose_name=_('Motivo da Rejeição')
    )
    
    admin_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Observações do Administrador'),
        help_text=_('Observações internas sobre a solicitação')
    )
    
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='reviewed_verifications',
        verbose_name=_('Revisado por')
    )
    
    reviewed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Data da Revisão')
    )
    
    # Campos de controle
    is_cpf_locked = models.BooleanField(
        default=False,
        verbose_name=_('CPF Bloqueado'),
        help_text=_('Se marcado, o CPF não pode mais ser alterado pelo usuário')
    )
    
    class Meta:
        verbose_name = _('Solicitação de Verificação')
        verbose_name_plural = _('Solicitações de Verificação')
        ordering = ['-created_at']
    
    def __str__(self):
        if hasattr(self, 'user') and self.user:
            return f"Solicitação de {self.user.username} - {self.get_status_display()}"
        return f"Solicitação - {self.get_status_display()}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        from .utils import validate_cpf
        
        # Validar CPF
        if self.cpf:
            if not validate_cpf(self.cpf):
                raise ValidationError(_('CPF inválido.'))
        
        # Verificar se o usuário já tem uma solicitação pendente
        if self.pk is None and hasattr(self, 'user') and self.user:  # Nova solicitação
            existing_pending = VerificationRequest.objects.filter(
                user=self.user,
                status='pending'
            ).exists()
            if existing_pending:
                raise ValidationError(_('Você já possui uma solicitação de verificação pendente.'))
    
    def save(self, *args, **kwargs):
        # Verificar se o status está mudando para aprovado
        status_changed_to_approved = False
        if self.pk:  # Se já existe no banco
            try:
                old_instance = VerificationRequest.objects.get(pk=self.pk)
                status_changed_to_approved = (old_instance.status != 'approved' and self.status == 'approved')
            except VerificationRequest.DoesNotExist:
                status_changed_to_approved = False
        else:
            status_changed_to_approved = (self.status == 'approved')
        
        # Se a solicitação foi aprovada, marcar o CPF como bloqueado
        if self.status == 'approved' and not self.is_cpf_locked:
            self.is_cpf_locked = True
            
            # Atualizar o CPF do usuário se ainda não estiver definido
            if hasattr(self, 'user') and self.user and not self.user.cpf:
                self.user.cpf = self.cpf
                self.user.save(update_fields=['cpf'])
        
        # Salvar a solicitação
        super().save(*args, **kwargs)
        
        # Após salvar, se o status mudou para aprovado, marcar o usuário como verificado
        if status_changed_to_approved and hasattr(self, 'user') and self.user:
            # Recarregar o usuário do banco para garantir que temos os dados mais recentes
            self.user.refresh_from_db()
            if not self.user.social_verified:
                self.user.social_verified = True
                self.user.save(update_fields=['social_verified'])
    
    @property
    def can_be_approved(self):
        """Verifica se a solicitação pode ser aprovada"""
        if not hasattr(self, 'user') or not self.user:
            return False
        return (
            self.status == 'pending' and
            self.user.is_email_verified and
            self.user.is_2fa_enabled and
            self.cpf and
            self.identity_document
        )
    
    @property
    def requirements_met(self):
        """Verifica se todos os requisitos foram atendidos"""
        if not hasattr(self, 'user') or not self.user:
            return {
                'email_verified': False,
                '2fa_enabled': False,
                'cpf_provided': bool(self.cpf),
                'document_provided': bool(self.identity_document),
                'full_name_provided': bool(self.full_name),
                'birth_date_provided': bool(self.birth_date),
                'phone_provided': bool(self.phone_number),
                'reason_provided': bool(self.reason),
            }
        requirements = {
            'email_verified': self.user.is_email_verified,
            '2fa_enabled': self.user.is_2fa_enabled,
            'cpf_provided': bool(self.cpf),
            'document_provided': bool(self.identity_document),
            'full_name_provided': bool(self.full_name),
            'birth_date_provided': bool(self.birth_date),
            'phone_provided': bool(self.phone_number),
            'reason_provided': bool(self.reason),
        }
        return requirements