import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import RiskDial from "../components/RiskDial";
import { listAthletes, deleteAthlete } from "../api";

export default function DashboardPage() {
  const [athletes, setAthletes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  const [sportFilter, setSportFilter] = useState("all");

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await listAthletes();
      setAthletes(res.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleDelete = async (id) => {
    if (!window.confirm("Remove this athlete profile? This can't be undone.")) return;
    try {
      await deleteAthlete(id);
      setAthletes((prev) => prev.filter((a) => a.id !== id));
    } catch (err) {
      setError(err.message);
    }
  };

  const sports = useMemo(() => {
    const set = new Set(athletes.map((a) => a.sport_type).filter(Boolean));
    return ["all", ...set];
  }, [athletes]);

  const visible = athletes.filter((a) => {
    const matchesSport = sportFilter === "all" || a.sport_type === sportFilter;
    const haystack = `${a.sport_type || ""} ${a.position || ""}`.toLowerCase();
    const matchesQuery = haystack.includes(query.toLowerCase());
    return matchesSport && matchesQuery;
  });

  const initials = (a) => (a.sport_type || "?").slice(0, 2).toUpperCase();

  return (
    <div className="app-shell">
      <Sidebar />
      <main className="main">
        <div className="page-header">
          <div>
            <h1>Athlete roster</h1>
            <p>{athletes.length} profile{athletes.length === 1 ? "" : "s"} on file</p>
          </div>
          <Link to="/athletes/new" className="btn btn-primary">
            + Add athlete
          </Link>
        </div>

        {error && <div className="error-banner">{error}</div>}

        <div className="toolbar">
          <input
            placeholder="Search by sport or position…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <select value={sportFilter} onChange={(e) => setSportFilter(e.target.value)}>
            {sports.map((s) => (
              <option key={s} value={s}>
                {s === "all" ? "All sports" : s}
              </option>
            ))}
          </select>
        </div>

        {loading && <p className="loading-line">Loading athletes…</p>}

        {!loading && visible.length === 0 && (
          <div className="empty-state">
            <h3>No athletes yet</h3>
            <p>Add your first athlete profile to start tracking injury risk.</p>
            <div style={{ marginTop: 16 }}>
              <Link to="/athletes/new" className="btn btn-primary">
                + Add athlete
              </Link>
            </div>
          </div>
        )}

        {!loading && visible.length > 0 && (
          <div className="athlete-grid">
            {visible.map((a) => (
              <div className="athlete-card" key={a.id}>
                <Link
                  to={`/athletes/${a.id}`}
                  style={{ textDecoration: "none", color: "inherit" }}
                >
                  <div className="athlete-card-top">
                    <div className="jersey">{initials(a)}</div>
                    <div style={{ flex: 1 }}>
                      <div className="athlete-name">{a.sport_type || "Unspecified sport"}</div>
                      <div className="athlete-sub">{a.position || "No position set"}</div>
                    </div>
                    <RiskDial riskScore={a.risk_score} />
                  </div>

                  <div className="athlete-stats">
                    <div className="stat-block">
                      <div className="stat-value mono">{a.age ?? "—"}</div>
                      <div className="stat-label">Age</div>
                    </div>
                    <div className="stat-block">
                      <div className="stat-value mono">{a.height_cm ?? "—"}</div>
                      <div className="stat-label">Height cm</div>
                    </div>
                    <div className="stat-block">
                      <div className="stat-value mono">{a.weight_kg ?? "—"}</div>
                      <div className="stat-label">Weight kg</div>
                    </div>
                  </div>
                </Link>

                <div className="card-actions">
                  <Link to={`/athletes/${a.id}`} className="btn btn-primary btn-sm">
                    Videos & analysis
                  </Link>
                  <Link to={`/athletes/${a.id}/edit`} className="btn btn-ghost btn-sm">
                    Edit
                  </Link>
                  <button className="btn btn-danger btn-sm" onClick={() => handleDelete(a.id)}>
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
