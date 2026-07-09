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