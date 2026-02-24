from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
import logging
import re

from .models import ClanProfile, RecruitmentApplication
from .forms import ClanProfileForm, RecruitmentApplicationForm
from .services import get_user_lead_clans, get_clan_basic_info, get_clan_full_details, get_user_characters, get_top_clans, get_clan_members
from apps.lineage.server.services.account_context import get_available_accounts
from utils.render_theme_page import render_theme_page


def _extract_char_id(char_dict):
    """
    Helper para extrair o ID do personagem levando em conta variações de coluna
    entre diferentes schemas (obj_Id, obj_id, charId, char_id).
    """
    return (
        char_dict.get("char_id")
        or char_dict.get("obj_Id")
        or char_dict.get("obj_id")
        or char_dict.get("charId")
    )


def _normalize_clan_id(value):
    """
    Remove pontuação/formatacao de números (ex: 268.988.327 -> 268988327)
    para IDs de clã vindos de querystring ou formulários.
    """
    if value is None:
        return None
    return re.sub(r"\D", "", str(value))


class TestClaimClanView(LoginRequiredMixin, View):
    def get(self, request):
        accounts = get_available_accounts(request.user)
        logins = [acc.get('login') for acc in accounts if acc.get('login')]
        characters = get_user_characters(logins)

        # Clãs que os personagens do usuário fazem parte (para usar IDs como exemplo)
        user_clans_map = {}
        for char in characters:
            cid = char.get('clan_id') or char.get('clanid') or 0
            if cid and int(cid) > 0:
                cid = int(cid)
                if cid not in user_clans_map:
                    info = get_clan_basic_info(cid)
                    user_clans_map[cid] = {
                        'clan_id': cid,
                        'clan_name': (info.get('clan_name') or info.get('name', f'Clã {cid}')) if info else f'Clã {cid}',
                        'characters': []
                    }
                user_clans_map[cid]['characters'].append(char.get('char_name', '?'))
        user_clans = list(user_clans_map.values())

        # Top 10 clãs do servidor (banco L2)
        top_clans = get_top_clans(limit=10)

        return render_theme_page(request, 'clans', 'test_claim.html', {
            'title': _('Painel de Testes - Clãs'),
            'characters': characters,
            'user_clans': user_clans,
            'top_clans': top_clans or [],
        })
        
    def post(self, request):
        clan_id = _normalize_clan_id(request.POST.get('clan_id'))
        char_id = request.POST.get('char_id')
        
        if clan_id and char_id:
            logger = logging.getLogger(__name__)
            accounts = get_available_accounts(request.user)
            logins = [acc.get('login') for acc in accounts if acc.get('login')]
            characters = get_user_characters(logins)
            # DEBUG: loga IDs de personagens disponíveis e o recebido do formulário
            debug_ids = [str(_extract_char_id(c)) for c in characters]
            logger.info("TestClaimClanView.post - char_id form=%s, available_ids=%s", char_id, debug_ids)

            # Valida se o char pertence mesmo às contas do usuário
            selected_char = next(
                (c for c in characters if str(_extract_char_id(c)) == str(char_id)),
                None,
            )
            # Em modo de teste, se não achar exatamente, usa o primeiro personagem como fallback
            if not selected_char and characters:
                logger.warning(
                    "TestClaimClanView.post - nenhum match exato para char_id=%s, usando fallback=%s",
                    char_id,
                    _extract_char_id(characters[0]),
                )
                selected_char = characters[0]
            
            if selected_char:
                game_data = get_clan_basic_info(clan_id)
                clan_name = game_data.get('clan_name', f'Test Clan {clan_id}') if game_data else f'Test Clan {clan_id}'
                clan_level = game_data.get('clan_level') or game_data.get('level', 1) if game_data else 1
                
                # Store mock data in session
                mock_clans = request.session.get('mock_lead_clans', [])
                
                leader_id = _extract_char_id(selected_char)

                if not any(str(c.get('clan_id')) == str(clan_id) and str(c.get('leader_id')) == str(leader_id) for c in mock_clans):
                    mock_clans.append({
                        'clan_id': int(clan_id),
                        'clan_name': clan_name,
                        'level': clan_level,
                        'leader_id': leader_id,
                        'leader_name': selected_char.get('char_name')
                    })
                    request.session['mock_lead_clans'] = mock_clans
                    
                messages.success(request, _(f"Liderança do clã '{clan_name}' (ID: {clan_id}) reivindicada com o personagem '{selected_char.get('char_name')}' para testes!"))
            else:
                messages.error(request, _("Personagem inválido para sua conta."))
        else:
            messages.error(request, _("ID do Clã ou Personagem não informados."))
            
        return redirect('clans:dashboard')

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
        game_data = get_clan_full_details(clan_id)
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
        
        # Inject mock clans from session for testing
        mock_clans = request.session.get('mock_lead_clans', [])
        user_clans.extend(mock_clans)
        
        current_clan_id_raw = request.GET.get('clan_id')
        current_clan_id = _normalize_clan_id(current_clan_id_raw) if current_clan_id_raw else None
        selected_clan = None
        profile = None
        form = None
        applications = []
        clan_members = []
        
        if user_clans:
            if not current_clan_id:
                selected_clan = user_clans[0]
            else:
                selected_clan = next((c for c in user_clans if str(c.get('clan_id')) == str(current_clan_id)), user_clans[0]) if user_clans else None
            
            if selected_clan:
                profile, _created = ClanProfile.objects.get_or_create(clan_id=selected_clan['clan_id'])
                form = ClanProfileForm(instance=profile)
                applications = RecruitmentApplication.objects.filter(clan_profile=profile).order_by('-created_at')
                clan_members = get_clan_members(selected_clan['clan_id'])
        
        # Normalize clan dicts for template: ensure 'level' key (services returns clan_level)
        user_clans_normalized = []
        for c in user_clans:
            c_copy = dict(c)
            c_copy['level'] = c.get('clan_level') or c.get('level', '-')
            user_clans_normalized.append(c_copy)

        context = {
            'title': _("Painel do Clã"),
            'user_clans': user_clans_normalized,
            'selected_clan': selected_clan,
            'selected_clan_id': int(selected_clan['clan_id']) if selected_clan else None,
            'profile': profile,
            'form': form,
            'applications': applications,
            'clan_members': clan_members if selected_clan else [],
        }
        return render_theme_page(request, 'clans', 'dashboard.html', context)

    def post(self, request):
        accounts = get_available_accounts(request.user)
        logins = [acc.get('login') for acc in accounts if acc.get('login')]
        user_clans = get_user_lead_clans(logins)
        
        # Inject mock clans from session for testing
        mock_clans = request.session.get('mock_lead_clans', [])
        user_clans.extend(mock_clans)
        
        current_clan_id = _normalize_clan_id(request.POST.get('clan_id'))
        selected_clan = next((c for c in user_clans if str(c.get('clan_id')) == str(current_clan_id)), None) if user_clans else None
        
        if selected_clan:
            profile, _created = ClanProfile.objects.get_or_create(clan_id=selected_clan['clan_id'])
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
        accounts = get_available_accounts(request.user)
        logins = [acc.get('login') for acc in accounts if acc.get('login')]
        characters = get_user_characters(logins)
        form = RecruitmentApplicationForm()
        context = {
            'profile': profile,
            'form': form,
            'characters': characters,
            'title': _("Inscrever-se no Clã")
        }
        return render_theme_page(request, 'clans', 'apply.html', context)

    def post(self, request, clan_id):
        profile = get_object_or_404(ClanProfile, clan_id=clan_id)
        accounts = get_available_accounts(request.user)
        logins = [acc.get('login') for acc in accounts if acc.get('login')]
        characters = get_user_characters(logins)
        # Normaliza o char_id vindo do select para garantir apenas dígitos
        post_data = request.POST.copy()
        if 'char_id' in post_data:
            post_data['char_id'] = _normalize_clan_id(post_data.get('char_id'))
        form = RecruitmentApplicationForm(post_data)
        if form.is_valid():
            app = form.save(commit=False)
            app.user = request.user
            app.clan_profile = profile
            char_id = form.cleaned_data.get('char_id')
            char_name = form.cleaned_data.get('char_name') or ''
            if characters:
                # Valida que o personagem pertence às contas do usuário (mas em modo web não bloqueia se falhar)
                valid_char = next(
                    (c for c in characters if str(_extract_char_id(c)) == str(char_id)),
                    None,
                )
                if valid_char:
                    app.char_id = int(char_id)
                    app.char_name = valid_char.get('char_name', char_name)
                else:
                    # Fallback: aceita os dados enviados, apenas avisa o líder depois
                    app.char_id = int(char_id)
                    app.char_name = char_name.strip() or str(char_id)
            else:
                app.char_id = int(char_id)
                app.char_name = char_name.strip() or str(char_id)
            # Verifica spam
            if RecruitmentApplication.objects.filter(user=request.user, clan_profile=profile, status='PENDING').exists():
                messages.error(request, _("Você já tem uma inscrição pendente para este clã."))
                return redirect('clans:detail', clan_id=clan_id)
                
            app.save()
            messages.success(request, _("Inscrição enviada com sucesso!"))
            return redirect('clans:detail', clan_id=clan_id)
            
        # Form inválido: volta para a tela com erros visíveis
        messages.error(request, _("Corrija os erros marcados no formulário antes de enviar novamente."))
        context = {
            'profile': profile,
            'form': form,
            'characters': characters,
            'title': _("Inscrever-se no Clã")
        }
        return render_theme_page(request, 'clans', 'apply.html', context)

class ProcessApplicationView(LoginRequiredMixin, View):
    def post(self, request, pk, action):
        app = get_object_or_404(RecruitmentApplication, pk=pk)
        posted_leader_char_id = request.POST.get('leader_char_id')
        form_clan_id = _normalize_clan_id(request.POST.get('clan_id'))
        
        if not form_clan_id or str(form_clan_id) != str(app.clan_profile.clan_id):
            messages.error(request, _("Dados de clã inválidos."))
            return redirect('clans:dashboard')
            
        accounts = get_available_accounts(request.user)
        logins = [acc.get('login') for acc in accounts if acc.get('login')]
        user_clans = get_user_lead_clans(logins)
        
        # Inject mock clans from session for testing
        mock_clans = request.session.get('mock_lead_clans', [])
        user_clans.extend(mock_clans)
        
        # Security: server-side validation (não confiar em leader_char_id vindo do POST)
        leader_clan = next((c for c in user_clans if str(c.get('clan_id')) == str(form_clan_id)), None)
        if not leader_clan:
            messages.error(request, _("Você não tem permissão para processar esta inscrição com este personagem."))
            return redirect('clans:dashboard')
        
        # Keep leader_char_id available if needed for future hybrid invite logic
        leader_char_id = leader_clan.get('leader_id') or posted_leader_char_id
        
        if action == 'approve':
            # Implementar logica Híbrida: Atualizar o Lineage DB (char.clanid = clan_id)
            # Todo: update DB directly if character is offline, otherwise error message.
            app.status = 'APPROVED'
            app.save()
            messages.success(request, _("Inscrição aprovada com sucesso! (Recurso híbrido de convite pendente)"))
        elif action == 'reject':
            app.status = 'REJECTED'
            app.save()
            messages.info(request, _("Inscrição rejeitada."))
            
        return redirect(f"{reverse('clans:dashboard')}?clan_id={form_clan_id}")
