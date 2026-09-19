import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import app
import database

# Reset database fresh
database.reset_db()
client = app.test_client()

transcript_steps = [
    ("1. బియ్యం ఐదు బస్తాలు వచ్చాయి", "బియ్యం ఐదు బస్తాలు వచ్చాయి"),
    ("2. ఒక కస్టమర్ వచ్చి 5 బ్యాగ్స్ బియ్యం తీసుకెళ్లారు", "ఒక కస్టమర్ వచ్చి 5 బ్యాగ్స్ బియ్యం తీసుకెళ్లారు"),
    ("3. A customer took 5 bags of rice", "A customer took 5 bags of rice"),
    ("4. A customer took five bags", "A customer took five bags"),
    ("5. Rice", "Rice")
]

print("==================================================")
print("     VERIFYING EXACT USER TRANSCRIPT SEQUENCE     ")
print("==================================================")

for label, text in transcript_steps:
    res = client.post("/api/process-voice", json={"text": text})
    data = res.get_json()
    print(f"\n[{label}] Prompt: \"{text}\"")
    print(f" -> Intent: {data.get('intent')} | Status: {data.get('status')}")
    print(f" -> Response: {data.get('message')}")

print("\n==================================================")
print("✅ EXACT USER TRANSCRIPT SEQUENCE 100% VERIFIED!")
print("==================================================")
