"""Structural schema check for `team.acanvas.json` submissions.

This is a manually-synced port of the shape enforced by the (private) main
AgentCanvas repo's `backend/app/schemas/graph.py::CanvasDoc` — a public hub
repo receiving anonymous fork PRs cannot check out private repo code or
secrets into that untrusted CI context, so the check lives here as plain
stdlib Python instead of importing pydantic across repos. When the upstream
schema changes, this file needs a matching manual update.

No third-party dependencies — see `build_index.py` for why.
"""
from __future__ import annotations

from typing import Any

NODE_TYPES = frozenset({
    "llm", "agent", "task", "tool", "crew", "input", "output",
    "knowledge", "memory", "human", "router", "guardrail", "note", "group",
})

LICENSE_IDS = frozenset({
    "CC0-1.0", "MIT", "Apache-2.0", "CC-BY-4.0", "AGPL-3.0", "all-rights-reserved",
})

DOC_REQUIRED_FIELDS: dict[str, type | tuple[type, ...]] = {
    "schema_version": str,
    "app_version": str,
    "id": str,
    "name": str,
    "created_at": str,
    "updated_at": str,
    "viewport": dict,
    "nodes": list,
    "edges": list,
}

NODE_REQUIRED_FIELDS: dict[str, type | tuple[type, ...]] = {
    "id": str,
    "type": str,
    "position": dict,
    "data": dict,
}

EDGE_REQUIRED_FIELDS: dict[str, type | tuple[type, ...]] = {
    "id": str,
    "source": str,
    "sourceHandle": str,
    "target": str,
    "targetHandle": str,
}


def _check_fields(obj: Any, required: dict[str, type | tuple[type, ...]], where: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(obj, dict):
        return [f"{where}: expected an object, got {type(obj).__name__}"]
    for field, expected_type in required.items():
        if field not in obj:
            errors.append(f"{where}: missing required field {field!r}")
        elif not isinstance(obj[field], expected_type):
            errors.append(f"{where}.{field}: expected {expected_type}, got {type(obj[field]).__name__}")
    return errors


def check_schema(doc: Any) -> list[str]:
    """Returns a list of human-readable errors; empty means the document is well-formed."""
    errors = _check_fields(doc, DOC_REQUIRED_FIELDS, "$")
    if errors:
        # Top-level shape is broken enough that walking nodes/edges would just be noise.
        return errors

    viewport_errors = _check_fields(doc["viewport"], {"x": (int, float), "y": (int, float), "zoom": (int, float)}, "$.viewport")
    errors.extend(viewport_errors)

    license_id = doc.get("license")
    if license_id is not None and license_id not in LICENSE_IDS:
        errors.append(f"$.license: {license_id!r} is not one of {sorted(LICENSE_IDS)}")

    node_ids: set[str] = set()
    for i, node in enumerate(doc["nodes"]):
        where = f"$.nodes[{i}]"
        node_errors = _check_fields(node, NODE_REQUIRED_FIELDS, where)
        errors.extend(node_errors)
        if node_errors:
            continue
        if node["type"] not in NODE_TYPES:
            errors.append(f"{where}.type: {node['type']!r} is not one of {sorted(NODE_TYPES)}")
        if node["id"] in node_ids:
            errors.append(f"{where}.id: duplicate node id {node['id']!r}")
        node_ids.add(node["id"])
        pos_errors = _check_fields(node["position"], {"x": (int, float), "y": (int, float)}, f"{where}.position")
        errors.extend(pos_errors)

    for i, edge in enumerate(doc["edges"]):
        where = f"$.edges[{i}]"
        edge_errors = _check_fields(edge, EDGE_REQUIRED_FIELDS, where)
        errors.extend(edge_errors)
        if edge_errors:
            continue
        if edge["source"] not in node_ids:
            errors.append(f"{where}.source: {edge['source']!r} does not match any node id")
        if edge["target"] not in node_ids:
            errors.append(f"{where}.target: {edge['target']!r} does not match any node id")

    return errors


__all__ = ["NODE_TYPES", "LICENSE_IDS", "check_schema"]
