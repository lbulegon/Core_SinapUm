import { useMemo, useState } from "react";
import { GraphView } from "./GraphView";
import { SidePanel } from "./SidePanel";

/** Cole o JSON de ``run_analysis()`` ou só ``architecture.visual`` + ``insights.refactor_plan``. */
const SAMPLE = {
  nodes: [{ id: "app_a", risk: 40 }],
  edges: [{ source: "app_a", target: "app_b" }],
};

export function App() {
  const [raw, setRaw] = useState("");
  const [selected, setSelected] = useState<Record<string, unknown> | null>(null);

  const graphData = useMemo(() => {
    if (!raw.trim()) return { nodes: SAMPLE.nodes, links: SAMPLE.edges };
    try {
      const j = JSON.parse(raw) as Record<string, unknown>;
      const arch = (j.architecture as Record<string, unknown>) || j;
      const vis = (arch.visual as Record<string, unknown>) || j;
      const nodes = (vis.nodes as object[]) || [];
      const edges = (vis.edges as object[]) || [];
      return {
        nodes: nodes.map((n) => {
          const o = n as Record<string, unknown>;
          return { ...o, id: o.id as string };
        }),
        links: edges.map((e) => {
          const o = e as Record<string, unknown>;
          return { source: o.source as string, target: o.target as string };
        }),
      };
    } catch {
      return { nodes: SAMPLE.nodes, links: SAMPLE.edges };
    }
  }, [raw]);

  return (
    <div style={{ fontFamily: "system-ui", minHeight: "100vh", background: "#0a0a0a", color: "#fafafa" }}>
      <header style={{ padding: "1rem", borderBottom: "1px solid #333" }}>
        <h1 style={{ margin: 0, fontSize: "1.25rem" }}>SinapLint — Grafo arquitetural</h1>
        <p style={{ margin: "0.5rem 0 0", opacity: 0.75, fontSize: "0.875rem" }}>
          Cole o JSON do motor (campo <code>architecture</code> ou relatório completo).
        </p>
        <textarea
          value={raw}
          onChange={(e) => setRaw(e.target.value)}
          placeholder='{"architecture": { "visual": { "nodes": [...], "edges": [...] } } }'
          style={{
            width: "100%",
            minHeight: 72,
            marginTop: 8,
            background: "#111",
            color: "#eee",
            border: "1px solid #333",
            borderRadius: 8,
            padding: 8,
          }}
        />
      </header>
      <div style={{ display: "flex", position: "relative", height: "calc(100vh - 200px)" }}>
        <div style={{ flex: 1, position: "relative" }}>
          <GraphView
            data={graphData}
            onNodeClick={(n: object) => setSelected(n as Record<string, unknown>)}
          />
        </div>
        <SidePanel selected={selected} />
      </div>
    </div>
  );
}
