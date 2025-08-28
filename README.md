# LangGraph Customer Support Agent

A customer support workflow agent built with LangGraph that models 11-stage support processes using MCP (Model Context Protocol) server integration.

## 🏗️ Architecture Overview

This project implements a **graph-based customer support agent** that:
- Models customer support as 11 sequential stages
- Uses **LangGraph** for workflow orchestration
- Integrates **MCP servers** for ability execution
- Maintains **state persistence** across all stages
- Supports both **deterministic** and **non-deterministic** stage execution
- **Rule-based implementation** with LLM-ready prompt infrastructure for future AI integration

### Stage Flow
```
INTAKE → UNDERSTAND → PREPARE → ASK → WAIT → RETRIEVE → DECIDE → UPDATE → CREATE → DO → COMPLETE
```

## 📁 Project Structure

```
customer-agent/
├── agent/
│   ├── __init__.py
│   ├── config.py          # YAML configuration loader
│   ├── graph.py           # LangGraph workflow implementation
│   └── mcp_client.py      # MCP server client integration
├── config/
│   └── stages.yaml        # Stage definitions and ability mappings
├── mcp_server/
│   ├── __init__.py
│   ├── atlas_fastmcp_server.py    # External system integrations
│   └── common_fastmcp_server.py   # Internal processing tools
├── main.py                # Entry point
├── requirements.txt       # Dependencies
├── start_atlas_server.py  # ATLAS server launcher
└── start_common_server.py # COMMON server launcher
```

## 🚀 Quick Start



### 1. Install Dependencies
```bash
pip install -r requirements.txt
```
### 2. Run the MCP Servers
In separate terminal windows, start the two MCP servers:
**Terminal 1: Start ATLAS Server**
```bash
python start_atlas_server.py
```
**Terminal 2: Start COMMON Server**
```bash
python start_common_server.py
```

### 3. Run the Agent
```bash
python main.py
```

The agent will automatically:
- Load stage configurations from `config/stages.yaml`
- Execute all 11 stages sequentially
- Process the sample customer query
- Output the final structured payload

## 📋 Dependencies

The project requires these packages (see `requirements.txt`):
```
langgraph>=0.2.0    # Graph workflow orchestration
fastmcp>=0.4.0      # MCP server framework
requests>=2.31.0    # HTTP client for MCP calls
uvicorn>=0.24.0     # ASGI server (for future HTTP MCP integration)
```

## 🎯 Stage Definitions

### Deterministic Stages (Sequential Execution)
- **INTAKE**: Accept and initialize customer payload
- **UNDERSTAND**: Parse request text and extract entities
- **PREPARE**: Normalize fields, enrich records, add calculations
- **ASK**: Request clarifying information if needed
- **WAIT**: Capture and store customer responses
- **RETRIEVE**: Search knowledge base for relevant information
- **UPDATE**: Modify ticket status and close if resolved
- **CREATE**: Generate customer response draft
- **DO**: Execute API calls and trigger notifications
- **COMPLETE**: Output final structured payload

### Non-Deterministic Stage (Runtime Orchestration)
- **DECIDE**: Evaluate solutions and make escalation decisions based on confidence scores

## 🔧 MCP Server Integration

### Server Responsibilities

**ATLAS Server** (External Systems):
- `extract_entities`: Extract order IDs, dates from queries
- `enrich_records`: Fetch order information from external systems
- `clarify_question`: Generate clarifying questions
- `extract_answer`: Process customer responses
- `knowledge_base_search`: Search FAQ/KB systems
- `escalation_decision`: Determine if human escalation needed
- `update_ticket`: Modify ticket status in external systems
- `close_ticket`: Mark tickets as resolved
- `execute_api_calls`: Trigger CRM/order system actions
- `trigger_notifications`: Send customer notifications

**COMMON Server** (Internal Processing):
- `accept_payload`: Initialize customer request structure
- `parse_request_text`: Convert unstructured text to structured data
- `normalize_fields`: Standardize dates, codes, IDs
- `add_flags_calculations`: Compute priority and SLA risk scores
- `solution_evaluation`: Score potential solutions (1-100)
- `store_answer`: Update payload with customer responses
- `store_data`: Attach retrieved information to payload
- `response_generation`: Draft customer reply text
- `update_payload`: Record decision outcomes
- `output_payload`: Finalize structured output

## 📊 Sample Input/Output

### Input Payload
```json
{
  "customer_name": "Amiya",
  "email": "amiya@example.com", 
  "query": "My order 12345 has not been delivered yet.",
  "priority": "high",
  "ticket_id": "T-1001"
}
```

### Output Structure
The agent produces a comprehensive state object containing:
- Customer information and ticket details
- Parsed entities and enriched order data
- Knowledge base search results
- Solution evaluation and escalation decisions
- Generated response and action items
- Complete audit trail of all stage executions

## ⚙️ Configuration

### Stage Configuration (`config/stages.yaml`)
- **Input schema**: Defines expected customer payload structure
- **Stage definitions**: Maps each stage to its abilities and execution mode
- **Server routing**: Specifies which MCP server handles each ability
- **Decision threshold**: Configures escalation trigger (default: 90)
- **Stage prompts**: Provides execution guidance for each stage (ready for LLM integration)

### Customization
- Modify `stages.yaml` to add new abilities or change server routing
- Update `DECIDE_THRESHOLD` in `config/stages.yaml` to adjust escalation sensitivity
- Add new tools to MCP servers for extended functionality

## 🔍 Monitoring & Debugging

### Audit Trail
Every stage execution is logged with:
- Stage name and ability called
- MCP server used
- Input payload and output results
- Before/after state snapshots
- Execution timestamps

### State Management
The agent maintains persistent state across all stages:
- Customer and ticket information
- Parsed entities and enriched data
- Decision outcomes and escalation status
- Complete execution audit log

## 🤖 Current Implementation & Future AI Integration

### Rule-Based Architecture
The current implementation uses **deterministic rule-based logic** for all stage processing:
- **Hardcoded business rules** handle entity extraction, normalization, and decision making
- **Static thresholds** determine escalation (score < 90)
- **Predefined responses** generate customer communications
- **Fixed logic** processes customer queries and determines actions

### LLM-Ready Infrastructure
While currently rule-based, the architecture is **designed for seamless LLM integration**:

**Prompt Configuration (`config/stages.yaml`)**
Each stage includes a `prompt` field that defines the intended behavior:
```yaml
- name: DECIDE
  prompt: "Score solutions and escalate if score below threshold."
- name: CREATE  
  prompt: "Draft a clear customer response."
- name: ASK
  prompt: "Ask clarifying questions if critical fields are missing."
```

**Future LLM Integration Path**
The prompt infrastructure enables easy transition to AI-powered processing:
1. **Replace rule-based functions** with LLM calls using stage prompts
2. **Maintain same MCP architecture** - just swap tool implementations
3. **Preserve state management** and audit trail functionality

