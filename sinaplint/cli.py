"""
CLI SinapLint — interface estilo eslint/flake8 (`sinaplint check`).
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any, Optional, Sequence, TextIO

from sinaplint.engine import MIN_PASS_SCORE, SinapLint
from sinaplint.fixer import SinapFixer
from sinaplint.reporters.json import dumps as json_dumps


def _ensure_project_root() -> Path:
    """Raiz Core_SinapUm (pai do pacote sinaplint)."""
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

    lint = SinapLint(base_path=root)
    result = lint.run()
    fail_under = int(args.fail_under)

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

    if result["score"] < fail_under:
        print(
            f"\nFalha: score {result['score']} < {fail_under} (limiar).",
            file=sys.stderr,
        )
        return 1
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
        help="Raiz do projeto Core_SinapUm (default: pasta que contém sinaplint/).",
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

    fix = sub.add_parser(
        "fix",
        help="Aplica correções automáticas conservadoras (pause_orders, env_state). Rever diff antes de commitar.",
    )
    fix.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Raiz do projeto Core_SinapUm (default: pasta que contém sinaplint/).",
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
