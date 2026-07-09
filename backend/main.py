from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

import models
import schemas
import auth
from database import engine, get_db, Base

# Creates all tables in the database if they don't already exist
Base.metadata.create_all(bind=engine)



app = FastAPI(title="Sports Injury Risk Detection API")
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