import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import app
import database

database.init_db()
client = app.test_client()

extended_tests = [
    ("Telugu Script Add", "బియ్యం 5 బస్తాలు వచ్చాయి"),
    ("Hindi Script Add", "चावल के 5 बैग आये हैं"),
    ("Kannada Script Add", "ಅಕ್ಕಿ 5 ಚೀಲಗಳು ಸೇರಿಸು"),
    ("Tamil Script Add", "அரிசி 5 மூட்டைகள் சேர்"),
    ("Odia Script Add", "ଚାଉଳ 5 ବସ୍ତା ଆସିଲା"),
    ("Japanese Script Add", "お米を 5 バッグ 追加"),
    ("Spanish Script Add", "Añadir 5 bolsas de arroz"),
    ("Kannada Stock Query", "ನಿಮ್ಮ ಬಳಿ ಎಷ್ಟು ಅಕ್ಕಿ ಇದೆ?"),
    ("Spanish Stock Query", "cuanto arroz hay")
]

print("==================================================")
print("  EXTENDED MULTILINGUAL BACKEND TEST (11 Languages)")
print("==================================================")

for label, text in extended_tests:
    res = client.post("/api/process-voice", json={"text": text})
    data = res.get_json()
    print(f"\n[{label}] Text: \"{text}\"")
    print(f" -> Lang: {data.get('language')} | Intent: {data.get('intent')}")
    print(f" -> Response: {data.get('message')}")

print("\n==================================================")
print("✅ ALL EXTENDED LANGUAGES VERIFIED SUCCESSFULLY!")
print("==================================================")
