from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import ClanProfile, RecruitmentApplication
from .forms import ClanProfileForm, RecruitmentApplicationForm
from .services import get_user_lead_clans, get_clan_basic_info
from apps.lineage.server.database import LineageDB
from apps.lineage.server.services.account_context import get_available_accounts
from utils.dynamic_import import get_query_class
from utils.render_theme_page import render_theme_page

LineageStats = get_query_class("LineageStats")

class ClanListView(View):
    def get(self, request):
        clans = ClanProfile.objects.filter(recruiting=True)
        # We could enrich this list with game data (leader name, member count)
        # However, to avoid spamming the DB, we might do this via JS or caching.
        
        context = {
            'clans': clans,
            'title': _("Recrutamento de Clãs")
        }
        return render_theme_page(request, 'clans', 'list.html', context)

class ClanDetailView(View):
    def get(self, request, clan_id):
        profile = get_object_or_404(ClanProfile, clan_id=clan_id)
        
        # Look up game stat data using our helper
        game_data = get_clan_basic_info(clan_id)
            
        context = {
            'profile': profile,
            'game_data': game_data,
            'title': _("Perfil do Clã")
        }
        return render_theme_page(request, 'clans', 'detail.html', context)

class ClanDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        accounts = get_available_accounts(request.user)
        logins = [acc.get('login') for acc in accounts if acc.get('login')]
        user_clans = get_user_lead_clans(logins)
        
        current_clan_id = request.GET.get('clan_id')
        selected_clan = None
        profile = None
        form = None
        applications = []
        
        if user_clans:
            if not current_clan_id:
                selected_clan = user_clans[0]
            else:
                selected_clan = next((c for c in user_clans if str(c.get('clan_id')) == str(current_clan_id)), user_clans[0])
            
            if selected_clan:
                profile, created = ClanProfile.objects.get_or_create(
                    clan_id=selected_clan['clan_id'],
                    defaults={'description': ''}
                )
                form = ClanProfileForm(instance=profile)
                applications = RecruitmentApplication.objects.filter(clan_profile=profile).order_by('-created_at')
        
        context = {
            'title': _("Painel do Clã"),
            'user_clans': user_clans,
            'selected_clan': selected_clan,
            'profile': profile,
            'form': form,
            'applications': applications,
        }
        return render_theme_page(request, 'clans', 'dashboard.html', context)

    def post(self, request):
        accounts = get_available_accounts(request.user)
        logins = [acc.get('login') for acc in accounts if acc.get('login')]
        user_clans = get_user_lead_clans(logins)
        
        current_clan_id = request.POST.get('clan_id')
        selected_clan = next((c for c in user_clans if str(c.get('clan_id')) == str(current_clan_id)), None)
        
        if selected_clan:
            profile, _ = ClanProfile.objects.get_or_create(clan_id=selected_clan['clan_id'])
            form = ClanProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, _("Perfil do clã atualizado com sucesso!"))
            else:
                messages.error(request, _("Erro ao atualizar perfil do clã."))
        else:
            messages.error(request, _("Você não é o líder deste clã."))
            
        redirect_url = reverse('clans:dashboard')
        if current_clan_id:
            redirect_url += f"?clan_id={current_clan_id}"
        return redirect(redirect_url)

class ApplyToClanView(LoginRequiredMixin, View):
    def get(self, request, clan_id):
        profile = get_object_or_404(ClanProfile, clan_id=clan_id)
        form = RecruitmentApplicationForm()
        
        context = {
            'profile': profile,
            'form': form,
            'title': _("Inscrever-se no Clã")
        }
        return render_theme_page(request, 'clans', 'apply.html', context)

    def post(self, request, clan_id):
        profile = get_object_or_404(ClanProfile, clan_id=clan_id)
        form = RecruitmentApplicationForm(request.POST)
        
        if form.is_valid():
            app = form.save(commit=False)
            app.user = request.user
            app.clan_profile = profile
            # Verifica spam
            if RecruitmentApplication.objects.filter(user=request.user, clan_profile=profile, status='PENDING').exists():
                messages.error(request, _("Você já tem uma inscrição pendente para este clã."))
                return redirect('clans:detail', clan_id=clan_id)
                
            app.save()
            messages.success(request, _("Inscrição enviada com sucesso!"))
            return redirect('clans:detail', clan_id=clan_id)
            
        context = {
            'profile': profile,
            'form': form,
            'title': _("Inscrever-se no Clã")
        }
        return render_theme_page(request, 'clans', 'apply.html', context)

class ProcessApplicationView(LoginRequiredMixin, View):
    def post(self, request, pk, action):
        app = get_object_or_404(RecruitmentApplication, pk=pk)
        
        # Segurança: Verificar se usuario logado é mesmo lider do clan app.clan_profile.clan_id
        
        if action == 'accept':
            # Implementar logica Híbrida: Atualizar o Lineage DB (char.clanid = clan_id)
            pass
        elif action == 'reject':
            app.status = 'REJECTED'
            app.save()
            messages.info(request, _("Inscrição rejeitada."))
            
        return redirect('clans:dashboard')
