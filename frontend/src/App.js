import { useState } from "react";
import { login, createAthlete, listAthletes } from "./api";

function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState("");
  const [athletes, setAthletes] = useState([]);

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
              <li key={a.id}>{a.sport_type} - {a.position} - Age {a.age}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;