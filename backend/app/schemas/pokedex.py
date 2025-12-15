from pydantic import BaseModel
from typing import List, Optional


class MoveBase(BaseModel):
    move_id: str
    name_en: str
    name_ko: str
    type: str
    power: Optional[int] = None
    energy: Optional[int] = None
    move_type: str  # "fast" or "charged"
    is_legacy: bool = False


class MoveResponse(MoveBase):
    class Config:
        from_attributes = True


class PokemonListItem(BaseModel):
    id: int
    pokedex_number: int
    name_en: str
    name_ko: str
    types: List[str]
    image_url: str
    can_dynamax: bool = False
    can_gigantamax: bool = False

    class Config:
        from_attributes = True


class EvolutionInfo(BaseModel):
    id: int
    pokedex_number: int
    name_en: str
    name_ko: str


class RaidPerfectCP(BaseModel):
    lv20_cp_100: int  # No weather boost
    lv25_cp_100: int  # Weather-boosted


class CurrentSeasonInfo(BaseModel):
    season_id: str
    season_name_ko: str
    raid_tier: str
    raid_attack_tier: Optional[str] = None
    gbl_great_tier: str
    gbl_ultra_tier: str
    gbl_master_tier: str
    raid_role_ko: Optional[str] = None


class PokemonDetail(BaseModel):
    id: int
    pokedex_number: int
    name_en: str
    name_ko: str
    types: List[str]
    base_attack: int
    base_defense: int
    base_stamina: int
    image_url: str
    sprite_url: Optional[str] = None
    can_dynamax: bool = False
    can_gigantamax: bool = False
    evolutions: Optional[List[EvolutionInfo]] = None
    moves_fast: List[MoveResponse]
    moves_charged: List[MoveResponse]
    raid_perfect_cp: RaidPerfectCP
    current_season: Optional[CurrentSeasonInfo] = None
    raid_counters: Optional[dict] = None

    class Config:
        from_attributes = True


class TeamMember(BaseModel):
    pokemon_id: int
    pokemon_name_ko: str
    pokemon_image_url: str
    fast_move_id: str
    fast_move_name_ko: str
    charged_move_id: str
    charged_move_name_ko: str
    role_ko: str


class RaidTeam(BaseModel):
    name_ko: str
    description_ko: Optional[str] = None
    members: List[TeamMember]


class RaidCountersResponse(BaseModel):
    boss_id: int
    boss_name_ko: str
    boss_name_en: str
    boss_types: List[str]
    boss_image_url: str
    recommended_teams: List[RaidTeam]


class TopAttacker(BaseModel):
    pokemon_id: int
    pokedex_number: int
    name_ko: str
    name_en: str
    types: List[str]
    image_url: str
    raid_attack_tier: str
    recommended_fast_moves: List[MoveResponse]
    recommended_charged_moves: List[MoveResponse]

    class Config:
        from_attributes = True


class TopAttackersResponse(BaseModel):
    season_id: str
    season_name_ko: str
    type_filter: Optional[str] = None
    attackers: List[TopAttacker]
