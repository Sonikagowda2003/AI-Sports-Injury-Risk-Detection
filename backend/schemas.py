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

from typing import Optional, Dict, List
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
    upper_body_symmetry_score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------
# Injury risk prediction / anomaly detection / recommendations (Milestone 3)
# ---------------------------------------------------------

class InjuryRiskAssessmentOut(BaseModel):
    id: int
    video_id: int
    athlete_id: int
    biomechanical_deviation_score: float
    historical_injury_factor_score: float
    movement_asymmetry_score: float
    training_load_score: float
    fatigue_indicator_score: float
    overall_risk_score: float
    risk_category: str
    category_risks: Dict[str, float]
    anomaly_detected: bool
    fatigue_trend: str
    performance_decline_detected: bool
    recommendations: Dict[str, List[str]]
    created_at: datetime

    class Config:
        from_attributes = True


class AnalyzeVideoResponse(BaseModel):
    report: BiomechanicalReportOut
    risk_assessment: InjuryRiskAssessmentOut


class RiskTrendPoint(BaseModel):
    video_id: int
    created_at: datetime
    overall_risk_score: float
    risk_category: str

    class Config:
        from_attributes = True