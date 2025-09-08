from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext_lazy as _, get_language
from django.views.generic import ListView, DetailView, TemplateView
from django.utils import translation
from django.db.models import Prefetch
from .models import (
    WikiPage, WikiPageTranslation,
    WikiUpdate, WikiUpdateTranslation,
)


class WikiPagesMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language()
        
        # Get all active pages with translations
        pages = WikiPage.objects.filter(
            is_active=True,
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiPageTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        ).order_by('order')
        
        # Add pages to context
        context['pages'] = [
            {
                'page': page,
                'translation': page._translation[0] if page._translation else None
            }
            for page in pages
        ]
        
        return context


class WikiHomeView(WikiPagesMixin, ListView):
    model = WikiPage
    template_name = 'wiki/home.html'
    context_object_name = 'pages'

    def get_queryset(self):
        return WikiPage.objects.filter(is_active=True).order_by('order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['updates'] = WikiUpdate.objects.filter(is_active=True).order_by('-release_date')[:5]
        return context


class WikiPageListView(WikiPagesMixin, ListView):
    model = WikiPage
    template_name = 'wiki/pages.html'
    context_object_name = 'pages'

    def get_queryset(self):
        content_type = self.kwargs.get('content_type', 'other')
        return WikiPage.objects.filter(
            is_active=True,
            content_type=content_type
        ).order_by('order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        content_type = self.kwargs.get('content_type', 'other')
        context['content_type'] = content_type
        context['content_type_display'] = dict(WikiPage.CONTENT_TYPES).get(content_type, content_type)
        return context


class WikiPageDetailView(WikiPagesMixin, DetailView):
    model = WikiPage
    template_name = 'wiki/page_detail.html'
    context_object_name = 'page'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return WikiPage.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language()
        
        # Get the translation for the current language
        translation = self.object.translations.filter(language=language).first()
        context['translation'] = translation
        context['content_type_display'] = self.object.get_content_type_display()
        
        return context


class WikiUpdateListView(WikiPagesMixin, ListView):
    model = WikiUpdate
    template_name = 'wiki/updates.html'
    context_object_name = 'updates'

    def get_queryset(self):
        return WikiUpdate.objects.filter(is_active=True).order_by('-release_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Server Updates')
        return context


class WikiUpdateDetailView(WikiPagesMixin, DetailView):
    model = WikiUpdate
    template_name = 'wiki/update_detail.html'
    context_object_name = 'update'

    def get_queryset(self):
        return WikiUpdate.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"v{self.object.version}"
        return context


class WikiSearchView(WikiPagesMixin, TemplateView):
    template_name = 'wiki/search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        language = get_language()
        
        if query:
            # Search in pages
            pages = WikiPage.objects.filter(
                is_active=True,
                translations__language=language,
                translations__title__icontains=query
            ) | WikiPage.objects.filter(
                is_active=True,
                translations__language=language,
                translations__content__icontains=query
            )
            
            # Search in updates
            updates = WikiUpdate.objects.filter(
                is_active=True,
                translations__language=language,
                translations__title__icontains=query
            ) | WikiUpdate.objects.filter(
                is_active=True,
                translations__language=language,
                translations__content__icontains=query
            )
            
            context['pages'] = pages.distinct()
            context['updates'] = updates.distinct()
            context['query'] = query
            context['results_count'] = pages.count() + updates.count()
        
        return context


class WikiSitemapView(WikiPagesMixin, TemplateView):
    template_name = 'wiki/sitemap.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language()
        
        # Get all active pages
        pages = WikiPage.objects.filter(
            is_active=True,
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiPageTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        ).order_by('content_type', 'order')
        
        # Group pages by content type
        pages_by_type = {}
        for page in pages:
            content_type = page.get_content_type_display()
            if content_type not in pages_by_type:
                pages_by_type[content_type] = []
            pages_by_type[content_type].append(page)
        
        context['pages_by_type'] = pages_by_type
        return context
