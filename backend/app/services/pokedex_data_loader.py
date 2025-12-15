"""
Pokédex Data Loader Service
Loads and caches JSON data files for Pokémon GO features
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class PokedexDataLoader:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.pokemon_base: List[Dict] = []
        self.moves: List[Dict] = []
        self.pokemon_moves: List[Dict] = []
        self.seasonal_tiers: List[Dict] = []
        self.raid_counters: List[Dict] = []
        self.pvp_party_rankings: List[Dict] = []

        self.load_all_data()

    def load_all_data(self):
        """Load all JSON data files"""
        self.pokemon_base = self._load_json("pokemon_base.json")
        self.moves = self._load_json("moves.json")
        self.pokemon_moves = self._load_json("pokemon_moves.json")
        self.seasonal_tiers = self._load_json("seasonal_tiers.json")
        self.raid_counters = self._load_json("raid_counters.json")
        self.pvp_party_rankings = self._load_json("pvp_party_rankings.json")

    def _load_json(self, filename: str) -> List[Dict]:
        """Load a JSON file and return its contents"""
        file_path = self.data_dir / filename
        if not file_path.exists():
            print(f"Warning: {file_path} not found. Returning empty list.")
            return []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return []

    def get_pokemon_by_id(self, pokemon_id: int) -> Optional[Dict]:
        """Get Pokémon base data by pokedex_number"""
        for pokemon in self.pokemon_base:
            if pokemon.get("pokedex_number") == pokemon_id:
                return pokemon
        return None

    def get_all_pokemon(self) -> List[Dict]:
        """Get all Pokémon"""
        return self.pokemon_base

    def search_pokemon(self, query: str) -> List[Dict]:
        """Search Pokémon by Korean or English name"""
        query = query.lower()
        results = []
        for pokemon in self.pokemon_base:
            name_en = pokemon.get("name_en", "").lower()
            name_ko = pokemon.get("name_ko", "").lower()
            if query in name_en or query in name_ko:
                results.append(pokemon)
        return results

    def get_move_by_id(self, move_id: str) -> Optional[Dict]:
        """Get move data by move_id"""
        for move in self.moves:
            if move.get("move_id") == move_id:
                return move
        return None

    def get_pokemon_moves(self, pokemon_id: int) -> Dict[str, List[Dict]]:
        """Get all moves for a Pokémon"""
        fast_moves = []
        charged_moves = []

        for pm in self.pokemon_moves:
            if pm.get("pokemon_id") == pokemon_id:
                move_data = self.get_move_by_id(pm.get("move_id"))
                if move_data:
                    if pm.get("category") == "fast":
                        fast_moves.append(move_data)
                    elif pm.get("category") == "charged":
                        charged_moves.append(move_data)

        return {
            "fast": fast_moves,
            "charged": charged_moves
        }

    def get_current_season(self) -> Optional[str]:
        """Get current season_id based on today's date"""
        today = datetime.now().date()

        for tier in self.seasonal_tiers:
            start = datetime.fromisoformat(tier.get("start_date")).date()
            end = datetime.fromisoformat(tier.get("end_date")).date()
            if start <= today <= end:
                return tier.get("season_id")

        return None

    def get_seasonal_tier(self, pokemon_id: int, season_id: Optional[str] = None) -> Optional[Dict]:
        """Get seasonal tier info for a Pokémon"""
        if season_id is None:
            season_id = self.get_current_season()

        if season_id is None:
            return None

        for tier in self.seasonal_tiers:
            if tier.get("season_id") == season_id and tier.get("pokemon_id") == pokemon_id:
                return tier

        return None

    def get_raid_counters(self, boss_id: int, season_id: Optional[str] = None) -> Optional[Dict]:
        """Get raid counter teams for a boss"""
        if season_id is None:
            season_id = self.get_current_season()

        for counter in self.raid_counters:
            if counter.get("boss_pokemon_id") == boss_id:
                # Match season_id or use general counters (season_id = null)
                if counter.get("season_id") == season_id or counter.get("season_id") is None:
                    return counter

        return None

    def get_top_attackers(self, type_filter: Optional[str] = None, min_tier: str = "A") -> List[Dict]:
        """Get top raid attackers for current season"""
        season_id = self.get_current_season()
        if season_id is None:
            return []

        tier_order = {"S": 1, "A": 2, "B": 3, "C": 4, "NONE": 5}
        min_tier_value = tier_order.get(min_tier, 2)

        attackers = []
        for tier in self.seasonal_tiers:
            if tier.get("season_id") != season_id:
                continue

            raid_attack_tier = tier.get("raid_attack_tier", "NONE")
            tier_value = tier_order.get(raid_attack_tier, 5)

            if tier_value > min_tier_value:
                continue

            pokemon_id = tier.get("pokemon_id")
            pokemon = self.get_pokemon_by_id(pokemon_id)

            if pokemon is None:
                continue

            # Type filter
            if type_filter:
                if type_filter not in pokemon.get("types", []):
                    continue

            attackers.append({
                "pokemon": pokemon,
                "tier_info": tier
            })

        # Sort by tier (S > A > B)
        attackers.sort(key=lambda x: tier_order.get(x["tier_info"].get("raid_attack_tier", "NONE"), 5))

        return attackers

    def get_pvp_party_rankings(self, league: str = "Great", limit: int = 20) -> Optional[Dict]:
        """Get PvP party rankings for a specific league"""
        season_id = self.get_current_season()

        for ranking_data in self.pvp_party_rankings:
            if ranking_data.get("league") == league:
                # Check if it matches current season or is a general ranking
                if ranking_data.get("season_id") == season_id or ranking_data.get("season_id") is None:
                    rankings = ranking_data.get("rankings", [])
                    return {
                        "league": league,
                        "season_id": ranking_data.get("season_id"),
                        "rankings": rankings[:limit]
                    }

        return None

    def reload_data(self):
        """Reload all JSON data files"""
        self.load_all_data()


# Global instance
_data_loader = None


def get_data_loader() -> PokedexDataLoader:
    """Get global data loader instance"""
    global _data_loader
    if _data_loader is None:
        _data_loader = PokedexDataLoader()
    return _data_loader
