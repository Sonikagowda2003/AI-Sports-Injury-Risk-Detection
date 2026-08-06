import { useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import {
  getAthlete,
  listVideos,
  uploadVideo,
  analyzeVideo,
  getReport,
  getRiskAssessment,
  getRiskTrend,
} from "../api";

const RISK_CLASS = {
  "Low Risk": "low",
  "Moderate Risk": "moderate",
  "High Risk": "high",
  "Critical Risk": "critical",
};

const FACTOR_LABELS = {
  biomechanical_deviation_score: "Biomechanical deviations",
  historical_injury_factor_score: "Historical injury factors",
  movement_asymmetry_score: "Movement asymmetry",
  training_load_score: "Training load",
  fatigue_indicator_score: "Fatigue indicators",
};

const RECOMMENDATION_LABELS = {
  exercise_recommendations: "Exercises",
  mobility_suggestions: "Mobility",
  strengthening_recommendations: "Strengthening",
  recovery_plan: "Recovery",
  training_modifications: "Training modifications",
};

function RiskBar({ label, value }) {
  const riskClass = value >= 60 ? "critical" : value >= 40 ? "high" : value >= 20 ? "moderate" : "low";
  return (
    <div className="risk-bar-row">
      <div className="risk-bar-label">
        <span>{label}</span>
        <strong>{Math.round(value)}</strong>
      </div>
      <div className="risk-bar-track">
        <div className={`risk-bar-fill ${riskClass}`} style={{ width: `${Math.min(100, value)}%` }} />
      </div>
    </div>
  );
}

function RiskAssessmentPanel({ assessment }) {
  const riskClass = RISK_CLASS[assessment.risk_category] || "moderate";

  return (
    <div className="assessment-panel">
      <div className="assessment-header">
        <div>
          <div className="video-meta">Injury risk score</div>
          <div className="assessment-score">{Math.round(assessment.overall_risk_score)}</div>
        </div>
        <span className={`risk-pill ${riskClass}`}>{assessment.risk_category}</span>
      </div>

      <div className="assessment-section">
        <div className="assessment-subhead">Weighted factors</div>
        {Object.entries(FACTOR_LABELS).map(([key, label]) => (
          <RiskBar key={key} label={label} value={assessment[key]} />
        ))}
      </div>

      <div className="assessment-section">
        <div className="assessment-subhead">Injury category breakdown</div>
        {Object.entries(assessment.category_risks || {}).map(([category, value]) => (
          <RiskBar key={category} label={category} value={value} />
        ))}
      </div>

      <div className="assessment-section badges">
        {assessment.anomaly_detected && (
          <span className="badge badge-warn">Movement anomaly detected</span>
        )}
        {assessment.performance_decline_detected && (
          <span className="badge badge-danger">Performance decline vs. baseline</span>
        )}
        <span className={`badge badge-fatigue-${assessment.fatigue_trend}`}>
          Fatigue trend: {assessment.fatigue_trend.replace("_", " ")}
        </span>
      </div>

      <div className="assessment-section">
        <div className="assessment-subhead">Recommendations</div>
        <div className="recommendation-grid">
          {Object.entries(RECOMMENDATION_LABELS).map(([key, label]) => (
            <div className="recommendation-card" key={key}>
              <div className="recommendation-card-title">{label}</div>
              <ul>
                {(assessment.recommendations?.[key] || []).map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function RiskTrend({ athleteId }) {
  const [points, setPoints] = useState(null);

  useEffect(() => {
    getRiskTrend(athleteId)
      .then((res) => setPoints(res.data))
      .catch(() => setPoints([]));
  }, [athleteId]);

  if (!points || points.length === 0) return null;

  return (
    <div className="trend-card">
      <div className="assessment-subhead">Risk trend across analyzed videos</div>
      <div className="trend-bars">
        {points.map((p) => {
          const riskClass = RISK_CLASS[p.risk_category] || "moderate";
          return (
            <div className="trend-bar-wrap" key={p.video_id} title={`${Math.round(p.overall_risk_score)} — ${p.risk_category}`}>
              <div
                className={`trend-bar ${riskClass}`}
                style={{ height: `${Math.max(6, p.overall_risk_score)}%` }}
              />
              <div className="trend-bar-date">
                {new Date(p.created_at).toLocaleDateString(undefined, { month: "short", day: "numeric" })}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function ReportPanel({ report }) {
  const riskClass = RISK_CLASS[report.risk_category] || "moderate";
  return (
    <div className="report-panel">
      <span className={`risk-pill ${riskClass}`}>{report.risk_category}</span>

      <div className="report-grid" style={{ marginTop: 14 }}>
        <div className="report-metric">
          <div className="label">Movement quality</div>
          <div className="value">{report.movement_quality_score}</div>
        </div>
        <div className="report-metric">
          <div className="label">Symmetry</div>
          <div className="value">{report.symmetry_score}</div>
        </div>
        <div className="report-metric">
          <div className="label">Posture stability</div>
          <div className="value">{report.posture_stability_score}</div>
        </div>
        <div className="report-metric">
          <div className="label">Knee valgus risk</div>
          <div className="value">{report.knee_valgus_risk_pct}%</div>
        </div>
        <div className="report-metric">
          <div className="label">Frames analyzed</div>
          <div className="value">{report.frames_analyzed}</div>
        </div>
      </div>

      <div className="rom-list">
        {Object.entries(report.range_of_motion || {}).map(([joint, degrees]) => (
          <span className="rom-chip" key={joint}>
            {joint.replace("_", " ")}
            <strong>{Math.round(degrees)}°</strong>
          </span>
        ))}
      </div>
    </div>
  );
}

function VideoRow({ video, onAnalyzed }) {
  const [report, setReport] = useState(null);
  const [assessment, setAssessment] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState("");
  const [status, setStatus] = useState(video.status);

  useEffect(() => {
    if (status === "completed") {
      getReport(video.id)
        .then((res) => setReport(res.data))
        .catch(() => {});
      getRiskAssessment(video.id)
        .then((res) => setAssessment(res.data))
        .catch(() => {});
    }
  }, [status, video.id]);

  const handleAnalyze = async () => {
    setAnalyzing(true);
    setError("");
    try {
      const res = await analyzeVideo(video.id);
      setReport(res.data.report);
      setAssessment(res.data.risk_assessment);
      setStatus("completed");
      onAnalyzed?.();
    } catch (err) {
      setStatus("failed");
      setError(err.message);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="video-row">
      <div className="video-row-top">
        <div>
          <div className="video-name">{video.filename}</div>
          <div className="video-meta">
            Uploaded {new Date(video.uploaded_at).toLocaleString()}
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span className={`status-pill ${status}`}>{status}</span>
          {status !== "completed" && (
            <button className="btn btn-primary btn-sm" onClick={handleAnalyze} disabled={analyzing}>
              {analyzing ? "Analyzing…" : "Analyze"}
            </button>
          )}
        </div>
      </div>

      {error && <div className="error-banner" style={{ marginTop: 12 }}>{error}</div>}
      {report && <ReportPanel report={report} />}
      {assessment && <RiskAssessmentPanel assessment={assessment} />}
    </div>
  );
}

export default function AthleteDetailPage() {
  const { id } = useParams();
  const [athlete, setAthlete] = useState(null);
  const [videos, setVideos] = useState([]);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const fileInputRef = useRef(null);

  const load = async () => {
    try {
      const [athleteRes, videosRes] = await Promise.all([getAthlete(id), listVideos(id)]);
      setAthlete(athleteRes.data);
      setVideos(videosRes.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;
    setUploading(true);
    setError("");
    try {
      await uploadVideo(id, file);
      setFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
      const videosRes = await listVideos(id);
      setVideos(videosRes.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="app-shell">
      <Sidebar />
      <main className="main">
        <Link to="/dashboard" className="back-link">
          ← Back to roster
        </Link>

        <div className="page-header" style={{ marginTop: 8 }}>
          <div>
            <div className="detail-header">
              <h1>{athlete ? athlete.sport_type || "Athlete" : "Loading…"}</h1>
            </div>
            <p>{athlete?.position || "No position set"}</p>
          </div>
          {athlete && (
            <Link to={`/athletes/${id}/edit`} className="btn btn-ghost">
              Edit profile
            </Link>
          )}
        </div>

        {error && <div className="error-banner">{error}</div>}

        {!loading && (
          <>
            <RiskTrend athleteId={id} />

            <form className="upload-card" onSubmit={handleUpload}>
              <div>
                <strong>Upload movement video</strong>
                <div className="video-meta">
                  MediaPipe pose estimation runs on this to score injury risk.
                </div>
              </div>
              <input
                ref={fileInputRef}
                type="file"
                accept="video/*"
                onChange={(e) => setFile(e.target.files[0])}
              />
              <button className="btn btn-primary" disabled={!file || uploading}>
                {uploading ? "Uploading…" : "Upload"}
              </button>
            </form>

            {videos.length === 0 ? (
              <div className="empty-state">
                <h3>No videos yet</h3>
                <p>Upload a movement video above to run a biomechanical risk analysis.</p>
              </div>
            ) : (
              <div className="video-list">
                {videos.map((v) => (
                  <VideoRow key={v.id} video={v} onAnalyzed={load} />
                ))}
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}
