# performance_test.py - Milestone 4: Load Testing with Locust
"""
Load testing script for performance benchmarking
Tests various endpoints under different load conditions
Run with: locust -f performance_test.py --host=http://localhost:8000
"""

from locust import HttpUser, TaskSet, task, between, events
import random
from datetime import datetime
import json

class AnalyticsTaskSet(TaskSet):
    """Task set for analytics endpoint testing"""
    
    @task(5)
    def health_check(self):
        """Health check endpoint"""
        self.client.get("/health")
    
    @task(4)
    def get_team_overview(self):
        """Load team overview dashboard"""
        self.client.get(
            "/dashboard/team-overview",
            headers={"Authorization": f"Bearer {self.user.token}"}
        )
    
    @task(3)
    def get_athlete_dashboard(self):
        """Load athlete dashboard"""
        athlete_id = random.randint(1, 50)
        self.client.get(
            f"/dashboard/athlete/{athlete_id}",
            headers={"Authorization": f"Bearer {self.user.token}"}
        )
    
    @task(3)
    def get_performance_trends(self):
        """Get performance trends"""
        athlete_id = random.randint(1, 50)
        days = random.choice([7, 14, 30, 60])
        self.client.get(
            f"/analytics/performance-trends/{athlete_id}?days={days}",
            headers={"Authorization": f"Bearer {self.user.token}"}
        )
    
    @task(2)
    def get_injury_risk(self):
        """Get injury risk assessment"""
        athlete_id = random.randint(1, 50)
        self.client.get(
            f"/analytics/injury-risk/{athlete_id}",
            headers={"Authorization": f"Bearer {self.user.token}"}
        )
    
    @task(2)
    def get_comparative_analysis(self):
        """Get comparative analysis"""
        sport = random.choice(["basketball", "soccer", "volleyball", None])
        params = f"?sport_type={sport}" if sport else ""
        self.client.get(
            f"/analytics/comparative-analysis{params}",
            headers={"Authorization": f"Bearer {self.user.token}"}
        )
    
    @task(1)
    def export_team_report(self):
        """Export team report"""
        self.client.get(
            "/reports/team/json",
            headers={"Authorization": f"Bearer {self.user.token}"}
        )
    
    @task(1)
    def get_athlete_list(self):
        """Get athletes list"""
        sport = random.choice(["basketball", "soccer", "volleyball", None])
        params = f"?sport_type={sport}" if sport else ""
        self.client.get(
            f"/athletes{params}",
            headers={"Authorization": f"Bearer {self.user.token}"}
        )


class AnalyticsUser(HttpUser):
    """Simulated analytics user"""
    tasks = [AnalyticsTaskSet]
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login and get auth token"""
        response = self.client.post(
            "/auth/login",
            json={
                "email": f"testuser{random.randint(1, 100)}@example.com",
                "password": "test-password"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token", "")
        else:
            self.token = ""
            print(f"Login failed: {response.status_code}")


class APILoadTest(HttpUser):
    """Heavy load testing user - rapid fire requests"""
    tasks = [AnalyticsTaskSet]
    wait_time = between(0.1, 0.5)  # Shorter wait time for load testing
    
    def on_start(self):
        """Quick login"""
        response = self.client.post(
            "/auth/login",
            json={
                "email": "loadtest@example.com",
                "password": "test-password"
            }
        )
        self.token = response.json().get("access_token", "") if response.status_code == 200 else ""


# ========== CUSTOM EVENT HANDLERS ==========

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when load test starts"""
    print("=" * 80)
    print("PERFORMANCE TEST STARTED")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 80)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when load test stops"""
    print("\n" + "=" * 80)
    print("PERFORMANCE TEST COMPLETED")
    print("=" * 80)
    
    # Print statistics
    print("\nResponse Time Statistics (ms):")
    print(f"  Min:     {environment.stats.total.min_response_time:.2f}")
    print(f"  Max:     {environment.stats.total.max_response_time:.2f}")
    print(f"  Median:  {environment.stats.total.get_response_time_percentile(0.5):.2f}")
    print(f"  95th:    {environment.stats.total.get_response_time_percentile(0.95):.2f}")
    print(f"  99th:    {environment.stats.total.get_response_time_percentile(0.99):.2f}")
    
    print("\nRequest Statistics:")
    print(f"  Total Requests: {environment.stats.total.num_requests}")
    print(f"  Total Failures: {environment.stats.total.num_failures}")
    print(f"  Requests/sec:   {environment.stats.total.total_rps:.2f}")
    
    if environment.stats.total.num_requests > 0:
        failure_rate = (environment.stats.total.num_failures / environment.stats.total.num_requests) * 100
        print(f"  Failure Rate:   {failure_rate:.2f}%")
    
    print("\nEndpoint Breakdown:")
    for method, path in sorted(environment.stats.entries.keys()):
        stats = environment.stats.entries[(method, path)]
        print(f"  {method:6} {path:50} - "
              f"Requests: {stats.num_requests:6} | "
              f"Failures: {stats.num_failures:6} | "
              f"Avg: {stats.avg_response_time:.0f}ms")


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response, context, **kwargs):
    """Log individual requests"""
    if response_time > 1000:  # Log slow requests (> 1 second)
        print(f"⚠️  SLOW REQUEST: {request_type} {name} - {response_time:.0f}ms")
    
    if response and response.status_code >= 400:
        print(f"❌ ERROR: {request_type} {name} - {response.status_code}")


# ========== PERFORMANCE TESTING SCENARIOS ==========

"""
Run different load testing scenarios:

1. Baseline Test (5 users, 1 minute):
   locust -f performance_test.py --host=http://localhost:8000 \
     -u 5 -r 1 -t 1m --headless

2. Moderate Load (50 users, 5 minutes):
   locust -f performance_test.py --host=http://localhost:8000 \
     -u 50 -r 10 -t 5m --headless

3. Heavy Load (200 users, 10 minutes):
   locust -f performance_test.py --host=http://localhost:8000 \
     -u 200 -r 20 -t 10m --headless

4. Stress Test (ramp up to 500 users):
   locust -f performance_test.py --host=http://localhost:8000 \
     -u 500 -r 50 -t 15m --headless

5. Soak Test (100 users, 1 hour):
   locust -f performance_test.py --host=http://localhost:8000 \
     -u 100 -r 10 -t 1h --headless --csv=results

IMPORTANT PERFORMANCE TARGETS:
- Average response time: < 200ms
- 95th percentile: < 500ms
- 99th percentile: < 1000ms
- Error rate: < 1%
- Minimum throughput: 100 requests/second
"""


# ========== PERFORMANCE BENCHMARKS ==========

"""
Expected Performance Metrics (Based on Requirements):

Dashboard Endpoints:
- /dashboard/team-overview: < 150ms (avg)
- /dashboard/athlete/{id}: < 200ms (avg)

Analytics Endpoints:
- /analytics/performance-trends: < 100ms (avg)
- /analytics/injury-risk: < 150ms (avg)
- /analytics/comparative-analysis: < 200ms (avg)

Report Endpoints:
- /reports/*/csv: < 500ms (avg) [includes file generation]
- /reports/team/json: < 300ms (avg)

Authentication:
- /auth/login: < 100ms (avg)
- /auth/register: < 100ms (avg)

File Upload (Video):
- /athletes/{id}/videos: 50-100ms (avg) [plus network transfer]

Video Analysis:
- /videos/{id}/analyze: < 5000ms (avg) [depends on video length]
"""


# ========== INTEGRATION SCENARIOS ==========

class UserJourney(HttpUser):
    """Simulate realistic user journey"""
    wait_time = between(2, 5)
    
    def on_start(self):
        """Login"""
        response = self.client.post(
            "/auth/login",
            json={
                "email": "coach@example.com",
                "password": "coach-password"
            }
        )
        self.token = response.json().get("access_token", "") if response.status_code == 200 else ""
    
    @task
    def coach_workflow(self):
        """Simulate coach checking team and athlete progress"""
        # 1. Check team overview
        self.client.get(
            "/dashboard/team-overview",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        # 2. Get athletes list
        self.client.get(
            "/athletes",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        # 3. Check specific athlete
        athlete_id = random.randint(1, 50)
        self.client.get(
            f"/dashboard/athlete/{athlete_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        # 4. View performance trends
        self.client.get(
            f"/analytics/performance-trends/{athlete_id}?days=30",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        # 5. Export report
        self.client.get(
            f"/reports/athlete/{athlete_id}/csv",
            headers={"Authorization": f"Bearer {self.token}"}
        )


if __name__ == "__main__":
    print("Performance Test Suite for Sports Injury Detection API")
    print("Run with: locust -f performance_test.py --host=http://localhost:8000")
