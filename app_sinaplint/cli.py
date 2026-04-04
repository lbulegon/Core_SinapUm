"""
CLI SinapLint — interface estilo eslint/flake8 (`sinaplint check`).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Optional, Sequence, TextIO

from app_sinaplint.delta_runner import run_check_with_delta
from app_sinaplint.engine import MIN_PASS_SCORE, SinapLint, SinapLintOrchestrator
from app_sinaplint.fixer import SinapFixer
from app_sinaplint.reporters.json import dumps as json_dumps


def _ensure_project_root() -> Path:
    """Raiz Core_SinapUm (pai do pacote app_sinaplint)."""
    return Path(__file__).resolve().parent.parent


def _colorize(text: str, *, use_color: bool, kind: str) -> str:
    """Cores opcionais (`pip install colorama` recomendado em Windows)."""
    if not use_color:
        return text
    try:
        from colorama import Fore, Style

        colors = {
            "title": Fore.CYAN + Style.BRIGHT,
            "score_ok": Fore.GREEN,
            "score_warn": Fore.YELLOW,
            "score_bad": Fore.RED,
            "label": Fore.WHITE + Style.BRIGHT,
        }
        reset = Style.RESET_ALL
        prefix = colors.get(kind, "")
        return f"{prefix}{text}{reset}"
    except ImportError:
        return text


def _score_style(score: int, fail_under: int) -> str:
    if score < fail_under:
        return "score_bad"
    if score < 90:
        return "score_warn"
    return "score_ok"


def _resolve_color(args: argparse.Namespace) -> bool:
    if getattr(args, "no_color", False):
        return False
    if getattr(args, "color", False):
        return True
    if os.environ.get("NO_COLOR"):
        return False
    return sys.stdout.isatty()


def _print_report_human(
    result: dict[str, Any],
    stream: TextIO = sys.stdout,
    *,
    use_color: bool = False,
    fail_under: int = MIN_PASS_SCORE,
) -> None:
    """Relatório legível (score, problemas, sugestões, módulos)."""
    out = stream.write

    def emit(msg: str, kind: str = "") -> None:
        if kind and use_color:
            out(_colorize(msg, use_color=use_color, kind=kind) + "\n")
        else:
            out(msg + "\n")

    if use_color:
        try:
            import colorama

            colorama.init(strip=False)
        except ImportError:
            pass

    out("\n")
    emit("\U0001f9e0 SinapLint Report", "title")
    out("\n")
    score = int(result["score"])
    qual = result["quality"]
    score_line = f"\U0001f4ca Score: {score}/100 ({qual})"
    if use_color:
        emit(score_line, _score_style(score, fail_under))
    else:
        out(score_line + "\n")
    out("\n")

    st = result.get("structure") or {}
    errs = st.get("errors") or []
    if errs:
        emit("\u274c Estrutura:", "label")
        for e in errs:
            out(f"  - {e}\n")
        out("\n")
    else:
        if use_color:
            emit("Estrutura: OK (nada faltando)", "score_ok")
        else:
            out("Estrutura: OK (nada faltando)\n")
        out("\n")

    pats = result.get("pattern_issues") or []
    if pats:
        emit("\u26a0\ufe0f Padrões (regex):", "label")
        for p in pats:
            out(f"  - {p.get('path')} → {p.get('message')}\n")
        out("\n")

    asts = result.get("ast_issues") or []
    if asts:
        emit("AST:", "label")
        for a in asts:
            out(f"  - {a.get('path')} → {a.get('message')}\n")
        out("\n")

    sug = result.get("suggestions") or []
    if sug:
        emit("Sugestões:", "label")
        for s in sug:
            out(f"  • {s.get('problem')}: {s.get('suggestion')}\n")
        out("\n")

    ai_rf = result.get("ai_refactor") or []
    if ai_rf:
        emit("\U0001f916 Sugestões de refactor (heurísticas):", "label")
        for row in ai_rf:
            kind = row.get("kind", "")
            iss = row.get("issue") or {}
            ar = row.get("ai") or {}
            loc = iss.get("path") or ""
            msg = iss.get("message") or ""
            prefix = f"[{kind}]"
            if loc:
                out(f"  {prefix} {loc} — {msg}\n")
            else:
                out(f"  {prefix} {msg}\n")
            out(f"      → {ar.get('suggestion', '')}\n")
            ex = ar.get("example")
            if ex:
                out(f"      ex.: {ex}\n")
        out("\n")

    scores = result.get("scores") or {}
    if scores:
        emit("Scores por camada (0–100):", "label")
        out(
            f"  code: {scores.get('code')} | architecture: {scores.get('architecture')} | "
            f"modularity: {scores.get('modularity')}\n"
        )
        out("\n")

    ctx = result.get("_context") or {}
    metrics = ctx.get("metrics") or {}
    if metrics.get("django_apps_count"):
        emit("Apps Django (app_*) e dependências cruzadas:", "label")
        out(
            f"  apps: {metrics.get('django_apps_count')} | "
            f"arestas: {metrics.get('cross_app_dependency_edges')} | "
            f"peso: {metrics.get('total_dependency_weight')}\n"
        )
        out("\n")

    arch = result.get("architecture") or {}
    ins = arch.get("insights") or {}
    rk = ins.get("risk") or {}
    if rk:
        emit("Risco arquitetural (aggregado):", "label")
        out(
            f"  risk_score: {rk.get('risk_score')} | nível: {rk.get('risk_level')} | "
            f"critical: {', '.join(rk.get('critical_apps') or [])}\n"
        )
        out("\n")
    plan = ins.get("refactor_plan") or []
    if plan[:3]:
        emit("Plano de refactor (impacto → investimento):", "label")
        for row in plan[:5]:
            acts = row.get("actions") or []
            acts_s = "; ".join(acts) if acts else "—"
            out(
                f"  - {row.get('app')}: {row.get('priority')} "
                f"(impact_score {row.get('impact_score')}) — {acts_s}\n"
            )
        out("\n")
    rp = ins.get("refactor_priority") or []
    if rp[:3] and not plan:
        emit("Prioridade de refactor (legado):", "label")
        for row in rp[:5]:
            out(f"  - {row.get('app')}: {row.get('priority')} — {row.get('reason')}\n")
        out("\n")
    gods = ins.get("anti_patterns") or []
    if gods:
        emit("Anti-padrões (god app):", "label")
        for g in gods[:8]:
            out(f"  - {g.get('app')}: {g.get('reason')} (fan-in {g.get('fan_in')}, saídas {g.get('out_degree')})\n")
        out("\n")

    cyc = arch.get("cycles") or []
    if cyc:
        emit("Ciclos arquiteturais (SCC entre app_*):", "label")
        for group in cyc[:12]:
            out(f"  - {' → '.join(group)} (grupo)\n")
        if len(cyc) > 12:
            out(f"  … e mais {len(cyc) - 12} grupo(s)\n")
        out("\n")
    coup = (arch.get("coupling") or {}).get("issues") or []
    if coup:
        emit("Acoplamento (avisos):", "label")
        for line in coup[:10]:
            out(f"  - {line}\n")
        out("\n")

    delta = result.get("delta") or {}
    if delta.get("base_available"):
        emit("Delta vs branch base:", "label")
        dsc = int(delta.get("score_change") or 0)
        darch = int(delta.get("architecture_score_change") or 0)
        out(
            f"  score: {delta.get('score_before')} → {delta.get('score_after')} "
            f"({dsc:+d}) | "
            f"arch score: {darch:+d} | "
            f"tendência: {delta.get('trend')}\n"
        )
        if delta.get("new_cycles_count"):
            out(f"  novos grupos SCC: {delta.get('new_cycles_count')}\n")
        if delta.get("coupling_increased"):
            out("  peso de dependências entre apps aumentou em relação à base.\n")
        if delta.get("coupling_decreased"):
            out("  peso de dependências entre apps diminuiu em relação à base.\n")
        out("\n")

    ca = result.get("clean_architecture") or {}
    ca_sum = ca.get("summary") or {}
    n_v = int(ca_sum.get("violations_count") or 0)
    if n_v:
        emit("Clean Architecture (violações de camada):", "label")
        out(f"  {n_v} violação(ões); plano: {ca_sum.get('plan_items', 0)} item(ns)\n")
        for v in (ca.get("violations") or [])[:6]:
            out(
                f"  - {v.get('from_layer')}→{v.get('to_layer')}: "
                f"{v.get('from')} importa `{v.get('to_module')}`\n"
            )
        out("\n")

    emit("\U0001f4e6 Módulos orbitais:", "label")
    for m in result.get("modules") or []:
        out(
            f"  - {m['module']} | missing: {m.get('missing')} | penalty: {m['penalty']}\n"
        )
    out("\n")
    out("-" * 52 + "\n")


def cmd_check(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve() if args.root else _ensure_project_root()
    if not root.is_dir():
        print(f"Erro: diretório inválido: {root}", file=sys.stderr)
        return 2

    if getattr(args, "delta_base", None):
        result = run_check_with_delta(root, str(args.delta_base))
    else:
        result = SinapLintOrchestrator().run(root)
    fail_under = int(args.fail_under)

    if getattr(args, "smart_block", False):
        from app_sinaplint.engine.delta.blocking import DeltaBlocker, load_blocking_rules

        policy_path = getattr(args, "policy", None)
        rules = load_blocking_rules(Path(policy_path).resolve() if policy_path else None)
        rules["fail_under_score"] = fail_under
        result["blocking"] = DeltaBlocker(rules).evaluate(result)

    if args.json:
        payload = json_dumps(result)
        if args.output:
            Path(args.output).write_text(payload, encoding="utf-8")
            print(f"JSON escrito em {args.output}", file=sys.stderr)
        else:
            print(payload)
    else:
        use_color = _resolve_color(args)
        _print_report_human(
            result,
            use_color=use_color,
            fail_under=fail_under,
        )
        if args.output:
            Path(args.output).write_text(json_dumps(result), encoding="utf-8")
            print(f"JSON também gravado em {args.output}", file=sys.stderr)

    if getattr(args, "smart_block", False):
        from app_sinaplint.engine.delta.blocking import format_blocking_message

        b = result.get("blocking") or {}
        if b.get("blocked"):
            print("\n" + format_blocking_message(b), file=sys.stderr)
            return 1
        return 0

    if result["score"] < fail_under:
        print(
            f"\nFalha: score {result['score']} < {fail_under} (limiar).",
            file=sys.stderr,
        )
        return 1
    return 0


def cmd_pr_comment(args: argparse.Namespace) -> int:
    """Gera Markdown premium para comentário no PR (a partir do JSON do ``check``)."""
    inp = Path(args.input).resolve()
    if not inp.is_file():
        print(f"Erro: ficheiro não encontrado: {inp}", file=sys.stderr)
        return 2
    try:
        data = json.loads(inp.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"Erro ao ler JSON: {e}", file=sys.stderr)
        return 2

    from app_sinaplint.engine.delta.comment_formatter import generate_pr_comment

    sha = (getattr(args, "sha", None) or "").strip()
    if len(sha) > 7:
        sha = sha[:7]
    base_l = (getattr(args, "base_ref", None) or "").strip()
    body = generate_pr_comment(data, short_sha=sha, base_label=base_l)

    outp = getattr(args, "output", None)
    if outp:
        Path(outp).write_text(body, encoding="utf-8")
        print(f"Markdown escrito em {outp}", file=sys.stderr)
    else:
        print(body)
    return 0


def cmd_fix(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve() if args.root else _ensure_project_root()
    if not root.is_dir():
        print(f"Erro: diretório inválido: {root}", file=sys.stderr)
        return 2

    fixer = SinapFixer(root)
    dry = bool(args.dry_run)
    fixes = fixer.fix_files(dry_run=dry)

    print("\nSinapLint Fix\n")
    if dry:
        print("(modo dry-run: nenhum arquivo foi alterado)\n")
    if not fixes:
        print("Nada para corrigir no âmbito SinapLint (ou já marcado com sinaplint-autofix).")
    else:
        for fr in fixes:
            print(f"  - {fr.path}\n    {fr.description}")
    print()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sinaplint",
        description="Governança arquitetural do Core_SinapUm (estrutura, módulos PAOR, padrões, AST).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="sinaplint 1.0.0",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser(
        "check",
        help="Executa análise e reporta score, problemas e sugestões.",
    )
    check.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Raiz do projeto Core_SinapUm (default: pasta que contém app_sinaplint/).",
    )
    check.add_argument(
        "--json",
        action="store_true",
        help="Emitir resultado completo em JSON (stdout ou --output).",
    )
    check.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Gravar relatório JSON neste arquivo.",
    )
    check.add_argument(
        "--fail-under",
        type=int,
        default=MIN_PASS_SCORE,
        metavar="N",
        help=f"Exit code 1 se score < N (default: {MIN_PASS_SCORE}).",
    )
    check.add_argument(
        "--delta-base",
        type=str,
        default=None,
        metavar="REF",
        help=(
            "Comparar com o estado da branch base (ex.: main). "
            "Requer git e fetch da ref remota (ex.: origin/main). "
            "Inclui delta e delta_summary no JSON."
        ),
    )
    check.add_argument(
        "--smart-block",
        action="store_true",
        help=(
            "Aplicar política de bloqueio (score + delta: SCC, acoplamento, queda de score). "
            "Exit 1 se bloqueado. O limiar --fail-under define também fail_under_score. "
            "Ficheiro JSON opcional: --policy ou SINAPLINT_POLICY_JSON."
        ),
    )
    check.add_argument(
        "--policy",
        type=Path,
        default=None,
        metavar="PATH",
        help="JSON com regras (ver docs). Ignorado sem --smart-block.",
    )
    check.add_argument(
        "--color",
        action="store_true",
        help="Forçar cores no terminal (requer colorama).",
    )
    check.add_argument(
        "--no-color",
        action="store_true",
        help="Desativar cores (respeita também a variável NO_COLOR).",
    )
    check.set_defaults(func=cmd_check)

    pr_comm = sub.add_parser(
        "pr-comment",
        help="Gera Markdown para comentário no PR a partir do JSON do check (CI).",
    )
    pr_comm.add_argument(
        "-i",
        "--input",
        type=Path,
        required=True,
        help="Ficheiro JSON (ex.: sinaplint-report.json).",
    )
    pr_comm.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Gravar Markdown neste ficheiro (default: stdout).",
    )
    pr_comm.add_argument(
        "--sha",
        type=str,
        default="",
        help="SHA do commit (mostrado no cabeçalho; truncado a 7 caracteres).",
    )
    pr_comm.add_argument(
        "--base-ref",
        type=str,
        default="",
        metavar="BRANCH",
        help="Nome da branch base (rótulo no texto; opcional se já estiver em delta).",
    )
    pr_comm.set_defaults(func=cmd_pr_comment)

    fix = sub.add_parser(
        "fix",
        help="Aplica correções automáticas conservadoras (pause_orders, env_state). Rever diff antes de commitar.",
    )
    fix.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Raiz do projeto Core_SinapUm (default: pasta que contém app_sinaplint/).",
    )
    fix.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostra o que seria alterado sem gravar arquivos.",
    )
    fix.set_defaults(func=cmd_fix)

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(list(argv))
    if hasattr(args, "func"):
        return int(args.func(args))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
