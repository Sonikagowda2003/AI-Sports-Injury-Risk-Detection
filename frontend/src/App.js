import { useState } from "react";
import { login, createAthlete, listAthletes, uploadVideo, analyzeVideo } from "./api";

function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState("");
  const [athletes, setAthletes] = useState([]);

  const [athleteId, setAthleteId] = useState("");
  const [videoFile, setVideoFile] = useState(null);
  const [videoId, setVideoId] = useState(null);
  const [report, setReport] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);

  const handleLogin = async () => {
    const res = await login({ email, password });
    setToken(res.data.access_token);
  };

  const handleCreateAthlete = async () => {
    await createAthlete(
      { sport_type: "Football", position: "Forward", age: 22, height_cm: 175, weight_kg: 70 },
      token
    );
    alert("Athlete created!");
  };

  const handleListAthletes = async () => {
    const res = await listAthletes(token);
    setAthletes(res.data);
  };

  const handleUpload = async () => {
    if (!athleteId || !videoFile) {
      alert("Enter an Athlete ID and choose a video file first.");
      return;
    }
    const res = await uploadVideo(athleteId, videoFile, token);
    setVideoId(res.data.id);
    setReport(null);
    alert("Video uploaded! Now click Analyze.");
  };

  const handleAnalyze = async () => {
    setAnalyzing(true);
    try {
      const res = await analyzeVideo(videoId, token);
      setReport(res.data);
    } catch (err) {
      alert("Analysis failed: " + (err.response?.data?.detail || err.message));
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div style={{ padding: 40 }}>
      <h1>Sports Injury Risk Detection</h1>
      <input placeholder="Email" onChange={(e) => setEmail(e.target.value)} />
      <input placeholder="Password" type="password" onChange={(e) => setPassword(e.target.value)} />
      <button onClick={handleLogin}>Login</button>

      {token && (
        <div style={{ marginTop: 20 }}>
          <button onClick={handleCreateAthlete}>Create Sample Athlete</button>
          <button onClick={handleListAthletes}>List My Athletes</button>
          <ul>
            {athletes.map((a) => (
              <li key={a.id}>{a.sport_type} - {a.position} - Age {a.age} (ID: {a.id})</li>
            ))}
          </ul>

          <div style={{ marginTop: 30, borderTop: "1px solid #ccc", paddingTop: 20 }}>
            <h3>Milestone 2: Movement Analysis</h3>

            <input
              placeholder="Athlete ID"
              value={athleteId}
              onChange={(e) => setAthleteId(e.target.value)}
            />
            <br />
            <input
              type="file"
              accept="video/*"
              onChange={(e) => setVideoFile(e.target.files[0])}
              style={{ marginTop: 10 }}
            />
            <br />
            <button onClick={handleUpload} style={{ marginTop: 10 }}>
              Upload Video
            </button>
            <button
              onClick={handleAnalyze}
              disabled={!videoId || analyzing}
              style={{ marginTop: 10, marginLeft: 10 }}
            >
              {analyzing ? "Analyzing..." : "Analyze"}
            </button>

            {report && (
              <div style={{ marginTop: 15, border: "1px solid #ccc", padding: 15, maxWidth: 400 }}>
                <h4>Biomechanical Report</h4>
                <p><b>Movement Quality Score:</b> {report.movement_quality_score} / 100</p>
                <p><b>Risk Category:</b> {report.risk_category}</p>
                <p><b>Symmetry Score:</b> {report.symmetry_score}%</p>
                <p><b>Posture Stability:</b> {report.posture_stability_score}%</p>
                <p><b>Knee Valgus Risk:</b> {report.knee_valgus_risk_pct}%</p>
                <p><b>Frames Analyzed:</b> {report.frames_analyzed}</p>
                <p><b>Range of Motion:</b></p>
                <ul>
                  {report.range_of_motion &&
                    Object.entries(report.range_of_motion).map(([joint, value]) => (
                      <li key={joint}>{joint}: {value.toFixed(1)}°</li>
                    ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;