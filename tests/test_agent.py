"""Quick test of agent functionality."""
import sys
import agent

print("Testing agent with a simple query...")
print("=" * 60)

iteration = 0
for msg in agent.run_research_agent("Transformer models"):
    iteration += 1
    if msg["type"] == "log":
        print(f"[LOG] {msg['message']}")
    elif msg["type"] == "complete":
        print(f"\n[COMPLETE] Papers processed: {len(msg.get('papers', []))}")
        print(f"[COMPLETE] Contradictions found: {len(msg.get('contradictions', []))}")
        concepts = msg.get('concepts', [])
        if concepts:
            print(f"[COMPLETE] Key concepts: {', '.join(concepts[:5])}")

    if iteration > 30:  # Limit output for testing
        print("... (truncated for testing)")
        break

print("=" * 60)
print("Test complete!")
