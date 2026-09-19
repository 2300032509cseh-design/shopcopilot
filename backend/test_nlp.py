from nlp_engine import parse_voice_command

test_prompts = [
    "Rice ke 5 bags aaye hain",
    "How much rice do I have?",
    "Add 2 peti biscuits",
    "One peti is 12 packets",
    "Biyyam 2 bags remove cheyyi",
    "What will finish first?",
    "What should I order?",
    "Add 5 sugar"
]

print("--- TESTING NLP PARSER ---")
for prompt in test_prompts:
    res = parse_voice_command(prompt, custom_vocab_terms=['peti'])
    print(f"Prompt: '{prompt}'")
    print(f"  -> Intent: {res['intent']} | Product: {res['product']} | Qty: {res['quantity']} | Unit: {res['unit']} | Confidence: {res['confidence']}")
    print("-" * 50)
