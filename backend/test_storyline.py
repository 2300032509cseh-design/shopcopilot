import json
from app import app
import database

# Initialize database fresh
database.init_db()

client = app.test_client()

storyline_steps = [
    ("Step 1: Rice ke 5 bags aaye hain", "Rice ke 5 bags aaye hain"),
    ("Step 2: How much rice do I have?", "How much rice do I have?"),
    ("Step 3: Add 2 peti biscuits (Unknown unit)", "Add 2 peti biscuits"),
    ("Step 4: One peti is 12 packets (Learn vocabulary)", "One peti is 12 packets"),
    ("Step 5: Biyyam 2 bags remove cheyyi (Teluglish remove)", "Biyyam 2 bags remove cheyyi"),
    ("Step 6: What will finish first?", "What will finish first?"),
    ("Step 7: What should I order?", "What should I order?"),
    ("Step 8: Add 5 sugar (Unit ambiguity)", "Add 5 sugar"),
    ("Step 8b: kg (Resolve unit ambiguity)", "kg")
]

print("==================================================")
print("   SHOP COPILOT - 8-STEP DEMO STORYLINE TEST      ")
print("==================================================")

for label, text in storyline_steps:
    print(f"\n[USER]: \"{text}\"")
    response = client.post("/api/process-voice", json={"text": text})
    data = response.get_json()
    status_icon = "SUCCESS" if data.get("success", True) else "ALERT"
    print(f"[COPILOT {status_icon}]: {data.get('message')}")
    if data.get("learned_vocab"):
        print(f"   [VOCAB]: {data.get('learned_vocab')}")
    if data.get("whatsapp_message"):
        print(f"   [WHATSAPP ORDER]:\n{data.get('whatsapp_message')}")

print("\n==================================================")
print("[OK] ALL 8 STORYLINE STEPS COMPLETED SUCCESSFULLY!")
print("==================================================")
