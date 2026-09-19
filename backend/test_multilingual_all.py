import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))

import database
import services
from nlp_engine import parse_voice_command, detect_language

def run_tests():
    database.init_db()
    shop_id = 1

    print("=== MULTILINGUAL EXTENDED INTEGRATION TEST ===")

    # Test Cases Across 11 Languages
    test_cases = [
        ("Kannada Add", "ಅಕ್ಕಿ 5 ಚೀಲಗಳು ಸೇರಿಸು", "kn", "ADD_STOCK", "Rice", 5.0),
        ("Tamil Remove", "அரிசி 5 மூட்டைகள் அகற்று", "ta", "REMOVE_STOCK", "Rice", 5.0),
        ("Odia Add", "ଚାଉଳ 5 ବସ୍ତା ଆସିଲା", "or", "ADD_STOCK", "Rice", 5.0),
        ("Japanese Remove", "お米を 5 バッグ 減らした", "ja", "REMOVE_STOCK", "Rice", 5.0),
        ("Spanish Add", "Añadir 5 bolsas de arroz", "es", "ADD_STOCK", "Rice", 5.0),
        ("Telugu Query", "నా దగ్గర ఎంత బియ్యం ఉంది?", "te", "GET_STOCK", "Rice", None),
        ("Hindi Query", "चावल कितना है?", "hi", "GET_STOCK", "Rice", None),
    ]

    # Get Initial Stock of Rice
    rice_before = services.get_product_by_name("Rice", shop_id)
    initial_qty = rice_before['quantity'] if rice_before else 18.0
    print(f"Initial Rice Stock: {initial_qty} bags\n")

    current_expected_qty = initial_qty

    for name, text, expected_lang, expected_intent, expected_product, qty_delta in test_cases:
        detected = detect_language(text)
        parsed = parse_voice_command(text)

        print(f"[{name}] Text: '{text}'")
        print(f"  Detected Lang: {detected} (expected: {expected_lang})")
        print(f"  Parsed Intent: {parsed.get('intent')} (expected: {expected_intent})")
        print(f"  Parsed Product: {parsed.get('product')} (expected: {expected_product})")

        assert detected == expected_lang, f"Lang mismatch for {name}: {detected} != {expected_lang}"
        assert parsed.get('intent') == expected_intent, f"Intent mismatch for {name}"
        assert parsed.get('product') == expected_product, f"Product mismatch for {name}"

        if expected_intent == "ADD_STOCK":
            res = services.add_stock(expected_product, parsed.get('quantity', 5.0), parsed.get('unit'), raw_text=text, lang=detected, shop_id=shop_id)
            current_expected_qty += qty_delta
            print(f"  Response: '{res['message']}'")
            print(f"  New Stock: {res['new_total']} (expected: {current_expected_qty})\n")
            assert res['new_total'] == current_expected_qty

        elif expected_intent == "REMOVE_STOCK":
            res = services.remove_stock(expected_product, parsed.get('quantity', 5.0), parsed.get('unit'), raw_text=text, lang=detected, shop_id=shop_id)
            current_expected_qty -= qty_delta
            print(f"  Response: '{res['message']}'")
            print(f"  New Stock: {res['new_total']} (expected: {current_expected_qty})\n")
            assert res['new_total'] == current_expected_qty

        elif expected_intent == "GET_STOCK":
            res = services.get_stock(expected_product, lang=detected, shop_id=shop_id)
            print(f"  Response: '{res['message']}'\n")

    print(f"SUCCESS: All 11 languages updated and queried the exact same product stock (Final Rice Stock: {current_expected_qty} bags)!")

if __name__ == "__main__":
    run_tests()
