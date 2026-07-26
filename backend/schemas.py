from pydantic import BaseModel
from typing import Optional


# ---------------------------------------------------------
# User / Auth schemas
# ---------------------------------------------------------

class UserCreate(BaseModel):
    email: str
    password: str
    role: str  # athlete, coach, physiotherapist, sports_scientist, admin


class UserLogin(BaseModel):
    email: str
    password: str


# ---------------------------------------------------------
# Athlete schemas
# ---------------------------------------------------------

class AthleteCreate(BaseModel):
    sport_type: Optional[str] = None
    position: Optional[str] = None
    age: Optional[int] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    injury_history: Optional[str] = None
    training_load: Optional[str] = None

from typing import Optional, Dict
from datetime import datetime

class VideoUploadOut(BaseModel):
    id: int
    athlete_id: int
    filename: str
    status: str
    uploaded_at: datetime

    class Config:
        from_attributes = True

class BiomechanicalReportOut(BaseModel):
    id: int
    video_id: int
    frames_analyzed: int
    symmetry_score: float
    posture_stability_score: float
    knee_valgus_risk_pct: float
    movement_quality_score: float
    risk_category: str
    range_of_motion: Dict[str, float]
    created_at: datetime

    class Config:
        from_attributes = True