import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { GraphView } from "./GraphView";

type AnalyzeResult = Record<string, unknown> | null;

function scoreTone(score: number): string {
  if (score >= 80) return "tone-ok";
  if (score >= 60) return "tone-warn";
  return "tone-bad";
}

export function LandingPage() {
  const [repo, setRepo] = useState("");
  const [result, setResult] = useState<AnalyzeResult>(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const graphData = useMemo(() => {
    if (!result) {
      return {
        nodes: [{ id: "app_exemplo", risk: 12 }],
        links: [] as { source: string; target: string }[],
      };
    }
    const arch = (result.architecture as Record<string, unknown>) || {};
    const vis = (arch.visual as Record<string, unknown>) || {};
    const nodes = (vis.nodes as object[]) || [];
    const edges = (vis.edges as object[]) || [];
    return {
      nodes: nodes.map((n) => {
        const o = n as Record<string, unknown>;
        return { ...o, id: String(o.id ?? "?") };
      }),
      links: edges.map((e) => {
        const o = e as Record<string, unknown>;
        return { source: String(o.source), target: String(o.target) };
      }),
    };
  }, [result]);

  async function analyze() {
    setErr(null);
    setResult(null);
    setLoading(true);
    try {
      const res = await fetch("/api/analyze-repo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo: repo.trim() }),
      });
      const data = (await res.json()) as Record<string, unknown>;
      if (!res.ok && data.error) {
        setErr(String(data.error));
        setLoading(false);
        return;
      }
      if ((data as { parse_error?: boolean }).parse_error) {
        setErr("Resposta JSON inválida do motor.");
        setLoading(false);
        return;
      }
      setResult(data);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Pedido falhou. O servidor de demo está a correr?");
    } finally {
      setLoading(false);
    }
  }

  const score = result ? Number(result.score ?? 0) : null;
  const archSub = result
    ? Number((result.scores as Record<string, unknown> | undefined)?.architecture ?? NaN)
    : null;
  const risk = result
    ? ((result.architecture as Record<string, unknown> | undefined)?.insights as Record<string, unknown> | undefined)?.risk as
        | Record<string, unknown>
        | undefined
    : undefined;

  return (
    <div className="page">
      <div className="noise" aria-hidden />
      <header className="hero">
        <p className="eyebrow">Governança arquitetural contínua</p>
        <h1 className="title">
          Cole o repositório.
          <br />
          <span className="title-accent">Veja se a arquitetura aguenta.</span>
        </h1>
        <p className="lede">
          Demo local: arranca <code>tools/sinaplint-demo-server/server.py</code> (porta 8765) ou Django (8000) e ajusta o proxy
          no Vite. <Link to="/dashboard">Dashboard SaaS</Link> (sessão + API Django).
        </p>

        <div className="row">
          <input
            className="input"
            value={repo}
            onChange={(e) => setRepo(e.target.value)}
            placeholder="https://github.com/org/Core_SinapUm"
            onKeyDown={(e) => e.key === "Enter" && analyze()}
          />
          <button type="button" className="btn" onClick={analyze} disabled={loading || !repo.trim()}>
            {loading ? "A analisar…" : "Analisar"}
          </button>
        </div>
        {err && <p className="error">{err}</p>}
      </header>

      {result && score != null && (
        <section className="panel">
          <div className="score-grid">
            <div>
              <p className="label">Score global</p>
              <p className={`score-big ${scoreTone(score)}`}>{score}</p>
              <p className="sub">{String(result.quality ?? "—")}</p>
            </div>
            {archSub != null && !Number.isNaN(archSub) && (
              <div>
                <p className="label">Arquitetura</p>
                <p className="score-mid">{archSub}</p>
              </div>
            )}
            {risk?.risk_score != null && (
              <div>
                <p className="label">Risco agregado</p>
                <p className="score-mid">{String(risk.risk_score)}</p>
                <p className="sub">{String(risk.risk_level ?? "")}</p>
              </div>
            )}
          </div>

          <div className="graph-wrap">
            <p className="label">Pré-visualização do grafo (apps)</p>
            <GraphView data={graphData} onNodeClick={() => undefined} />
          </div>
        </section>
      )}
    </div>
  );
}
