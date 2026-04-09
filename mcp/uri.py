"""
Parser e validação de URIs MCP Resources: sinap://{vertical}/{entity}/{id?}

Não altera nenhum comportamento existente do Core_SinapUm.
"""
import re
from dataclasses import dataclass
from typing import Optional, Dict, Any, List


# Verticais conhecidos (extensível)
DEFAULT_VERTICALS = frozenset({"vitrinezap", "motopro", "mrfoo", "system"})

# Entidades por vertical (extensível; None = qualquer)
DEFAULT_ENTITIES: Dict[str, Optional[frozenset]] = {
    "vitrinezap": frozenset({"catalog", "orders", "logs"}),
    "motopro": frozenset({"orders", "slots", "routes", "logs"}),
    "mrfoo": frozenset({"menu", "graph", "shopping_list", "orders", "logs"}),
    "system": frozenset({"tools", "logs", "prompts"}),
}

SINAP_SCHEME = "sinap"
URI_PATTERN = re.compile(
    r"^sinap://([a-z0-9_]+)/([a-z0-9_]+)(?:/([^?]+))?(?:\?(.*))?$",
    re.IGNORECASE,
)


@dataclass
class SinapURI:
    """URI parseada sinap://vertical/entity/id?query"""

    vertical: str
    entity: str
    id: Optional[str] = None
    query: Optional[Dict[str, str]] = None
    raw: Optional[str] = None

    def __str__(self) -> str:
        base = f"sinap://{self.vertical}/{self.entity}"
        if self.id:
            base += f"/{self.id}"
        if self.query:
            qs = "&".join(f"{k}={v}" for k, v in self.query.items())
            base += f"?{qs}"
        return base

    def to_dict(self) -> Dict[str, Any]:
        return {
            "vertical": self.vertical,
            "entity": self.entity,
            "id": self.id,
            "query": self.query,
            "raw": self.raw,
        }


def parse_sinap_uri(uri: str) -> Optional[SinapURI]:
    """
    Parse uma URI no formato sinap://vertical/entity/id ou sinap://vertical/entity?k=v.

    Returns:
        SinapURI se válida, None caso contrário.
    """
    if not uri or not uri.strip().lower().startswith("sinap://"):
        return None
    uri = uri.strip()
    m = URI_PATTERN.match(uri)
    if not m:
        return None
    vertical, entity, id_part, query_str = m.groups()
    vertical = vertical.lower()
    entity = entity.lower()
    id_part = id_part.strip("/") if id_part else None
    query: Optional[Dict[str, str]] = None
    if query_str:
        query = {}
        for part in query_str.split("&"):
            if "=" in part:
                k, v = part.split("=", 1)
                query[k.strip()] = v.strip()
    return SinapURI(
        vertical=vertical,
        entity=entity,
        id=id_part or None,
        query=query,
        raw=uri,
    )


def validate_sinap_uri(
    uri: str,
    allowed_verticals: Optional[frozenset] = None,
    allowed_entities: Optional[Dict[str, Optional[frozenset]]] = None,
) -> bool:
    """
    Valida se a URI é sinap:// e (opcionalmente) se vertical/entity são permitidos.
    """
    parsed = parse_sinap_uri(uri)
    if not parsed:
        return False
    allowed_verticals = allowed_verticals or DEFAULT_VERTICALS
    if parsed.vertical not in allowed_verticals:
        return False
    allowed_entities = allowed_entities or DEFAULT_ENTITIES
    entities = allowed_entities.get(parsed.vertical)
    if entities is not None and parsed.entity not in entities:
        return False
    return True


def is_sinap_uri(uri: str) -> bool:
    """Retorna True se a string é uma URI sinap:// válida."""
    return parse_sinap_uri(uri) is not None
