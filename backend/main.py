from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from analytics import AnalyticsService

import models
import schemas
import auth
from database import engine, get_db, Base
import os
import shutil
from fastapi import UploadFile, File
import pose_estimation
import biomechanics
import injury_prediction
import anomaly_detection
import recommendations
from typing import List

# Creates all tables in the database if they don't already exist
Base.metadata.create_all(bind=engine)



app = FastAPI(title="Sports Injury Risk Detection API")
UPLOAD_DIR = "uploaded_videos"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Root
# ---------------------------------------------------------

@app.get("/")
def root():
    return {"message": "API is running"}


# ---------------------------------------------------------
# Auth endpoints
# ---------------------------------------------------------

@app.post("/auth/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = auth.hash_password(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_pw, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully", "email": new_user.email, "role": new_user.role}


@app.post("/auth/login")
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == credentials.email).first()
    if not user or not auth.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = auth.create_access_token({"sub": user.email, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}


# ---------------------------------------------------------
# Athlete endpoints (CRUD)
# ---------------------------------------------------------

@app.post("/athletes")
def create_athlete(
    athlete: schemas.AthleteCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_user),
):
    if current_user["role"] not in ["athlete", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    user = db.query(models.User).filter(models.User.email == current_user["email"]).first()
    new_profile = models.Athlete(user_id=user.id, **athlete.dict())
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return new_profile


@app.get("/athletes")
def list_athletes(
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_user),
):
    if current_user["role"] == "athlete":
        user = db.query(models.User).filter(models.User.email == current_user["email"]).first()
        return db.query(models.Athlete).filter(models.Athlete.user_id == user.id).all()
    return db.query(models.Athlete).all()


@app.get("/athletes/{athlete_id}")
def get_athlete(
    athlete_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_user),
):
    profile = db.query(models.Athlete).filter(models.Athlete.id == athlete_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Athlete not found")
    return profile


@app.put("/athletes/{athlete_id}")
def update_athlete(
    athlete_id: int,
    athlete: schemas.AthleteCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_user),
):
    profile = db.query(models.Athlete).filter(models.Athlete.id == athlete_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Athlete not found")
    for key, value in athlete.dict().items():
        setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return profile


@app.delete("/athletes/{athlete_id}")
def delete_athlete(
    athlete_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_user),
):
    profile = db.query(models.Athlete).filter(models.Athlete.id == athlete_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Athlete not found")

    db.delete(profile)
    db.commit()
    return {"message": "Deleted"}

# ---------------------------------------------------------
# Video upload & pose/biomechanics analysis (Milestone 2)
# ---------------------------------------------------------

@app.post("/athletes/{athlete_id}/videos")
def upload_video(
    athlete_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_user),
):
    athlete = db.query(models.Athlete).filter(models.Athlete.id == athlete_id).first()
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")

    file_path = os.path.join(UPLOAD_DIR, f"athlete{athlete_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    video = models.VideoUpload(
        athlete_id=athlete_id,
        filename=file.filename,
        file_path=file_path,
        status="uploaded",
    )
    db.add(video)
    db.commit()
    db.refresh(video)
    return video


@app.post("/videos/{video_id}/analyze", response_model=schemas.AnalyzeVideoResponse)
def analyze_video(
    video_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_user),
):
    video = db.query(models.VideoUpload).filter(models.VideoUpload.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    video.status = "analyzing"
    db.commit()

    try:
        frames_data = pose_estimation.extract_pose_from_video(video.file_path)
        results = biomechanics.analyze_sequence(frames_data)

        if "error" in results:
            video.status = "failed"
            db.commit()
            raise HTTPException(status_code=422, detail=results["error"])

        report = models.BiomechanicalReport(
            video_id=video.id,
            frames_analyzed=results["frames_analyzed"],
            symmetry_score=results["symmetry_score"],
            posture_stability_score=results["posture_stability_score"],
            knee_valgus_risk_pct=results["knee_valgus_risk_pct"],
            movement_quality_score=results["movement_quality_score"],
            risk_category=results["risk_category"],
            range_of_motion=results["range_of_motion"],
            upper_body_symmetry_score=results["upper_body_symmetry_score"],
        )
        db.add(report)
        db.commit()
        db.refresh(report)

        # ---- Milestone 3: injury prediction, anomaly detection, recommendations ----
        athlete = db.query(models.Athlete).filter(models.Athlete.id == video.athlete_id).first()

        previous_reports = (
            db.query(models.BiomechanicalReport)
            .join(models.VideoUpload, models.BiomechanicalReport.video_id == models.VideoUpload.id)
            .filter(
                models.VideoUpload.athlete_id == video.athlete_id,
                models.BiomechanicalReport.id != report.id,
            )
            .order_by(models.BiomechanicalReport.created_at.asc())
            .all()
        )

        anomaly_result = anomaly_detection.detect_anomalies(results, previous_reports)
        risk_result = injury_prediction.predict_injury_risk(
            results, athlete, anomaly_result["fatigue_score"]
        )
        rec_result = recommendations.generate_recommendations(risk_result, anomaly_result)

        assessment = models.InjuryRiskAssessment(
            video_id=video.id,
            athlete_id=video.athlete_id,
            biomechanical_deviation_score=risk_result["biomechanical_deviation_score"],
            historical_injury_factor_score=risk_result["historical_injury_factor_score"],
            movement_asymmetry_score=risk_result["movement_asymmetry_score"],
            training_load_score=risk_result["training_load_score"],
            fatigue_indicator_score=risk_result["fatigue_indicator_score"],
            overall_risk_score=risk_result["overall_risk_score"],
            risk_category=risk_result["risk_category"],
            category_risks=risk_result["category_risks"],
            anomaly_detected=anomaly_result["anomaly_detected"],
            fatigue_trend=anomaly_result["fatigue_trend"],
            performance_decline_detected=anomaly_result["performance_decline_detected"],
            recommendations=rec_result,
        )
        db.add(assessment)

        video.status = "completed"
        db.commit()
        db.refresh(assessment)

        return {"report": report, "risk_assessment": assessment}

    except HTTPException:
        raise
    except Exception as e:
        video.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/videos/{video_id}/report", response_model=schemas.BiomechanicalReportOut)
def get_report(
    video_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_user),
):
    report = db.query(models.BiomechanicalReport).filter(
        models.BiomechanicalReport.video_id == video_id
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found for this video")
    return report


@app.get("/videos/{video_id}/risk-assessment", response_model=schemas.InjuryRiskAssessmentOut)
def get_risk_assessment(
    video_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_user),
):
    assessment = db.query(models.InjuryRiskAssessment).filter(
        models.InjuryRiskAssessment.video_id == video_id
    ).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Risk assessment not found for this video")
    return assessment


@app.get("/athletes/{athlete_id}/risk-trend", response_model=List[schemas.RiskTrendPoint])
def get_risk_trend(
    athlete_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_user),
):
    """Chronological overall_risk_score history, for the athlete risk-trend chart."""
    return (
        db.query(models.InjuryRiskAssessment)
        .filter(models.InjuryRiskAssessment.athlete_id == athlete_id)
        .order_by(models.InjuryRiskAssessment.created_at.asc())
        .all()
    )


@app.get("/athletes/{athlete_id}/videos")
def list_videos(
    athlete_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_user),
):
    return db.query(models.VideoUpload).filter(models.VideoUpload.athlete_id == athlete_id).all()