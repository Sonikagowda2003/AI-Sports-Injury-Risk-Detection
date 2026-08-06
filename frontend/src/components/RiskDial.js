// Displays an athlete's injury-risk score as a small dial.
// The backend doesn't return a risk_score yet (that lands with the
// Milestone 2 biomechanics model) — until then every athlete shows
// as "pending" rather than faking a number.
export default function RiskDial({ riskScore }) {
  if (riskScore === undefined || riskScore === null) {
    return (
      <div className="risk-dial pending" title="Risk assessment not yet available">
        N/A
      </div>
    );
  }

  let color = "var(--accent)";
  if (riskScore >= 70) color = "var(--danger)";
  else if (riskScore >= 40) color = "var(--warn)";

  return (
    <div
      className="risk-dial"
      style={{ borderColor: color, color }}
      title={`Injury risk score: ${riskScore}/100`}
    >
      {riskScore}
    </div>
  );
}
