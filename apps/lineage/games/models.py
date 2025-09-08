from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.main.home.models import User
from core.models import BaseModel
from django.templatetags.static import static
import random
from django.utils import timezone
from datetime import timedelta
from .choices import *


class Prize(BaseModel):    
    # Campos básicos do prêmio
    name = models.CharField(max_length=255, verbose_name=_("Prize Name"))
    image = models.ImageField(upload_to='prizes/', null=True, blank=True, verbose_name=_("Image"))
    weight = models.PositiveIntegerField(default=1, help_text=_("Quanto maior o peso, maior a chance de ser sorteado."), verbose_name=_("Weight"))
    
    # Campos adicionais
    item_id = models.IntegerField(verbose_name=_("Item ID"))
    enchant = models.IntegerField(default=0, verbose_name=_("Enchant Level"))
    rarity = models.CharField(max_length=15, choices=RARITY_CHOICES, default='COMUM', verbose_name=_("Rarity"))
    
    # Método para retornar a URL da imagem
    def get_image_url(self):
        return self.image.url if self.image else static("roulette/images/default.png")

    def __str__(self):
        return f'{self.name} ({self.rarity})'

    class Meta:
        verbose_name = _("Prize")
        verbose_name_plural = _("Prizes")


class SpinHistory(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("User"))
    prize = models.ForeignKey(Prize, on_delete=models.CASCADE, verbose_name=_("Prize"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    def __str__(self):
        return f'{self.user.username} won {self.prize.name}'

    class Meta:
        verbose_name = _("Spin History")
        verbose_name_plural = _("Spin Histories")


class Bag(BaseModel):
    user = models.OneToOneField(User, related_name='bag', on_delete=models.CASCADE, verbose_name=_("User"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    def __str__(self):
        return f"Bag de {self.user.username}"

    class Meta:
        verbose_name = _("Bag")
        verbose_name_plural = _("Bags")


class BagItem(BaseModel):
    bag = models.ForeignKey(Bag, related_name='items', on_delete=models.CASCADE, verbose_name=_("Bag"))
    item_id = models.IntegerField(verbose_name=_("Item ID"))
    item_name = models.CharField(max_length=100, verbose_name=_("Item Name"))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_("Quantity"))
    enchant = models.IntegerField(default=0, verbose_name=_("Enchant Level"))
    added_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Added At"))

    class Meta:
        unique_together = ('bag', 'item_id', 'enchant')
        verbose_name = _("Bag Item")
        verbose_name_plural = _("Bag Items")

    def __str__(self):
        return f"{self.item_name} +{self.enchant} x{self.quantity} (Bag)"


class Item(BaseModel):
    name = models.CharField(max_length=100, verbose_name=_("Item Name"))
    enchant = models.IntegerField(default=0, verbose_name=_("Enchant Level"))
    item_id = models.IntegerField(verbose_name=_("Item ID"))
    image = models.ImageField(upload_to='items/', verbose_name=_("Image"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    rarity = models.CharField(max_length=20, choices=RARITY_CHOICES, verbose_name=_("Rarity"))
    can_be_populated = models.BooleanField(default=True, verbose_name=_("Can Be Populated"))
    
    def __str__(self):
        return f"{self.name} ({self.get_rarity_display()})"

    class Meta:
        verbose_name = _("Item")
        verbose_name_plural = _("Items")


class BoxType(BaseModel):
    name = models.CharField(max_length=100, verbose_name=_("Box Type Name"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price"))
    boosters_amount = models.PositiveIntegerField(default=5, verbose_name=_("Boosters Amount"))
    
    # Probabilidades por raridade (em %)
    chance_common = models.FloatField(default=60, verbose_name=_("Chance of Common"))
    chance_rare = models.FloatField(default=25, verbose_name=_("Chance of Rare"))
    chance_epic = models.FloatField(default=10, verbose_name=_("Chance of Epic"))
    chance_legendary = models.FloatField(default=5, verbose_name=_("Chance of Legendary"))

    max_epic_items = models.IntegerField(default=0, verbose_name=_("Max Epic Items"))
    max_legendary_items = models.IntegerField(default=0, verbose_name=_("Max Legendary Items"))
    allowed_items = models.ManyToManyField(Item, blank=True, related_name='allowed_in_boxes')

    def __str__(self):
        return self.name

    def get_rarity_by_chance(self):
        roll = random.uniform(0, 100)
        if roll <= self.chance_legendary:
            return 'legendary'
        elif roll <= self.chance_legendary + self.chance_epic:
            return 'epic'
        elif roll <= self.chance_legendary + self.chance_epic + self.chance_rare:
            return 'rare'
        return 'common'

    def get_highest_rarity(self):
        """Retorna a maior raridade disponível na caixa baseada nas chances"""
        if self.chance_legendary > 0:
            return 'legendary'  # Nome correto do arquivo
        elif self.chance_epic > 0:
            return 'epic'
        elif self.chance_rare > 0:
            return 'rare'
        return 'common'

    class Meta:
        verbose_name = _("Box Type")
        verbose_name_plural = _("Box Types")


class Box(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("User"))
    box_type = models.ForeignKey(BoxType, on_delete=models.CASCADE, verbose_name=_("Box Type"))
    opened = models.BooleanField(default=False, verbose_name=_("Opened"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    def __str__(self):
        return f"Box de {self.box_type.name} - {self.user.username}"

    class Meta:
        verbose_name = _("Box")
        verbose_name_plural = _("Boxes")


class BoxItem(BaseModel):
    box = models.ForeignKey(Box, on_delete=models.CASCADE, related_name='items', verbose_name=_("Box"))
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name=_("Item"))
    probability = models.FloatField(default=1.0, verbose_name=_("Probability"))
    opened = models.BooleanField(default=False, verbose_name=_("Opened"))

    def __str__(self):
        return f"{self.item.name} ({'Aberto' if self.opened else 'Fechado'})"

    class Meta:
        verbose_name = _("Box Item")
        verbose_name_plural = _("Box Items")


class BoxItemHistory(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='box_item_history', verbose_name=_("User"))
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name=_("Item"))
    box = models.ForeignKey(Box, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Box"))
    rarity = models.CharField(max_length=20, choices=RARITY_CHOICES, verbose_name=_("Rarity"))
    enchant = models.IntegerField(default=0, verbose_name=_("Enchant Level"))
    obtained_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Obtained At"))

    def __str__(self):
        return f"{self.user.username} ganhou {self.item.name} +{self.enchant} [{self.rarity}]"

    class Meta:
        verbose_name = _("Box Item History")
        verbose_name_plural = _("Box Item Histories")


class Recompensa(BaseModel):
    TIPO_CHOICES = [
        ('NIVEL', _('Por Nível')),
        ('CONQUISTA', _('Por Conquista')),
        ('CONQUISTAS_MULTIPLAS', _('Por Quantidade de Conquistas')),
    ]

    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES, verbose_name=_("Tipo de Recompensa"))
    referencia = models.CharField(max_length=100, verbose_name=_("Referência"))  # nível ou código conquista
    item_id = models.IntegerField(verbose_name=_("Item ID"))
    item_name = models.CharField(max_length=100, verbose_name=_("Item Name"))
    enchant = models.IntegerField(default=0, verbose_name=_("Enchant"))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_("Quantidade"))

    class Meta:
        verbose_name = _("Recompensa")
        verbose_name_plural = _("Recompensas")

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.referencia} => {self.item_name} +{self.enchant} x{self.quantity}"
    
    @property
    def referencia_como_inteiro(self):
        try:
            return int(self.referencia)
        except (ValueError, TypeError):
            return None


class RecompensaRecebida(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recompensas_recebidas_games", verbose_name=_("User"))
    recompensa = models.ForeignKey(Recompensa, on_delete=models.CASCADE, verbose_name=_("Reward"))
    data = models.DateTimeField(auto_now_add=True, verbose_name=_("Date"))

    class Meta:
        unique_together = ('user', 'recompensa')
        verbose_name = _("Received Reward")
        verbose_name_plural = _("Received Rewards")

    def __str__(self):
        return f"{self.user.username} - {self.recompensa}"


class EconomyWeapon(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_("User"))
    level = models.IntegerField(default=0, verbose_name=_("Level"))  # +0 a +10
    fragments = models.IntegerField(default=0, verbose_name=_("Fragments"))

    class Meta:
        verbose_name = _("Economy Weapon")
        verbose_name_plural = _("Economy Weapons")

    def __str__(self):
        return f"{self.user.username} [+{self.level}] ({self.fragments} frags)"


class Monster(BaseModel):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    level = models.IntegerField(verbose_name=_("Level"))
    required_weapon_level = models.IntegerField(verbose_name=_("Required Weapon Level"))
    fragment_reward = models.IntegerField(verbose_name=_("Fragment Reward"))
    image = models.ImageField(upload_to='monsters/', null=True, blank=True, verbose_name=_("Image"))
    respawn_seconds = models.PositiveIntegerField(default=60, verbose_name=_("Respawn Time (seconds)"))
    last_defeated_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Last Defeated At"))

    # Atributos básicos
    attack = models.IntegerField(default=10, verbose_name=_("Attack"))
    defense = models.IntegerField(default=5, verbose_name=_("Defense"))
    hp = models.IntegerField(default=100, verbose_name=_("HP"))

    class Meta:
        verbose_name = _("Monster")
        verbose_name_plural = _("Monsters")

    @property
    def is_alive(self):
        if not self.last_defeated_at:
            return True
        return timezone.now() >= self.last_defeated_at + timedelta(seconds=self.respawn_seconds)

    def __str__(self):
        return f"{self.name} (Level {self.level})"


class RewardItem(BaseModel):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    item_id = models.PositiveIntegerField(verbose_name=_("Item ID"))
    enchant = models.PositiveIntegerField(default=0, verbose_name=_("Enchant"))
    amount = models.PositiveIntegerField(default=1, verbose_name=_("Amount"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))

    class Meta:
        verbose_name = _("Reward Item")
        verbose_name_plural = _("Reward Items")

    def __str__(self):
        return f"{self.name} +{self.enchant}"


class BattlePassSeason(BaseModel):
    name = models.CharField(max_length=100)
    start_date = models.DateTimeField(verbose_name=_("Start Date"))
    end_date = models.DateTimeField(verbose_name=_("End Date"))
    is_active = models.BooleanField(default=False, verbose_name=_("Is Active"))
    premium_price = models.PositiveIntegerField(default=50, verbose_name=_("Premium Price"))

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_active:
            BattlePassSeason.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class BattlePassLevel(BaseModel):
    season = models.ForeignKey(BattlePassSeason, on_delete=models.CASCADE, verbose_name=_("Season"))
    level = models.PositiveIntegerField(verbose_name=_("Level"))
    required_xp = models.PositiveIntegerField(verbose_name=_("Required XP"))

    class Meta:
        unique_together = ('season', 'level')
        verbose_name = _("Battle Pass Level")
        verbose_name_plural = _("Battle Pass Levels")

    def __str__(self):
        return f"Level {self.level} - {self.season}"


class BattlePassReward(BaseModel):
    level = models.ForeignKey(BattlePassLevel, on_delete=models.CASCADE, verbose_name=_("Level"))
    description = models.CharField(max_length=255, verbose_name=_("Description"))
    is_premium = models.BooleanField(default=False, verbose_name=_("Is Premium"))
    # Campos para itens
    item_id = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Item ID"))
    item_name = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("Item Name"))
    item_enchant = models.PositiveIntegerField(default=0, verbose_name=_("Item Enchant"))
    item_amount = models.PositiveIntegerField(default=1, verbose_name=_("Item Amount"))

    class Meta:
        verbose_name = _("Battle Pass Reward")
        verbose_name_plural = _("Battle Pass Rewards")

    def __str__(self):
        return f"{self.description} ({_('Premium') if self.is_premium else _('Free')})"

    def add_to_user_bag(self, user):
        if self.item_id and self.item_name:
            bag = Bag.objects.get(user=user)
            bag_item, created = BagItem.objects.get_or_create(
                bag=bag,
                item_id=self.item_id,
                enchant=self.item_enchant,
                defaults={
                    'item_name': self.item_name,
                    'quantity': self.item_amount,
                }
            )
            if not created:
                bag_item.quantity += self.item_amount
                bag_item.save()
            return bag_item
        return None


class UserBattlePassProgress(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("User"))
    season = models.ForeignKey(BattlePassSeason, on_delete=models.CASCADE, verbose_name=_("Season"))
    xp = models.PositiveIntegerField(default=0, verbose_name=_("XP"))
    claimed_rewards = models.ManyToManyField(BattlePassReward, blank=True, verbose_name=_("Claimed Rewards"))
    has_premium = models.BooleanField(default=False, verbose_name=_("Has Premium"))

    class Meta:
        unique_together = ('user', 'season')
        verbose_name = _("User Battle Pass Progress")
        verbose_name_plural = _("User Battle Pass Progresses")

    def get_current_level(self):
        return self.season.battlepasslevel_set.filter(required_xp__lte=self.xp).order_by('-level').first()

    def add_xp(self, amount):
        self.xp += amount
        self.save()

    def __str__(self):
        return f"{self.user.username} - {self.season} (XP: {self.xp})"


class BattlePassItemExchange(BaseModel):
    item_id = models.PositiveIntegerField(verbose_name=_("Item ID"))
    item_name = models.CharField(max_length=100, verbose_name=_("Item Name"))
    item_enchant = models.PositiveIntegerField(default=0, verbose_name=_("Item Enchant"))
    xp_amount = models.PositiveIntegerField(verbose_name=_("XP Amount"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    max_exchanges = models.PositiveIntegerField(default=0, verbose_name=_("Max Exchanges"), 
        help_text=_("0 = sem limite"))
    current_exchanges = models.PositiveIntegerField(default=0, verbose_name=_("Current Exchanges"))

    class Meta:
        verbose_name = _("Battle Pass Item Exchange")
        verbose_name_plural = _("Battle Pass Item Exchanges")

    def __str__(self):
        return f"{self.item_name} +{self.item_enchant} -> {self.xp_amount} XP"

    def can_exchange(self):
        if not self.is_active:
            return False
        if self.max_exchanges == 0:
            return True
        return self.current_exchanges < self.max_exchanges

    def exchange(self, user, quantity=1):
        if not self.can_exchange():
            return False, _("Esta troca não está mais disponível.")

        try:
            bag = Bag.objects.get(user=user)
            bag_item = BagItem.objects.get(
                bag=bag,
                item_id=self.item_id,
                enchant=self.item_enchant
            )

            if bag_item.quantity < quantity:
                return False, _("Você não possui quantidade suficiente deste item.")

            # Remove os itens da bag
            bag_item.quantity -= quantity
            if bag_item.quantity == 0:
                bag_item.delete()
            else:
                bag_item.save()

            # Adiciona XP ao progresso do Battle Pass
            progress = UserBattlePassProgress.objects.get(
                user=user,
                season=BattlePassSeason.objects.filter(is_active=True).first()
            )
            total_xp = self.xp_amount * quantity
            progress.add_xp(total_xp)

            # Incrementa o contador de trocas
            self.current_exchanges += quantity
            self.save()

            return True, _("Troca realizada com sucesso! Você recebeu {} XP.").format(total_xp)

        except Bag.DoesNotExist:
            return False, _("Você não possui uma bag.")
        except BagItem.DoesNotExist:
            return False, _("Você não possui este item.")
        except UserBattlePassProgress.DoesNotExist:
            return False, _("Você não possui progresso no Battle Pass atual.")
        except Exception as e:
            return False, str(e)
