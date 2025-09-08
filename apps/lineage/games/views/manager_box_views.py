from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from apps.lineage.games.models import *
from apps.lineage.games.forms import *


# DASHBOARD (admin)
@staff_member_required
def dashboard(request):
    context = {
        'box_type_count': BoxType.objects.count(),
        'box_count': Box.objects.count(),
        'item_count': Item.objects.count(),
    }
    return render(request, 'box/manager/dashboard.html', context)


# VIEWS DA SESSAO BOX (admin)
@staff_member_required
def box_list_view(request):
    boxes = Box.objects.select_related('user', 'box_type').all()
    return render(request, 'box/manager/box/list.html', {'boxes': boxes})


@staff_member_required
def box_create_view(request):
    if request.method == 'POST':
        form = BoxForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('games:box_list'))
    else:
        form = BoxForm()
    return render(request, 'box/manager/box/create.html', {'form': form})


@staff_member_required
def box_edit_view(request, pk):
    box = get_object_or_404(Box, pk=pk)
    if request.method == 'POST':
        form = BoxForm(request.POST, instance=box)
        if form.is_valid():
            form.save()
            return redirect(reverse('games:box_list'))
    else:
        form = BoxForm(instance=box)
    return render(request, 'box/manager/box/edit.html', {'form': form, 'box': box})


@staff_member_required
def box_delete_view(request, pk):
    box = get_object_or_404(Box, pk=pk)
    if request.method == 'POST':
        box.delete()
        return redirect(reverse('games:box_list'))
    return render(request, 'box/manager/box/delete.html', {'box': box})


# VIEWS DA SESSAO BOX TYPE (admin)
@staff_member_required
def box_type_list_view(request):
    box_types = BoxType.objects.all()
    return render(request, 'box/manager/box_type/list.html', {'box_types': box_types})


@staff_member_required
def box_type_create_view(request):
    if request.method == 'POST':
        form = BoxTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('games:box_type_list')
    else:
        form = BoxTypeForm()
    return render(request, 'box/manager/box_type/form.html', {'form': form})


@staff_member_required
def box_type_edit_view(request, pk):
    box_type = get_object_or_404(BoxType, pk=pk)
    if request.method == 'POST':
        form = BoxTypeForm(request.POST, instance=box_type)
        if form.is_valid():
            form.save()
            return redirect('games:box_type_list')
    else:
        form = BoxTypeForm(instance=box_type)
    return render(request, 'box/manager/box_type/form.html', {'form': form, 'box_type': box_type})


@staff_member_required
def box_type_delete_view(request, pk):
    box_type = get_object_or_404(BoxType, pk=pk)
    if request.method == 'POST':
        box_type.delete()
        return redirect('games:box_type_list')
    return render(request, 'box/manager/box_type/delete_confirm.html', {'box_type': box_type})


# VIEWS DA SESSAO BOX ITEMS (admin)
@staff_member_required
def item_list_view(request):
    items = Item.objects.all()
    return render(request, 'box/manager/items/item_list.html', {'items': items})


@staff_member_required
def item_create_view(request):
    form = ItemForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('games:item_list')
    return render(request, 'box/manager/items/item_form.html', {'form': form})


@staff_member_required
def item_edit_view(request, pk):
    item = get_object_or_404(Item, pk=pk)
    form = ItemForm(request.POST or None, request.FILES or None, instance=item)
    if form.is_valid():
        form.save()
        return redirect('games:item_list')
    return render(request, 'box/manager/items/item_form.html', {'form': form})


@staff_member_required
def item_delete_view(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('games:item_list')
    return render(request, 'box/manager/items/item_confirm_delete.html', {'item': item})
