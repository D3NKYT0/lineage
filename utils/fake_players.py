from django.conf import settings

def apply_fake_players(real_count: int) -> int:
    fake = int(real_count * settings.FAKE_PLAYERS_FACTOR)
    if settings.FAKE_PLAYERS_MIN and fake < settings.FAKE_PLAYERS_MIN:
        fake = settings.FAKE_PLAYERS_MIN
    if settings.FAKE_PLAYERS_MAX and fake > settings.FAKE_PLAYERS_MAX:
        fake = settings.FAKE_PLAYERS_MAX
    return fake 