with open('backend/services.py', 'r', encoding='utf-8') as f:
    text = f.read()

new_functions = """
# --- 6. SUPPLIERS, ANALYTICS & ADVANCED MEMORY SERVICES ---

def get_suppliers(shop_id=DEFAULT_SHOP_ID):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, products_supplied, contact_phone, typical_lead_days, last_order_date
        FROM suppliers
        WHERE shop_id = ?
        ORDER BY name ASC
    ''', (shop_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_supplier_for_product(product_name, shop_id=DEFAULT_SHOP_ID):
    suppliers = get_suppliers(shop_id)
    if not product_name:
        return suppliers[0] if suppliers else None
    p_clean = product_name.lower()
    for s in suppliers:
        if p_clean in s['products_supplied'].lower():
            return s
    return suppliers[0] if suppliers else None

def get_shop_memory_summary(shop_id=DEFAULT_SHOP_ID, lang='en'):
    vocab = get_vocabulary_map(shop_id)
    suppliers = get_suppliers(shop_id)
    products = get_all_products(shop_id)
    
    vocab_parts = [f"1 {term} = {v['qty']} {v['unit']}" for term, v in vocab.items()]
    vocab_str = ", ".join(vocab_parts) if vocab_parts else "peti (12 packets), bora (50 kg)"

    p_units = list(set([f"{p['name']} ({p['unit']})" for p in products[:3]]))
    p_units_str = ", ".join(p_units)

    sup_parts = [f"{s['products_supplied']} from {s['name']}" for s in suppliers[:2]]
    sup_str = ", ".join(sup_parts)

    msg = f"I remember that your custom units are: {vocab_str}. Your usual product units are: {p_units_str}. Suppliers: {sup_str}."
    
    if lang == 'te':
        msg = f"నాకు తెలుసు! మీ షాప్‌లో నేర్చుకున్న కొలతలు: {vocab_str}. ముఖ్యమైన నిల్వలు: {p_units_str}."
    elif lang == 'hi':
        msg = f"मुझे याद है! आपकी दुकान की मापें: {vocab_str}। मुख्य सामान: {p_units_str}।"
    elif lang == 'kn':
        msg = f"ನನಗೆ ನೆನಪಿದೆ! ನಿಮ್ಮ ಅಂಗಡಿಯ ಘಟಕಗಳು: {vocab_str}. ದಾಸ್ತಾನು: {p_units_str}."
    elif lang == 'ja':
        msg = f"覚えています！カスタム単位: {vocab_str}、主な在庫: {p_units_str}。"
    elif lang == 'es':
        msg = f"Recuerdo las unidades de tu tienda: {vocab_str}. En stock: {p_units_str}."

    return {
        "success": True,
        "language": lang,
        "vocabulary": vocab,
        "suppliers": suppliers,
        "message": msg
    }

def get_daily_briefing(shop_id=DEFAULT_SHOP_ID, lang='en'):
    products = get_all_products(shop_id)
    low_stock = [p for p in products if p['quantity'] <= p['reorder_level']]
    stockouts = predict_stockout(lang=lang, shop_id=shop_id)['predictions']
    reorder_res = generate_reorder(lang=lang, shop_id=shop_id)

    urgent_items = [s['product'] for s in stockouts if s['days_remaining'] <= 3]
    total_val = sum(p['quantity'] * (p.get('purchase_price') or p.get('price') or 0) for p in products)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE id = (SELECT user_id FROM shops WHERE id = ?)", (shop_id,))
    user = cursor.fetchone()
    conn.close()

    msg = f"Good morning! You have {len(low_stock)} items low in stock. "
    if urgent_items:
        msg += f"Urgent attention needed for: {', '.join(urgent_items)}. "
    msg += f"Total inventory valuation is ₹{total_val:,.0f}."

    if lang == 'te':
        msg = f"శుభోదయం! మీ షాప్‌లో {len(low_stock)} సరుకులు తక్కువగా ఉన్నాయి. మొత్తం నిల్వ విలువ ₹{total_val:,.0f}."
    elif lang == 'hi':
        msg = f"सुप्रभात! आपकी दुकान में {len(low_stock)} आइटम कम हैं। कुल स्टॉक मूल्य ₹{total_val:,.0f} है।"

    return {
        "success": True,
        "language": lang,
        "low_stock_count": len(low_stock),
        "urgent_items": urgent_items,
        "total_valuation": total_val,
        "reorder_items": reorder_res.get("items", []),
        "message": msg
    }

def get_inventory_valuation(shop_id=DEFAULT_SHOP_ID, lang='en'):
    products = get_all_products(shop_id)
    total_purchase_cost = sum(p['quantity'] * (p.get('purchase_price') or (p.get('price', 0)*0.85)) for p in products)
    total_market_value = sum(p['quantity'] * (p.get('price') or 0) for p in products)
    potential_profit = max(0.0, total_market_value - total_purchase_cost)

    msg = f"Your current inventory is worth approximately ₹{total_purchase_cost:,.0f} at purchase cost, with a potential retail market value of ₹{total_market_value:,.0f} (Estimated profit: ₹{potential_profit:,.0f})."
    
    if lang == 'te':
        msg = f"మీ ప్రస్తుత నిల్వల కొనుగోలు విలువ సుమారు ₹{total_purchase_cost:,.0f}, అమ్ముడుపోయే మార్కెట్ విలువ ₹{total_market_value:,.0f}."
    elif lang == 'hi':
        msg = f"आपके वर्तमान स्टॉक का खरीद मूल्य लगभग ₹{total_purchase_cost:,.0f} है, और बिक्री मूल्य ₹{total_market_value:,.0f} है।"

    return {
        "success": True,
        "language": lang,
        "total_purchase_cost": total_purchase_cost,
        "total_market_value": total_market_value,
        "potential_profit": potential_profit,
        "message": msg
    }

def get_product_margins(shop_id=DEFAULT_SHOP_ID, lang='en'):
    products = get_all_products(shop_id)
    margin_items = []

    for p in products:
        sell_p = p.get('price') or 0.0
        buy_p = p.get('purchase_price') or (sell_p * 0.85)
        margin = max(0.0, sell_p - buy_p)
        margin_pct = (margin / sell_p * 100) if sell_p > 0 else 0.0

        margin_items.append({
            "product": p['name'],
            "unit": p['unit'],
            "purchase_price": buy_p,
            "selling_price": sell_p,
            "margin": margin,
            "margin_pct": round(margin_pct, 1)
        })

    margin_items.sort(key=lambda x: x['margin'], reverse=True)
    top_margin = margin_items[0] if margin_items else None

    if top_margin:
        msg = f"The product with the highest profit margin is {top_margin['product']} with a margin of ₹{top_margin['margin']:g}/{top_margin['unit']} ({top_margin['margin_pct']}% profit margin)."
    else:
        msg = "No product margins calculated."

    if lang == 'te' and top_margin:
        msg = f"అత్యధిక లాభం ఇచ్చే సరుకు: {top_margin['product']} (ప్రతి {top_margin['unit']} పై ₹{top_margin['margin']:g} లాభం)."
    elif lang == 'hi' and top_margin:
        msg = f"सबसे ज्यादा मुनाफे वाला सामान: {top_margin['product']} (प्रति {top_margin['unit']} ₹{top_margin['margin']:g} लाभ)।"

    return {
        "success": True,
        "language": lang,
        "margins": margin_items,
        "top_margin_product": top_margin,
        "message": msg
    }
"""

if "def get_suppliers" not in text:
    text += new_functions
    with open('backend/services.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Added advanced services to backend/services.py!")
else:
    print("Services already present in backend/services.py")
