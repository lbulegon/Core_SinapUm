import { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type Overview = {
  summary: {
    plan: { name: string; slug: string | null; max_analyses_per_month: number; max_repos: number };
    usage: {
      used: number;
      limit: number;
      unlimited: boolean;
      repos_used: number;
      repos_limit: number;
    };
  };
  billing: {
    plan: { name: string; slug: string | null };
    subscription: {
      status: string;
      current_period_end: string | null;
    } | null;
  };
  history: Array<{
    id: number;
    repo: string;
    score: number;
    created_at: string;
    architecture_score: number | null;
  }>;
};

function UsageCard({ data }: { data: Overview["summary"] }) {
  const { used, limit, unlimited } = data.usage;
  const pct = unlimited || limit <= 0 ? 0 : Math.min(100, (used / limit) * 100);
  return (
    <div className="dash-card">
      <h2 className="dash-card-title">Uso mensal</h2>
      <p className="dash-metric">
        {used} / {unlimited ? "∞" : limit}
      </p>
      {!unlimited && limit > 0 && (
        <div className="dash-bar-track">
          <div className="dash-bar-fill" style={{ width: `${pct}%` }} />
        </div>
      )}
      <p className="dash-sub">
        Repositórios: {data.usage.repos_used} / {data.usage.repos_limit || "∞"}
      </p>
      <p className="dash-sub">Plano: {data.plan.name}</p>
    </div>
  );
}

function BillingCard({ data }: { data: Overview["billing"] }) {
  const sub = data.subscription;
  return (
    <div className="dash-card">
      <h2 className="dash-card-title">Billing</h2>
      <p className="dash-metric">{data.plan.name}</p>
      {sub ? (
        <>
          <p className="dash-sub">Estado: {sub.status}</p>
          <p className="dash-sub">
            Renovação: {sub.current_period_end ? new Date(sub.current_period_end).toLocaleString() : "—"}
          </p>
        </>
      ) : (
        <p className="dash-sub">Sem assinatura Stripe (plano Free)</p>
      )}
    </div>
  );
}

function HistoryChart({ rows }: { rows: Overview["history"] }) {
  const chartData = useMemo(
    () =>
      [...rows]
        .reverse()
        .map((r) => ({
          label: new Date(r.created_at).toLocaleDateString(),
          score: r.score,
        })),
    [rows]
  );
  if (chartData.length === 0) {
    return <p className="dash-sub">Sem análises registadas (use POST com repo_url).</p>;
  }
  return (
    <div className="dash-chart">
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={chartData} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
          <XAxis dataKey="label" tick={{ fill: "#8a8278", fontSize: 11 }} />
          <YAxis domain={[0, 100]} tick={{ fill: "#8a8278", fontSize: 11 }} />
          <Tooltip
            contentStyle={{ background: "#12100e", border: "1px solid #2a2622", borderRadius: 8 }}
            labelStyle={{ color: "#f4eee6" }}
          />
          <Line type="monotone" dataKey="score" stroke="#c45c26" strokeWidth={2} dot={{ r: 3 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export function DashboardPage() {
  const [data, setData] = useState<Overview | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setErr(null);
    setLoading(true);
    try {
      const res = await fetch("/api/sinaplint/saas/dashboard/overview/", {
        credentials: "include",
      });
      if (res.status === 401 || res.status === 403) {
        setErr("Sessão necessária — inicia sessão no Django (mesmo domínio/porta com proxy).");
        setData(null);
        return;
      }
      if (!res.ok) {
        setErr(`Erro ${res.status}`);
        setData(null);
        return;
      }
      setData((await res.json()) as Overview);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Falha de rede");
      setData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <div className="page dash-page">
      <div className="noise" aria-hidden />
      <header className="dash-header">
        <div>
          <p className="eyebrow">SinapLint SaaS</p>
          <h1 className="title" style={{ marginBottom: "0.5rem" }}>
            Dashboard
          </h1>
          <p className="lede" style={{ marginBottom: 0 }}>
            Uso, plano e histórico de análises persistidas.
          </p>
        </div>
        <div className="dash-header-actions">
          <button type="button" className="btn btn-ghost" onClick={() => void load()}>
            Atualizar
          </button>
          <Link to="/" className="btn btn-ghost">
            ← Landing
          </Link>
        </div>
      </header>

      {loading && <p className="lede">A carregar…</p>}
      {err && <p className="error">{err}</p>}

      {data && !loading && (
        <>
          <div className="dash-grid-2">
            <UsageCard data={data.summary} />
            <BillingCard data={data.billing} />
          </div>
          <section className="panel dash-history-panel">
            <h2 className="dash-card-title">Evolução do score</h2>
            <HistoryChart rows={data.history} />
            <h3 className="dash-table-title">Últimas análises</h3>
            <div className="dash-table-wrap">
              <table className="dash-table">
                <thead>
                  <tr>
                    <th>Repo</th>
                    <th>Score</th>
                    <th>Data</th>
                  </tr>
                </thead>
                <tbody>
                  {data.history.slice(0, 15).map((h) => (
                    <tr key={h.id}>
                      <td>{h.repo}</td>
                      <td>{h.score}</td>
                      <td>{new Date(h.created_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}
    </div>
  );
}
