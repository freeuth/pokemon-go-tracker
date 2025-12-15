from sqlalchemy import Column, Integer, String, Float, JSON, Boolean
from app.core.database import Base


class Pokemon(Base):
    __tablename__ = "pokemon"

    id = Column(Integer, primary_key=True, index=True)
    pokedex_number = Column(Integer, unique=True, index=True)
    name_en = Column(String, index=True)
    name_ko = Column(String, index=True)
    types = Column(JSON)  # ["Dragon", "Flying"]
    base_attack = Column(Integer)
    base_defense = Column(Integer)
    base_stamina = Column(Integer)
    image_url = Column(String)
    sprite_url = Column(String, nullable=True)
    evolutions = Column(JSON, nullable=True)  # [{id, name_en, name_ko}]


class Move(Base):
    __tablename__ = "moves"

    id = Column(Integer, primary_key=True, index=True)
    move_id = Column(String, unique=True, index=True)
    name_en = Column(String, index=True)
    name_ko = Column(String, index=True)
    type = Column(String)  # "Dragon", "Fire", etc.
    power = Column(Integer, nullable=True)
    energy = Column(Integer, nullable=True)
    move_type = Column(String)  # "fast" or "charged"
    is_legacy = Column(Boolean, default=False)


class PokemonMove(Base):
    __tablename__ = "pokemon_moves"

    id = Column(Integer, primary_key=True, index=True)
    pokemon_id = Column(Integer, index=True)
    move_id = Column(String, index=True)
    category = Column(String)  # "fast" or "charged"


class SeasonalTier(Base):
    __tablename__ = "seasonal_tiers"

    id = Column(Integer, primary_key=True, index=True)
    season_id = Column(String, index=True)
    season_name_ko = Column(String)
    start_date = Column(String)  # ISO format date
    end_date = Column(String)  # ISO format date
    pokemon_id = Column(Integer, index=True)
    raid_tier = Column(String)  # "NONE", "1", "3", "5", "MEGA", "LEGENDARY"
    raid_attack_tier = Column(String, nullable=True)  # "S", "A", "B", "C", "NONE"
    gbl_great_tier = Column(String, default="NONE")  # "S", "A", "B", "C", "NONE"
    gbl_ultra_tier = Column(String, default="NONE")
    gbl_master_tier = Column(String, default="NONE")
    raid_role_ko = Column(String, nullable=True)  # "딜러", "탱커", etc.


class RaidCounter(Base):
    __tablename__ = "raid_counters"

    id = Column(Integer, primary_key=True, index=True)
    boss_pokemon_id = Column(Integer, index=True)
    season_id = Column(String, nullable=True, index=True)
    team_name_ko = Column(String)
    team_description_ko = Column(String, nullable=True)
    team_order = Column(Integer, default=0)
    members = Column(JSON)  # List of team member details
