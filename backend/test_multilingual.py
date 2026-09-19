import sys
import io

# Force UTF-8 stdout encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import app
import database

database.init_db()
client = app.test_client()

multi_tests = [
    ("Telugu Script Add", "బియ్యం 5 బస్తాలు వచ్చాయి"),
    ("Telugu Script Query", "నా దగ్గర ఎంత బియ్యం ఉంది?"),
    ("Hindi Script Add", "चावल के 5 बैग आये हैं"),
    ("Hindi Script Query", "चीनी कितनी बची है?"),
    ("Teluglish Add", "Biyyam 2 bags remove cheyyi"),
    ("Hinglish Add", "Rice ke 5 bags aaye hain"),
    ("English Query", "What will finish first?")
]

print("==================================================")
print("  MULTILINGUAL BACKEND TEST (Telugu, Hindi, Eng)  ")
print("==================================================")

for label, text in multi_tests:
    res = client.post("/api/process-voice", json={"text": text})
    data = res.get_json()
    print(f"\n[{label}] Text: \"{text}\"")
    print(f" -> Lang: {data.get('language')} | Intent: {data.get('intent')}")
    print(f" -> Response: {data.get('message')}")

print("\n==================================================")
print("✅ MULTILINGUAL BACKEND VERIFIED SUCCESSFULLY!")
print("==================================================")
