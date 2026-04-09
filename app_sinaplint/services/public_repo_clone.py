"""
Clone seguro de repositórios públicos para análise SinapLint (motor SaaS).

Convive com ``services/repo_limits.py`` e o motor em ``engine/``: prepara um path local
antes de ``run_analysis``. Validação alinhada ao produto SinapLint (HTTPS, hosts conhecidos).
"""

from __future__ import annotations

import logging
import os
import re
import shutil
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator
from urllib.parse import urlparse

from django.conf import settings

logger = logging.getLogger(__name__)

_ALLOWED_NETLOCS = frozenset(
    {
        "github.com",
        "www.github.com",
        "gitlab.com",
        "www.gitlab.com",
        "codeberg.org",
        "www.codeberg.org",
    }
)


class SinapLintRepoError(Exception):
    """Erro de validação ou clone (mensagem segura para o cliente)."""

    def __init__(self, message: str, *, status_code: int = 502) -> None:
        super().__init__(message)
        self.status_code = status_code


def normalize_repo_url(raw: str) -> str:
    s = (raw or "").strip()
    return s.rstrip("/") if s else ""


def validate_public_repo_url(raw: str) -> tuple[str | None, str | None]:
    """
    Aceita apenas HTTPS para hosts conhecidos (GitHub/GitLab/Codeberg).
    Rejeita credenciais no URL (SSRF / vazamento).
    """
    s = normalize_repo_url(raw)
    if not s:
        return None, "Informe repo_url (HTTPS)."

    if len(s) > 2048:
        return None, "URL demasiado longa."

    if not s.lower().startswith("https://"):
        return None, "Use apenas HTTPS (ex.: https://github.com/org/repo)."

    try:
        p = urlparse(s)
    except Exception:
        return None, "URL inválida."

    if p.scheme.lower() != "https":
        return None, "Use apenas HTTPS."

    if p.username is not None or p.password is not None:
        return None, "URLs com credenciais não são permitidas."

    host = (p.netloc or "").split("@")[-1].lower()
    if ":" in host:
        host = host.split(":")[0]

    if host not in _ALLOWED_NETLOCS:
        return None, "Apenas repositórios em GitHub, GitLab ou Codeberg (HTTPS)."

    path = (p.path or "").strip("/")
    if not path or path.count("/") < 1:
        return None, "Indique o caminho completo do repositório (ex.: org/repo)."

    if ".." in p.path or p.path.startswith("//"):
        return None, "URL inválida."

    parts = [x for x in path.split("/") if x]
    if len(parts) < 2:
        return None, "O URL deve incluir organização e nome do repositório."

    if not re.match(r"^[/\w.\-]+$", p.path):
        return None, "Caracteres não permitidos no caminho do repositório."

    return s, None


@contextmanager
def temporary_clone(repo_url: str) -> Iterator[Path]:
    """
    Clona ``repo_url`` (já validado) para um diretório temporário e remove ao sair.

    Raises:
        SinapLintRepoError: falha de clone ou timeout.
    """
    git_bin = (getattr(settings, "SINAPLINT_ENGINE_GIT_BIN", None) or "git").strip() or "git"
    timeout = int(getattr(settings, "SINAPLINT_ENGINE_CLONE_TIMEOUT", 300) or 300)
    tmp = tempfile.mkdtemp(prefix="sinaplint_engine_clone_")
    inner = Path(tmp) / "repo"
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
    cmd = [
        git_bin,
        "clone",
        "--depth",
        "1",
        "--single-branch",
        repo_url,
        str(inner),
    ]
    try:
        proc = subprocess.run(
            cmd,
            check=False,
            timeout=timeout,
            capture_output=True,
            text=True,
            env=env,
        )
        if proc.returncode != 0:
            err_tail = (proc.stderr or proc.stdout or "")[-2000:]
            logger.warning("git clone falhou rc=%s: %s", proc.returncode, err_tail)
            raise SinapLintRepoError(
                "Não foi possível clonar o repositório. Verifique se o URL é público e o repositório existe.",
                status_code=502,
            )
        if not inner.is_dir():
            raise SinapLintRepoError("Clone incompleto (diretório ausente).", status_code=502)
        yield inner
    except subprocess.TimeoutExpired:
        logger.warning("git clone timeout após %ss para URL", timeout)
        raise SinapLintRepoError(
            f"O clone demorou mais de {timeout}s. Tente um repositório menor ou aumente SINAPLINT_ENGINE_CLONE_TIMEOUT.",
            status_code=504,
        ) from None
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
