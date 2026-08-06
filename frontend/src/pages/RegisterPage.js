import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const ROLES = ["athlete", "coach", "physiotherapist", "sports_scientist", "admin"];

export default function RegisterPage() {
  const { register, login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("athlete");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register(email, password, role);
      // Registration succeeded — log the user straight in.
      await login(email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-shell">
      <div className="auth-visual">
        <h2>Built for the whole performance team.</h2>
        <p>
          Athletes, coaches, physios, and sports scientists each get a view
          suited to their role — one account, one roster.
        </p>
        <div className="auth-dial" />
      </div>

      <div className="auth-form-side">
        <div className="auth-box">
          <h1>Create your account</h1>
          <p className="subtitle">Set up access to the platform.</p>

          {error && <div className="error-banner">{error}</div>}

          <form onSubmit={handleSubmit}>
            <div className="field">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="field">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={6}
              />
            </div>
            <div className="field">
              <label htmlFor="role">Role</label>
              <select id="role" value={role} onChange={(e) => setRole(e.target.value)}>
                {ROLES.map((r) => (
                  <option key={r} value={r}>
                    {r.replace("_", " ")}
                  </option>
                ))}
              </select>
            </div>
            <button className="btn btn-primary" style={{ width: "100%" }} disabled={loading}>
              {loading ? "Creating account…" : "Create account"}
            </button>
          </form>

          <div className="auth-switch">
            Already have an account? <Link to="/login">Log in</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
