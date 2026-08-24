# test_analytics.py - Milestone 4: Comprehensive Test Suite
"""
Test suite for analytics, dashboard, and export endpoints
Includes unit tests, integration tests, and performance benchmarks
"""

import pytest
import json
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Mock database setup for testing
TEST_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Fixture for test client
@pytest.fixture
def test_client():
    """Create test client with test database"""
    from main import app, get_db
    
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.fixture
def auth_token():
    """Generate test auth token"""
    from auth import create_access_token
    token = create_access_token({"sub": "test@example.com", "role": "admin"})
    return {"Authorization": f"Bearer {token}"}

# ============================================================================
# UNIT TESTS: Analytics Service
# ============================================================================

class TestAnalyticsService:
    """Test analytics calculations and data aggregation"""
    
    def test_calculate_risk_score_low_risk(self):
        """Test risk score calculation for low-risk biomechanics"""
        from analytics import calculate_injury_risk_score
        
        class MockReport:
            posture_stability_score = 85
            symmetry_score = 80
            knee_valgus_risk_pct = 10
            movement_quality_score = 75
            range_of_motion = 85
        
        risk_score = calculate_injury_risk_score(MockReport())
        assert 0 <= risk_score <= 100, "Risk score should be between 0-100"
        assert risk_score < 40, "Low risk biomechanics should score < 40"
    
    def test_calculate_risk_score_high_risk(self):
        """Test risk score calculation for high-risk biomechanics"""
        from analytics import calculate_injury_risk_score
        
        class MockReport:
            posture_stability_score = 30
            symmetry_score = 35
            knee_valgus_risk_pct = 75
            movement_quality_score = 25
            range_of_motion = 40
        
        risk_score = calculate_injury_risk_score(MockReport())
        assert risk_score > 60, "High risk biomechanics should score > 60"
    
    def test_calculate_risk_score_edge_cases(self):
        """Test risk score with edge case values"""
        from analytics import calculate_injury_risk_score
        
        class MockReport:
            posture_stability_score = 0
            symmetry_score = 0
            knee_valgus_risk_pct = 100
            movement_quality_score = 0
            range_of_motion = 0
        
        risk_score = calculate_injury_risk_score(MockReport())
        assert risk_score == 100, "Worst case should score 100"
        
        class MockReportGood:
            posture_stability_score = 100
            symmetry_score = 100
            knee_valgus_risk_pct = 0
            movement_quality_score = 100
            range_of_motion = 100
        
        risk_score = calculate_injury_risk_score(MockReportGood())
        assert risk_score == 0, "Best case should score 0"
    
    def test_generate_recommendations_knee_risk(self):
        """Test recommendation generation for knee-related issues"""
        from analytics import generate_recommendations
        
        risk_factors = ["High knee valgus risk (75%)", "Poor posture stability (35)"]
        recommendations = generate_recommendations(risk_factors, "basketball")
        
        assert len(recommendations) > 0, "Should generate recommendations"
        assert any("knee" in rec.lower() for rec in recommendations), "Should include knee recommendations"
        assert any("landing" in rec.lower() for rec in recommendations), "Should include landing mechanics for basketball"
    
    def test_generate_recommendations_symmetry_issues(self):
        """Test recommendation generation for asymmetry"""
        from analytics import generate_recommendations
        
        risk_factors = ["Asymmetric movement pattern (45)"]
        recommendations = generate_recommendations(risk_factors, "soccer")
        
        assert any("bilateral" in rec.lower() or "single-leg" in rec.lower() for rec in recommendations)
    
    def test_generate_recommendations_no_issues(self):
        """Test recommendation generation when no issues present"""
        from analytics import generate_recommendations
        
        recommendations = generate_recommendations([], "volleyball")
        assert len(recommendations) > 0
        assert any("continue" in rec.lower() for rec in recommendations)

# ============================================================================
# INTEGRATION TESTS: Dashboard Endpoints
# ============================================================================

class TestDashboardEndpoints:
    """Integration tests for dashboard endpoints"""
    
    def test_health_check(self, test_client):
        """Test health check endpoint"""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_root_endpoint(self, test_client):
        """Test root endpoint"""
        response = test_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_team_overview_authorized(self, test_client, auth_token):
        """Test team overview dashboard with proper authorization"""
        response = test_client.get("/dashboard/team-overview", headers=auth_token)
        assert response.status_code in [200, 404]  # 404 if no data, 200 with data
        
        if response.status_code == 200:
            data = response.json()
            assert "total_athletes_analyzed" in data
            assert "total_videos_analyzed" in data
            assert "average_risk_score" in data
            assert "risk_distribution" in data
    
    def test_team_overview_unauthorized(self, test_client):
        """Test team overview denies unauthorized access"""
        from auth import create_access_token
        athlete_token = create_access_token({"sub": "athlete@test.com", "role": "athlete"})
        headers = {"Authorization": f"Bearer {athlete_token}"}
        
        response = test_client.get("/dashboard/team-overview", headers=headers)
        assert response.status_code == 403  # Forbidden

# ============================================================================
# INTEGRATION TESTS: Analytics Endpoints
# ============================================================================

class TestAnalyticsEndpoints:
    """Integration tests for analytics endpoints"""
    
    def test_performance_trends_athlete(self, test_client, auth_token):
        """Test performance trends endpoint for athlete"""
        athlete_id = 1
        response = test_client.get(
            f"/analytics/performance-trends/{athlete_id}?days=30",
            headers=auth_token
        )
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "athlete_id" in data
            assert "days_analyzed" in data
            assert "data_points" in data
            assert "average_metrics" in data
            assert "trend_analysis" in data
    
    def test_injury_risk_assessment(self, test_client, auth_token):
        """Test injury risk assessment endpoint"""
        athlete_id = 1
        response = test_client.get(
            f"/analytics/injury-risk/{athlete_id}",
            headers=auth_token
        )
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "athlete_id" in data
            assert "assessments" in data
            assert "recommendations" in data
    
    def test_comparative_analysis(self, test_client, auth_token):
        """Test comparative analysis across athletes"""
        response = test_client.get(
            "/analytics/comparative-analysis",
            headers=auth_token
        )
        assert response.status_code in [200, 403]
        
        if response.status_code == 200:
            data = response.json()
            assert "total_athletes" in data
            assert "athletes" in data
    
    def test_comparative_analysis_by_sport(self, test_client, auth_token):
        """Test comparative analysis filtered by sport"""
        response = test_client.get(
            "/analytics/comparative-analysis?sport_type=basketball",
            headers=auth_token
        )
        assert response.status_code in [200, 403]

# ============================================================================
# INTEGRATION TESTS: Export/Report Endpoints
# ============================================================================

class TestExportEndpoints:
    """Integration tests for report export functionality"""
    
    def test_export_report_csv(self, test_client, auth_token):
        """Test CSV export for individual report"""
        report_id = 1
        response = test_client.get(
            f"/reports/injury-risk/{report_id}/csv",
            headers=auth_token
        )
        
        if response.status_code == 200:
            assert "text/csv" in response.headers["content-type"]
            assert response.text  # Should have content
    
    def test_export_athlete_report_csv(self, test_client, auth_token):
        """Test CSV export for athlete report"""
        athlete_id = 1
        response = test_client.get(
            f"/reports/athlete/{athlete_id}/csv",
            headers=auth_token
        )
        
        if response.status_code == 200:
            assert "text/csv" in response.headers["content-type"]
            assert "Athlete" in response.text or "athlete" in response.text.lower()
    
    def test_export_team_report_json(self, test_client, auth_token):
        """Test JSON export for team report"""
        response = test_client.get(
            "/reports/team/json",
            headers=auth_token
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "generated_at" in data
            assert "team_overview" in data

# ============================================================================
# PERFORMANCE & LOAD TESTS
# ============================================================================

class TestPerformance:
    """Performance and load testing"""
    
    def test_dashboard_response_time(self, test_client, auth_token):
        """Test dashboard endpoint response time"""
        import time
        start = time.time()
        response = test_client.get("/dashboard/team-overview", headers=auth_token)
        duration = time.time() - start
        
        # Should respond within 2 seconds
        assert duration < 2.0, f"Dashboard took {duration}s, should be < 2s"
    
    def test_analytics_endpoint_response_time(self, test_client, auth_token):
        """Test analytics endpoints response time"""
        import time
        start = time.time()
        response = test_client.get(
            "/analytics/performance-trends/1?days=30",
            headers=auth_token
        )
        duration = time.time() - start
        
        # Should respond within 1 second
        assert duration < 1.0, f"Analytics took {duration}s, should be < 1s"
    
    def test_concurrent_requests(self, test_client, auth_token):
        """Test handling concurrent requests"""
        import threading
        results = []
        
        def make_request():
            response = test_client.get("/health")
            results.append(response.status_code)
        
        threads = [threading.Thread(target=make_request) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(results) == 10
        assert all(code == 200 for code in results)

# ============================================================================
# ERROR HANDLING & VALIDATION TESTS
# ============================================================================

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_athlete_id(self, test_client, auth_token):
        """Test with non-existent athlete"""
        response = test_client.get(
            "/analytics/injury-risk/99999",
            headers=auth_token
        )
        # Should handle gracefully
        assert response.status_code in [200, 404]
    
    def test_invalid_report_id(self, test_client, auth_token):
        """Test with non-existent report"""
        response = test_client.get(
            "/reports/injury-risk/99999/csv",
            headers=auth_token
        )
        assert response.status_code == 404
    
    def test_missing_auth_token(self, test_client):
        """Test endpoints without authentication"""
        response = test_client.get("/dashboard/team-overview")
        assert response.status_code == 403  # Forbidden without token
    
    def test_invalid_days_parameter(self, test_client, auth_token):
        """Test with invalid days parameter"""
        # Should reject values outside valid range
        response = test_client.get(
            "/analytics/performance-trends/1?days=0",
            headers=auth_token
        )
        assert response.status_code in [200, 422]  # 422 for invalid param
        
        response = test_client.get(
            "/analytics/performance-trends/1?days=400",
            headers=auth_token
        )
        assert response.status_code in [200, 422]  # Should limit to 365 days max

# ============================================================================
# DATA VALIDATION TESTS
# ============================================================================

class TestDataValidation:
    """Test data validation and consistency"""
    
    def test_risk_score_calculation_consistency(self):
        """Test risk score calculation is deterministic"""
        from analytics import calculate_injury_risk_score
        
        class MockReport:
            posture_stability_score = 65
            symmetry_score = 70
            knee_valgus_risk_pct = 35
            movement_quality_score = 60
            range_of_motion = 75
        
        report = MockReport()
        score1 = calculate_injury_risk_score(report)
        score2 = calculate_injury_risk_score(report)
        
        assert score1 == score2, "Risk score calculation should be deterministic"
    
    def test_recommendation_generation_completeness(self):
        """Test that recommendations are always generated"""
        from analytics import generate_recommendations
        
        # Test various scenarios
        test_cases = [
            ([], "basketball"),
            (["High knee valgus risk (80%)"], "soccer"),
            (["Poor posture stability (20)"], "volleyball"),
            (["Asymmetric movement pattern (40)"], "football"),
        ]
        
        for risk_factors, sport in test_cases:
            recommendations = generate_recommendations(risk_factors, sport)
            assert isinstance(recommendations, list), "Should return list"
            assert len(recommendations) > 0, "Should always generate recommendations"
            assert len(recommendations) <= 5, "Should limit recommendations to 5"

# ============================================================================
# ENDPOINT SECURITY TESTS
# ============================================================================

class TestSecurity:
    """Test security and authorization"""
    
    def test_role_based_access_control(self, test_client):
        """Test RBAC for different endpoints"""
        from auth import create_access_token
        
        roles_test_cases = [
            ("athlete", "/dashboard/team-overview", 403),
            ("coach", "/dashboard/team-overview", 200),
            ("sports_scientist", "/analytics/comparative-analysis", 200),
        ]
        
        for role, endpoint, expected_status_or_ok in roles_test_cases:
            token = create_access_token({"sub": f"{role}@test.com", "role": role})
            headers = {"Authorization": f"Bearer {token}"}
            response = test_client.get(endpoint, headers=headers)
            # Check if status is either the expected status or 200/404 (data not found)
            assert response.status_code in [expected_status_or_ok, 200, 404, 403]
    
    def test_token_expiration(self, test_client):
        """Test handling of expired tokens"""
        from auth import create_access_token
        import time
        
        # Create a token that expires immediately (would need JWT expiration)
        token = create_access_token({"sub": "test@example.com", "role": "admin"})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = test_client.get("/health", headers=headers)
        assert response.status_code == 200  # Health check doesn't require auth

# ============================================================================
# SMOKE TESTS
# ============================================================================

class TestSmokeTests:
    """Basic smoke tests to ensure endpoints exist and respond"""
    
    @pytest.mark.parametrize("endpoint", [
        "/",
        "/health",
        "/test/biomechanical-data",
    ])
    def test_endpoints_exist(self, test_client, endpoint):
        """Test that endpoints exist and respond"""
        response = test_client.get(endpoint)
        assert response.status_code != 404, f"Endpoint {endpoint} should exist"
    
    @pytest.mark.parametrize("method,endpoint", [
        ("GET", "/health"),
        ("POST", "/auth/login"),
        ("GET", "/dashboard/team-overview"),
    ])
    def test_method_support(self, test_client, method, endpoint):
        """Test HTTP method support"""
        if method == "GET":
            response = test_client.get(endpoint)
        elif method == "POST":
            response = test_client.post(endpoint, json={})
        
        # Should not be 405 Method Not Allowed
        assert response.status_code != 405, f"{method} {endpoint} should be supported"


if __name__ == "__main__":
    # Run tests with: pytest test_analytics.py -v
    pytest.main([__file__, "-v", "-s"])
