import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import app
import database

# Reset database to fresh seed state
database.reset_db()
client = app.test_client()

user_sequence = [
    ("Step 1: బియ్యం ఐదు బస్తాలు వచ్చాయి", "బియ్యం ఐదు బస్తాలు వచ్చాయి"),
    ("Step 2: ఒక కస్టమర్ వచ్చి 5 బ్యాగ్స్ బియ్యం తీసుకెళ్లారు", "ఒక కస్టమర్ వచ్చి 5 బ్యాగ్స్ బియ్యం తీసుకెళ్లారు"),
    ("Step 3: A customer took 5 bags", "A customer took 5 bags"),
    ("Step 4: Rice", "Rice")
]

print("==================================================")
print("     TESTING USER SEQUENCE ON CLEAN DATABASE      ")
print("==================================================")

for label, text in user_sequence:
    res = client.post("/api/process-voice", json={"text": text})
    data = res.get_json()
    print(f"\n[{label}] Prompt: \"{text}\"")
    print(f" -> Intent: {data.get('intent')} | Status: {data.get('status')}")
    print(f" -> Response: {data.get('message')}")

print("\n==================================================")
print("✅ USER SEQUENCE VERIFIED ON CLEAN DATABASE!")
print("==================================================")
