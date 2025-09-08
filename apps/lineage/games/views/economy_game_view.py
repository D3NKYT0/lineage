from django.utils.translation import gettext as _
import random

from django.shortcuts import render, redirect, get_object_or_404
from apps.main.home.decorator import conditional_otp_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse

from ..models import EconomyWeapon, Monster, Bag, BagItem, RewardItem


def add_reward_to_bag(user, item_id, item_name, enchant=0, quantity=1):
    # Pega a bag do usuário (supondo que tenha um método assim)
    bag = Bag.objects.get(user=user)

    bag_item, created = BagItem.objects.get_or_create(
        bag=bag,
        item_id=item_id,
        enchant=enchant,
        defaults={
            'item_name': item_name,
            'quantity': quantity,
        }
    )

    if not created:
        bag_item.quantity += quantity
        bag_item.save()

    return bag_item


@conditional_otp_required
def economy_game(request):
    weapon, created = EconomyWeapon.objects.get_or_create(user=request.user)
    monsters = Monster.objects.all().order_by('level')

    for mon in monsters:
        if not mon.is_alive:
            respawn_time = mon.last_defeated_at + timedelta(seconds=mon.respawn_seconds)
            mon.respawn_timestamp = max(0, int(respawn_time.timestamp()))  # timestamp em segundos
        else:
            mon.respawn_timestamp = None

    return render(request, "game/economy_game.html", {
        "weapon": weapon,
        "monsters": monsters,
    })


@conditional_otp_required
def fight_monster(request, monster_id):
    monster = get_object_or_404(Monster, id=monster_id)
    weapon = EconomyWeapon.objects.get(user=request.user)

    if not monster.is_alive:
        messages.error(request, "Esse monstro ainda está se regenerando! Aguarde o respawn.")
        return redirect("games:economy-game")
    
    reward = RewardItem.objects.first()
    if not reward:
        messages.error(request, "Esse mini-game ainda nao tem premiação, fale com um administrador!")
        return redirect("games:economy-game")

    if request.user.fichas < 1:
        messages.error(request, "Você não tem fichas suficientes!")
        return redirect("games:economy-game")

    if weapon.level < monster.required_weapon_level:
        messages.error(request, "Sua arma é fraca demais para esse monstro!")
        return redirect("games:economy-game")

    # Consome ficha
    request.user.fichas -= 1
    request.user.save()

    # --- Atributos do jogador
    weapon_attack = weapon.level * 10
    player_hp = 250 + (weapon.level * 5)  # um pouco de resistência extra

    # --- Atributos do monstro balanceados por level
    monster_hp = monster.hp or (50 + (monster.level * 20))
    monster_attack = monster.attack or (5 + (monster.level * 2))
    monster_defense = monster.defense or (2 + (monster.level * 2))

    rounds = 0
    while player_hp > 0 and monster_hp > 0:
        rounds += 1

        # Jogador ataca
        damage_to_monster = max(weapon_attack - monster_defense, 5)
        monster_hp -= damage_to_monster

        if monster_hp <= 0:
            break

        # Monstro ataca
        damage_to_player = max(monster_attack - (weapon.level * 2), 2)
        player_hp -= damage_to_player

    if monster_hp <= 0:
        weapon.fragments += monster.fragment_reward
        weapon.save()
        monster.last_defeated_at = timezone.now()
        monster.save()
        messages.success(
            request,
            f"✅ Você derrotou {monster.name} em {rounds} turnos e ganhou {monster.fragment_reward} fragmentos!"
        )
    else:
        messages.warning(
            request,
            f"❌ {monster.name} te derrotou após {rounds} turnos! Tente novamente com uma arma mais forte."
        )

    return redirect("games:economy-game")


@conditional_otp_required
def enchant_weapon(request):
    weapon = EconomyWeapon.objects.get(user=request.user)

    if weapon.fragments < 10:
        messages.error(request, "Você precisa de pelo menos 10 fragmentos para tentar encantar.")
        return redirect("games:economy-game")

    # Consome fragmentos
    weapon.fragments -= 10

    # Chance de sucesso reduz conforme o nível
    base_chance = max(0.01, 0.95 - (weapon.level * 0.07))  # Ex: +0 = 95%, +5 = 60%
    if random.random() < base_chance:
        weapon.level += 1

        if weapon.level >= 10:
            messages.success(request, "Parabéns! Sua arma atingiu +10! Recompensa desbloqueada!")

            # Resetar o progresso da arma para reiniciar o jogo
            weapon.level = 0
            weapon.fragments = 0

            reward = RewardItem.objects.first()
            if reward:
                add_reward_to_bag(
                    request.user,
                    reward.item_id,
                    reward.name,
                    reward.enchant,
                    reward.amount
                )

        else:
            messages.success(request, f"Enchant bem-sucedido! Sua arma está em +{weapon.level}.")
    else:
        messages.warning(request, "Enchant falhou! A arma não quebrou, mas você perdeu fragmentos.")

    weapon.save()
    return redirect("games:economy-game")


@conditional_otp_required
def is_monster_alive(request, monster_id):
    monster = get_object_or_404(Monster, id=monster_id)
    is_alive = monster.is_alive
    time_remaining = 0

    if not is_alive:
        respawn_time = monster.last_defeated_at + timedelta(seconds=monster.respawn_seconds)
        time_remaining = max(0, int((respawn_time - timezone.now()).total_seconds()))

    return JsonResponse({
        "is_alive": is_alive,
        "time_remaining": time_remaining,
    })
