from fastmcp import FastMCP
from typing import Dict, Any

app = FastMCP("COMMON")


@app.tool()
def parse_request_text(payload: Dict[str, Any]) -> Dict[str, Any]:
    lower = (payload.get("query") or "").lower()
    intent = "shipping_issue" if ("ship" in lower or "deliver" in lower) else "unknown"
    return {"parsed": {"intent": intent, "tokens": lower.split()}}


@app.tool()
def normalize_fields(ticket: Dict[str, Any] | None = None) -> Dict[str, Any]:
    ticket = ticket or {}
    priority = (ticket.get("ticket").get("priority") or "normal").lower()
    return {"ticket": {"priority": priority}}


@app.tool()
def add_flags_calculations(ticket: Dict[str, Any] | None = None, parsed: Dict[str, Any] | None = None) -> Dict[str, Any]:
    ticket = ticket or {}
    parsed = parsed or {}
    priority = ticket.get("ticket").get("priority", "normal")
    intent = parsed.get("intent")
    sla_risk = "high" if priority == "high" else ("medium" if intent == "shipping_issue" else "low")
    return {"flags": {"sla_risk": sla_risk}}


@app.tool()
def solution_evaluation(state: Dict[str, Any] | None = None) -> Dict[str, Any]:
    state = state or {}
    order = state.get("order")
    if order and order.get("status") == "in_transit" and order.get("eta_days", 99) <= 2:
        best = {"solution": "inform_and_wait", "score": 93}
    else:
        best = {"solution": "expedite_or_replace", "score": 85}
    return {"decision": best}


@app.tool()
def response_generation(state: Dict[str, Any] | None = None) -> Dict[str, Any]:
    state = state or {}
    name = (state.get("customer") or {}).get("name", "Customer")
    decision = (state.get("decision") or {}).get("solution", "reviewing")
    text = f"Hi {name}, we are working on your request. Proposed action: {decision}."
    return {"response": {"text": text}}


@app.tool()
def accept_payload(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    return {
        "ticket": {
            "id": payload.get("ticket_id"),
            "priority": payload.get("priority", "normal"),
            "status": "new",
        },
        "customer": {
            "name": payload.get("customer_name"),
            "email": payload.get("email"),
        },
        "query": payload.get("query", ""),
    }


@app.tool()
def store_answer(state: Dict[str, Any] | None = None) -> Dict[str, Any]:
    state = state or {}
    answer = state.get("answer")
    entities = dict(state.get("entities", {}))
    if answer and not entities.get("order_id"):
        entities["order_id"] = answer
    return {"entities": entities}


@app.tool()
def store_data(state: Dict[str, Any] | None = None) -> Dict[str, Any]:
    state = state or {}
    hits = state.get("kb_hits", [])
    return {"kb_summary": [hit.get("title") for hit in hits]}


@app.tool()
def update_payload(state: Dict[str, Any] | None = None) -> Dict[str, Any]:
    state = state or {}
    return {"decisions": {"final": state.get("decision"), "escalation": state.get("escalation")}}


@app.tool()
def output_payload(_: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return {"output": {"final": True}}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)

