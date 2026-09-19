with open('backend/nlp_engine.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = "    # 2. Reorder Intent"

new_intents = """    # 1.5 Memory Summary Intent
    if any(phrase in text_lower for phrase in [
        "what do you remember", "remember about my shop", "shop memory", "what you remember",
        "నా షాప్ గురించి నీకు ఏమి తెలుసు", "आपको मेरी दुकान के बारे में क्या याद है", "ನನ್ನ ಅಂಗಡಿಯ ಬಗ್ಗೆ ಏನು ನೆನಪಿದೆ"
    ]):
        return {
            "intent": "GET_MEMORY",
            "product": None,
            "quantity": None,
            "unit": None,
            "price": None,
            "confidence": 0.98,
            "language": detected_lang,
            "raw_text": text_clean
        }

    # 1.6 Daily Briefing Intent
    if any(phrase in text_lower for phrase in [
        "daily briefing", "morning briefing", "briefing", "shop briefing", "prepare it",
        "ఈరోజు బ్రీఫింగ్", "दैनिक ब्रीफिंग", "ದೈನಂದಿನ ಬ್ರೀಫಿಂಗ್"
    ]):
        return {
            "intent": "GET_BRIEFING",
            "product": None,
            "quantity": None,
            "unit": None,
            "price": None,
            "confidence": 0.98,
            "language": detected_lang,
            "raw_text": text_clean
        }

    # 1.7 Total Inventory Valuation Intent
    if any(phrase in text_lower for phrase in [
        "inventory value", "inventory worth", "money tied up", "total value of all", "value of stock",
        "మొత్తం నిల్వల విలువ", "कुल स्टॉक का मूल्य", "ಒಟ್ಟು ದಾಸ್ತಾನು ಮೌಲ್ಯ"
    ]):
        return {
            "intent": "GET_VALUATION",
            "product": None,
            "quantity": None,
            "unit": None,
            "price": None,
            "confidence": 0.95,
            "language": detected_lang,
            "raw_text": text_clean
        }

    # 1.8 Profit Margin Intent
    if any(phrase in text_lower for phrase in [
        "highest margin", "profit margin", "which margin", "best profit", "margin",
        "ఏ సరుకుపై ఎక్కువ లాభం", "सबसे ज्यादा मार्जिन", "ಹೆಚ್ಚಿನ ಲಾಭ"
    ]):
        return {
            "intent": "GET_MARGINS",
            "product": None,
            "quantity": None,
            "unit": None,
            "price": None,
            "confidence": 0.95,
            "language": detected_lang,
            "raw_text": text_clean
        }

    # 1.9 Supplier Lookup Intent
    if any(phrase in text_lower for phrase in [
        "who supplies", "supplier for", "who supply", "supplier", "suppliers",
        "ఎవరు సఫలై చేస్తారు", "कौन आपूर्ति करता है", "ಯಾರು ಪೂರೈಸುತ್ತಾರೆ"
    ]):
        product = None
        for syn, canonical in PRODUCT_SYNONYMS.items():
            if syn in text_lower or syn in text_clean:
                product = canonical
                break
        return {
            "intent": "GET_SUPPLIER",
            "product": product,
            "quantity": None,
            "unit": None,
            "price": None,
            "confidence": 0.95,
            "language": detected_lang,
            "raw_text": text_clean
        }

    # 2. Reorder Intent"""

text = text.replace(target, new_intents)
with open('backend/nlp_engine.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated nlp_engine.py successfully!")
