type Props = {
  selected: Record<string, unknown> | null;
};

export function SidePanel({ selected }: Props) {
  if (!selected) {
    return (
      <aside
        style={{
          width: 320,
          flexShrink: 0,
          background: "#111",
          borderLeft: "1px solid #333",
          padding: 16,
          fontSize: 14,
          opacity: 0.7,
        }}
      >
        Clique num nó para ver risco, impacto e métricas.
      </aside>
    );
  }

  const id = String(selected.id ?? "");
  const risk = selected.risk ?? selected.risk_index ?? "—";
  const impact = selected.impact_score ?? "—";
  const deps = selected.dependencies ?? "—";
  const cycles = selected.in_cycles ?? "—";
  const fi = selected.fan_in ?? "—";

  return (
    <aside
      style={{
        width: 320,
        flexShrink: 0,
        background: "#111",
        borderLeft: "1px solid #333",
        padding: 16,
        fontSize: 14,
      }}
    >
      <h2 style={{ marginTop: 0, fontSize: 18 }}>{id}</h2>
      <p>
        <strong>Risk / heatmap:</strong> {String(risk)}
      </p>
      <p>
        <strong>Impact score:</strong> {String(impact)}
      </p>
      <p>
        <strong>Dependencies (saída):</strong> {String(deps)}
      </p>
      <p>
        <strong>Em ciclos (SCC):</strong> {String(cycles)}
      </p>
      <p>
        <strong>Fan-in:</strong> {String(fi)}
      </p>
    </aside>
  );
}
