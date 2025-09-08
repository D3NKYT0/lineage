from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import ShopPackage, ShopItem, ShopPackageItem, PromotionCode
from .forms import ShopPackageForm, PromotionCodeForm, ShopItemForm


@staff_member_required
def dashboard(request):
    # Get statistics for the dashboard
    items_count = ShopItem.objects.filter(ativo=True).count()
    packages_count = ShopPackage.objects.filter(ativo=True).count()
    promotions_count = PromotionCode.objects.filter(ativo=True).count()
    
    context = {
        'items_count': items_count,
        'packages_count': packages_count,
        'promotions_count': promotions_count,
    }
    
    return render(request, 'shop/manager/dashboard.html', context)


@staff_member_required
def items(request):
    items = ShopItem.objects.all()
    if request.method == 'POST':
        form = ShopItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Item cadastrado com sucesso!")
            return redirect('shop:dashboard')
    else:
        form = ShopItemForm()

    return render(request, 'shop/manager/items.html', {
        'form': form,
        'items': items
    })


@staff_member_required
def packages(request):
    packages = ShopPackage.objects.all()
    items = ShopItem.objects.filter(ativo=True)

    if request.method == 'POST':
        form = ShopPackageForm(request.POST)
        if form.is_valid():
            package = form.save(commit=False)
            package.save()

            itens_data = request.POST.get('itens', '')  # '1:3,2:1'
            if itens_data:
                ShopPackageItem.objects.filter(pacote=package).delete()
                for item_info in itens_data.split(','):
                    if ':' in item_info:
                        item_id, quantidade = item_info.split(':')
                        try:
                            item = ShopItem.objects.get(pk=int(item_id))
                            ShopPackageItem.objects.create(
                                pacote=package,
                                item=item,
                                quantidade=int(quantidade)
                            )
                        except (ShopItem.DoesNotExist, ValueError):
                            continue
            messages.success(request, "Pacote cadastrado com sucesso!")
            return redirect('shop:dashboard')
        else:
            messages.error(request, "Erro ao cadastrar pacote. Verifique os campos.")
    else:
        form = ShopPackageForm()

    return render(request, 'shop/manager/packages.html', {
        'form': form,
        'packages': packages,
        'items': items
    })


@staff_member_required
def promotions(request):
    promotions = PromotionCode.objects.all()
    if request.method == 'POST':
        form = PromotionCodeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Promoção cadastrada com sucesso!")
            return redirect('shop:dashboard')
    else:
        form = PromotionCodeForm()

    return render(request, 'shop/manager/promotions.html', {
        'form': form,
        'promotions': promotions
    })


@staff_member_required
def edit_package(request, package_id):
    package = get_object_or_404(ShopPackage, pk=package_id)
    items = ShopItem.objects.all()  # Itens disponíveis
    package_items = ShopPackageItem.objects.filter(pacote=package)  # Itens já associados ao pacote

    if request.method == 'POST':
        form = ShopPackageForm(request.POST, instance=package)
        if form.is_valid():
            form.save()
            messages.success(request, "Pacote atualizado com sucesso!")
            return redirect('shop:dashboard')
    else:
        form = ShopPackageForm(instance=package)

    return render(request, 'shop/manager/edit_package.html', {
        'form': form,
        'package': package,
        'items': items,
        'package_items': package_items
    })


@staff_member_required
def add_item_to_package(request, package_id):
    package = get_object_or_404(ShopPackage, pk=package_id)
    item_ids = request.POST.getlist('itens')  # Lista de IDs dos itens selecionados

    for item_id in item_ids:
        try:
            item = ShopItem.objects.get(pk=item_id)
            # Criando a relação entre o pacote e o item
            ShopPackageItem.objects.create(pacote=package, item=item, quantidade=1)
        except ShopItem.DoesNotExist:
            continue

    messages.success(request, "Itens adicionados ao pacote com sucesso!")
    return redirect('shop:edit_package', package_id=package.id)


@staff_member_required
def remove_item_from_package(request, item_id):
    package_item = get_object_or_404(ShopPackageItem, pk=item_id)
    package = package_item.pacote

    package_item.delete()
    messages.success(request, "Item removido do pacote com sucesso!")

    return redirect('shop:edit_package', package_id=package.id)
