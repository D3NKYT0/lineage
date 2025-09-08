from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
import json

from .models import License, LicenseVerification
from .manager import license_manager


def is_superuser(user):
    return user.is_superuser


@login_required
@user_passes_test(is_superuser)
def dashboard(request):
    """
    Dashboard principal de licenças
    """
    current_license = license_manager.get_current_license()
    recent_verifications = LicenseVerification.objects.select_related('license').order_by('-verification_date')[:10]
    
    # Estatísticas
    total_licenses = License.objects.count()
    active_licenses = License.objects.filter(status='active').count()
    expired_licenses = License.objects.filter(status='expired').count()
    suspended_licenses = License.objects.filter(status='suspended').count()
    
    context = {
        'current_license': current_license,
        'recent_verifications': recent_verifications,
        'total_licenses': total_licenses,
        'active_licenses': active_licenses,
        'expired_licenses': expired_licenses,
        'suspended_licenses': suspended_licenses,
        'license_info': license_manager.get_license_info(),
    }
    
    return render(request, 'licence/dashboard.html', context)


@login_required
@user_passes_test(is_superuser)
def license_list(request):
    """
    Lista todas as licenças
    """
    licenses = License.objects.all().order_by('-created_at')
    
    # Filtros
    license_type = request.GET.get('type')
    status = request.GET.get('status')
    search = request.GET.get('search')
    
    if license_type:
        licenses = licenses.filter(license_type=license_type)
    
    if status:
        licenses = licenses.filter(status=status)
    
    if search:
        licenses = licenses.filter(
            Q(domain__icontains=search) |
            Q(company_name__icontains=search) |
            Q(contact_email__icontains=search) |
            Q(license_key__icontains=search)
        )
    
    # Paginação
    paginator = Paginator(licenses, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Contadores para estatísticas
    total_licenses = licenses.count()
    active_licenses = licenses.filter(status='active').count()
    pro_licenses = licenses.filter(license_type='pro').count()
    free_licenses = licenses.filter(license_type='free').count()
    
    context = {
        'page_obj': page_obj,
        'license_types': License.LICENSE_TYPES,
        'license_status': License.LICENSE_STATUS,
        'total_licenses': total_licenses,
        'active_licenses': active_licenses,
        'pro_licenses': pro_licenses,
        'free_licenses': free_licenses,
    }
    
    return render(request, 'licence/list.html', context)


@login_required
@user_passes_test(is_superuser)
def license_detail(request, license_id):
    """
    Detalhes de uma licença específica
    """
    license_obj = get_object_or_404(License, id=license_id)
    verifications = license_obj.verifications.all().order_by('-verification_date')[:50]
    
    context = {
        'license': license_obj,
        'verifications': verifications,
    }
    
    return render(request, 'licence/detail.html', context)


@login_required
@user_passes_test(is_superuser)
def license_create(request):
    """
    Cria uma nova licença
    """
    if request.method == 'POST':
        license_type = request.POST.get('license_type')
        domain = request.POST.get('domain')
        contact_email = request.POST.get('contact_email')
        company_name = request.POST.get('company_name', '')
        contact_phone = request.POST.get('contact_phone', '')
        contract_number = request.POST.get('contract_number', '')
        
        try:
            if license_type == 'free':
                success, result = license_manager.create_free_license(
                    domain, contact_email, company_name, contact_phone
                )
            else:
                success, result = license_manager.create_pro_license(
                    domain, contact_email, company_name, contact_phone, contract_number
                )
            
            if success:
                # Busca a licença criada para obter a chave
                license_obj = License.objects.get(id=result)
                messages.success(request, f"Licença criada com sucesso! Chave: {license_obj.license_key}")
                return redirect('licence:detail', license_id=result)
            else:
                messages.error(request, f"Erro ao criar licença: {result}")
                
        except Exception as e:
            messages.error(request, f"Erro inesperado: {str(e)}")
    
    context = {
        'license_types': License.LICENSE_TYPES,
    }
    
    return render(request, 'licence/create.html', context)


@login_required
@user_passes_test(is_superuser)
def license_edit(request, license_id):
    """
    Edita uma licença existente
    """
    license_obj = get_object_or_404(License, id=license_id)
    
    if request.method == 'POST':
        try:
            license_obj.domain = request.POST.get('domain')
            license_obj.contact_email = request.POST.get('contact_email')
            license_obj.company_name = request.POST.get('company_name', '')
            license_obj.contact_phone = request.POST.get('contact_phone', '')
            license_obj.contract_number = request.POST.get('contract_number', '')
            license_obj.notes = request.POST.get('notes', '')
            
            # Atualiza funcionalidades se for L2JPremium PRO
            if license_obj.license_type == 'pro':
                features = {}
                for feature in ['support', 'updates', 'customization', 'priority_support', 'source_code', 'installation_service', 'database_integration']:
                    features[feature] = request.POST.get(f'feature_{feature}') == 'on'
                license_obj.features_enabled.update(features)
            
            license_obj.save()
            messages.success(request, "Licença atualizada com sucesso!")
            return redirect('licence:detail', license_id=license_obj.id)
            
        except Exception as e:
            messages.error(request, f"Erro ao atualizar licença: {str(e)}")
    
    context = {
        'license': license_obj,
        'license_types': License.LICENSE_TYPES,
        'license_status': License.LICENSE_STATUS,
    }
    
    return render(request, 'licence/edit.html', context)


@login_required
@user_passes_test(is_superuser)
def license_activate(request, license_id):
    """
    Ativa uma licença
    """
    license_obj = get_object_or_404(License, id=license_id)
    
    try:
        license_obj.activate(license_obj.domain)
        messages.success(request, "Licença ativada com sucesso!")
    except Exception as e:
        messages.error(request, f"Erro ao ativar licença: {str(e)}")
    
    return redirect('licence:detail', license_id=license_obj.id)


@login_required
@user_passes_test(is_superuser)
def license_deactivate(request, license_id):
    """
    Desativa uma licença
    """
    license_obj = get_object_or_404(License, id=license_id)
    
    try:
        license_obj.deactivate()
        messages.success(request, "Licença desativada com sucesso!")
    except Exception as e:
        messages.error(request, f"Erro ao desativar licença: {str(e)}")
    
    return redirect('licence:detail', license_id=license_obj.id)


@login_required
@user_passes_test(is_superuser)
def license_reactivate(request, license_id):
    """
    Reativa uma licença suspensa
    """
    license_obj = get_object_or_404(License, id=license_id)
    
    try:
        license_obj.reactivate()
        messages.success(request, "Licença reativada com sucesso!")
    except Exception as e:
        messages.error(request, f"Erro ao reativar licença: {str(e)}")
    
    return redirect('licence:detail', license_id=license_obj.id)


@login_required
@user_passes_test(is_superuser)
def license_renew(request, license_id):
    """
    Renova uma licença
    """
    license_obj = get_object_or_404(License, id=license_id)
    
    try:
        days = int(request.POST.get('days', 365))
        license_obj.renew(days)
        messages.success(request, f"Licença renovada por {days} dias!")
    except Exception as e:
        messages.error(request, f"Erro ao renovar licença: {str(e)}")
    
    return redirect('licence:detail', license_id=license_obj.id)


@login_required
@user_passes_test(is_superuser)
def license_delete(request, license_id):
    """
    Remove uma licença
    """
    license_obj = get_object_or_404(License, id=license_id)
    
    if request.method == 'POST':
        try:
            license_obj.delete()
            messages.success(request, "Licença removida com sucesso!")
            return redirect('licence:list')
        except Exception as e:
            messages.error(request, f"Erro ao remover licença: {str(e)}")
    
    context = {
        'license': license_obj,
    }
    
    return render(request, 'licence/delete.html', context)


@login_required
@user_passes_test(is_superuser)
def status(request):
    """
    Página de status da licença atual
    """
    license_info = license_manager.get_license_info()
    current_license = license_manager.get_current_license()
    
    # Calcula o progresso das horas de suporte
    support_progress = 0
    if current_license and current_license.license_type == 'pro':
        if current_license.support_hours_limit > 0:
            support_progress = (current_license.support_hours_used / current_license.support_hours_limit) * 100
    
    context = {
        'license_info': license_info,
        'current_license': current_license,
        'is_valid': license_manager.check_license_status(),
        'support_progress': support_progress,
    }
    
    return render(request, 'licence/status.html', context)


# API Views para ativação remota
@csrf_exempt
@require_http_methods(["POST"])
def api_activate_license(request):
    """
    API para ativação remota de licença
    """
    try:
        data = json.loads(request.body)
        license_key = data.get('license_key')
        domain = data.get('domain')
        contact_email = data.get('contact_email')
        company_name = data.get('company_name', '')
        contact_phone = data.get('contact_phone', '')
        
        if not all([license_key, domain, contact_email]):
            return JsonResponse({
                'success': False,
                'error': 'Campos obrigatórios: license_key, domain, contact_email'
            }, status=400)
        
        success, message = license_manager.activate_license(
            license_key, domain, contact_email, company_name, contact_phone
        )
        
        return JsonResponse({
            'success': success,
            'message': message
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def api_license_status(request):
    """
    API para verificar status da licença
    """
    try:
        license_info = license_manager.get_license_info()
        is_valid = license_manager.check_license_status(request)
        
        return JsonResponse({
            'success': True,
            'is_valid': is_valid,
            'license_info': license_info
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def api_license_features(request):
    """
    API para verificar funcionalidades disponíveis
    """
    try:
        feature = request.GET.get('feature')
        
        if feature:
            can_use = license_manager.can_use_feature(feature, request)
            return JsonResponse({
                'success': True,
                'feature': feature,
                'can_use': can_use
            })
        else:
            license_info = license_manager.get_license_info()
            return JsonResponse({
                'success': True,
                'features': license_info.get('features', {}) if license_info else {}
            })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@user_passes_test(is_superuser)
def test_block(request):
    """
    Página de teste do sistema de bloqueio de login por licença
    """
    from utils.license_manager import check_license_status
    
    context = {
        'is_valid': check_license_status(),
        'license_info': license_manager.get_license_info(),
    }
    
    return render(request, 'licence/test_block.html', context)
