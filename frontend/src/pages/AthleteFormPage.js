import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import { createAthlete, getAthlete, updateAthlete } from "../api";

const EMPTY_FORM = {
  sport_type: "",
  position: "",
  age: "",
  height_cm: "",
  weight_kg: "",
  injury_history: "",
  training_load: "",
};

export default function AthleteFormPage() {
  const { id } = useParams();
  const isEdit = Boolean(id);
  const navigate = useNavigate();

  const [form, setForm] = useState(EMPTY_FORM);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(isEdit);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!isEdit) return;
    getAthlete(id)
      .then((res) => {
        const a = res.data;
        setForm({
          sport_type: a.sport_type || "",
          position: a.position || "",
          age: a.age ?? "",
          height_cm: a.height_cm ?? "",
          weight_kg: a.weight_kg ?? "",
          injury_history: a.injury_history || "",
          training_load: a.training_load || "",
        });
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [id, isEdit]);

  const handleChange = (field) => (e) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSaving(true);

    const payload = {
      ...form,
      age: form.age === "" ? null : Number(form.age),
      height_cm: form.height_cm === "" ? null : Number(form.height_cm),
      weight_kg: form.weight_kg === "" ? null : Number(form.weight_kg),
    };

    try {
      if (isEdit) {
        await updateAthlete(id, payload);
      } else {
        await createAthlete(payload);
      }
      navigate("/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="app-shell">
      <Sidebar />
      <main className="main">
        <div className="page-header">
          <div>
            <h1>{isEdit ? "Edit athlete" : "Add athlete"}</h1>
            <p>{isEdit ? "Update this athlete's profile." : "Create a new athlete profile."}</p>
          </div>
        </div>

        {error && <div className="error-banner">{error}</div>}

        {loading ? (
          <p className="loading-line">Loading athlete…</p>
        ) : (
          <form className="form-card" onSubmit={handleSubmit}>
            <div className="field-row">
              <div className="field">
                <label htmlFor="sport_type">Sport</label>
                <input
                  id="sport_type"
                  value={form.sport_type}
                  onChange={handleChange("sport_type")}
                  placeholder="e.g. Football"
                />
              </div>
              <div className="field">
                <label htmlFor="position">Position</label>
                <input
                  id="position"
                  value={form.position}
                  onChange={handleChange("position")}
                  placeholder="e.g. Forward"
                />
              </div>
            </div>

            <div className="field-row">
              <div className="field">
                <label htmlFor="age">Age</label>
                <input id="age" type="number" min="0" value={form.age} onChange={handleChange("age")} />
              </div>
              <div className="field">
                <label htmlFor="height_cm">Height (cm)</label>
                <input
                  id="height_cm"
                  type="number"
                  step="0.1"
                  value={form.height_cm}
                  onChange={handleChange("height_cm")}
                />
              </div>
            </div>

            <div className="field-row">
              <div className="field">
                <label htmlFor="weight_kg">Weight (kg)</label>
                <input
                  id="weight_kg"
                  type="number"
                  step="0.1"
                  value={form.weight_kg}
                  onChange={handleChange("weight_kg")}
                />
              </div>
              <div className="field">
                <label htmlFor="training_load">Training load</label>
                <input
                  id="training_load"
                  value={form.training_load}
                  onChange={handleChange("training_load")}
                  placeholder="e.g. High, 5 sessions/week"
                />
              </div>
            </div>

            <div className="field">
              <label htmlFor="injury_history">Injury history</label>
              <textarea
                id="injury_history"
                rows={3}
                value={form.injury_history}
                onChange={handleChange("injury_history")}
                placeholder="Any past injuries relevant to risk assessment"
              />
            </div>

            <div style={{ display: "flex", gap: 10, marginTop: 8 }}>
              <button className="btn btn-primary" disabled={saving}>
                {saving ? "Saving…" : isEdit ? "Save changes" : "Create athlete"}
              </button>
              <button
                type="button"
                className="btn btn-ghost"
                onClick={() => navigate("/dashboard")}
              >
                Cancel
              </button>
            </div>
          </form>
        )}
      </main>
    </div>
  );
}
