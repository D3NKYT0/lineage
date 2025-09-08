from .models import Event
from django.db import models

from django.shortcuts import render
from django.http import JsonResponse
from apps.main.home.decorator import conditional_otp_required


@conditional_otp_required
def calendar(request):
    context = {
        'segment': 'calendar',
    }
    return render(request, 'pages/calendar.html', context)


@conditional_otp_required
def get_events(request):
    # Mapa de cores
    color_map = {
        'bg-red': {'color': '#dc3545', 'textColor': 'white'},
        'bg-orange': {'color': '#fd7e14', 'textColor': 'white'},
        'bg-green': {'color': '#198754', 'textColor': 'white'},
        'bg-blue': {'color': '#0d6efd', 'textColor': 'white'},
        'bg-purple': {'color': '#6f42c1', 'textColor': 'white'},
        'bg-info': {'color': '#0dcaf0', 'textColor': 'white'},
        'bg-yellow': {'color': '#ffc107', 'textColor': 'black'},
        'bg-secondary': {'color': '#6c757d', 'textColor': 'white'}
    }

    events = Event.objects.filter(models.Q(user=request.user) | models.Q(user=None))
    data = []
    for event in events:
        event_data = {
            "id": event.id,
            "title": event.title,
            "start": event.start_date.strftime('%Y-%m-%d'),
            "end": event.end_date.strftime('%Y-%m-%d'),
            "className": event.className
        }
        
        # Adiciona as cores baseado na className
        if event.className in color_map:
            event_data.update(color_map[event.className])
        
        data.append(event_data)
    
    return JsonResponse(data, safe=False)
