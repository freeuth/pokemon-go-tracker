from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.schemas.pokedex import (
    RaidCountersResponse, RaidTeam, TeamMember,
    TopAttackersResponse, TopAttacker, MoveResponse
)
from app.services.pokedex_data_loader import get_data_loader

router = APIRouter(prefix="/api/raids", tags=["Raids"])


@router.get("/{boss_id}/counters", response_model=RaidCountersResponse)
async def get_raid_counters(boss_id: int):
    """
    Get recommended counter teams for a raid boss

    - **boss_id**: Pokédex number of the raid boss

    Returns:
    - Boss information (name, types, image)
    - Recommended teams with Pokémon and move combinations
    - All names and moves in Korean
    """
    loader = get_data_loader()

    # Get boss Pokémon
    boss = loader.get_pokemon_by_id(boss_id)
    if not boss:
        raise HTTPException(status_code=404, detail=f"Boss Pokémon {boss_id} not found")

    # Get counter data
    counter_data = loader.get_raid_counters(boss_id)
    if not counter_data:
        raise HTTPException(
            status_code=404,
            detail=f"No counter teams found for boss {boss_id}"
        )

    # Build teams
    teams = []
    for team_data in counter_data.get("recommended_teams", []):
        members = []
        for member_data in team_data.get("members", []):
            pokemon_id = member_data["pokemon_id"]
            pokemon = loader.get_pokemon_by_id(pokemon_id)

            if pokemon:
                # Get move names
                fast_move = loader.get_move_by_id(member_data["fast_move_id"])
                charged_move = loader.get_move_by_id(member_data["charged_move_id"])

                members.append(TeamMember(
                    pokemon_id=pokemon_id,
                    pokemon_name_ko=pokemon["name_ko"],
                    pokemon_image_url=pokemon["image_url"],
                    fast_move_id=member_data["fast_move_id"],
                    fast_move_name_ko=fast_move["name_ko"] if fast_move else "",
                    charged_move_id=member_data["charged_move_id"],
                    charged_move_name_ko=charged_move["name_ko"] if charged_move else "",
                    role_ko=member_data["role_ko"]
                ))

        teams.append(RaidTeam(
            name_ko=team_data["name_ko"],
            description_ko=team_data.get("description_ko"),
            members=members
        ))

    return RaidCountersResponse(
        boss_id=boss_id,
        boss_name_ko=boss["name_ko"],
        boss_name_en=boss["name_en"],
        boss_types=boss["types"],
        boss_image_url=boss["image_url"],
        recommended_teams=teams
    )


@router.get("/top-attackers", response_model=TopAttackersResponse)
async def get_top_raid_attackers(
    type: Optional[str] = Query(None, description="Filter by type (e.g., Dragon, Fire)"),
    min_tier: str = Query("A", description="Minimum tier (S or A)")
):
    """
    Get top raid attackers for the current season

    - **type**: Optional type filter (Dragon, Fire, Water, etc.)
    - **min_tier**: Minimum tier to include (default: A, shows S and A tier)

    Returns S~A tier raid attackers with recommended move sets
    """
    loader = get_data_loader()

    attackers_data = loader.get_top_attackers(type_filter=type, min_tier=min_tier)

    if not attackers_data:
        raise HTTPException(
            status_code=404,
            detail="No top attackers found for current season"
        )

    # Get season info
    season_id = loader.get_current_season()
    season_name_ko = "현재 시즌"
    if attackers_data and attackers_data[0]["tier_info"]:
        season_name_ko = attackers_data[0]["tier_info"].get("season_name_ko", "현재 시즌")

    # Build response
    attackers = []
    for attacker_data in attackers_data:
        pokemon = attacker_data["pokemon"]
        tier_info = attacker_data["tier_info"]

        # Get recommended moves
        moves_data = loader.get_pokemon_moves(pokemon["pokedex_number"])
        fast_moves = [MoveResponse(**move) for move in moves_data["fast"][:3]]  # Top 3
        charged_moves = [MoveResponse(**move) for move in moves_data["charged"][:3]]  # Top 3

        attackers.append(TopAttacker(
            pokemon_id=pokemon["pokedex_number"],
            pokedex_number=pokemon["pokedex_number"],
            name_ko=pokemon["name_ko"],
            name_en=pokemon["name_en"],
            types=pokemon["types"],
            image_url=pokemon["image_url"],
            raid_attack_tier=tier_info.get("raid_attack_tier", "A"),
            recommended_fast_moves=fast_moves,
            recommended_charged_moves=charged_moves
        ))

    return TopAttackersResponse(
        season_id=season_id or "unknown",
        season_name_ko=season_name_ko,
        type_filter=type,
        attackers=attackers
    )
