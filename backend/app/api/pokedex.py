from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.schemas.pokedex import (
    PokemonListItem, PokemonDetail, MoveResponse,
    EvolutionInfo, RaidPerfectCP, CurrentSeasonInfo
)
from app.services.pokedex_data_loader import get_data_loader
from app.utils.cp_calculator import calculate_raid_perfect_cp

router = APIRouter(prefix="/api/pokedex", tags=["Pokédex"])


@router.get("", response_model=List[PokemonListItem])
async def list_pokemon(
    search: Optional[str] = Query(None, description="Search by Korean or English name"),
    region: Optional[str] = Query(None, description="Filter by region (kanto, johto, hoenn, sinnoh, unova, kalos, alola, galar, paldea)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(2000, ge=1, le=2000)
):
    """
    Get list of all Pokémon or search by name

    - **search**: Search query (Korean or English name)
    - **region**: Filter by region
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    loader = get_data_loader()

    if search:
        pokemon_list = loader.search_pokemon(search)
    else:
        pokemon_list = loader.get_all_pokemon()

    # Filter by region
    if region:
        region_ranges = {
            "kanto": (1, 151),
            "johto": (152, 251),
            "hoenn": (252, 386),
            "sinnoh": (387, 493),
            "unova": (494, 649),
            "kalos": (650, 721),
            "alola": (722, 809),
            "galar": (810, 905),
            "paldea": (906, 1025)
        }
        if region.lower() in region_ranges:
            start, end = region_ranges[region.lower()]
            pokemon_list = [p for p in pokemon_list if start <= p["pokedex_number"] <= end]

    # Pagination
    pokemon_list = pokemon_list[skip:skip + limit]

    # Convert to response format
    result = []
    for pokemon in pokemon_list:
        result.append(PokemonListItem(
            id=pokemon["pokedex_number"],
            pokedex_number=pokemon["pokedex_number"],
            name_en=pokemon["name_en"],
            name_ko=pokemon["name_ko"],
            types=pokemon["types"],
            image_url=pokemon["image_url"],
            can_dynamax=pokemon.get("can_dynamax", False),
            can_gigantamax=pokemon.get("can_gigantamax", False)
        ))

    return result


@router.get("/{pokemon_id}", response_model=PokemonDetail)
async def get_pokemon_detail(pokemon_id: int):
    """
    Get detailed information about a specific Pokémon

    - **pokemon_id**: Pokédex number

    Returns:
    - Basic stats (attack, defense, stamina)
    - Types
    - Moves (fast and charged, with Korean names)
    - Evolution line
    - Raid perfect IV CP (level 20 and 25)
    - Current season tier information
    """
    loader = get_data_loader()

    pokemon = loader.get_pokemon_by_id(pokemon_id)
    if not pokemon:
        raise HTTPException(status_code=404, detail=f"Pokémon {pokemon_id} not found")

    # Get moves
    moves_data = loader.get_pokemon_moves(pokemon_id)
    fast_moves = [MoveResponse(**move) for move in moves_data["fast"]]
    charged_moves = [MoveResponse(**move) for move in moves_data["charged"]]

    # Calculate raid perfect CP
    raid_cp = calculate_raid_perfect_cp(
        pokemon["base_attack"],
        pokemon["base_defense"],
        pokemon["base_stamina"]
    )

    # Get current season tier
    tier_data = loader.get_seasonal_tier(pokemon_id)
    current_season = None
    if tier_data:
        current_season = CurrentSeasonInfo(
            season_id=tier_data["season_id"],
            season_name_ko=tier_data["season_name_ko"],
            raid_tier=tier_data["raid_tier"],
            raid_attack_tier=tier_data.get("raid_attack_tier"),
            gbl_great_tier=tier_data["gbl_great_tier"],
            gbl_ultra_tier=tier_data["gbl_ultra_tier"],
            gbl_master_tier=tier_data["gbl_master_tier"],
            raid_role_ko=tier_data.get("raid_role_ko")
        )

    # Get raid counters
    raid_counters = loader.get_raid_counters(pokemon_id)

    # Parse evolutions
    evolutions = []
    if pokemon.get("evolutions"):
        for evo in pokemon["evolutions"]:
            evolutions.append(EvolutionInfo(**evo))

    return PokemonDetail(
        id=pokemon["pokedex_number"],
        pokedex_number=pokemon["pokedex_number"],
        name_en=pokemon["name_en"],
        name_ko=pokemon["name_ko"],
        types=pokemon["types"],
        base_attack=pokemon["base_attack"],
        base_defense=pokemon["base_defense"],
        base_stamina=pokemon["base_stamina"],
        image_url=pokemon["image_url"],
        sprite_url=pokemon.get("sprite_url"),
        can_dynamax=pokemon.get("can_dynamax", False),
        can_gigantamax=pokemon.get("can_gigantamax", False),
        evolutions=evolutions if evolutions else None,
        moves_fast=fast_moves,
        moves_charged=charged_moves,
        raid_perfect_cp=RaidPerfectCP(**raid_cp),
        current_season=current_season,
        raid_counters=raid_counters
    )
