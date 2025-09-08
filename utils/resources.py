def get_class_name(class_id):
    class_map = {
        # HUMANS
        0: 'Human Fighter',
        1: 'Human Warrior',
        2: 'Gladiator',
        3: 'Warlord',
        4: 'Human Knight',
        5: 'Paladin',
        6: 'Dark Avenger',
        7: 'Rogue',
        8: 'Treasure Hunter',
        9: 'Hawkeye',
        10: 'Human Mage',
        11: 'Human Wizard',
        12: 'Sorcerer',
        13: 'Necromancer',
        14: 'Warlock',
        15: 'Cleric',
        16: 'Bishop',
        17: 'Prophet',
        # ELVES
        18: 'Elven Fighter',
        19: 'Elven Knight',
        20: 'Temple Knight',
        21: 'Swordsinger',
        22: 'Elven Scout',
        23: 'Plainswalker',
        24: 'Silver Ranger',
        25: 'Elven Mage',
        26: 'Elven Wizard',
        27: 'Spellsinger',
        28: 'Elemental Summoner',
        29: 'Elven Oracle',
        30: 'Elven Elder',
        # DARK ELVES
        31: 'Dark Elven Fighter',
        32: 'Pallus Knight',
        33: 'Shillien Knight',
        34: 'Bladedancer',
        35: 'Assasin',
        36: 'Abyss Walker',
        37: 'Phantom Ranger',
        38: 'Dark Elven Mage',
        39: 'Dark Wizard',
        40: 'Spellhowler',
        41: 'Phantom Summoner',
        42: 'Shillien Oracle',
        43: 'Shillien Elder',
        # ORCS
        44: 'Orc Fighter',
        45: 'Orc Raider',
        46: 'Destroyer',
        47: 'Monk',
        48: 'Tyrant',
        49: 'Orc Mage',
        50: 'Orc Shaman',
        51: 'Overlord',
        52: 'Warcryer',
        # DWARVES
        53: 'Dwarven Fighter',
        54: 'Scavenger',
        55: 'Bounty Hunter',
        56: 'Artisan',
        57: 'Warsmith',
        # HUMANS 3rd Professions
        88: 'Duelist',
        89: 'Dread Nought',
        90: 'Phoenix Knight',
        91: 'Hell Knight',
        92: 'Sagittarius',
        93: 'Adventurer',
        94: 'Archmage',
        95: 'Soultaker',
        96: 'Arcane Lord',
        97: 'Cardinal',
        98: 'Hierophant',
        # ELVES 3rd Professions
        99: 'Evas Templar',
        100: 'Sword Muse',
        101: 'Wind Rider',
        102: 'Moonlight Sentinel',
        103: 'Mystic Muse',
        104: 'Elemental Master',
        105: 'Evas Saint',
        # DARK ELVES 3rd Professions
        106: 'Shillien Templar',
        107: 'Spectral Dancer',
        108: 'Ghost Hunter',
        109: 'Ghost Sentinel',
        110: 'Storm Screamer',
        111: 'Spectral Master',
        112: 'Shillien Saint',
        # ORCS 3rd Professions
        113: 'Titan',
        114: 'Grand Khauatari',
        115: 'Dominator',
        116: 'Doomcryer',
        # DWARVES 3rd Professions
        117: 'Fortune Seeker',
        118: 'Maestro',
        # KAMAEL Classes
        123: 'Male Kamael Soldier',
        124: 'Female Kamael Soldier',
        125: 'Trooper',
        126: 'Warder',
        127: 'Berserker',
        128: 'Male Soul Breaker',
        129: 'Female Soul Breaker',
        130: 'Arbalester',
        131: 'Doombringer',
        132: 'Male Soul Hound',
        133: 'Female Soul Hound',
        134: 'Trickster',
        135: 'Inspector',
        136: 'Judicator',
    }
    return class_map.get(class_id, 'Unknown')


def gen_avatar(class_id, gender=0):
    # Mapeando class_id para referências
    ids = {
        0: '1', 1: '1', 2: '1', 3: '1', 4: '1', 5: '1', 6: '1', 7: '1', 8: '1', 9: '1', 10: '2', 11: '2', 12: '2', 13: '2', 14: '2', 
        15: '2', 16: '2', 17: '2', 18: '3', 19: '3', 20: '3', 21: '3', 22: '3', 23: '3', 24: '3', 25: '3', 26: '3', 27: '3', 28: '3', 
        29: '3', 30: '3', 31: '4', 32: '4', 33: '4', 34: '4', 35: '4', 36: '4', 37: '4', 38: '4', 39: '4', 40: '4', 41: '4', 42: '4', 
        43: '4', 44: '5', 45: '5', 46: '5', 47: '5', 48: '5', 49: '6', 50: '6', 51: '6', 52: '6', 53: '7', 54: '7', 55: '7', 56: '7', 
        57: '7', 88: '1', 89: '1', 90: '1', 91: '1', 92: '1', 93: '1', 94: '2', 95: '2', 96: '2', 97: '2', 98: '2', 99: '3', 100: '3', 
        101: '3', 102: '3', 103: '3', 104: '3', 105: '3', 106: '4', 107: '4', 108: '4', 109: '4', 110: '4', 111: '4', 112: '4', 113: '5', 
        114: '5', 115: '6', 116: '6', 117: '7', 118: '7'
    }
    
    # Obtendo a referência (se o class_id não existir, default para 8 - Kamael)
    ref = ids.get(class_id, '8')
    
    # Retorno baseado na referência e gênero
    if ref == '1':
        return "human_male_fighter.jpg" if gender == 0 else "human_female_fighter.jpg"
    elif ref == '2':
        return "human_male_mage.jpg" if gender == 0 else "human_female_mage.jpg"
    elif ref == '3':
        return "elf_male.jpg" if gender == 0 else "elf_female.jpg"
    elif ref == '4':
        return "dark_male.jpg" if gender == 0 else "dark_female.jpg"
    elif ref == '5':
        return "orc_male_fighter.jpg" if gender == 0 else "orc_female_fighter.jpg"
    elif ref == '6':
        return "orc_male_mage.jpg" if gender == 0 else "orc_female_mage.jpg"
    elif ref == '7':
        return "dwarf_male.jpg" if gender == 0 else "dwarf_female.jpg"
    else:
        return "kamael_male.jpg" if gender == 0 else "kamael_female.jpg"
