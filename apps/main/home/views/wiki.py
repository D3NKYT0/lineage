from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _

def wiki_home(request):
    """Main wiki page view"""
    context = {
        'title': _('Wiki - Lineage 2'),
        'description': _('Complete guide and information about Lineage 2 server'),
    }
    return render(request, 'wiki/home.html', context)

def wiki_general(request):
    """General information wiki page"""
    context = {
        'title': _('General Information - Wiki'),
        'description': _('General information about the server'),
    }
    return render(request, 'wiki/general.html', context)

def wiki_rates(request):
    """Server rates information"""
    context = {
        'title': _('Server Rates - Wiki'),
        'description': _('Information about server rates and experience'),
    }
    return render(request, 'wiki/rates.html', context)

def wiki_raids(request):
    """Raid bosses and instances information"""
    context = {
        'title': _('Raid Bosses and Instances - Wiki'),
        'description': _('Information about raid bosses and instances'),
    }
    return render(request, 'wiki/raids.html', context)

def wiki_assistance(request):
    """Game assistance information"""
    context = {
        'title': _('Game Assistance - Wiki'),
        'description': _('Help and assistance for players'),
    }
    return render(request, 'wiki/assistance.html', context)

def wiki_events(request):
    """Events guide information"""
    context = {
        'title': _('Events Guide - Wiki'),
        'description': _('Guide for server events'),
    }
    return render(request, 'wiki/events.html', context)

def wiki_updates(request):
    """Server updates information"""
    context = {
        'title': _('Server Updates - Wiki'),
        'description': _('Latest server updates and changes'),
    }
    return render(request, 'wiki/updates.html', context)

def wiki_features(request):
    """Server features information"""
    context = {
        'title': _('Server Features - Wiki'),
        'description': _('Information about server features'),
    }
    return render(request, 'wiki/features.html', context) 