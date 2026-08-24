// DashboardPage.jsx - Milestone 4: Analytics Dashboard
/**
 * Main dashboard page for coaches and sports scientists
 * Displays team overview, athlete metrics, risk assessments, and trends
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../api';
import RiskDial from '../components/RiskDial';
import './DashboardPage.css';

const DashboardPage = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Team overview state
  const [teamOverview, setTeamOverview] = useState(null);
  const [athletes, setAthletes] = useState([]);
  const [selectedAthlete, setSelectedAthlete] = useState(null);
  const [athleteDetails, setAthleteDetails] = useState(null);
  const [performanceTrends, setPerformanceTrends] = useState(null);
  
  // Filter and view state
  const [sportFilter, setSportFilter] = useState('');
  const [selectedMetric, setSelectedMetric] = useState('symmetry_score');
  const [dateRange, setDateRange] = useState(30);
  const [viewMode, setViewMode] = useState('overview'); // 'overview' or 'detailed'
  
  // Load dashboard data
  useEffect(() => {
    loadDashboardData();
  }, [user?.role]);
  
  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Only coaches and sports scientists can access dashboard
      if (user?.role !== 'coach' && user?.role !== 'sports_scientist' && user?.role !== 'admin') {
        setError('You do not have permission to access the dashboard');
        setLoading(false);
        return;
      }
      
      // Load team overview
      const overviewResponse = await api.get('/dashboard/team-overview');
      setTeamOverview(overviewResponse.data);
      
      // Load athletes list
      const athletesResponse = await api.get('/athletes');
      setAthletes(athletesResponse.data || []);
      
      setLoading(false);
    } catch (err) {
      console.error('Error loading dashboard:', err);
      setError(err.response?.data?.detail || 'Failed to load dashboard data');
      setLoading(false);
    }
  };
  
  // Load athlete details when selected
  useEffect(() => {
    if (selectedAthlete) {
      loadAthleteDetails(selectedAthlete);
    }
  }, [selectedAthlete]);
  
  const loadAthleteDetails = async (athleteId) => {
    try {
      // Load athlete dashboard
      const dashboardResponse = await api.get(`/dashboard/athlete/${athleteId}`);
      setAthleteDetails(dashboardResponse.data);
      
      // Load performance trends
      const trendsResponse = await api.get(
        `/analytics/performance-trends/${athleteId}?days=${dateRange}`
      );
      setPerformanceTrends(trendsResponse.data);
    } catch (err) {
      console.error('Error loading athlete details:', err);
      setError('Failed to load athlete details');
    }
  };
  
  // Handle date range change
  const handleDateRangeChange = (days) => {
    setDateRange(days);
    if (selectedAthlete) {
      loadAthleteDetails(selectedAthlete);
    }
  };
  
  // Export functions
  const handleExportTeamReport = async () => {
    try {
      const response = await api.get('/reports/team/json', {
        responseType: 'json'
      });
      const element = document.createElement('a');
      element.setAttribute('href', 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(response.data, null, 2)));
      element.setAttribute('download', `team_report_${new Date().toISOString().split('T')[0]}.json`);
      element.style.display = 'none';
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
    } catch (err) {
      setError('Failed to export team report');
    }
  };
  
  const handleExportAthleteReport = async (athleteId) => {
    try {
      const response = await api.get(`/reports/athlete/${athleteId}/csv`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `athlete_${athleteId}_report.csv`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
    } catch (err) {
      setError('Failed to export athlete report');
    }
  };
  
  if (loading) {
    return (
      <div className="dashboard-container loading">
        <div className="spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="dashboard-container error">
        <div className="error-message">
          <h3>Error</h3>
          <p>{error}</p>
          <button onClick={loadDashboardData}>Retry</button>
        </div>
      </div>
    );
  }
  
  const filteredAthletes = athletes.filter(
    athlete => !sportFilter || athlete.sport_type === sportFilter
  );
  
  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>Sports Injury Risk Analysis Dashboard</h1>
        <div className="header-controls">
          <button 
            className="view-toggle"
            onClick={() => setViewMode(viewMode === 'overview' ? 'detailed' : 'overview')}
          >
            {viewMode === 'overview' ? '📊 Detailed View' : '👁️ Overview'}
          </button>
          <button className="export-btn" onClick={handleExportTeamReport}>
            📥 Export Team Report
          </button>
        </div>
      </header>
      
      {viewMode === 'overview' ? (
        <OverviewView 
          teamOverview={teamOverview}
          athletes={filteredAthletes}
          onSelectAthlete={setSelectedAthlete}
          sportFilter={sportFilter}
          onSportFilterChange={setSportFilter}
          onExport={handleExportAthleteReport}
        />
      ) : (
        <DetailedView
          selectedAthlete={selectedAthlete}
          athleteDetails={athleteDetails}
          performanceTrends={performanceTrends}
          dateRange={dateRange}
          onDateRangeChange={handleDateRangeChange}
          onSelectAthlete={setSelectedAthlete}
          athletes={filteredAthletes}
          onExport={handleExportAthleteReport}
        />
      )}
    </div>
  );
};

// Overview View Component
const OverviewView = ({ 
  teamOverview, 
  athletes, 
  onSelectAthlete, 
  sportFilter, 
  onSportFilterChange,
  onExport 
}) => {
  if (!teamOverview) {
    return <div className="no-data">No team data available</div>;
  }
  
  const sports = [...new Set(athletes.map(a => a.sport_type))];
  
  return (
    <div className="overview-view">
      {/* Team Statistics Summary */}
      <section className="team-stats-section">
        <h2>Team Overview</h2>
        <div className="stats-grid">
          <StatCard 
            title="Total Athletes Analyzed"
            value={teamOverview.total_athletes_analyzed}
            icon="👥"
          />
          <StatCard 
            title="Total Assessments"
            value={teamOverview.total_videos_analyzed}
            icon="📹"
          />
          <StatCard 
            title="Average Risk Score"
            value={teamOverview.average_risk_score.toFixed(1)}
            icon="📈"
            status={teamOverview.average_risk_score > 65 ? 'high' : teamOverview.average_risk_score > 40 ? 'moderate' : 'low'}
          />
          <StatCard 
            title="Risk Trend"
            value={teamOverview.trend}
            icon={teamOverview.trend === 'improving' ? '📉' : '📊'}
          />
        </div>
      </section>
      
      {/* Risk Distribution Chart */}
      <section className="risk-distribution-section">
        <h2>Risk Distribution</h2>
        <div className="risk-chart">
          <RiskDistributionChart riskData={teamOverview.risk_distribution} />
        </div>
      </section>
      
      {/* Athletes List */}
      <section className="athletes-section">
        <h2>Team Athletes</h2>
        <div className="filter-controls">
          <label>Filter by Sport:</label>
          <select value={sportFilter} onChange={(e) => onSportFilterChange(e.target.value)}>
            <option value="">All Sports</option>
            {sports.map(sport => (
              <option key={sport} value={sport}>{sport}</option>
            ))}
          </select>
        </div>
        
        <div className="athletes-grid">
          {athletes.length === 0 ? (
            <p className="no-data">No athletes found</p>
          ) : (
            athletes.map(athlete => (
              <AthleteCard 
                key={athlete.id}
                athlete={athlete}
                onSelect={() => onSelectAthlete(athlete.id)}
                onExport={() => onExport(athlete.id)}
              />
            ))
          )}
        </div>
      </section>
    </div>
  );
};

// Detailed View Component
const DetailedView = ({
  selectedAthlete,
  athleteDetails,
  performanceTrends,
  dateRange,
  onDateRangeChange,
  onSelectAthlete,
  athletes,
  onExport
}) => {
  if (!selectedAthlete) {
    return (
      <div className="detailed-view">
        <h2>Select an athlete to view detailed analysis</h2>
        <div className="athlete-selector">
          {athletes.map(athlete => (
            <button 
              key={athlete.id}
              className="athlete-btn"
              onClick={() => onSelectAthlete(athlete.id)}
            >
              {athlete.first_name} {athlete.last_name}
            </button>
          ))}
        </div>
      </div>
    );
  }
  
  if (!athleteDetails) {
    return <div className="loading">Loading athlete data...</div>;
  }
  
  return (
    <div className="detailed-view">
      {/* Athlete Header */}
      <div className="athlete-header">
        <div className="athlete-info">
          <h2>{athleteDetails.athlete_name}</h2>
          <p className="meta-info">
            {athleteDetails.sport_type} • {athleteDetails.position}
          </p>
        </div>
        <button className="export-btn" onClick={() => onExport(selectedAthlete)}>
          📥 Export Report
        </button>
      </div>
      
      {/* Risk Assessment */}
      {athleteDetails.assessment && (
        <section className="assessment-section">
          <h3>Injury Risk Assessment</h3>
          <div className="assessment-grid">
            <div className="assessment-card">
              <h4>Total Assessments</h4>
              <p className="value">{athleteDetails.assessment.total_assessments}</p>
            </div>
            <div className="assessment-card">
              <h4>Highest Risk Score</h4>
              <RiskDial 
                value={athleteDetails.assessment.highest_risk_score}
                size="medium"
              />
            </div>
          </div>
          
          {/* Recommendations */}
          <div className="recommendations">
            <h4>Recommendations</h4>
            <ul>
              {athleteDetails.assessment.recommendations.map((rec, idx) => (
                <li key={idx}>✓ {rec}</li>
              ))}
            </ul>
          </div>
        </section>
      )}
      
      {/* Performance Trends */}
      {performanceTrends && (
        <section className="trends-section">
          <h3>Performance Trends</h3>
          <div className="date-range-selector">
            {[7, 14, 30, 60, 90].map(days => (
              <button
                key={days}
                className={dateRange === days ? 'active' : ''}
                onClick={() => onDateRangeChange(days)}
              >
                {days}d
              </button>
            ))}
          </div>
          
          <div className="metrics-display">
            <MetricsCard 
              title="Symmetry Score"
              value={performanceTrends.average_metrics.symmetry_score}
              trend={performanceTrends.trend_analysis.symmetry_trend}
            />
            <MetricsCard 
              title="Posture Stability"
              value={performanceTrends.average_metrics.posture_score}
              trend={performanceTrends.trend_analysis.posture_trend}
            />
            <MetricsCard 
              title="Movement Quality"
              value={performanceTrends.average_metrics.movement_quality}
              trend={performanceTrends.trend_analysis.movement_quality_trend}
            />
          </div>
          
          {/* Trends Chart */}
          {performanceTrends.data_points.length > 0 && (
            <TrendsChart data={performanceTrends.data_points} />
          )}
        </section>
      )}
      
      {/* Recent Assessments */}
      {athleteDetails.recent_videos && athleteDetails.recent_videos.length > 0 && (
        <section className="recent-videos-section">
          <h3>Recent Assessments</h3>
          <div className="videos-list">
            {athleteDetails.recent_videos.map(video => (
              <VideoItem key={video.id} video={video} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
};

// Sub-components
const StatCard = ({ title, value, icon, status }) => (
  <div className={`stat-card ${status || ''}`}>
    <div className="stat-icon">{icon}</div>
    <div className="stat-content">
      <h4>{title}</h4>
      <p className="stat-value">{value}</p>
    </div>
  </div>
);

const AthleteCard = ({ athlete, onSelect, onExport }) => (
  <div className="athlete-card">
    <h3>{athlete.first_name} {athlete.last_name}</h3>
    <p className="position">{athlete.position}</p>
    <p className="sport">{athlete.sport_type}</p>
    <div className="athlete-actions">
      <button onClick={onSelect} className="view-btn">View Details</button>
      <button onClick={onExport} className="export-small-btn">Export</button>
    </div>
  </div>
);

const MetricsCard = ({ title, value, trend }) => (
  <div className={`metrics-card ${trend}`}>
    <h4>{title}</h4>
    <p className="metric-value">{value.toFixed(1)}</p>
    <p className="trend-indicator">
      {trend === 'improving' && '📈 Improving'}
      {trend === 'declining' && '📉 Declining'}
      {trend === 'stable' && '➡️ Stable'}
    </p>
  </div>
);

const VideoItem = ({ video }) => (
  <div className="video-item">
    <span className="video-name">{video.filename}</span>
    <span className={`status ${video.status}`}>{video.status}</span>
    <span className="date">{new Date(video.created_at).toLocaleDateString()}</span>
  </div>
);

const RiskDistributionChart = ({ riskData }) => {
  const total = Object.values(riskData).reduce((a, b) => a + b, 0);
  if (total === 0) return <p>No data available</p>;
  
  return (
    <div className="distribution-bars">
      {Object.entries(riskData).map(([category, count]) => (
        <div key={category} className="bar-item">
          <div className="bar-label">{category}</div>
          <div className="bar-container">
            <div 
              className={`bar ${category.toLowerCase().replace(' ', '-')}`}
              style={{ width: `${(count / total) * 100}%` }}
            >
              {count}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

const TrendsChart = ({ data }) => {
  // Simplified trend visualization
  return (
    <div className="trends-chart">
      <svg viewBox="0 0 600 200" className="chart-svg">
        {/* This is a simplified placeholder - in production, use a charting library like recharts */}
        <polyline 
          points={data.map((d, i) => `${(i / data.length) * 600},${200 - (d.symmetry_score * 2)}`).join(' ')}
          className="trend-line"
        />
      </svg>
      <p className="chart-label">Symmetry Score Trend</p>
    </div>
  );
};

export default DashboardPage;
