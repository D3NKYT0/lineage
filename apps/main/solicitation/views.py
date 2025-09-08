from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404, render
from django.views import View
from .models import Solicitation, SolicitationHistory, SolicitationParticipant
from .choices import STATUS_CHOICES
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .forms import SolicitationForm, SolicitationStatusForm
from django.contrib import messages
from django.shortcuts import redirect
from utils.notifications import send_notification
from django.urls import reverse
import logging
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.main.home.models import PerfilGamer


logger = logging.getLogger(__name__)


def is_staff_or_owner(user, solicitation):
    return user.is_staff or solicitation.user == user


class SolicitationDashboardView(LoginRequiredMixin, View):
    def get(self, request, protocol):
        # Obtém a proposta de crédito pelo protocolo
        solicitation = get_object_or_404(Solicitation, protocol=protocol)

        # Obtém os participantes associados à solicitação
        participants = SolicitationParticipant.objects.filter(solicitation=solicitation)

        # Obtém o histórico de eventos associados à solicitação
        history = SolicitationHistory.objects.filter(solicitation=solicitation).order_by('-timestamp')

        # Formulário para mudança de status (apenas para staff)
        status_form = None
        if request.user.is_staff:
            status_form = SolicitationStatusForm(initial={'status': solicitation.status})

        # Passa os dados para o contexto
        context = {
            'solicitation': solicitation,
            'participants': participants,
            'history': history,
            'status_form': status_form,
        }

        return render(request, 'pages/solicitation_dashboard.html', context)
    

class SolicitationListView(LoginRequiredMixin, ListView):
    model = Solicitation
    template_name = 'pages/solicitation_list.html'
    context_object_name = 'solicitations'
    paginate_by = 10

    def get_queryset(self):
        # Verifica se o usuário é admin
        if self.request.user.is_staff:
            # Se for admin, retorna todas as solicitações
            return Solicitation.objects.all()
        else:
            # Se não for admin, retorna apenas as solicitações do usuário logado
            return Solicitation.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_staff:
            # Adiciona estatísticas para staff
            context['total_open'] = Solicitation.objects.filter(status='open').count()
            context['total_pending'] = Solicitation.objects.filter(status='pending').count()
            context['total_in_progress'] = Solicitation.objects.filter(status='in_progress').count()
            context['total_waiting_user'] = Solicitation.objects.filter(status='waiting_user').count()
            context['total_resolved'] = Solicitation.objects.filter(status='resolved').count()
        return context


class SolicitationCreateView(LoginRequiredMixin, CreateView):
    model = Solicitation
    form_class = SolicitationForm
    template_name = 'pages/solicitation_create.html'
    success_url = reverse_lazy('solicitation:solicitation_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)

        perfil = PerfilGamer.objects.get(user=self.request.user)
        perfil.adicionar_xp(50)

        try:
            # Envia notificação para os staffs
            send_notification(
                user=None,  # None para broadcast para staff
                notification_type='staff',
                message=f'Nova solicitação criada: {form.instance.title}',
                created_by=self.request.user,
                link=reverse('solicitation:solicitation_dashboard', kwargs={'protocol': form.instance.protocol})
            )
        except Exception as e:
            logger.error(f"Erro ao criar notificação: {str(e)}")

        messages.success(self.request, f"Solicitação criada com sucesso! Protocolo: {form.instance.protocol}")
        return response


class SolicitationStatusUpdateView(LoginRequiredMixin, View):
    def post(self, request, protocol):
        solicitation = get_object_or_404(Solicitation, protocol=protocol)
        
        # Apenas staff pode mudar status
        if not request.user.is_staff:
            messages.error(request, _("Você não tem permissão para alterar o status desta solicitação."))
            return redirect('solicitation:solicitation_dashboard', protocol=protocol)
        
        form = SolicitationStatusForm(request.POST)
        if form.is_valid():
            old_status = solicitation.status
            new_status = form.cleaned_data['status']
            assigned_to = form.cleaned_data['assigned_to']
            comment = form.cleaned_data['comment']
            
            # Atualiza o status
            solicitation.status = new_status
            if assigned_to:
                solicitation.assigned_to = assigned_to
            
            # Atualiza timestamps se necessário
            if new_status == 'resolved' and not solicitation.resolved_at:
                solicitation.resolved_at = timezone.now()
            elif new_status == 'closed' and not solicitation.closed_at:
                solicitation.closed_at = timezone.now()
            
            solicitation.save()
            
            # Cria entrada no histórico
            status_choices_dict = dict(STATUS_CHOICES)
            old_status_display = status_choices_dict.get(old_status, old_status)
            new_status_display = status_choices_dict.get(new_status, new_status)
            action_text = f"Status alterado de '{old_status_display}' para '{new_status_display}'"
            if comment:
                action_text += f" - {comment}"
            
            SolicitationHistory.objects.create(
                solicitation=solicitation,
                action=action_text,
                user=request.user
            )
            
            # Notifica o usuário sobre a mudança de status
            if solicitation.user and solicitation.user != request.user:
                try:
                    send_notification(
                        user=solicitation.user,
                        notification_type='solicitation_update',
                        message=f'Sua solicitação {solicitation.protocol} teve o status alterado para {new_status_display}',
                        created_by=request.user,
                        link=reverse('solicitation:solicitation_dashboard', kwargs={'protocol': solicitation.protocol})
                    )
                except Exception as e:
                    logger.error(f"Erro ao enviar notificação: {str(e)}")
            
            messages.success(request, f"Status da solicitação alterado para '{new_status_display}'")
        else:
            messages.error(request, _("Erro ao alterar status. Verifique os dados informados."))
        
        return redirect('solicitation:solicitation_dashboard', protocol=protocol)


class AddEventToHistoryView(View):
    def get(self, request, protocol):
        solicitation = get_object_or_404(Solicitation, protocol=protocol)

        # Verifica se o usuário tem permissão
        if not is_staff_or_owner(request.user, solicitation):
            messages.error(request, _("Você não tem permissão para adicionar eventos ao histórico dessa solicitação."))
            return redirect('solicitation:solicitation_dashboard', protocol=protocol)

        # Verifica se o status é final (resolved, closed, cancelled, rejected)
        final_statuses = ['resolved', 'closed', 'cancelled', 'rejected']
        if solicitation.status in final_statuses:
            messages.error(request, _("Não é possível adicionar eventos a uma solicitação que está {}.").format(solicitation.get_status_display().lower()))
            return redirect('solicitation:solicitation_dashboard', protocol=protocol)

        # Verifica se há algum evento no histórico e se o último foi de um usuário comum
        last_event = solicitation.solicitation_history.last()
        
        # Se o usuário não for staff, o próximo evento precisa ser registrado por um staff
        if last_event is not None and last_event.user is not None and not request.user.is_staff:
            if not last_event.user.is_staff:
                messages.info(request, _("O próximo evento precisa ser registrado por um staff."))
                return redirect('solicitation:solicitation_dashboard', protocol=protocol)

        # Exibe formulário de evento
        return render(request, 'pages/add_event_to_history.html', {'solicitation': solicitation})

    def post(self, request, protocol):
        solicitation = get_object_or_404(Solicitation, protocol=protocol)

        # Verifica se o usuário tem permissão
        if not is_staff_or_owner(request.user, solicitation):
            messages.error(request, _("Você não tem permissão para adicionar eventos ao histórico dessa solicitação."))
            return redirect('solicitation:solicitation_dashboard', protocol=protocol)

        # Verifica se o status é final (resolved, closed, cancelled, rejected)
        final_statuses = ['resolved', 'closed', 'cancelled', 'rejected']
        if solicitation.status in final_statuses:
            messages.error(request, _("Não é possível adicionar eventos a uma solicitação que está {}.").format(solicitation.get_status_display().lower()))
            return redirect('solicitation:solicitation_dashboard', protocol=protocol)

        # Verifica se o último evento foi de um usuário comum, mas permite que staff registre eventos sem restrição
        last_event = solicitation.solicitation_history.last()

        # Se o usuário não for staff, o próximo evento precisa ser registrado por um staff
        if last_event is not None and last_event.user is not None and not request.user.is_staff:
            if not last_event.user.is_staff:
                messages.error(request, _("Você só pode registrar um evento depois que um staff fizer a próxima alteração."))
                return redirect('solicitation:solicitation_dashboard', protocol=protocol)

        # Adiciona evento ao histórico
        action = request.POST.get('action')
        image = request.FILES.get('image')

        # Cria o evento com o usuário que fez a alteração
        SolicitationHistory.objects.create(
            solicitation=solicitation,
            action=action,
            image=image,
            user=request.user  # Associando o usuário que fez a alteração
        )

        messages.success(request, _("Evento registrado com sucesso."))
        return redirect('solicitation:solicitation_dashboard', protocol=protocol)
