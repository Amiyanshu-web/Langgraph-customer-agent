from typing import Any, Dict

from langgraph.graph import StateGraph, END

from .config import load_stage_mapping, load_threshold_and_prompts
from .mcp_client import invoke_mcp_tool


DECIDE_THRESHOLD = 90
STAGE_PROMPTS: Dict[str, str] = {}


def _apply(current: Dict[str, Any], stage: str, ability: str, updates: Dict[str, Any], server: str | None = None) -> None:
    """Apply updates into current state dict and append an audit record."""
    audit = list(current.get("audit_log", []))
    before = {k: current.get(k) for k in updates.keys()}
    current.update(updates)
    after = {k: current.get(k) for k in updates.keys()}
    entry = {"stage": stage, "ability": ability, "server": server, "updates": updates, "before": before, "after": after}
    audit.append(entry)
    current["audit_log"] = audit


def _invoke(stage: str, ability: str, payload: Dict[str, Any], mapping: Dict[str, Dict[str, str]]):
    server = mapping.get(stage, {}).get(ability, "COMMON")
    
    # Use MCP client to call the tool
    return invoke_mcp_tool(server, ability, payload)



def _node_intake(state: Dict[str, Any], mapping: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
    current = dict(state)
    updates, server = _invoke("INTAKE", "accept_payload", current.get("input") or {}, mapping)
    _apply(current, "INTAKE", "accept_payload", updates, server)
    return current


def _node_understand(state: Dict[str, Any], mapping: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
    current = dict(state)
    up, sv = _invoke("UNDERSTAND", "parse_request_text", {"query": current.get("query")}, mapping)
    _apply(current, "UNDERSTAND", "parse_request_text", up, sv)
    up, sv = _invoke("UNDERSTAND", "extract_entities", {"query": current.get("query")}, mapping)
    _apply(current, "UNDERSTAND", "extract_entities", up, sv)
    return current


def _node_prepare(state: Dict[str, Any], mapping: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
    current = dict(state)
    up, sv = _invoke("PREPARE", "normalize_fields", {"ticket": current.get("ticket")}, mapping)
    _apply(current, "PREPARE", "normalize_fields", up, sv)
    up, sv = _invoke("PREPARE", "enrich_records", {"entities": current.get("entities")}, mapping)
    _apply(current, "PREPARE", "enrich_records", up, sv)
    up, sv = _invoke("PREPARE", "add_flags_calculations", {"ticket": current.get("ticket"), "parsed": current.get("parsed")}, mapping)
    _apply(current, "PREPARE", "add_flags_calculations", up, sv)
    return current


def _node_ask(state: Dict[str, Any], mapping: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
    current = dict(state)
    up, sv = _invoke("ASK", "clarify_question", current, mapping)
    _apply(current, "ASK", "clarify_question", up, sv)
    return current


def _node_wait(state: Dict[str, Any], mapping: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
    current = dict(state)
    up, sv = _invoke("WAIT", "extract_answer", current, mapping)
    _apply(current, "WAIT", "extract_answer", up, sv)
    up, sv = _invoke("WAIT", "store_answer", current, mapping)
    _apply(current, "WAIT", "store_answer", up, sv)
    return current


def _node_retrieve(state: Dict[str, Any], mapping: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
    current = dict(state)
    up, sv = _invoke("RETRIEVE", "knowledge_base_search", {"parsed": current.get("parsed")}, mapping)
    _apply(current, "RETRIEVE", "knowledge_base_search", up, sv)
    up, sv = _invoke("RETRIEVE", "store_data", current, mapping)
    _apply(current, "RETRIEVE", "store_data", up, sv)
    return current


def _node_decide(state: Dict[str, Any], mapping: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
    current = dict(state)
    up, sv = _invoke("DECIDE", "solution_evaluation", current, mapping)
    _apply(current, "DECIDE", "solution_evaluation", up, sv)
    decision = current.get("decision") or {}
    if (decision or {}).get("score", 0) < DECIDE_THRESHOLD:
        up, sv = _invoke("DECIDE", "escalation_decision", decision, mapping)
        _apply(current, "DECIDE", "escalation_decision", up, sv)
    else:
        _apply(current, "DECIDE", "escalation_decision", {"escalation": {"required": False}})
    up, sv = _invoke("DECIDE", "update_payload", current, mapping)
    _apply(current, "DECIDE", "update_payload", up, sv)
    return current


def _node_update(state: Dict[str, Any], mapping: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
    current = dict(state)
    up, sv = _invoke("UPDATE", "update_ticket", current, mapping)
    _apply(current, "UPDATE", "update_ticket", up, sv)
    up, sv = _invoke("UPDATE", "close_ticket", current, mapping)
    _apply(current, "UPDATE", "close_ticket", up, sv)
    return current


def _node_create(state: Dict[str, Any], mapping: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
    current = dict(state)
    up, sv = _invoke("CREATE", "response_generation", current, mapping)
    _apply(current, "CREATE", "response_generation", up, sv)
    return current


def _node_do(state: Dict[str, Any], mapping: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
    current = dict(state)
    up, sv = _invoke("DO", "execute_api_calls", current, mapping)
    _apply(current, "DO", "execute_api_calls", up, sv)
    up, sv = _invoke("DO", "trigger_notifications", current, mapping)
    _apply(current, "DO", "trigger_notifications", up, sv)
    return current


def _node_complete(state: Dict[str, Any], mapping: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
    current = dict(state)
    up, sv = _invoke("COMPLETE", "output_payload", current, mapping)
    _apply(current, "COMPLETE", "output_payload", up, sv)
    return current


def _build_graph(mapping: Dict[str, Dict[str, str]]) -> Any:
    g = StateGraph(dict)
    g.add_node("INTAKE", lambda s: _node_intake(s, mapping))
    g.add_node("UNDERSTAND", lambda s: _node_understand(s, mapping))
    g.add_node("PREPARE", lambda s: _node_prepare(s, mapping))
    g.add_node("ASK", lambda s: _node_ask(s, mapping))
    g.add_node("WAIT", lambda s: _node_wait(s, mapping))
    g.add_node("RETRIEVE", lambda s: _node_retrieve(s, mapping))
    g.add_node("DECIDE", lambda s: _node_decide(s, mapping))
    g.add_node("UPDATE", lambda s: _node_update(s, mapping))
    g.add_node("CREATE", lambda s: _node_create(s, mapping))
    g.add_node("DO", lambda s: _node_do(s, mapping))
    g.add_node("COMPLETE", lambda s: _node_complete(s, mapping))

    # Deterministic edges
    g.set_entry_point("INTAKE")
    g.add_edge("INTAKE", "UNDERSTAND")
    g.add_edge("UNDERSTAND", "PREPARE")
    g.add_edge("PREPARE", "ASK")
    g.add_edge("ASK", "WAIT")
    g.add_edge("WAIT", "RETRIEVE")
    g.add_edge("RETRIEVE", "DECIDE")
    g.add_edge("DECIDE", "UPDATE")
    g.add_edge("UPDATE", "CREATE")
    g.add_edge("CREATE", "DO")
    g.add_edge("DO", "COMPLETE")
    g.add_edge("COMPLETE", END)

    return g.compile()


def run_pipeline(input_payload: Dict[str, Any]) -> Dict[str, Any]:
    mapping = load_stage_mapping()
    global DECIDE_THRESHOLD, STAGE_PROMPTS
    DECIDE_THRESHOLD, STAGE_PROMPTS = load_threshold_and_prompts()
    print("Mapping:", mapping)
    print("*"*50)
    app = _build_graph(mapping)
    # print(app.get_graph().draw_mermaid_png())
    # print("*"*50)
    start: Dict[str, Any] = {"input": input_payload, **input_payload, "audit_log": [], "prompts": STAGE_PROMPTS}
    final_state: Dict[str, Any] = app.invoke(start)
    return final_state

