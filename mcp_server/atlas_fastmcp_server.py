from fastmcp import FastMCP
from typing import Dict, Any, List

app = FastMCP("ATLAS")

FAKE_ORDERS = {
    "12345": {
        "order_id": "12345",
        "status": "in_transit",
        "eta_days": 2,
        "items": [{"sku": "SKU123", "name": "Wireless Mouse", "qty": 1}],
    }
}

KB = [
    {"id": "kb1", "title": "Delayed shipment policy", "score": 0.92, "intent": "shipping_issue"},
    {"id": "kb2", "title": "How to track your order", "score": 0.88, "intent": "shipping_issue"},
    {"id": "kb3", "title": "General support", "score": 0.5, "intent": "unknown"},
]

@app.tool()
def extract_entities(payload: Dict[str, Any]) -> Dict[str, Any]:
    words = (payload.get("query") or "").split()
    order_id = None
    for w in words:
        if w.isdigit() and len(w) >= 5:
            order_id = w
            break
    return {"entities": {"order_id": order_id}}


@app.tool()
def enrich_records(entities: Dict[str, Any] | None = None) -> Dict[str, Any]:
    entities = entities or {}
    order_id = entities.get("entities").get("order_id")
    order_info = FAKE_ORDERS.get(order_id)
    return {"order": order_info}


@app.tool()
def clarify_question(state: Dict[str, Any] | None = None) -> Dict[str, Any]:
    state = state or {}
    need_order = (state.get("entities") or {}).get("order_id") is None
    question = "Could you share your order id?" if need_order else "Thanks, we have all details."
    return {"ask": {"question": question}}


@app.tool()
def extract_answer(state: Dict[str, Any] | None = None) -> Dict[str, Any]:
    state = state or {}
    current_order = (state.get("entities") or {}).get("order_id")
    answer = None if current_order else "12345"
    return {"answer": answer}


@app.tool()
def knowledge_base_search(parsed: Dict[str, Any] | None = None) -> Dict[str, Any]:
    parsed = parsed or {}
    print("Parsed", parsed)
    intent = parsed.get("parsed").get("intent")
    hits: List[Dict[str, Any]] = [k for k in KB if k["intent"] == intent]
    if not hits:
        hits = [k for k in KB if k["intent"] == "unknown"]
    return {"kb_hits": hits}


@app.tool()
def update_ticket(state: Dict[str, Any] | None = None) -> Dict[str, Any]:
    state = state or {}
    ticket = dict(state.get("ticket") or {})
    ticket["status"] = "in_progress"
    return {"ticket": ticket}


@app.tool()
def close_ticket(state: Dict[str, Any] | None = None) -> Dict[str, Any]:
    state = state or {}
    ticket = dict(state.get("ticket") or {})
    if not (state.get("escalation") or {}).get("required"):
        ticket["status"] = "resolved"
    return {"ticket": ticket}


@app.tool()
def execute_api_calls(state: Dict[str, Any] | None = None) -> Dict[str, Any]:
    state = state or {}
    actions: List[str] = []
    decision = (state.get("decision") or {}).get("solution")
    if decision == "inform_and_wait":
        actions.append("no_api_needed")
    else:
        actions.append("expedite_shipping")
    return {"actions": actions}


@app.tool()
def trigger_notifications(state: Dict[str, Any] | None = None) -> Dict[str, Any]:
    state = state or {}
    email = (state.get("customer") or {}).get("email")
    return {"notifications": [{"type": "email", "to": email}]}

@app.tool()
def escalation_decision(decision: Dict[str, Any] | None = None) -> Dict[str, Any]:
    decision = decision or {}
    score = decision.get("score", 0)
    if score < 90:
        best = {"required": True, "reason": "Low confidence in solution"}
    else:
        best = {"required": False}
    return {"escalation": best}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

