from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class PokemonAnalysis(Base):
    __tablename__ = "pokemon_analyses"

    id = Column(Integer, primary_key=True, index=True)
    pokemon_name = Column(String(100))
    cp = Column(Integer)
    hp = Column(Integer)
    level = Column(Float)
    iv_percentage = Column(Float)
    attack_iv = Column(Integer)
    defense_iv = Column(Integer)
    stamina_iv = Column(Integer)

    # Battle ratings
    battle_rating = Column(String(10))  # A+, A, B, C, etc.
    raid_rating = Column(String(10))

    # Recommendations
    recommendations = Column(JSON)  # Store as JSON

    # Image metadata
    image_filename = Column(String(500))
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<PokemonAnalysis {self.pokemon_name} CP:{self.cp}>"
