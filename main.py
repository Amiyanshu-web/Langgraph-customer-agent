import json
from agent.graph import run_pipeline


def main():
    sample_input = {
        "customer_name": "Amiya",
        "email": "amiya@example.com",
        "query": "My order 12345 has not been delivered yet.",
        "priority": "high",
        "ticket_id": "T-1001",
    }

    state = run_pipeline(sample_input)

    print("\n=== Final Payload ===")
    print(json.dumps(state, indent=2))


if __name__ == "__main__":
    main()

