from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from app.services.pokedex_data_loader import get_data_loader

router = APIRouter(prefix="/api/pvp", tags=["PvP"])


class PvPTeamMember(BaseModel):
    pokemon_id: int
    pokemon_name_ko: str
    pokemon_name_en: str
    pokemon_image_url: str
    fast_move_id: str
    fast_move_name_ko: str
    charged_move_id: str
    charged_move_name_ko: str


class PvPPartyRanking(BaseModel):
    rank: int
    team: List[PvPTeamMember]
    estimated_rating: int
    notes_ko: str


class PvPPartyRankingsResponse(BaseModel):
    league: str
    league_name_ko: str
    season_id: str
    rankings: List[PvPPartyRanking]


@router.get("/party-rankings", response_model=PvPPartyRankingsResponse)
async def get_pvp_party_rankings(
    league: str = Query("Great", description="League: Great, Ultra, or Master"),
    limit: int = Query(20, ge=1, le=50, description="Number of rankings to return")
):
    """
    Get PvP party rankings for a specific league

    - **league**: Great (슈퍼리그), Ultra (하이퍼리그), or Master (마스터리그)
    - **limit**: Number of top teams to return (default: 20)

    Returns ranked party compositions with:
    - Team members (3 Pokémon)
    - Recommended moves (Korean names)
    - Estimated rating
    - Strategy notes in Korean
    """
    loader = get_data_loader()

    # Validate league
    valid_leagues = ["Great", "Ultra", "Master"]
    if league not in valid_leagues:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid league. Must be one of: {', '.join(valid_leagues)}"
        )

    ranking_data = loader.get_pvp_party_rankings(league=league, limit=limit)

    if not ranking_data:
        raise HTTPException(
            status_code=404,
            detail=f"No party rankings found for {league} League"
        )

    # League name mapping
    league_names = {
        "Great": "슈퍼리그",
        "Ultra": "하이퍼리그",
        "Master": "마스터리그"
    }

    # Build response
    rankings = []
    for ranking in ranking_data["rankings"]:
        team_members = []
        for member in ranking["team"]:
            pokemon_id = member["pokemon_id"]
            pokemon = loader.get_pokemon_by_id(pokemon_id)

            if not pokemon:
                continue

            # Get move names
            fast_move = loader.get_move_by_id(member["fast_move_id"])
            charged_move = loader.get_move_by_id(member["charged_move_id"])

            team_members.append(PvPTeamMember(
                pokemon_id=pokemon_id,
                pokemon_name_ko=pokemon["name_ko"],
                pokemon_name_en=pokemon["name_en"],
                pokemon_image_url=pokemon["image_url"],
                fast_move_id=member["fast_move_id"],
                fast_move_name_ko=fast_move["name_ko"] if fast_move else "",
                charged_move_id=member["charged_move_id"],
                charged_move_name_ko=charged_move["name_ko"] if charged_move else ""
            ))

        rankings.append(PvPPartyRanking(
            rank=ranking["rank"],
            team=team_members,
            estimated_rating=ranking["estimated_rating"],
            notes_ko=ranking["notes_ko"]
        ))

    return PvPPartyRankingsResponse(
        league=league,
        league_name_ko=league_names[league],
        season_id=ranking_data.get("season_id", "unknown"),
        rankings=rankings
    )
