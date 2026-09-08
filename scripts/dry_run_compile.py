"""Key-less dry-run compile check for `team.acanvas.json` submissions.

Ports the *blocking* subset of the main AgentCanvas repo's
`backend/app/compiler/{graph,topology,validators}.py` — graph topology and
required-field checks — into plain stdlib Python. It never imports crewai or
litellm and never talks to an LLM provider, so it needs no API keys and stays
safe to run on untrusted fork-PR content.

This intentionally does not port the warn-level checks (AC-W1xx/AC-W3xx —
unused agents, disabled-in-v1 node types, undefined template vars): those are
judgment calls for the human PR reviewer, not merge blockers. Only the
error-level checks that mean "this graph cannot compile into a Crew" are
included. Manually re-sync with the upstream module if it changes.

No third-party dependencies — see `build_index.py` for why.
"""
from __future__ import annotations

from typing import Any

#: frontend/src/nodes/registry.ts NODE_DEFINITIONS — compilable: false
NON_COMPILABLE_NODE_TYPES = frozenset({"note", "group"})

CONTEXT_HANDLE = "context"

#: mirrors backend/app/compiler/validators.py::REQUIRED_FIELDS
REQUIRED_FIELDS: dict[str, list[str]] = {
    "llm": ["provider", "model"],
    "agent": ["role", "goal", "backstory"],
    "task": ["description", "expected_output"],
    "tool": ["tool_id"],
    "crew": ["process"],
    "input": ["var_name", "label"],
}


class Graph:
    def __init__(self, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> None:
        self.nodes = nodes
        self.edges = edges
        self._by_id = {n["id"]: n for n in nodes}

    def node(self, node_id: str) -> dict[str, Any] | None:
        return self._by_id.get(node_id)

    def nodes_of_type(self, node_type: str) -> list[dict[str, Any]]:
        return [n for n in self.nodes if n["type"] == node_type and not n.get("ui", {}).get("bypassed")]

    def incoming(self, node_id: str, handle: str) -> list[dict[str, Any]]:
        result = []
        for e in self.edges:
            if e["target"] == node_id and e["targetHandle"] == handle:
                src = self.node(e["source"])
                if src is not None:
                    result.append(src)
        return result

    def normalize(self) -> "Graph":
        keep = {
            n["id"] for n in self.nodes
            if not n.get("ui", {}).get("bypassed") and n["type"] not in NON_COMPILABLE_NODE_TYPES
        }
        return Graph(
            nodes=[n for n in self.nodes if n["id"] in keep],
            edges=[e for e in self.edges if e["source"] in keep and e["target"] in keep],
        )


def _context_adjacency(graph: Graph) -> dict[str, list[str]]:
    adj: dict[str, list[str]] = {}
    for e in graph.edges:
        if e["targetHandle"] == CONTEXT_HANDLE:
            adj.setdefault(e["source"], []).append(e["target"])
    return adj


def find_cycle(graph: Graph) -> list[str] | None:
    adj = _context_adjacency(graph)
    state: dict[str, int] = {}
    path: list[str] = []
    found: list[str] | None = None

    def dfs(node_id: str) -> bool:
        nonlocal found
        state[node_id] = 1
        path.append(node_id)
        for nxt in adj.get(node_id, []):
            s = state.get(nxt, 0)
            if s == 1:
                found = path[path.index(nxt):]
                return True
            if s == 0 and dfs(nxt):
                return True
        path.pop()
        state[node_id] = 2
        return False

    for n in graph.nodes:
        if state.get(n["id"], 0) == 0 and dfs(n["id"]):
            break
    return found


def dry_run_compile(doc: dict[str, Any]) -> list[str]:
    """Returns a list of human-readable compile errors; empty means it would compile."""
    errors: list[str] = []
    g = Graph(nodes=list(doc.get("nodes", [])), edges=list(doc.get("edges", []))).normalize()

    crews = g.nodes_of_type("crew")
    if not crews:
        errors.append("AC-E101: no Crew node in the graph")
    for extra in crews[1:]:
        errors.append(f"AC-E102: multiple Crew nodes ({extra['id']!r} is extra)")

    crew = crews[0] if crews else None
    if crew is not None:
        if not g.incoming(crew["id"], "task"):
            errors.append(f"AC-E107: Crew {crew['id']!r} has no Task connected")
        if crew.get("data", {}).get("process") == "hierarchical" and not g.incoming(crew["id"], "llm"):
            errors.append(f"AC-E103: Crew {crew['id']!r} uses hierarchical process but has no manager LLM")

    cycle = find_cycle(g)
    if cycle:
        errors.append(f"AC-E105: context-edge cycle through {cycle}")

    for n in g.nodes:
        node_id = n["id"]
        data = n.get("data", {})
        for field in REQUIRED_FIELDS.get(n["type"], []):
            value = data.get(field)
            if value is None or str(value).strip() == "":
                code = "AC-E204" if n["type"] == "task" and field in ("description", "expected_output") else "AC-E201"
                errors.append(f"{code}: {n['type']} {node_id!r} is missing required field {field!r}")

        if n["type"] == "task" and not g.incoming(node_id, "agent"):
            errors.append(f"AC-E202: task {node_id!r} has no Agent connected")

    return errors


__all__ = ["Graph", "find_cycle", "dry_run_compile", "REQUIRED_FIELDS", "NON_COMPILABLE_NODE_TYPES"]
