from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import Optional, List, Optional
import os
import uuid
from datetime import datetime

from app.core.database import get_db
from app.models.pokemon_analysis import PokemonAnalysis
from app.services.iv_calculator import iv_calculator
from pydantic import BaseModel

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

# Directory to store uploaded images
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class AnalysisResponse(BaseModel):
    id: int
    pokemon_name: Optional[str]
    cp: Optional[int]
    hp: Optional[int]
    level: Optional[float]
    iv_percentage: Optional[float]
    attack_iv: Optional[int]
    defense_iv: Optional[int]
    stamina_iv: Optional[int]
    battle_rating: Optional[str]
    raid_rating: Optional[str]
    recommendations: Optional[dict]
    analyzed_at: datetime

    class Config:
        from_attributes = True


@router.post("/upload", response_model=AnalysisResponse)
async def upload_screenshot(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload Pokemon screenshot and analyze IV
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        # Save uploaded file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Analyze the image
        analysis_result = iv_calculator.analyze_screenshot(file_path)

        # Save to database
        db_analysis = PokemonAnalysis(
            pokemon_name=analysis_result['pokemon_name'],
            cp=analysis_result['cp'],
            hp=analysis_result['hp'],
            level=analysis_result['level'],
            iv_percentage=analysis_result['iv_percentage'],
            attack_iv=analysis_result['attack_iv'],
            defense_iv=analysis_result['defense_iv'],
            stamina_iv=analysis_result['stamina_iv'],
            battle_rating=analysis_result['battle_rating'],
            raid_rating=analysis_result['raid_rating'],
            recommendations=analysis_result['recommendations'],
            image_filename=unique_filename
        )

        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)

        return db_analysis

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/history", response_model=List[AnalysisResponse])
async def get_analysis_history(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get analysis history"""
    analyses = (
        db.query(PokemonAnalysis)
        .order_by(PokemonAnalysis.analyzed_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return analyses


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """Get specific analysis by ID"""
    analysis = db.query(PokemonAnalysis).filter(PokemonAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis
