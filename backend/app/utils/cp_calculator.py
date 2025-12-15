"""
Pokémon GO CP Calculator

Formula:
CP = floor( (Attack * sqrt(Defense) * sqrt(Stamina) * CPM^2) / 10 )

Where:
- Attack = BaseAttack + IV_Attack
- Defense = BaseDefense + IV_Defense
- Stamina = BaseStamina + IV_Stamina
- CPM = CP Multiplier for the given level
"""

import math

# CP Multipliers for each level (Level 1-50)
CP_MULTIPLIERS = {
    1: 0.094, 1.5: 0.135137432, 2: 0.16639787, 2.5: 0.192650919,
    3: 0.21573247, 3.5: 0.236572661, 4: 0.25572005, 4.5: 0.273530381,
    5: 0.29024988, 5.5: 0.306057377, 6: 0.3210876, 6.5: 0.335445036,
    7: 0.34921268, 7.5: 0.362457751, 8: 0.37523559, 8.5: 0.387592406,
    9: 0.39956728, 9.5: 0.411193551, 10: 0.42250001, 10.5: 0.432926419,
    11: 0.44310755, 11.5: 0.453059958, 12: 0.46279839, 12.5: 0.472336083,
    13: 0.48168495, 13.5: 0.4908558, 14: 0.49985844, 14.5: 0.508701765,
    15: 0.51739395, 15.5: 0.525942511, 16: 0.53435433, 16.5: 0.542635767,
    17: 0.55079269, 17.5: 0.558830576, 18: 0.56675452, 18.5: 0.574569153,
    19: 0.58227891, 19.5: 0.589887917, 20: 0.59740001, 20.5: 0.604818814,
    21: 0.61215729, 21.5: 0.619399365, 22: 0.62656713, 22.5: 0.633644533,
    23: 0.64065295, 23.5: 0.647576426, 24: 0.65443563, 24.5: 0.661214806,
    25: 0.667934, 25.5: 0.674577537, 26: 0.68116492, 26.5: 0.687680648,
    27: 0.69414365, 27.5: 0.700538673, 28: 0.70688421, 28.5: 0.713164996,
    29: 0.71939909, 29.5: 0.725571552, 30: 0.7317, 30.5: 0.737769484,
    31: 0.74378943, 31.5: 0.749761343, 32: 0.75568551, 32.5: 0.761563842,
    33: 0.76739717, 33.5: 0.773186415, 34: 0.77893275, 34.5: 0.784637474,
    35: 0.79030001, 35.5: 0.795920839, 36: 0.80100091, 36.5: 0.806041097,
    37: 0.81103976, 37.5: 0.815999016, 38: 0.82083659, 38.5: 0.825637797,
    39: 0.83039537, 39.5: 0.835111049, 40: 0.83979, 40.5: 0.844444444,
    41: 0.84908295, 41.5: 0.853688487, 42: 0.85827119, 42.5: 0.862822544,
    43: 0.86733371, 43.5: 0.871814761, 44: 0.87626406, 44.5: 0.880683781,
    45: 0.88507263, 45.5: 0.889432942, 46: 0.89375929, 46.5: 0.898057012,
    47: 0.90232277, 47.5: 0.906560982, 48: 0.91077404, 48.5: 0.914961487,
    49: 0.91912271, 49.5: 0.923259003, 50: 0.9273706
}


def calculate_cp(base_attack: int, base_defense: int, base_stamina: int,
                 iv_attack: int, iv_defense: int, iv_stamina: int,
                 level: float) -> int:
    """
    Calculate CP for a Pokémon

    Args:
        base_attack: Base attack stat
        base_defense: Base defense stat
        base_stamina: Base stamina (HP) stat
        iv_attack: Attack IV (0-15)
        iv_defense: Defense IV (0-15)
        iv_stamina: Stamina IV (0-15)
        level: Pokémon level (1-50, including half levels like 20.5)

    Returns:
        CP value (integer)
    """
    if level not in CP_MULTIPLIERS:
        raise ValueError(f"Invalid level: {level}. Must be between 1 and 50 (including half levels)")

    if not (0 <= iv_attack <= 15 and 0 <= iv_defense <= 15 and 0 <= iv_stamina <= 15):
        raise ValueError("IVs must be between 0 and 15")

    cpm = CP_MULTIPLIERS[level]

    attack = base_attack + iv_attack
    defense = base_defense + iv_defense
    stamina = base_stamina + iv_stamina

    cp = math.floor(
        (attack * math.sqrt(defense) * math.sqrt(stamina) * cpm * cpm) / 10
    )

    # CP cannot be less than 10
    return max(10, cp)


def calculate_raid_perfect_cp(base_attack: int, base_defense: int, base_stamina: int) -> dict:
    """
    Calculate perfect IV (15/15/15) CP for raid catches

    Args:
        base_attack: Base attack stat
        base_defense: Base defense stat
        base_stamina: Base stamina stat

    Returns:
        dict with lv20_cp_100 (no weather boost) and lv25_cp_100 (weather boost)
    """
    lv20_cp = calculate_cp(base_attack, base_defense, base_stamina, 15, 15, 15, 20)
    lv25_cp = calculate_cp(base_attack, base_defense, base_stamina, 15, 15, 15, 25)

    return {
        "lv20_cp_100": lv20_cp,
        "lv25_cp_100": lv25_cp
    }


def calculate_hp(base_stamina: int, iv_stamina: int, level: float) -> int:
    """
    Calculate HP for a Pokémon

    Args:
        base_stamina: Base stamina stat
        iv_stamina: Stamina IV (0-15)
        level: Pokémon level (1-50)

    Returns:
        HP value (integer)
    """
    if level not in CP_MULTIPLIERS:
        raise ValueError(f"Invalid level: {level}")

    cpm = CP_MULTIPLIERS[level]
    stamina = base_stamina + iv_stamina

    hp = math.floor(stamina * cpm)

    # HP cannot be less than 10
    return max(10, hp)
