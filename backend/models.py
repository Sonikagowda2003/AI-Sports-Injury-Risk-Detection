from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func
from database import Base



class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # athlete, coach, physiotherapist, sports_scientist, admin

class Athlete(Base):
    __tablename__ = "athletes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    sport_type = Column(String)
    position = Column(String)
    age = Column(Integer)
    height_cm = Column(Float)
    weight_kg = Column(Float)
    injury_history = Column(String, nullable=True)
    training_load = Column(String, nullable=True)

class VideoUpload(Base):
    __tablename__ = "video_uploads"
    id = Column(Integer, primary_key=True, index=True)
    athlete_id = Column(Integer, ForeignKey("athletes.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="uploaded")  # uploaded, analyzing, completed, failed

class BiomechanicalReport(Base):
    __tablename__ = "biomechanical_reports"
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("video_uploads.id", ondelete="CASCADE"), nullable=False)
    frames_analyzed = Column(Integer)
    symmetry_score = Column(Float)
    posture_stability_score = Column(Float)
    knee_valgus_risk_pct = Column(Float)
    movement_quality_score = Column(Float)
    risk_category = Column(String)
    range_of_motion = Column(JSON)
    upper_body_symmetry_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class InjuryRiskAssessment(Base):
    """
    Milestone 3: combines the biomechanics report with athlete history,
    training load, and a fatigue/anomaly signal into a weighted injury
    risk score, per-category breakdown, and corrective recommendations.
    """
    __tablename__ = "injury_risk_assessments"
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("video_uploads.id", ondelete="CASCADE"), nullable=False)
    athlete_id = Column(Integer, ForeignKey("athletes.id", ondelete="CASCADE"), nullable=False)

    biomechanical_deviation_score = Column(Float)
    historical_injury_factor_score = Column(Float)
    movement_asymmetry_score = Column(Float)
    training_load_score = Column(Float)
    fatigue_indicator_score = Column(Float)

    overall_risk_score = Column(Float)
    risk_category = Column(String)
    category_risks = Column(JSON)  # {"ACL Injury Risk": 42.3, ...}

    anomaly_detected = Column(Boolean, default=False)
    fatigue_trend = Column(String)  # improving | stable | declining | insufficient_data
    performance_decline_detected = Column(Boolean, default=False)

    recommendations = Column(JSON)  # {"exercise_recommendations": [...], ...}
    created_at = Column(DateTime(timezone=True), server_default=func.now())