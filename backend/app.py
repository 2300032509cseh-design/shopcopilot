import os
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

import database
from nlp_engine import parse_voice_command, detect_language, PRODUCT_SYNONYMS
import services

load_dotenv()

app = Flask(__name__)
CORS(app)

database.init_db()

# In-memory Session State for Conversational Clarifications & Confirmations
pending_session_state = None

def get_auth_context():
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        payload = services.decode_jwt_token(token)
        if payload:
            return payload.get("user_id", 1), payload.get("shop_id", 1)
    return 1, 1 # Default demo user & shop fallback

def is_full_command(text: str) -> bool:
    text_lower = text.lower()
    has_product = any(syn in text_lower or syn in text for syn in PRODUCT_SYNONYMS.keys())
    has_action = any(k in text_lower or k in text for k in [
        'add', 'remove', 'took', 'took out', 'aaye', 'aaya', 'vachayi', 'gaye', 'gaya', 'sold', 'becha',
        'how much', 'kitna', 'yentha', 'order', 'predict', 'finish', 'చేర్చు', 'తీసుకెళ్లారు', 'వచ్చాయి',
        'ಸೇರಿಸು', 'ತೆಗೆದುಕೊಂಡರು', 'சேர்', 'அகற்று', 'ଆସିଲା', 'ନେଲେ', 'এলো', 'निल', 'आले', 'नेले', 'വന്നു', 'എടുത്തു',
        '追加', '減らした', 'añadir', 'quitar'
    ])
    return has_product and has_action

def get_product_clarification_msg(action, lang):
    if lang == 'te': return "ఏ సరుకును మార్చాలో దయచేసి పేరు చెప్పండి (ఉదా: బియ్యం, చక్కెర)."
    if lang == 'hi': return "कौन सा सामान बदलना है, कृपया नाम बताएं (उदा: चावल, चीनी)।"
    if lang == 'kn': return "ಯಾವ ಉತ್ಪನ್ನವನ್ನು ಬದಲಾಯಿಸಬೇಕೆಂದು ತಿಳಿಸಿ (ಉದಾ: ಅಕ್ಕಿ, ಸಕ್ಕರೆ)."
    if lang == 'ta': return "எந்த பொருளை மாற்ற வேண்டும் என்று கூறவும் (எ.கா: அரிசி, சர்க்கரை)."
    if lang == 'or': return "କେଉଁ ସାମଗ୍ରୀ ବଦଳାଇବେ କୁହନ୍ତୁ (ଯଥା: ଚାଉଳ, ଚିନି)।"
    if lang == 'bn': return "কোন পণ্যটি পরিবর্তন করতে চান বলুন (যেমন: চাল, চিনি)।"
    if lang == 'mr': return "कोणते उत्पादन बदलायचे ते सांगा (उदा: तांदूळ, साखर)."
    if lang == 'ml': return "ഏത് ഉൽപ്പന്നമാണ് മാറ്റേണ്ടതെന്ന് പറയുക (ഉദാ: അരി, പഞ്ചസാര)."
    if lang == 'ja': return "どの商品を変更しますか？（例：お米、砂糖）"
    if lang == 'es': return "¿Qué producto desea actualizar? (ej: Arroz, Azúcar)"
    return "Which product would you like to update? (e.g. Rice, Sugar, Biscuits)"

def get_unit_clarification_msg(qty, product_name, lang):
    q = int(qty) if isinstance(qty, float) and qty.is_integer() else qty
    pname = services.get_translated_product_name(product_name, lang)
    if lang == 'te': return f"మీరు {pname} {q} కిలోలు లేదా {q} బస్తాలు అని ఉద్దేశించారా?"
    if lang == 'hi': return f"क्या आपका मतलब {pname} {q} किलो या {q} बैग है?"
    if lang == 'kn': return f"ನೀವು {pname} {q} ಕೆಜಿ ಅಥವಾ {q} ಚೀಲಗಳು ಎಂದು ಉದ್ದೇಶಿಸಿದ್ದೀರಾ?"
    if lang == 'ta': return f"நீங்கள் {pname} {q} கிலோ அல்லது {q} மூட்டைகள் என கூறுகிறீர்களா?"
    if lang == 'or': return f"ଆପଣ {pname} {q} କିଲୋ କିମ୍ବା {q} ବସ୍ତା ବୋଲି କହୁଛନ୍ତି କି?"
    if lang == 'bn': return f"আপনি কি {pname} {q} কেজি বা {q} ব্যাগ বোঝাতে চেয়েছেন?"
    if lang == 'mr': return f"तुमचा अर्थ {pname} {q} किलो किंवा {q} पोते आहे का?"
    if lang == 'ml': return f"{pname} {q} കിലോ അല്ലെങ്കിൽ {q} ചാക്കുകൾ എന്നാണോ ഉദ്ദേശിച്ചത്?"
    if lang == 'ja': return f"{pname} {q}キロ または {q}パック のことですか？"
    if lang == 'es': return f"¿Se refiere a {q} kg o {q} bolsas de {pname}?"
    return f"Do you mean {q} kg or {q} bags of {product_name}?"

def get_fallback_msg(lang):
    if lang == 'te': return "క్షమించండి, నాకు అర్థం కాలేదు. 'బియ్యం 5 బస్తాలు వచ్చాయి' లేదా 'చక్కెర ఎంత ఉంది?' అని చెప్పి చూడండి."
    if lang == 'hi': return "क्षमा करें, मुझे समझ नहीं आया। 'चावल 5 बैग आये हैं' या 'चीनी कितनी है?' बोलकर देखें।"
    if lang == 'kn': return "ಕ್ಷಮಿಸಿ, ಅರ್ಥವಾಗಲಿಲ್ಲ. 'ಅಕ್ಕಿ 5 ಚೀಲಗಳು ಬಂದಿವೆ' ಅಥವಾ 'ಸಕ್ಕರೆ ಎಷ್ಟಿದೆ?' ಎಂದು ಹೇಳಿ."
    if lang == 'ta': return "மன்னிக்கவும், புரியவில்லை. 'அரிசி 5 மூட்டைகள் வந்தது' அல்லது 'சர்க்கரை எவ்வளவு இருக்கு?' என்று கூறவும்."
    if lang == 'or': return "କ୍ଷମା କରିବେ, ବୁଝିପାରିଲି ନାହିଁ। 'ଚାଉଳ ୫ ବସ୍ତା ଆସିଲା' କିମ୍ବା 'ଚିନି କେତେ ଅଛି?' କୁହନ୍ତୁ।"
    if lang == 'bn': return "দুঃখিত, বুঝতে পারিনি। 'চাল ৫ ব্যাগ এসেছে' বা 'চিনি কত আছে?' বলুন।"
    if lang == 'mr': return "क्षमस्व, समजले नाही. 'तांदूळ ५ पोते आले' किंवा 'साखर किती आहे?' असे म्हणा."
    if lang == 'ml': return "ക്ഷമിക്കണം, മനസ്സിലായില്ല. 'അരി 5 ചാക്കുകൾ വന്നു' അല്ലെങ്കിൽ 'പഞ്ചസാര എത്രയുണ്ട്?' എന്ന് പറയൂ."
    if lang == 'ja': return "すみません、よく分かりませんでした。「お米 5パック 追加」や「砂糖の在庫は？」とお話しください。"
    if lang == 'es': return "Lo siento, no entendí. Pruebe decir 'Arroz 5 bolsas' o '¿Cuánto azúcar hay?'."
    return "I couldn't quite catch that. Try saying 'Rice 5 bags added' or 'How much sugar is left?'"

# --- AUTHENTICATION ROUTES ---

@app.route("/api/auth/register", methods=["POST"])
def auth_register():
    data = request.json or {}
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    shop_name = data.get("shop_name", "My Shop")

    if not name or not email or not password:
        return jsonify({"success": False, "message": "Name, email, and password are required."}), 400

    res = services.register_user(name, email, password, shop_name)
    return jsonify(res)

@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    data = request.json or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required."}), 400

    res = services.login_user(email, password)
    return jsonify(res)

@app.route("/api/auth/me", methods=["GET"])
def auth_me():
    user_id, shop_id = get_auth_context()
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, shop_name FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({"success": False, "message": "User not found."}), 404

    return jsonify({
        "success": True,
        "user": dict(user),
        "shop_id": shop_id
    })

# --- CONVERSATION HISTORY ROUTES ---

@app.route("/api/conversations", methods=["GET", "POST"])
def manage_conversations():
    user_id, shop_id = get_auth_context()

    if request.method == "POST":
        data = request.json or {}
        title = data.get("title", "New Conversation")
        conv = services.create_conversation(shop_id, title)
        return jsonify({"success": True, "conversation": conv})

    convs = services.get_conversations(shop_id)
    return jsonify({"success": True, "conversations": convs})

@app.route("/api/conversations/<int:conv_id>/messages", methods=["GET"])
def get_conversation_msgs(conv_id):
    messages = services.get_conversation_messages(conv_id)
    return jsonify({"success": True, "messages": messages})

@app.route("/api/memory", methods=["GET", "POST"])
def manage_memories():
    user_id, shop_id = get_auth_context()

    if request.method == "POST":
        data = request.json or {}
        memory_type = data.get("memory_type", "vocabulary")
        key = data.get("key")
        value = data.get("value")
        if key and value:
            services.save_shop_memory(shop_id, memory_type, key, value)
            return jsonify({"success": True, "message": "Memory saved."})
        return jsonify({"success": False, "message": "Key and value required."}), 400

    memories = services.get_shop_memories(shop_id)
    return jsonify({"success": True, "memories": memories})

# --- MAIN VOICE & INVENTORY PROCESSOR ROUTE ---

@app.route("/api/process-voice", methods=["POST"])
def process_voice():
    global pending_session_state
    user_id, shop_id = get_auth_context()

    data = request.json or {}
    text = data.get("text", "").strip()
    user_pref_lang = data.get("language")
    conversation_id = data.get("conversation_id")
    confirmed = data.get("confirmed", False)

    if not text:
        return jsonify({"success": False, "message": "No voice text received."}), 400

    if not conversation_id:
        convs = services.get_conversations(shop_id)
        if convs:
            conversation_id = convs[0]['id']
        else:
            new_conv = services.create_conversation(shop_id, "Today's Inventory")
            conversation_id = new_conv['id']

    vocab_map = services.get_vocabulary_map(shop_id)
    custom_terms = list(vocab_map.keys())

    user_pref_lang = (data.get("language") or "").split("-")[0].lower()

    detected_script = detect_language(text)
    if user_pref_lang and user_pref_lang not in ['auto', 'en', '']:
        detected_lang = user_pref_lang
    elif detected_script != 'en':
        detected_lang = detected_script
    else:
        detected_lang = 'en'

    services.save_chat_message(conversation_id, "user", text, intent=None, language=detected_lang)

    def respond(res_dict):
        if isinstance(res_dict, dict) and "message" in res_dict:
            res_dict["speech_text"] = services.get_phonetic_speech_text(res_dict["message"], detected_lang)
        return jsonify(res_dict)

    # --- 1. HANDLE CONVERSATIONAL PENDING CLARIFICATION ---
    if pending_session_state and not confirmed:
        if is_full_command(text):
            pending_session_state = None
        else:
            state = pending_session_state
            text_lower = text.lower()

            if state.get("status") == "NEED_PRODUCT_CLARIFICATION":
                matched_product = None
                for syn, canonical in PRODUCT_SYNONYMS.items():
                    if syn in text_lower or syn in text:
                        matched_product = canonical
                        break

                if matched_product:
                    action = state.get("pending_action", "REMOVE_STOCK")
                    qty = state.get("quantity", 1.0)
                    unit = state.get("unit")
                    price = state.get("price")
                    pending_session_state = None

                    if action == "REMOVE_STOCK":
                        result = services.remove_stock(matched_product, qty, unit, price=price, raw_text=text, lang=detected_lang, shop_id=shop_id)
                    else:
                        result = services.add_stock(matched_product, qty, unit, price=price, raw_text=text, lang=detected_lang, shop_id=shop_id)

                    result["intent"] = action
                    services.save_chat_message(conversation_id, "copilot", result['message'], intent=action, language=detected_lang)
                    return respond(result)

            elif state.get("status") == "NEED_UNIT_CLARIFICATION":
                chosen_unit = None
                for u in ['kg', 'kilo', 'bags', 'bag', 'packets', 'packet', 'cartons', 'boxes', 'pieces', 'litres', 'కిలోలు', 'బస్తాలు', 'బ్యాగ్స్', 'బ్యాగ్', 'కిలో', 'किलो', 'बैग', 'ಚೀಲಗಳು', 'മൂட்டைகள்', 'ବସ୍ତା', 'パック']:
                    if u in text_lower or u in text:
                        chosen_unit = u
                        break

                if chosen_unit:
                    action = state.get("intent")
                    product_name = state.get("product")
                    qty = state.get("quantity", 1.0)
                    price = state.get("price")
                    pending_session_state = None

                    if action == "REMOVE_STOCK":
                        result = services.remove_stock(product_name, qty, chosen_unit, price=price, raw_text=text, lang=detected_lang, shop_id=shop_id)
                    else:
                        result = services.add_stock(product_name, qty, chosen_unit, price=price, raw_text=text, lang=detected_lang, shop_id=shop_id)

                    result["intent"] = action
                    services.save_chat_message(conversation_id, "copilot", result['message'], intent=action, language=detected_lang)
                    return jsonify(result)

    # --- 2. REGULAR NLP PARSING + CONTEXT RESOLUTION ---
    nlp_res = parse_voice_command(text, custom_vocab_terms=custom_terms)
    nlp_res = services.resolve_context_aware_command(conversation_id, nlp_res)

    intent = nlp_res.get("intent")
    product_name = nlp_res.get("product")
    qty = nlp_res.get("quantity")
    unit = nlp_res.get("unit")
    price = nlp_res.get("price")
    lang = detected_lang

    # Intent 0: GET_MEMORY (What do you remember about my shop?)
    if intent == "GET_MEMORY":
        res = services.get_shop_memory_summary(shop_id=shop_id, lang=lang)
        res["intent"] = intent
        services.save_chat_message(conversation_id, "copilot", res['message'], intent=intent, language=lang)
        return respond(res)

    # Intent 0.1: GET_BRIEFING (Daily Briefing)
    elif intent == "GET_BRIEFING":
        res = services.get_daily_briefing(shop_id=shop_id, lang=lang)
        res["intent"] = intent
        services.save_chat_message(conversation_id, "copilot", res['message'], intent=intent, language=lang)
        return respond(res)

    # Intent 0.2: GET_VALUATION (Total Inventory Value)
    elif intent == "GET_VALUATION":
        res = services.get_inventory_valuation(shop_id=shop_id, lang=lang)
        res["intent"] = intent
        services.save_chat_message(conversation_id, "copilot", res['message'], intent=intent, language=lang)
        return respond(res)

    # Intent 0.3: GET_MARGINS (Profit Margin Analysis)
    elif intent == "GET_MARGINS":
        res = services.get_product_margins(shop_id=shop_id, lang=lang)
        res["intent"] = intent
        services.save_chat_message(conversation_id, "copilot", res['message'], intent=intent, language=lang)
        return respond(res)

    # Intent 0.4: GET_SUPPLIER (Who supplies X?)
    elif intent == "GET_SUPPLIER":
        supplier = services.get_supplier_for_product(product_name, shop_id=shop_id)
        if supplier:
            prod_label = services.get_translated_product_name(product_name, lang) if product_name else ("సరుకులు" if lang == 'te' else "items")
            if lang == 'te':
                msg = f"{prod_label} ను {supplier['name']} సరఫరా చేస్తారు (ఫోన్: {supplier['contact_phone']}, ఆర్డర్ సమయం: {supplier['typical_lead_days']} రోజులు)."
            elif lang == 'hi':
                msg = f"{prod_label} की आपूर्ति {supplier['name']} करते हैं (फोन: {supplier['contact_phone']}, डिलीवरी समय: {supplier['typical_lead_days']} दिन)।"
            elif lang == 'kn':
                msg = f"{prod_label} ಅನ್ನು {supplier['name']} ಪೂರೈಸುತ್ತಾರೆ (ಫೋನ್: {supplier['contact_phone']}, ವಿತರಣಾ ಸಮಯ: {supplier['typical_lead_days']} ದಿನಗಳು)."
            elif lang == 'ta':
                msg = f"{prod_label} பொருளை {supplier['name']} விநியோகிக்கிறார் (போன்: {supplier['contact_phone']}, விநியோக நேரம்: {supplier['typical_lead_days']} நாட்கள்)."
            else:
                msg = f"{supplier['name']} supplies {supplier['products_supplied']} (Phone: {supplier['contact_phone']}, Lead time: {supplier['typical_lead_days']} days)."
        else:
            msg = "No supplier information found."
            if lang == 'te': msg = "ఏ సరఫరాదారుల సమాచారం దొరకలేదు."
            elif lang == 'hi': msg = "कोई आपूर्तिकर्ता जानकारी नहीं मिली।"
        services.save_chat_message(conversation_id, "copilot", msg, intent=intent, language=lang)
        return respond({"success": True, "intent": intent, "supplier": supplier, "language": lang, "message": msg})

    # Intent 1: LEARN_VOCABULARY
    elif intent == "LEARN_VOCABULARY":
        term = nlp_res.get("term")
        if term and qty:
            target_unit = unit or 'packets'
            res = services.learn_vocabulary(term, qty, target_unit, lang=lang, shop_id=shop_id)
            res["intent"] = intent
            services.save_chat_message(conversation_id, "copilot", res['message'], intent=intent, language=lang)
            return respond(res)
        else:
            msg = services.build_localized_msg('NEED_VOCAB', {'term': 'term'}, lang=lang)
            services.save_chat_message(conversation_id, "copilot", msg, intent=intent, language=lang)
            return respond({"success": False, "message": msg, "language": lang})

    # Intent 2: ADD_STOCK
    elif intent == "ADD_STOCK":
        if not product_name:
            pending_session_state = {
                "pending_action": "ADD_STOCK",
                "quantity": qty or 1.0,
                "unit": unit,
                "price": price,
                "status": "NEED_PRODUCT_CLARIFICATION"
            }
            msg = get_product_clarification_msg("ADD_STOCK", lang)
            services.save_chat_message(conversation_id, "copilot", msg, intent=intent, language=lang)
            return respond({
                "success": True,
                "status": "NEED_PRODUCT_CLARIFICATION",
                "intent": "ADD_STOCK",
                "language": lang,
                "message": msg
            })

        if qty is None:
            qty = 1.0

        product = services.get_product_by_name(product_name, shop_id)
        if product and not unit:
            pending_session_state = {
                "intent": "ADD_STOCK",
                "product": product['name'],
                "quantity": qty,
                "price": price,
                "status": "NEED_UNIT_CLARIFICATION"
            }
            msg = get_unit_clarification_msg(qty, product['name'], lang)
            services.save_chat_message(conversation_id, "copilot", msg, intent=intent, language=lang)
            return respond({
                "success": True,
                "status": "NEED_UNIT_CLARIFICATION",
                "intent": "ADD_STOCK",
                "product": product['name'],
                "quantity": qty,
                "language": lang,
                "message": msg
            })

        result = services.add_stock(product_name, qty, unit, price=price, raw_text=text, lang=lang, shop_id=shop_id)
        if result.get("status") == "NEED_VOCABULARY_LEARNING":
            pending_session_state = result

        result["intent"] = intent
        services.save_chat_message(conversation_id, "copilot", result['message'], intent=intent, language=lang)
        return respond(result)

    # Intent 3: REMOVE_STOCK
    elif intent == "REMOVE_STOCK":
        if not product_name:
            pending_session_state = {
                "pending_action": "REMOVE_STOCK",
                "quantity": qty or 1.0,
                "unit": unit,
                "price": price,
                "status": "NEED_PRODUCT_CLARIFICATION"
            }
            msg = get_product_clarification_msg("REMOVE_STOCK", lang)
            services.save_chat_message(conversation_id, "copilot", msg, intent=intent, language=lang)
            return respond({
                "success": True,
                "status": "NEED_PRODUCT_CLARIFICATION",
                "intent": "REMOVE_STOCK",
                "quantity": qty,
                "unit": unit,
                "language": lang,
                "message": msg
            })

        if qty is None:
            qty = 1.0

        product = services.get_product_by_name(product_name, shop_id)
        if product:
            # SAFETY CONFIRMATION CHECK FOR LARGE REMOVALS
            if not confirmed and (qty >= 20 or qty >= (product['quantity'] * 0.5)):
                pname_lang = services.get_translated_product_name(product['name'], lang)
                unit_lang = services.get_translated_unit_name(unit or product['unit'], lang)
                curr_unit_lang = services.get_translated_unit_name(product['unit'], lang)
                if lang == 'te':
                    msg = f"⚠️ ధృవీకరణ అవసరం: {pname_lang} నుండి {qty} {unit_lang} తీసివేయాలా? ప్రస్తుతం ఉన్న నిల్వ {product['quantity']} {curr_unit_lang}."
                elif lang == 'hi':
                    msg = f"⚠️ पुष्टि आवश्यक है: {pname_lang} से {qty} {unit_lang} बताएं? वर्तमान स्टॉक {product['quantity']} {curr_unit_lang} है।"
                elif lang == 'kn':
                    msg = f"⚠️ ದೃಢೀಕರಣ ಅಗತ್ಯವಿದೆ: {pname_lang} ನಿಂದ {qty} {unit_lang} ತೆಗೆದುಹಾಕಬೇಕೆ? ಪ್ರಸ್ತುತ ದಾಸ್ತಾನು {product['quantity']} {curr_unit_lang}."
                else:
                    msg = f"⚠️ Confirmation required: Remove {qty} {unit_lang} of {pname_lang}? Current stock is {product['quantity']} {curr_unit_lang}."
                return respond({
                    "success": True,
                    "status": "NEED_CONFIRMATION",
                    "intent": "REMOVE_STOCK",
                    "product": product['name'],
                    "quantity": qty,
                    "unit": unit or product['unit'],
                    "current_stock": product['quantity'],
                    "language": lang,
                    "message": msg
                })

            if not unit:
                pending_session_state = {
                    "intent": "REMOVE_STOCK",
                    "product": product['name'],
                    "quantity": qty,
                    "price": price,
                    "status": "NEED_UNIT_CLARIFICATION"
                }
                msg = get_unit_clarification_msg(qty, product['name'], lang)
                services.save_chat_message(conversation_id, "copilot", msg, intent=intent, language=lang)
                return respond({
                    "success": True,
                    "status": "NEED_UNIT_CLARIFICATION",
                    "intent": "REMOVE_STOCK",
                    "product": product['name'],
                    "quantity": qty,
                    "language": lang,
                    "message": msg
                })

        result = services.remove_stock(product_name, qty, unit, price=price, raw_text=text, lang=lang, shop_id=shop_id)
        if result.get("status") == "NEED_VOCABULARY_LEARNING":
            pending_session_state = result

        result["intent"] = intent
        services.save_chat_message(conversation_id, "copilot", result['message'], intent=intent, language=lang)
        return respond(result)

    # Intent 4: GET_STOCK
    elif intent == "GET_STOCK":
        result = services.get_stock(product_name, lang=lang, shop_id=shop_id)
        result["intent"] = intent
        services.save_chat_message(conversation_id, "copilot", result['message'], intent=intent, language=lang)
        return respond(result)

    # Intent 5: GET_LOW_STOCK
    elif intent == "GET_LOW_STOCK":
        result = services.get_low_stock(lang=lang, shop_id=shop_id)
        result["intent"] = intent
        services.save_chat_message(conversation_id, "copilot", result['message'], intent=intent, language=lang)
        return respond(result)

    # Intent 6: PREDICT_STOCKOUT
    elif intent == "PREDICT_STOCKOUT":
        result = services.predict_stockout(lang=lang, shop_id=shop_id)
        result["intent"] = intent
        services.save_chat_message(conversation_id, "copilot", result['message'], intent=intent, language=lang)
        return respond(result)

    # Intent 7: REORDER
    elif intent == "REORDER":
        result = services.generate_reorder(lang=lang, shop_id=shop_id)
        result["intent"] = intent
        services.save_chat_message(conversation_id, "copilot", result['message'], intent=intent, language=lang)
        return respond(result)

    # Intent 8: GET_SALES
    elif intent == "GET_SALES":
        txs = services.get_transactions(shop_id=shop_id, limit=10)
        removals = [t for t in txs if t['action'] == 'REMOVE']
        if removals:
            parts = [f"{t['product_name']}: {t['quantity']} {t['unit']}" for t in removals[:3]]
            summary_str = ", ".join(parts)
            msg = f"Recent sales: {summary_str}."
        else:
            msg = "No sales recorded yet today."

        services.save_chat_message(conversation_id, "copilot", msg, intent=intent, language=lang)
        return respond({"success": True, "intent": intent, "language": lang, "message": msg})

    # Fallback
    fallback_msg = get_fallback_msg(lang)
    services.save_chat_message(conversation_id, "copilot", fallback_msg, intent="UNKNOWN", language=lang)
    return respond({
        "success": False,
        "intent": "UNKNOWN",
        "language": lang,
        "message": fallback_msg
    })

# --- RESTFUL API ENDPOINTS ---

@app.route("/api/suppliers", methods=["GET", "POST"])
def manage_suppliers():
    user_id, shop_id = get_auth_context()
    if request.method == "POST":
        data = request.json or {}
        name = data.get("name")
        products_supplied = data.get("products_supplied", "General Goods")
        contact_phone = data.get("contact_phone", "")
        lead_days = int(data.get("typical_lead_days", 2))

        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO suppliers (name, products_supplied, contact_phone, typical_lead_days, shop_id)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(shop_id, name) DO UPDATE SET
                products_supplied = excluded.products_supplied,
                contact_phone = excluded.contact_phone,
                typical_lead_days = excluded.typical_lead_days
        """, (name, products_supplied, contact_phone, lead_days, shop_id))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": f"Supplier '{name}' saved."})

    suppliers = services.get_suppliers(shop_id)
    return jsonify({"success": True, "suppliers": suppliers})

@app.route("/api/analytics", methods=["GET"])
def get_analytics():
    user_id, shop_id = get_auth_context()
    valuation = services.get_inventory_valuation(shop_id)
    margins = services.get_product_margins(shop_id)
    briefing = services.get_daily_briefing(shop_id)
    txs = services.get_transactions(shop_id, limit=100)
    
    removals = [t for t in txs if t['action'] == 'REMOVE']
    revenue = sum(t['quantity'] * (t.get('price') or 0.0) for t in removals)
    items_sold = sum(t['quantity'] for t in removals)

    return jsonify({
        "success": True,
        "revenue": revenue,
        "items_sold": items_sold,
        "transactions_count": len(txs),
        "valuation": valuation,
        "margins": margins,
        "briefing": briefing
    })

@app.route("/api/briefing", methods=["GET"])
def get_briefing():
    user_id, shop_id = get_auth_context()
    briefing = services.get_daily_briefing(shop_id)
    return jsonify(briefing)

@app.route("/api/inventory/import-csv", methods=["POST"])
def import_inventory_csv_route():
    user_id, shop_id = get_auth_context()
    
    csv_content = None
    if 'file' in request.files:
        file = request.files['file']
        csv_content = file.read().decode('utf-8', errors='ignore')
    elif request.is_json:
        data = request.json or {}
        csv_content = data.get("csv_text")
    
    if not csv_content:
        return jsonify({"success": False, "message": "No CSV content or file provided."}), 400

    res = services.import_inventory_csv(csv_content, shop_id=shop_id)
    return jsonify(res)

@app.route("/api/inventory/bulk-add", methods=["POST"])
def bulk_add_inventory_route():
    user_id, shop_id = get_auth_context()
    data = request.json or {}
    products_list = data.get("products", [])
    res = services.bulk_add_products(products_list, shop_id=shop_id)
    return jsonify(res)

@app.route("/api/stock-assistant", methods=["GET"])
def stock_assistant_route():
    user_id, shop_id = get_auth_context()
    lang = request.args.get("lang", "en")
    res = services.get_stock_assistant_data(shop_id=shop_id, lang=lang)
    return jsonify(res)

@app.route("/api/products", methods=["GET", "POST"])
def manage_products():
    user_id, shop_id = get_auth_context()
    if request.method == "POST":
        data = request.json or {}
        name = data.get("name")
        category = data.get("category", "General")
        quantity = float(data.get("quantity", 0))
        unit = data.get("unit", "pieces")
        price = float(data.get("price", 0.0))
        purchase_price = float(data.get("purchase_price", price * 0.85))
        reorder_level = float(data.get("reorder_level", 10))
        avg_daily_usage = float(data.get("avg_daily_usage", 1.0))
        lead_days = int(data.get("supplier_lead_days", 2))

        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO products (name, category, quantity, unit, price, purchase_price, reorder_level, avg_daily_usage, supplier_lead_days, shop_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(shop_id, name) DO UPDATE SET
                category = excluded.category,
                quantity = excluded.quantity,
                unit = excluded.unit,
                price = excluded.price,
                purchase_price = excluded.purchase_price,
                reorder_level = excluded.reorder_level,
                avg_daily_usage = excluded.avg_daily_usage,
                supplier_lead_days = excluded.supplier_lead_days,
                updated_at = CURRENT_TIMESTAMP
        """, (name, category, quantity, unit, price, purchase_price, reorder_level, avg_daily_usage, lead_days, shop_id))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": f"Product '{name}' saved successfully!"})

    products = services.get_all_products(shop_id)
    return jsonify({"success": True, "products": products})

@app.route("/api/transactions", methods=["GET"])
def get_transactions():
    user_id, shop_id = get_auth_context()
    txs = services.get_transactions(shop_id)
    return jsonify({"success": True, "transactions": txs})

@app.route("/api/vocabulary", methods=["GET", "POST"])
def manage_vocabulary():
    user_id, shop_id = get_auth_context()
    if request.method == "POST":
        data = request.json or {}
        term = data.get("term")
        equivalent_qty = float(data.get("equivalent_qty", 1.0))
        equivalent_unit = data.get("equivalent_unit", "units")
        res = services.learn_vocabulary(term, equivalent_qty, equivalent_unit, shop_id=shop_id)
        return jsonify(res)

    vocab = services.get_vocabulary_map(shop_id)
    items = [{"term": k, "equivalent_qty": v['qty'], "equivalent_unit": v['unit']} for k, v in vocab.items()]
    return jsonify({"success": True, "vocabulary": items})

@app.route("/api/insights", methods=["GET"])
def get_insights():
    user_id, shop_id = get_auth_context()
    insights = services.get_insights(shop_id)
    return jsonify({"success": True, "insights": insights})

@app.route("/api/reorder", methods=["GET", "POST"])
def get_reorder():
    user_id, shop_id = get_auth_context()
    reorder = services.generate_reorder(shop_id=shop_id)
    return jsonify(reorder)

if __name__ == "__main__":
    print("[Shop Copilot Server] Starting Stage 1 Multilingual Flask API on http://127.0.0.1:5050 ...")
    app.run(host="127.0.0.1", port=5050, debug=True)
