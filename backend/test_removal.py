import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from nlp_engine import parse_voice_command

test_removal_prompts = [
    "someone took out 2 bags of rice",
    "Rice 2 bags took out",
    "biyyam 2 bags remove cheyyi",
    "biyyam 2 bags teesukunaru",
    "బియ్యం 2 బస్తాలు తీసుకున్నారు",
    "బియ్యం 2 బస్తాలు తీసేశారు",
    "चावल 2 बैग निकाल लिया",
    "Sugar 3 kg sold"
]

print("--- TESTING STOCK SUBTRACTION / REMOVAL PARSING ---")
for prompt in test_removal_prompts:
    res = parse_voice_command(prompt)
    print(f"Prompt: \"{prompt}\"")
    print(f" -> Intent: {res['intent']} | Product: {res['product']} | Qty: {res['quantity']} | Unit: {res['unit']} | Lang: {res['language']}")
    print("-" * 60)
