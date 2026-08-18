# analytics.py - Milestone 4: Analytics and Dashboard Endpoints
"""
Analytics module for Sports Injury Risk Detection Platform
Handles team analytics, performance trends, injury predictions, and risk assessments
"""

from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, avg, max, min
import statistics
import json

class AnalyticsService:
    """Service for computing analytics across athletes and videos"""
    
    @staticmethod
    def get_team_risk_overview(db: Session, coach_id: int = None):
        """Get team-wide risk assessment overview"""
        from models import BiomechanicalReport, VideoUpload, Athlete
        
        reports = db.query(BiomechanicalReport).all()
        
        if not reports:
            return {
                "total_athletes_analyzed": 0,
                "total_videos_analyzed": 0,
                "average_risk_score": 0,
                "high_risk_count": 0,
                "moderate_risk_count": 0,
                "low_risk_count": 0,
                "risk_distribution": {},
                "trend": "stable"
            }
        
        risk_scores = []
        risk_categories = {"Low Risk": 0, "Moderate Risk": 0, "High Risk": 0, "Critical Risk": 0}
        
        for report in reports:
            # Calculate risk score based on biomechanics
            risk_score = calculate_injury_risk_score(report)
            risk_scores.append(risk_score)
            
            category = report.risk_category or "Low Risk"
            if category in risk_categories:
                risk_categories[category] += 1
        
        avg_risk = statistics.mean(risk_scores) if risk_scores else 0
        high_risk_count = sum(1 for r in reports if r.risk_category == "High Risk")
        
        return {
            "total_athletes_analyzed": len(set(r.video.athlete_id for r in reports if r.video)),
            "total_videos_analyzed": len(reports),
            "average_risk_score": round(avg_risk, 2),
            "high_risk_count": high_risk_count,
            "moderate_risk_count": risk_categories.get("Moderate Risk", 0),
            "low_risk_count": risk_categories.get("Low Risk", 0),
            "risk_distribution": risk_categories,
            "trend": "increasing" if avg_risk > 65 else "stable" if avg_risk > 40 else "improving"
        }
    
    @staticmethod
    def get_athlete_performance_trends(db: Session, athlete_id: int, days: int = 30):
        """Get performance trends for a specific athlete over time"""
        from models import BiomechanicalReport, VideoUpload
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        reports = db.query(BiomechanicalReport).join(
            VideoUpload, BiomechanicalReport.video_id == VideoUpload.id
        ).filter(
            VideoUpload.athlete_id == athlete_id,
            BiomechanicalReport.created_at >= cutoff_date
        ).order_by(BiomechanicalReport.created_at).all()
        
        if not reports:
            return {
                "athlete_id": athlete_id,
                "days_analyzed": days,
                "data_points": [],
                "average_metrics": {},
                "trend_analysis": {}
            }
        
        trend_data = []
        symmetry_scores = []
        posture_scores = []
        movement_quality_scores = []
        
        for report in reports:
            symmetry_scores.append(report.symmetry_score or 0)
            posture_scores.append(report.posture_stability_score or 0)
            movement_quality_scores.append(report.movement_quality_score or 0)
            
            trend_data.append({
                "date": report.created_at.isoformat(),
                "symmetry_score": report.symmetry_score,
                "posture_score": report.posture_stability_score,
                "movement_quality": report.movement_quality_score,
                "risk_category": report.risk_category
            })
        
        # Calculate trends
        def calculate_trend(scores):
            if len(scores) < 2:
                return "stable"
            first_half_avg = statistics.mean(scores[:len(scores)//2])
            second_half_avg = statistics.mean(scores[len(scores)//2:])
            diff = second_half_avg - first_half_avg
            if diff > 5:
                return "improving"
            elif diff < -5:
                return "declining"
            return "stable"
        
        return {
            "athlete_id": athlete_id,
            "days_analyzed": days,
            "data_points": trend_data,
            "average_metrics": {
                "symmetry_score": round(statistics.mean(symmetry_scores), 2) if symmetry_scores else 0,
                "posture_score": round(statistics.mean(posture_scores), 2) if posture_scores else 0,
                "movement_quality": round(statistics.mean(movement_quality_scores), 2) if movement_quality_scores else 0
            },
            "trend_analysis": {
                "symmetry_trend": calculate_trend(symmetry_scores),
                "posture_trend": calculate_trend(posture_scores),
                "movement_quality_trend": calculate_trend(movement_quality_scores)
            }
        }
    
    @staticmethod
    def get_injury_risk_assessment(db: Session, athlete_id: int):
        """Comprehensive injury risk assessment for an athlete"""
        from models import BiomechanicalReport, VideoUpload, Athlete
        
        athlete = db.query(Athlete).filter(Athlete.id == athlete_id).first()
        if not athlete:
            return {"error": "Athlete not found"}
        
        reports = db.query(BiomechanicalReport).join(
            VideoUpload, BiomechanicalReport.video_id == VideoUpload.id
        ).filter(VideoUpload.athlete_id == athlete_id).all()
        
        if not reports:
            return {
                "athlete_id": athlete_id,
                "athlete_name": f"{athlete.first_name} {athlete.last_name}",
                "assessments": []
            }
        
        assessments = []
        high_risk_factors = []
        
        for report in reports:
            risk_score = calculate_injury_risk_score(report)
            
            # Check specific risk factors
            if (report.knee_valgus_risk_pct or 0) > 60:
                high_risk_factors.append(f"High knee valgus risk ({report.knee_valgus_risk_pct}%)")
            
            if (report.posture_stability_score or 0) < 40:
                high_risk_factors.append(f"Poor posture stability ({report.posture_stability_score})")
            
            if (report.symmetry_score or 0) < 50:
                high_risk_factors.append(f"Asymmetric movement pattern ({report.symmetry_score})")
            
            assessments.append({
                "report_id": report.id,
                "date": report.created_at.isoformat(),
                "risk_score": risk_score,
                "risk_category": report.risk_category,
                "primary_concerns": high_risk_factors[:3]  # Top 3 concerns
            })
        
        return {
            "athlete_id": athlete_id,
            "athlete_name": f"{athlete.first_name} {athlete.last_name}",
            "sport_type": athlete.sport_type,
            "position": athlete.position,
            "total_assessments": len(assessments),
            "assessments": assessments,
            "highest_risk_score": max(a["risk_score"] for a in assessments) if assessments else 0,
            "injury_history": athlete.injury_history or "None reported",
            "recommendations": generate_recommendations(high_risk_factors, athlete.sport_type)
        }
    
    @staticmethod
    def get_comparative_analysis(db: Session, sport_type: str = None):
        """Compare performance across athletes in same sport"""
        from models import BiomechanicalReport, VideoUpload, Athlete
        
        query = db.query(Athlete)
        if sport_type:
            query = query.filter(Athlete.sport_type == sport_type)
        
        athletes = query.all()
        
        comparative_data = []
        
        for athlete in athletes:
            reports = db.query(BiomechanicalReport).join(
                VideoUpload, BiomechanicalReport.video_id == VideoUpload.id
            ).filter(VideoUpload.athlete_id == athlete.id).all()
            
            if reports:
                avg_symmetry = statistics.mean([r.symmetry_score for r in reports if r.symmetry_score])
                avg_posture = statistics.mean([r.posture_stability_score for r in reports if r.posture_stability_score])
                avg_movement = statistics.mean([r.movement_quality_score for r in reports if r.movement_quality_score])
                
                comparative_data.append({
                    "athlete_id": athlete.id,
                    "athlete_name": f"{athlete.first_name} {athlete.last_name}",
                    "position": athlete.position,
                    "avg_symmetry_score": round(avg_symmetry, 2),
                    "avg_posture_score": round(avg_posture, 2),
                    "avg_movement_quality": round(avg_movement, 2),
                    "total_assessments": len(reports)
                })
        
        # Sort by average symmetry (better is higher)
        comparative_data.sort(key=lambda x: x["avg_symmetry_score"], reverse=True)
        
        return {
            "sport_type": sport_type or "All Sports",
            "total_athletes": len(comparative_data),
            "athletes": comparative_data
        }


def calculate_injury_risk_score(report) -> float:
    """
    Calculate overall injury risk score based on biomechanical report
    Uses weighted scoring model from spec: 0-100 scale
    """
    score = 0
    
    # Biomechanical Deviations (35%)
    posture_score = (100 - (report.posture_stability_score or 0)) if report.posture_stability_score else 50
    symmetry_score = (100 - (report.symmetry_score or 0)) if report.symmetry_score else 50
    biom_deviation = (posture_score + symmetry_score) / 2 * 0.35
    score += biom_deviation
    
    # Knee Valgus Risk (included in biomechanical)
    knee_risk = (report.knee_valgus_risk_pct or 0) * 0.15
    score += knee_risk
    
    # Movement Quality (20%)
    movement_quality_risk = (100 - (report.movement_quality_score or 0)) if report.movement_quality_score else 50
    score += movement_quality_risk * 0.20
    
    # Range of Motion deviation (15%)
    rom_score = (report.range_of_motion or 0) if report.range_of_motion else 50
    score += (100 - rom_score) * 0.15
    
    # Posture-related scores (15%)
    posture_risk = (100 - (report.posture_stability_score or 0)) if report.posture_stability_score else 50
    score += posture_risk * 0.15
    
    return min(100, max(0, score))


def generate_recommendations(risk_factors: List[str], sport_type: str) -> List[str]:
    """Generate recommendations based on risk factors and sport type"""
    recommendations = []
    
    if not risk_factors:
        recommendations.append("Continue current training regimen")
        recommendations.append("Maintain current fitness level")
        return recommendations
    
    risk_text = " ".join(risk_factors).lower()
    
    # Generic recommendations
    if "knee" in risk_text or "valgus" in risk_text:
        recommendations.append("Perform knee stability exercises (lateral band walks, step-ups)")
        recommendations.append("Strengthen hip abductors and external rotators")
        recommendations.append("Monitor running form and landing mechanics")
    
    if "posture" in risk_text or "stability" in risk_text:
        recommendations.append("Work with strength coach on core stability")
        recommendations.append("Perform planks, dead bugs, and bird dogs")
        recommendations.append("Consider physical therapy assessment")
    
    if "asymmetric" in risk_text or "symmetry" in risk_text:
        recommendations.append("Perform bilateral strength training exercises")
        recommendations.append("Include single-leg exercises to address imbalances")
        recommendations.append("Video analysis of movement patterns recommended")
    
    # Sport-specific recommendations
    if sport_type and sport_type.lower() in ["basketball", "soccer", "volleyball"]:
        if not recommendations or "landing" not in recommendations[0].lower():
            recommendations.insert(0, "Focus on proper landing mechanics")
    
    recommendations.append("Schedule follow-up biomechanical assessment in 1-2 weeks")
    recommendations.append("Consult with sports medicine physician")
    
    return recommendations[:5]  # Return top 5 recommendations


def generate_export_data(db: Session, report_id: int = None, athlete_id: int = None):
    """Generate data for PDF/Excel export"""
    from models import BiomechanicalReport, Athlete
    
    if report_id:
        report = db.query(BiomechanicalReport).filter(BiomechanicalReport.id == report_id).first()
        if not report:
            return None
        
        return {
            "type": "individual_report",
            "report_id": report.id,
            "athlete_id": report.video.athlete_id,
            "analysis_date": report.created_at.isoformat(),
            "metrics": {
                "symmetry_score": report.symmetry_score,
                "posture_stability": report.posture_stability_score,
                "movement_quality": report.movement_quality_score,
                "knee_valgus_risk": report.knee_valgus_risk_pct,
                "range_of_motion": report.range_of_motion,
                "risk_category": report.risk_category,
                "frames_analyzed": report.frames_analyzed
            },
            "risk_score": calculate_injury_risk_score(report)
        }
    
    elif athlete_id:
        athlete = db.query(Athlete).filter(Athlete.id == athlete_id).first()
        if not athlete:
            return None
        
        reports = db.query(BiomechanicalReport).join(
            BiomechanicalReport.video
        ).filter(BiomechanicalReport.video.has(athlete_id=athlete_id)).all()
        
        return {
            "type": "athlete_report",
            "athlete_id": athlete_id,
            "athlete_name": f"{athlete.first_name} {athlete.last_name}",
            "sport_type": athlete.sport_type,
            "position": athlete.position,
            "injury_history": athlete.injury_history,
            "total_assessments": len(reports),
            "reports": [generate_export_data(db, report_id=r.id) for r in reports],
            "assessment": AnalyticsService.get_injury_risk_assessment(db, athlete_id)
        }
    
    return None
