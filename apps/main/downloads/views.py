from django.views.generic import ListView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import DownloadCategory, DownloadLink

class DownloadListView(ListView):
    model = DownloadCategory
    template_name = 'public/downloads.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return DownloadCategory.objects.filter(is_active=True).prefetch_related(
            'downloads'
        ).filter(downloads__is_active=True).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Downloads')
        return context

class InternalDownloadListView(LoginRequiredMixin, ListView):
    model = DownloadCategory
    template_name = 'downloads/internal_downloads.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return DownloadCategory.objects.filter(is_active=True).prefetch_related(
            'downloads'
        ).filter(downloads__is_active=True).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Downloads')
        context['segment'] = 'downloads'
        return context

def download_redirect(request, pk):
    download = get_object_or_404(DownloadLink, pk=pk, is_active=True)
    
    # Incrementa o contador de downloads
    download.increment_download_count()
    
    # Redireciona para a URL do download
    return redirect(download.url) 