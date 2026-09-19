import os
import re
import json

# Comprehensive Multilingual Product Synonym Mapping across Languages
# (Telugu, Hindi, Kannada, Tamil, Odia, Bengali, Marathi, Malayalam, Japanese, Spanish, English)
PRODUCT_SYNONYMS = {
    # Rice
    'biyyam': 'Rice', 'chawal': 'Rice', 'rice': 'Rice', 'akki': 'Rice', 'arisi': 'Rice',
    'chawala': 'Rice', 'chal': 'Rice', 'tandul': 'Rice', 'ari': 'Rice', 'kome': 'Rice', 'arroz': 'Rice',
    'బియ్యం': 'Rice', 'చావల్': 'Rice', 'चावल': 'Rice', 'ಅಕ್ಕಿ': 'Rice', 'அரிசி': 'Rice',
    'ଚାଉଳ': 'Rice', 'চাল': 'Rice', 'तांदूळ': 'Rice', 'അരി': 'Rice', 'お米': 'Rice', 'ライス': 'Rice', '米': 'Rice',

    # Sugar
    'cheeni': 'Sugar', 'shakkar': 'Sugar', 'panchadara': 'Sugar', 'sugar': 'Sugar', 'chakkera': 'Sugar',
    'sakkare': 'Sugar', 'sarkkarai': 'Sugar', 'cini': 'Sugar', 'sakhar': 'Sugar', 'panchasara': 'Sugar',
    'satou': 'Sugar', 'azucar': 'Sugar', 'azúcar': 'Sugar',
    'పంచదార': 'Sugar', 'చక్కెర': 'Sugar', 'चीनी': 'Sugar', 'शक्कर': 'Sugar', 'ಸಕ್ಕರೆ': 'Sugar',
    'சர்க்கரை': 'Sugar', 'சீனி': 'Sugar', 'ଚିନି': 'Sugar', 'চিনি': 'Sugar', 'साखर': 'Sugar', 'പഞ്ചസാര': 'Sugar', '砂糖': 'Sugar',

    # Biscuits
    'biscuit': 'Biscuits', 'biscuits': 'Biscuits', 'bisuketto': 'Biscuits', 'galletas': 'Biscuits', 'galleta': 'Biscuits',
    'బిస్కెట్లు': 'Biscuits', 'బిస్కెట్': 'Biscuits', 'बिस्कुट': 'Biscuits', 'ಬಿಸ್ಕತ್ತು': 'Biscuits', 'ಬಿಸ್ಕಟ್': 'Biscuits',
    'பிஸ்கட்': 'Biscuits', 'ବିସ୍କୁଟ୍': 'Biscuits', 'বিস্কুট': 'Biscuits', 'बिस्किट': 'Biscuits',
    'ബിസ്കറ്റ്': 'Biscuits', 'ビスケット': 'Biscuits',

    # Oil
    'oil': 'Oil', 'telugupoo': 'Oil', 'nookulu': 'Oil', 'nune': 'Oil', 'tel': 'Oil',
    'enne': 'Oil', 'ennai': 'Oil', 'tela': 'Oil', 'enna': 'Oil', 'abura': 'Oil', 'oiru': 'Oil', 'aceite': 'Oil',
    'నూనె': 'Oil', 'तेल': 'Oil', 'ಎಣ್ಣೆ': 'Oil', 'எண்ணெய்': 'Oil', 'ତେଲ': 'Oil',
    'তেল': 'Oil', 'എണ്ണ': 'Oil', '油': 'Oil', 'オイル': 'Oil',

    # Milk
    'milk': 'Milk', 'doodh': 'Milk', 'paalu': 'Milk', 'haalu': 'Milk', 'paal': 'Milk',
    'khira': 'Milk', 'dudh': 'Milk', 'gyuunyuu': 'Milk', 'miruku': 'Milk', 'leche': 'Milk',
    'పాలు': 'Milk', 'दूध': 'Milk', 'ಹಾಲು': 'Milk', 'பால்': 'Milk', 'କ୍ଷୀର': 'Milk',
    'দুধ': 'Milk', 'പാൽ': 'Milk', '牛乳': 'Milk', 'ミルク': 'Milk',

    # Salt
    'salt': 'Salt', 'uppu': 'Salt', 'namak': 'Salt', 'luna': 'Salt', 'laban': 'Salt', 'shio': 'Salt', 'sal': 'Salt',
    'ఉప్పు': 'Salt', 'नमक': 'Salt', 'मीठ': 'Salt', 'ಉಪ್ಪು': 'Salt', 'உப்பு': 'Salt', 'ଲୁଣ': 'Salt', 'লবণ': 'Salt', 'ഉപ്പ്': 'Salt', '塩': 'Salt',

    # Wheat Flour / Atta
    'wheat': 'Wheat Flour', 'flour': 'Wheat Flour', 'atta': 'Wheat Flour', 'aata': 'Wheat Flour', 'harina': 'Wheat Flour',
    'గోధుమ పిండి': 'Wheat Flour', 'आटा': 'Wheat Flour', 'ಗೋಧಿ ಹಿಟ್ಟು': 'Wheat Flour', 'கோதுமை மாவு': 'Wheat Flour', 'ଅଟା': 'Wheat Flour', '小麦粉': 'Wheat Flour',

    # Dal
    'dal': 'Dal', 'daal': 'Dal', 'pappu': 'Dal', 'bele': 'Dal', 'paruppu': 'Dal', 'dali': 'Dal', 'parippu': 'Dal', 'lentejas': 'Dal',
    'పప్పు': 'Dal', 'दाल': 'Dal', 'ಬೇಳೆ': 'Dal', 'பருப்பு': 'Dal', 'ଡାଲି': 'Dal', 'ডাল': 'Dal', 'പരിപ്പ്': 'Dal',

    # Tea Powder
    'tea': 'Tea Powder', 'chai': 'Tea Powder', 'chaha': 'Tea Powder', 'té': 'Tea Powder',
    'టీ పొడి': 'Tea Powder', 'చాయ్': 'Tea Powder', 'चाय': 'Tea Powder', 'ಚಹಾ': 'Tea Powder', 'தேயிலை': 'Tea Powder', 'ଚା': 'Tea Powder', '紅茶': 'Tea Powder',

    # Soap
    'soap': 'Soap', 'sabbu': 'Soap', 'sabun': 'Soap', 'saboonu': 'Soap', 'sekken': 'Soap', 'jabon': 'Soap', 'jabón': 'Soap',
    'సబ్బు': 'Soap', 'साबुन': 'Soap', 'ಸಾಬೂನು': 'Soap', 'சோப்': 'Soap', 'ସାବୁନ୍': 'Soap', 'সাবান': 'Soap', 'साबण': 'Soap', '石鹸': 'Soap'
}

STANDARD_UNITS = [
    'bags', 'bag', 'kg', 'kilo', 'kilos', 'kilogram', 'kilograms',
    'cartons', 'carton', 'packets', 'packet', 'pkts', 'pkt',
    'boxes', 'box', 'litres', 'litre', 'ltr', 'dozens', 'dozen',
    'pieces', 'piece', 'pcs', 'crates', 'crate', 'bolsas', 'bolsa', 'sacos', 'paquetes', 'paquete', 'litros', 'litro',
    # Regional Unicode Units
    'బస్తాలు', 'బస్తా', 'కిలోలు', 'కిలో', 'ప్యాకెట్లు', 'ప్యాకెట్', 'లీటర్లు', 'లీటరు', 'పెట్టి',
    'बैग', 'किलो', 'पैकेट', 'लीटर', 'पेटी', 'बोरा', 'डब्बा',
    'ಚೀಲಗಳು', 'ಚೀಲ', 'ಕೆಜಿ', 'ಪ್ಯಾಕೆಟ್‌ಗಳು', 'ಲೀಟರ್', # Kannada
    'மூட்டைகள்', 'மூட்டை', 'கிலோ', 'பாக்கெட்டுகள்', 'லிட்டர்', # Tamil
    'ବସ୍ତା', 'କିଲୋ', 'ପ୍ୟାକେଟ୍', 'ଲିଟର', # Odia
    'ব্যাগ', 'কেজি', 'প্যাকেট', 'লিটার', # Bengali
    'पोते', 'पुडे', # Marathi
    'ചാക്കുകൾ', 'പാക്കറ്റുകൾ', 'ലിറ്റർ', # Malayalam
    'バッグ', 'キロ', 'パック', 'リットル', '箱', '個' # Japanese
]

NUMBER_WORDS = {
    'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
    'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50,
    'ek': 1, 'do': 2, 'teen': 3, 'char': 4, 'paanch': 5,
    'okati': 1, 'rendu': 2, 'moodu': 3, 'naalugu': 4, 'aidhu': 5,
    'ఒకటి': 1, 'రెండు': 2, 'మూడు': 3, 'నాలుగు': 4, 'ఐదు': 5,
    'एक': 1, 'दो': 2, 'तीन': 3, 'चार': 4, 'पांच': 5, 'पाँच': 5,
    'ಒಂದು': 1, 'ಎರಡು': 2, 'ಮೂರು': 3, 'ನಾಲ್ಕು': 4, 'ಐದು': 5, # Kannada
    'ஒன்று': 1, 'இரண்டு': 2, 'மூன்று': 3, 'நான்கு': 4, 'ஐந்து': 5, # Tamil
    'এক': 1, 'দুই': 2, 'তিন': 3, 'চার': 4, 'পাঁচ': 5, # Bengali / Odia
    'uno': 1, 'dos': 2, 'tres': 3, 'cuatro': 4, 'cinco': 5 # Spanish
}

FORBIDDEN_VOCAB_TERMS = {
    'a', 'an', 'the', 'customer', 'someone', 'person', 'people', 'man', 'took', 'take', 'taken',
    'add', 'added', 'remove', 'removed', 'sold', 'bought', 'rice', 'sugar', 'biscuits', 'oil', 'milk',
    'bags', 'bag', 'kg', 'kilo', 'packets', 'packet', 'cartons', 'carton', 'litres', 'litre',
    'what', 'how', 'which', 'when', 'who', 'where', 'why', 'is', 'are', 'means', 'ante', 'matlab'
}

def detect_language(text: str) -> str:
    text_lower = text.lower()
    if re.search(r'[\u0c00-\u0c7f]', text):
        return 'te' # Telugu Script
    
    # Romanized Telugu Keywords (Exhaustive dictionary)
    te_keywords = [
        'biyyam', 'biyam', 'biam', 'panchadara', 'panchadhara', 'chakkera', 'sakkera', 'nune', 'paalu', 'palu', 'uppu', 'pappu', 'godhuma', 'godhumapindi', 'teapodi', 'sabbu',
        'bastalu', 'basta', 'bagulu', 'baglu', 'kilolu', 'kilo', 'packettlu', 'packetlu', 'literlu', 'literu', 'peti', 'petilu',
        'entha', 'yentha', 'enni', 'yenni', 'ennayi', 'unnayi', 'unnai', 'unnay', 'undi', 'undhi', 'unnaya', 'undha', 'daggara', 'naa', 'nadaggara',
        'vachayi', 'vachindi', 'vachaayi', 'ochayi', 'ochindi', 'osthe', 'ochinay', 'vachinayi', 'vachaa', 'vachaam', 'vachinaye',
        'poyayi', 'poyindi', 'poyina', 'poyay', 'poyaa', 'poyinay', 'poyindhi', 'poinayi', 'poindi',
        'theesukunnaru', 'teesukunnaru', 'theesukonnaru', 'teesukonnaru', 'theesaru', 'teesaru', 'theesey', 'theeseyi', 'teesey', 'teeseyi',
        'theesa', 'theesi', 'teesa', 'teesi', 'teeyam', 'teeyi', 'thiyyi', 'thaya', 'tessukunnaru', 'tisukunaru', 'yesukunnaru',
        'ammanu', 'ammamu', 'ammesaru', 'ammesam', 'ammara', 'ammadu', 'ammakaalu', 'ammina', 'amminamu', 'ammesanu',
        'kavali', 'kaavali', 'kavalana', 'kavale', 'kavalasindi', 'cheyyi', 'chesey', 'chesam', 'chesaru', 'cheppu', 'cheppandi', 'cheppali', 'chudu', 'chudandi',
        'thakkuva', 'thakuva', 'ekkuva', 'saruku', 'sarukulu', 'samanu', 'samanulu', 'shoppu', 'dukanam', 'pettu', 'pettandi',
        'sarafara', 'sarafaraa', 'ante', 'yenti', 'enti', 'yem', 'yemi', 'em', 'emi'
    ]
    if any(w in text_lower for w in te_keywords):
        return 'te'

    if re.search(r'[\u0cb0-\u0cff]', text):
        return 'kn' # Kannada
    if re.search(r'[\u0b80-\u0bff]', text):
        return 'ta' # Tamil
    if re.search(r'[\u0b00-\u0b7f]', text):
        return 'or' # Odia
    if re.search(r'[\u0980-\u09ff]', text):
        return 'bn' # Bengali
    if re.search(r'[\u0d00-\u0d7f]', text):
        return 'ml' # Malayalam
    if re.search(r'[\u3040-\u30ff\u4e00-\u9faf]', text):
        return 'ja' # Japanese
    if re.search(r'[\u0900-\u097f]', text):
        if any(mr_w in text_lower for mr_w in ['आले', 'कमी', 'पुडे', 'पोते', 'तांदूळ', 'साखर', 'किती']):
            return 'mr' # Marathi
        return 'hi' # Hindi

    # Romanized Hindi Keywords
    hi_keywords = [
        'chawal', 'cheeni', 'shakkar', 'doodh', 'namak', 'kitna', 'kitni', 'kitne',
        'hai', 'hain', 'aaye', 'aaya', 'nikalo', 'nikal', 'batao', 'becha', 'bech', 'gaye', 'gaya',
        'khatam', 'baccha', 'bacha', 'maang', 'aapurti'
    ]
    if any(w in text_lower for w in hi_keywords):
        return 'hi'

    if any(es_w in text_lower for es_w in ['el ', 'la ', 'los ', 'las ', 'añadir', 'quitar', 'cuanto', 'cuánto', 'arroz', 'leche', 'aceite', 'azúcar', 'azucar', 'galletas', 'bolsas', 'vendió', 'llevó', 'llevaron']):
        return 'es' # Spanish
    return 'en'

def parse_with_local_rules(text: str, custom_vocab_terms: list = None) -> dict:
    text_clean = text.strip()
    text_lower = text_clean.lower()
    custom_vocab_terms = custom_vocab_terms or []
    detected_lang = detect_language(text_clean)

    # 1. Strict Vocabulary Definition Intent
    vocab_match = re.search(
        r'\b(?:one|1|1x|ఒకటి|ఒక|एक|ಒಂದು|ஒன்று)?\s*([a-zA-Z\u0c00-\u0c7f\u0cb0-\u0cff\u0b80-\u0bff\u0b00-\u0b7f\u0980-\u09ff\u0d00-\u0d7f\u0900-\u097f]+)\s+\b(?:means|ante|matlab|అంటే|मतलब|ಎಂದರೆ|என்றால்|=|is equal to|is)\b\s+(\d+(?:\.\d+)?)\s*([a-zA-Z\u0c00-\u0c7f\u0cb0-\u0cff\u0b80-\u0bff\u0b00-\u0b7f\u0980-\u09ff\u0d00-\u0d7f\u0900-\u097f]+)?',
        text_clean,
        re.IGNORECASE
    )
    if vocab_match:
        term, qty, unit = vocab_match.groups()
        term_clean = term.strip().lower()
        if term_clean not in FORBIDDEN_VOCAB_TERMS and len(term_clean) > 1:
            return {
                "intent": "LEARN_VOCABULARY",
                "product": None,
                "quantity": float(qty) if qty else None,
                "unit": unit.strip().lower() if unit else None,
                "price": None,
                "term": term_clean,
                "confidence": 0.95,
                "language": detected_lang,
                "raw_text": text_clean
            }

    # 1.5 Memory Summary Intent
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
        "who supplies", "supplier for", "who supply", "supplier", "suppliers", "supply",
        "ఎవరు సరఫరా చేస్తారు", "ఎవరు సప్లై చేస్తారు", "ఎవరు పంపిణీ చేస్తారు", "సరఫరాదారు", "సప్లైయర్", "సరఫరా", "సప్లై",
        "कौन आपूर्ति करता है", "आपूर्ति", "सप्लायर", "आपूर्तिकर्ता", "ಯಾರು ಪೂರೈಸುತ್ತಾರೆ", "பொருட்களை யார் தருகிறார்கள்"
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

    # 2. Reorder Intent
    if any(phrase in text_lower for phrase in [
        "what should i order", "prepare order", "generate order", "order list", "kya order", "yem order",
        "ఏమి ఆర్డర్ చేయాలి", "ఆర్డర్ చెయ్యి", "क्या ऑर्डर करना है", "ऑर्डर तैयार करो",
        "ಏನು ಆರ್ಡರ್ ಮಾಡಬೇಕು", "என்ன ஆர்டர் செய்ய வேண்டும்", "què pedir"
    ]):
        return {
            "intent": "REORDER",
            "product": None,
            "quantity": None,
            "unit": None,
            "price": None,
            "confidence": 0.95,
            "language": detected_lang,
            "raw_text": text_clean
        }

    # 3. Stockout Prediction Intent
    if any(phrase in text_lower for phrase in [
        "will finish", "khatam ho", "pothundhi", "days left", "days remaining", "predict",
        "ముందు అయిపోతుంది", "ఏది అయిపోతుంది", "कौन सा खत्म होगा", "कब खत्म होगा", "ಮೊದಲು ಮುಗಿಯುತ್ತದೆ", "எப்போது தீரும்"
    ]):
        product = None
        for syn, canonical in PRODUCT_SYNONYMS.items():
            if syn in text_lower or syn in text_clean:
                product = canonical
                break
        return {
            "intent": "PREDICT_STOCKOUT",
            "product": product,
            "quantity": None,
            "unit": None,
            "price": None,
            "confidence": 0.90,
            "language": detected_lang,
            "raw_text": text_clean
        }

    # 4. Low Stock Query Intent
    if any(phrase in text_lower for phrase in [
        "low stock", "running low", "kam stock", "thakkuva", "khatam hone wala",
        "తక్కువగా ఉన్నాయి", "తక్కువ స్టాక్", "कम स्टॉक", "ಕಡಿಮೆ ದಾಸ್ತಾನು", "குறைந்த இருப்பு"
    ]):
        return {
            "intent": "GET_LOW_STOCK",
            "product": None,
            "quantity": None,
            "unit": None,
            "price": None,
            "confidence": 0.90,
            "language": detected_lang,
            "raw_text": text_clean
        }

    # 5. Get Sales / Usage Intent
    if any(phrase in text_lower for phrase in [
        "sell today", "sold today", "sales", "becha", "ammanu",
        "ఈరోజు ఏమి అమ్మాను", "ఈరోజు అమ్మకాలు", "आज क्या बेचा", "ಇಂದು ಮಾರಾಟ"
    ]):
        return {
            "intent": "GET_SALES",
            "product": None,
            "quantity": None,
            "unit": None,
            "price": None,
            "confidence": 0.90,
            "language": detected_lang,
            "raw_text": text_clean
        }

    # 6. Stock Query Intent
    if any(phrase in text_lower for phrase in [
        "how much", "kitna", "kitne", "yentha", "how many", "check stock", "is left", "remaining",
        "ఎంత ఉంది", "ఎన్ని ఉన్నాయి", "కిత్నా హై", "कितना है", "कितनी है", "ಎಷ್ಟಿದೆ", "ಎಷ್ಟು ఉంది", "ಎಷ್ಟು",
        "எவ்வளவு உள்ளது", "எவ்வளவு", "କେତେ ଅଛି", "କେତେ", "কত আছে", "কত", "किती आहे", "किती", "എത്രയുണ്ട്", "എത്ര",
        "在庫は", "いくら", "どれくらい", "cuanto hay", "cuánto hay", "cuántos hay", "cuantos hay", "cuanto", "cuánto", "stock de", "stock"
    ]):
        product = None
        for syn, canonical in PRODUCT_SYNONYMS.items():
            if syn in text_lower or syn in text_clean:
                product = canonical
                break
        return {
            "intent": "GET_STOCK",
            "product": product,
            "quantity": None,
            "unit": None,
            "price": None,
            "confidence": 0.90,
            "language": detected_lang,
            "raw_text": text_clean
        }

    # Quantity Extraction
    qty = None
    num_match = re.search(r'\b(\d+(?:\.\d+)?)\b', text_clean)
    if num_match:
        qty = float(num_match.group(1))
    else:
        for word, val in NUMBER_WORDS.items():
            if word in text_lower or word in text_clean:
                qty = float(val)
                break

    # Price Extraction
    price = None
    price_match = re.search(r'(?:rs\.?|rupees|inr|rate|price|at|for|రూపాయలు|రూ|రస|रुपये|रु|రూ|₹)\s*(\d+(?:\.\d+)?)', text_clean, re.IGNORECASE)
    if not price_match:
        price_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:rs\.?|rupees|inr|rate|price|రూపాయలు|రూ|రస|रुपये|रु|₹)', text_clean, re.IGNORECASE)
    if price_match:
        p_val = float(price_match.group(1))
        if p_val != qty:
            price = p_val

    # Product Extraction
    product = None
    for syn, canonical in PRODUCT_SYNONYMS.items():
        if syn in text_lower or syn in text_clean:
            product = canonical
            break

    # Unit Extraction
    unit = None
    all_units = STANDARD_UNITS + [t.lower() for t in custom_vocab_terms]
    for u in all_units:
        if u in text_lower or u in text_clean:
            unit = u
            break

    if not unit and qty is not None:
        unit_after_num = re.search(r'\b(?:\d+|\d+\.\d+|one|two|three|four|five|six|seven|eight|nine|ten|twenty|thirty|forty|fifty|ek|do|teen|char|paanch)\s+([a-zA-Z\u0c00-\u0c7f\u0cb0-\u0cff\u0b80-\u0bff\u0b00-\u0b7f\u0980-\u09ff\u0d00-\u0d7f\u0900-\u097f]+)\b', text_clean, re.IGNORECASE)
        if unit_after_num:
            candidate = unit_after_num.group(1).lower()
            skip_words = ['of', 'de', 'ke', 'to', 'in', 'ka', 'ki', 'ko', 'aaye', 'gaye', 'add', 'remove', 'cheyyi', 'karo', 'వచ్చాయి', 'తీసెయ్యి', 'आये', 'హటాఓ', 'took', 'out', 'customer', 'took out']
            if candidate not in skip_words and candidate not in FORBIDDEN_VOCAB_TERMS and not any(syn == candidate for syn in PRODUCT_SYNONYMS.keys()):
                unit = candidate

    # --- ACTION DETERMINATION: REMOVE VS ADD ---
    remove_keywords = [
        'customer took', 'a customer took', 'customer bought', 'customer', 'bought', 'took out', 'took',
        'take out', 'taken out', 'take away', 'took away', 'out', 'gaye', 'gaya', 'gayi', 'remove',
        'nikalo', 'nikala', 'sold', 'becha', 'sale', 'sell', 'minus', 'gave', 'de diya', 'went', 'le gaya',
        'poinayi', 'theeyi', 'theesey', 'poyay', 'thaya', 'thiyyi', 'teesukoni', 'teesukunaru',
        'theesuku', 'theesaru', 'vadaaru', 'poyayi', 'poyindi', 'poyaya', 'teesuko', 'cheyyi remove',
        'తీసుకున్నారు', 'తీసుకెళ్లారు', 'తీసేశారు', 'తీశారు', 'అమ్మేశారు', 'పోయాయి', 'పోయింది', 'అమ్మాను', 'తీసివేయి', 'తీయి', 'తీసేయి', 'తీయ్యి', 'తొలగించు', 'తీసివేయు',
        'హటాఓ', 'निकालो', 'निकाल लिया', 'ले गये', 'ले गया', 'बेच दिया', 'घटाओ',
        'ತೆಗೆದುಕೊಂಡರು', 'ತೆಗೆದುಕೊಂಡಿದಾರೆ', 'ತಗೆದುಕೊಂಡರು', 'ಕಡಿಮೆ', 'எடுத்துக்கொண்டார்', 'எடுத்தார்', 'அகற்று',
        'ନେଲେ', 'କାଢ଼ନ୍ତୁ', 'নিল', 'সরান', 'नेले', 'कमी', 'എടുത്തു', 'നീക്കം', '取った', '減らした', '売った', 'quitar', 'restar', 'llevó', 'se llevaron'
    ]

    add_keywords = [
        'add', 'added', 'aaye', 'aaya', 'laaya', 'plus', 'received', 'vachayi', 'vachindi', 'esuko', 'vesko', 'karo',
        'వచ్చాయి', 'చేర్చు', 'వేయి', 'ఆయా', 'आये', 'जोड़ो', 'లాయా',
        'ಸೇರಿಸು', 'ಬಂತు', 'சேர்', 'வந்தது', 'ଆସିଲା', 'এলো', 'आले', 'വന്നു', '追加', 'añadir', 'compro'
    ]

    def kw_match(kw):
        if re.search(r'[\u0c00-\u0c7f\u0cb0-\u0cff\u0b80-\u0bff\u0b00-\u0b7f\u0980-\u09ff\u0d00-\u0d7f\u0900-\u097f\u3040-\u30ff\u4e00-\u9faf]', kw):
            return kw in text_clean or kw in text_lower
        return bool(re.search(r'\b' + re.escape(kw) + r'\b', text_lower))

    is_remove = any(kw_match(k) for k in remove_keywords)
    is_add = any(kw_match(k) for k in add_keywords)

    if is_remove:
        intent = "REMOVE_STOCK"
    elif is_add:
        intent = "ADD_STOCK"
    elif qty is not None and (product is not None or unit is not None):
        intent = "ADD_STOCK"
    else:
        intent = "GET_STOCK"

    confidence = 0.85 if (qty or product or intent == "GET_STOCK") else 0.50

    return {
        "intent": intent,
        "product": product,
        "quantity": qty,
        "unit": unit,
        "price": price,
        "confidence": confidence,
        "language": detected_lang,
        "raw_text": text_clean
    }

def parse_with_gemini(text: str, custom_vocab_terms: list = None) -> dict:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None

    try:
        from google import genai
        client = genai.Client(api_key=api_key)

        prompt = f"""
You are an expert multilingual NLP parser for a shop inventory voice app.
Supported languages: English, Hindi, Telugu, Kannada, Tamil, Odia, Bengali, Marathi, Malayalam, Japanese, Spanish, Hinglish, Teluglish.

Known products: Rice, Sugar, Biscuits, Oil, Milk.
Custom shop units: {custom_vocab_terms or []}.

Allowed Intents: ADD_STOCK, REMOVE_STOCK, GET_STOCK, GET_LOW_STOCK, GET_SALES, PREDICT_STOCKOUT, REORDER, LEARN_VOCABULARY.

User Spoken Text: "{text}"

Respond ONLY with valid JSON:
{{
  "intent": "INTENT_NAME",
  "product": "Canonical Product Name (Rice/Sugar/Biscuits/Oil/Milk) or null",
  "quantity": number_or_null,
  "unit": "unit string or null",
  "price": number_or_null,
  "term": "custom unit term or null if LEARN_VOCABULARY",
  "language": "te" or "hi" or "kn" or "ta" or "or" or "bn" or "mr" or "ml" or "ja" or "es" or "en",
  "confidence": 0.95
}}
"""
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        resp_text = response.text.strip()
        if resp_text.startswith("```json"):
            resp_text = resp_text[7:]
        if resp_text.endswith("```"):
            resp_text = resp_text[:-3]

        data = json.loads(resp_text.strip())
        data["raw_text"] = text
        return data
    except Exception as e:
        print("[Gemini Multilingual NLP Error]:", e)
        return None

def parse_voice_command(text: str, custom_vocab_terms: list = None) -> dict:
    local_result = parse_with_local_rules(text, custom_vocab_terms)
    if local_result and local_result.get("confidence", 0) >= 0.85:
        return local_result

    gemini_result = parse_with_gemini(text, custom_vocab_terms)
    if gemini_result and gemini_result.get("intent"):
        return gemini_result

    return local_result
