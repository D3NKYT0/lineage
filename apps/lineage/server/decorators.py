from django.shortcuts import render, redirect
from functools import wraps
from .models import ApiEndpointToggle
from django.http import JsonResponse
from apps.lineage.server.database import LineageDB
from django.contrib import messages
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.views import APIView
import json


def endpoint_enabled(endpoint_field):
    def decorator(view_func_or_class):
        # Check if it's a class-based view (Django View or DRF APIView)
        if isinstance(view_func_or_class, type) and (issubclass(view_func_or_class, View) or issubclass(view_func_or_class, APIView)):
            # For class-based views, we need to wrap the dispatch method
            original_dispatch = view_func_or_class.dispatch
            
            @wraps(original_dispatch)
            def wrapped_dispatch(self, request, *args, **kwargs):
                toggle = ApiEndpointToggle.objects.first()
                if not toggle or not getattr(toggle, endpoint_field, False):
                    # Check if it's a REST API request
                    if request.path.startswith('/api/'):
                        # Return JSON response instead of DRF Response
                        return JsonResponse(
                            {'error': f'Endpoint {endpoint_field} está desabilitado'},
                            status=503
                        )
                    else:
                        return render(request, "errors/404.html", status=404)
                return original_dispatch(self, request, *args, **kwargs)
            
            view_func_or_class.dispatch = wrapped_dispatch
            return view_func_or_class
        else:
            # For function-based views
            @wraps(view_func_or_class)
            def _wrapped_view(request, *args, **kwargs):
                toggle = ApiEndpointToggle.objects.first()
                if not toggle or not getattr(toggle, endpoint_field, False):
                    # Verifica se é uma requisição de API REST
                    if request.path.startswith('/api/'):
                        # Return JSON response instead of DRF Response
                        return JsonResponse(
                            {'error': f'Endpoint {endpoint_field} está desabilitado'},
                            status=503
                        )
                    else:
                        return render(request, "errors/404.html", status=404)
                return view_func_or_class(request, *args, **kwargs)
            return _wrapped_view
    return decorator


def safe_json_response(func):
    def wrapper(*args, **kwargs):
        data = func(*args, **kwargs)
        if data is None:
            return JsonResponse({"error": "Falha ao obter dados do banco de dados"}, status=400)
        return JsonResponse(data, safe=False)
    return wrapper


def require_lineage_connection(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        db = LineageDB()
        if not db.is_connected():
            messages.error(request, "Banco de dados do Lineage está indisponível no momento.")
            return redirect('profile')
        return view_func(request, *args, **kwargs)
    return wrapper
