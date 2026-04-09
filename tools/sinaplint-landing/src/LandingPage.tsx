import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { GraphView } from "./GraphView";

type AnalyzeResult = Record<string, unknown> | null;

/** Repositório público com `app_sinaplint` na raiz (ex.: fork do Core). Definir em `.env`: VITE_SINAPLINT_DEMO_REPO */
const DEMO_REPO_URL = (import.meta.env.VITE_SINAPLINT_DEMO_REPO as string | undefined)?.trim() || "";

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

  async function analyzeRepo(repoUrl: string) {
    const trimmed = repoUrl.trim();
    setErr(null);
    setResult(null);
    setLoading(true);
    try {
      const res = await fetch("/api/analyze-repo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo: trimmed }),
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

  async function analyze() {
    await analyzeRepo(repo);
  }

  async function runPublicDemo() {
    if (!DEMO_REPO_URL) return;
    setRepo(DEMO_REPO_URL);
    await analyzeRepo(DEMO_REPO_URL);
  }

  const score = result ? Number(result.score ?? 0) : null;
  const archSub = result
    ? Number((result.scores as Record<string, unknown> | undefined)?.architecture ?? NaN)
    : null;
  const insights = result
    ? ((result.architecture as Record<string, unknown> | undefined)?.insights as Record<string, unknown> | undefined)
    : undefined;
  const risk = insights?.risk as Record<string, unknown> | undefined;
  const refactorPriority = (insights?.refactor_priority as Record<string, unknown>[] | undefined) ?? [];
  const topRefactor = refactorPriority[0] as { app?: string; reason?: string; priority?: number } | undefined;
  const primaryRiskApp = topRefactor?.app ?? (risk?.critical_apps as string[] | undefined)?.[0];

  return (
    <div className="page">
      <div className="noise" aria-hidden />
      <header className="hero">
        <p className="eyebrow">Arquitetura mensurável · não é lint nem testes</p>
        <h1 className="title">
          Mede a tua arquitetura
          <br />
          <span className="title-accent">antes de ela te medir a ti em produção.</span>
        </h1>
        <p className="lede lede-tight">
          Grafo real, ciclos (SCC), acoplamento e evolução entre commits — para saberes{" "}
          <strong className="lede-strong">o que estruturalmente vai falhar primeiro</strong>, não só um número genérico de
          “qualidade”.
        </p>

        <div className="row row-cta">
          <input
            className="input"
            value={repo}
            onChange={(e) => setRepo(e.target.value)}
            placeholder="https://github.com/org/repo (público, HTTPS)"
            onKeyDown={(e) => e.key === "Enter" && analyze()}
          />
          <button type="button" className="btn" onClick={analyze} disabled={loading || !repo.trim()}>
            {loading ? "A analisar…" : "Analisar repositório público"}
          </button>
          {DEMO_REPO_URL ? (
            <button type="button" className="btn btn-secondary" onClick={runPublicDemo} disabled={loading}>
              Ver exemplo (sem configurar)
            </button>
          ) : null}
        </div>
        <p className="microcopy">
          <Link to="/dashboard">Abrir dashboard SaaS</Link>
          {" · "}
          <span className="muted-inline">
            Demo local: <code>tools/sinaplint-demo-server/server.py</code> (8765) ou Django; proxy <code>/api</code> no Vite.
          </span>
        </p>
        {err && <p className="error">{err}</p>}
      </header>

      <section className="landing-grid" aria-labelledby="landing-why">
        <h2 id="landing-why" className="sr-only">
          Porquê SinapLint
        </h2>
        <article className="landing-card">
          <h3 className="landing-card-title">O problema não é só bugs</h3>
          <p>
            Muitos sistemas rebentam por <strong>arquitetura que degrada</strong> — ciclos de dependências, hubs demasiado
            acoplados, mudanças que puxam metade do repositório. Isso custa tempo e risco antes de aparecer no Sonar ou no ESLint.
          </p>
        </article>
        <article className="landing-card">
          <h3 className="landing-card-title">Não é commodity de “code quality”</h3>
          <p>
            Não substituímos o lint: medimos <strong>estrutura e dependências</strong> (incl. delta entre versões), para CI e
            equipas que querem falhar PR quando a arquitetura piora.
          </p>
        </article>
        <article className="landing-card">
          <h3 className="landing-card-title">Decisão em segundos</h3>
          <p>
            Em vez de só métricas soltas, o foco é: <strong>onde está o maior risco agora</strong> e porquê — para corrigires
            primeiro o que mais dói.
          </p>
        </article>
      </section>

      {result && score != null && (
        <section className="panel">
          {primaryRiskApp && (
            <div className="insight-callout" role="status">
              <p className="label">Maior risco estrutural (corrige isto primeiro)</p>
              <p className="insight-headline">
                <span className="insight-app">{primaryRiskApp}</span>
              </p>
              {topRefactor?.reason ? (
                <p className="insight-reason">{String(topRefactor.reason)}</p>
              ) : (
                <p className="insight-reason muted-inline">
                  Acoplamento elevado e/ou participação em ciclos — ver prioridade no relatório completo.
                </p>
              )}
            </div>
          )}
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

      <footer className="landing-footer">
        <p>
          <strong>SinapLint</strong> analisa o sistema como um todo — grafo, ciclos e risco estrutural — para impedir que a
          arquitetura degrade antes do custo aparecer em produção.
        </p>
      </footer>
    </div>
  );
}
