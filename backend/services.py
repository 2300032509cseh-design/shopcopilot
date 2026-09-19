import os
import math
import jwt
import csv
import io
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection, DEFAULT_SHOP_ID
from nlp_engine import PRODUCT_SYNONYMS

JWT_SECRET = os.environ.get("JWT_SECRET", "shop_copilot_secret_jwt_key_2026")

PRODUCT_NAMES_TRANSLATED = {
    'Rice': {
        'te': 'బియ్యం', 'hi': 'चावल', 'kn': 'ಅಕ್ಕಿ', 'ta': 'அரிசி', 'or': 'ଚାଉଳ',
        'bn': 'চাল', 'mr': 'तांदूळ', 'ml': 'അരി', 'ja': 'お米', 'es': 'Arroz', 'en': 'Rice'
    },
    'Sugar': {
        'te': 'చక్కెర', 'hi': 'चीनी', 'kn': 'ಸಕ್ಕರೆ', 'ta': 'சர்க்கரை', 'or': 'ଚିନି',
        'bn': 'চিনি', 'mr': 'साखर', 'ml': 'പഞ്ചസാര', 'ja': '砂糖', 'es': 'Azúcar', 'en': 'Sugar'
    },
    'Biscuits': {
        'te': 'బిస్కెట్లు', 'hi': 'बिस्कुट', 'kn': 'ಬಿಸ್ಕತ್ತು', 'ta': 'பிஸ்கட்', 'or': 'ବିସ୍କୁଟ୍',
        'bn': 'বিস্কুট', 'mr': 'बिस्किट', 'ml': 'ബിസ്കറ്റ്', 'ja': 'ビスケット', 'es': 'Galletas', 'en': 'Biscuits'
    },
    'Oil': {
        'te': 'నూనె', 'hi': 'तेल', 'kn': 'ಎಣ್ಣೆ', 'ta': 'எண்ணெய்', 'or': 'ତେଲ',
        'bn': 'তেল', 'mr': 'तेल', 'ml': 'എണ്ണ', 'ja': '油', 'es': 'Aceite', 'en': 'Oil'
    },
    'Milk': {
        'te': 'పాలు', 'hi': 'दूध', 'kn': 'ಹಾಲು', 'ta': 'பால்', 'or': 'କ୍ଷୀର',
        'bn': 'দুধ', 'mr': 'दूध', 'ml': 'പാൽ', 'ja': '牛乳', 'es': 'Leche', 'en': 'Milk'
    },
    'Salt': {
        'te': 'ఉప్పు', 'hi': 'नमक', 'kn': 'ಉಪ್ಪು', 'ta': 'உப்பு', 'or': 'ଲୁଣ',
        'bn': 'লবণ', 'mr': 'मीठ', 'ml': 'ഉപ്പ്', 'ja': '塩', 'es': 'Sal', 'en': 'Salt'
    },
    'Wheat Flour': {
        'te': 'గోధుమ పిండి', 'hi': 'आटा', 'kn': 'ಗೋಧಿ ಹಿಟ್ಟು', 'ta': 'கோதுமை மாவு', 'or': 'ଅଟା',
        'bn': 'আটা', 'mr': 'आटा', 'ml': 'ഗോതമ്പ് മാവ്', 'ja': '小麦粉', 'es': 'Harina', 'en': 'Wheat Flour'
    },
    'Dal': {
        'te': 'పప్పు', 'hi': 'दाल', 'kn': 'ಬೇಳೆ', 'ta': 'பருப்பு', 'or': 'ଡାଲି',
        'bn': 'ডাল', 'mr': 'दाल', 'ml': 'പരിപ്പ്', 'ja': 'レンズ豆', 'es': 'Lentejas', 'en': 'Dal'
    },
    'Tea Powder': {
        'te': 'టీ పొడి', 'hi': 'చాయ్ పత్తి', 'kn': 'ಚಹಾ ಪುಡಿ', 'ta': 'தேயிலை', 'or': 'ଚା',
        'bn': 'চা', 'mr': 'चहा', 'ml': 'തേയില', 'ja': '紅茶', 'es': 'Té', 'en': 'Tea Powder'
    },
    'Soap': {
        'te': 'సబ్బు', 'hi': 'साबुन', 'kn': 'ಸಾಬೂನು', 'ta': 'சோப்', 'or': 'ସାବୁନ୍',
        'bn': 'সাবান', 'mr': 'साबण', 'ml': 'സോപ്പ്', 'ja': '石鹸', 'es': 'Jabón', 'en': 'Soap'
    }
}

UNIT_TRANSLATIONS = {
    'bags': 'bags', 'bag': 'bags', 'bastalu': 'bags', 'basta': 'bags', 'bagulu': 'bags', 'baglu': 'bags',
    'బస్తాలు': 'bags', 'బస్తా': 'bags', 'బ్యాగ్స్': 'bags', 'బ్యాగ్': 'bags',
    'बैग': 'bags', 'बोरा': 'bags', 'ಚೀಲಗಳು': 'bags', 'ಚೀಲ': 'bags', 'மூட்டைகள்': 'bags', 'மூட்டை': 'bags',
    'ବସ୍ତା': 'bags', 'ব্যাগ': 'bags', 'पोते': 'bags', 'ചാക്കുകൾ': 'bags', 'バッグ': 'bags', 'bolsas': 'bags', 'bolsa': 'bags',

    'kg': 'kg', 'kilo': 'kg', 'kilos': 'kg', 'kilogram': 'kg', 'kilolu': 'kg', 'kilalu': 'kg',
    'కిలోలు': 'kg', 'కిలో': 'kg', 'కేజీలు': 'kg', 'కేజీ': 'kg', 'किलो': 'kg',
    'ಕೆಜಿ': 'kg', 'ಕிலோ': 'kg', 'கிலோ': 'kg', 'କିଲୋ': 'kg', 'কেজি': 'kg', 'കിലോ': 'kg', 'キロ': 'kg',

    'packets': 'packets', 'packet': 'packets', 'pkts': 'packets', 'pkt': 'packets', 'packettlu': 'packets', 'packetlu': 'packets',
    'ప్యాకెట్లు': 'packets', 'ప్యాకెట్': 'packets', 'पैकेट': 'packets',
    'ಪ್ಯಾಕೆಟ್‌ಗಳು': 'packets', 'பாக்கெட்டுகள்': 'packets', 'ପ୍ୟାକେଟ୍': 'packets',
    'প্যাকেট': 'packets', 'পুডে': 'packets', 'പാക്കറ്റുകൾ': 'packets', 'パック': 'packets', 'paquetes': 'packets', 'paquete': 'packets',

    'litres': 'litres', 'litre': 'litres', 'ltr': 'litres',
    'లీటర్లు': 'litres', 'లీటరు': 'litres', 'लीटर': 'litres',
    'ಲೀಟರ್': 'litres', 'லிட்டர்': 'litres', 'ଲିଟର': 'litres', 'লিটার': 'litres', 'ലിറ്റർ': 'litres', 'リットル': 'litres', 'litros': 'litres', 'litro': 'litres',

    'cartons': 'cartons', 'carton': 'cartons',
    'boxes': 'boxes', 'box': 'boxes', '箱': 'boxes', 'cajas': 'boxes', 'caja': 'boxes',
    'pieces': 'pieces', 'piece': 'pieces', 'pcs': 'pieces', '個': 'pieces',
    'dozens': 'dozens', 'dozen': 'dozens',
    'పెట్టి': 'peti', 'పేటి': 'peti', 'पेटी': 'peti', 'ಪೆಟ್ಟಿಗೆ': 'peti'
}

UNIT_NAMES_TRANSLATED = {
    'bags': {
        'te': 'బస్తాలు', 'hi': 'बैग', 'kn': 'ಚೀಲಗಳು', 'ta': 'மூட்டைகள்', 'or': 'ବସ୍ତା',
        'bn': 'ব্যাগ', 'mr': 'पोते', 'ml': 'ചാക്കുകൾ', 'ja': 'パック', 'es': 'bolsas', 'en': 'bags'
    },
    'kg': {
        'te': 'కిలోలు', 'hi': 'किलो', 'kn': 'ಕೆಜಿ', 'ta': 'கிலோ', 'or': 'କିଲୋ',
        'bn': 'কেজি', 'mr': 'किलो', 'ml': 'കിലോ', 'ja': 'キロ', 'es': 'kg', 'en': 'kg'
    },
    'packets': {
        'te': 'ప్యాకెట్లు', 'hi': 'पैकेट', 'kn': 'ಪ್ಯಾಕೆಟ್‌ಗಳು', 'ta': 'பாக்கெட்டுகள்', 'or': 'ପ୍ୟାକେଟ୍',
        'bn': 'প্যাকেট', 'mr': 'পুডে', 'ml': 'പാക്കറ്റുകൾ', 'ja': 'パック', 'es': 'paquetes', 'en': 'packets'
    },
    'litres': {
        'te': 'లీటర్లు', 'hi': 'लीटर', 'kn': 'ಲೀಟರ್', 'ta': 'லிட்டர்', 'or': 'ଲିଟର',
        'bn': 'লিটার', 'mr': 'लीटर', 'ml': 'ലിറ്റർ', 'ja': 'リットル', 'es': 'litros', 'en': 'litres'
    },
    'cartons': {
        'te': 'కార్టన్లు', 'hi': 'कार्टन', 'kn': 'ಕಾರ್ಟನ್‌ಗಳು', 'ta': 'கார்ட்டன்கள்', 'or': 'କାର୍ଟନ୍',
        'bn': 'কার্টন', 'mr': 'कार्टन', 'ml': 'കാർട്ടണുകൾ', 'ja': 'カートン', 'es': 'cajas', 'en': 'cartons'
    },
    'boxes': {
        'te': 'పెట్టెలు', 'hi': 'डब्बे', 'kn': 'ಪೆಟ್ಟಿಗೆಗಳು', 'ta': 'பெட்டிகள்', 'or': 'ବାକ୍ସ',
        'bn': 'বাক্স', 'mr': 'खोके', 'ml': 'പെട്ടികൾ', 'ja': '箱', 'es': 'cajas', 'en': 'boxes'
    },
    'pieces': {
        'te': 'పీసులు', 'hi': 'पीस', 'kn': 'ಪೀಸ್‌ಗಳು', 'ta': 'பீஸ்கள்', 'or': 'ପିସ୍',
        'bn': 'পিস', 'mr': 'नग', 'ml': 'പീസുകൾ', 'ja': '個', 'es': 'piezas', 'en': 'pieces'
    },
    'dozens': {
        'te': 'డజన్లు', 'hi': 'दर्जन', 'kn': 'ಡಜನ್‌ಗಳು', 'ta': 'டஜன்கள்', 'or': 'ଡଜନ୍',
        'bn': 'ডজন', 'mr': 'डझन', 'ml': 'ഡസൻ', 'ja': 'ダース', 'es': 'docenas', 'en': 'dozens'
    },
    'peti': {
        'te': 'పేటీలు', 'hi': 'पेटी', 'kn': 'ಪೆಟ್ಟಿಗೆ', 'ta': 'பெட்டி', 'or': 'ପେଟି',
        'bn': 'পেটি', 'mr': 'पेटी', 'ml': 'പെട്ടി', 'ja': '箱', 'es': 'cajas', 'en': 'peti'
    }
}

UNIT_NAMES_SINGULAR = {
    'bags': {'te': 'బస్తా', 'hi': 'बैग', 'kn': 'ಚೀಲ', 'ta': 'மூட்டை', 'or': 'ବସ୍ତା', 'bn': 'ব্যাগ', 'mr': 'पोते', 'ml': 'ചാക്ക്', 'ja': 'パック', 'es': 'bolsa', 'en': 'bag'},
    'kg': {'te': 'కిలో', 'hi': 'किलो', 'kn': 'ಕೆಜಿ', 'ta': 'கிலோ', 'or': 'କିଲୋ', 'bn': 'কেজি', 'mr': 'किलो', 'ml': 'കിലോ', 'ja': 'キロ', 'es': 'kg', 'en': 'kg'},
    'packets': {'te': 'ప్యాకెట్', 'hi': 'पैकेट', 'kn': 'ಪ್ಯಾಕೆಟ್', 'ta': 'பாக்கெட்', 'or': 'ପ୍ୟାକେଟ୍', 'bn': 'প্যাকেট', 'mr': 'पुडा', 'ml': 'പാക്കറ്റ്', 'ja': 'パック', 'es': 'paquete', 'en': 'packet'},
    'litres': {'te': 'లీటరు', 'hi': 'लीटर', 'kn': 'ಲೀಟರ್', 'ta': 'லிட்டர்', 'or': 'ଲିଟର', 'bn': 'লিটার', 'mr': 'लीटर', 'ml': 'ലിറ്റർ', 'ja': 'リットル', 'es': 'litro', 'en': 'litre'},
    'boxes': {'te': 'పెట్టె', 'hi': 'डब्बा', 'kn': 'ಪೆಟ್ಟಿಗೆ', 'ta': 'பெட்டி', 'or': 'ବାକ୍ସ', 'bn': 'বাক্স', 'mr': 'खोका', 'ml': 'പെട്ടി', 'ja': '箱', 'es': 'caja', 'en': 'box'},
    'pieces': {'te': 'పీస్', 'hi': 'पीस', 'kn': 'ಪೀಸ್', 'ta': 'பீஸ்', 'or': 'ପିସ୍', 'bn': 'পিস', 'mr': 'नग', 'ml': 'പീസ്', 'ja': '個', 'es': 'pieza', 'en': 'piece'}
}

def get_translated_unit_name(unit_name, lang='en'):
    if not unit_name:
        return ""
    u_clean = str(unit_name).strip().lower()
    canonical = UNIT_TRANSLATIONS.get(u_clean, u_clean)
    if canonical in UNIT_NAMES_TRANSLATED:
        return UNIT_NAMES_TRANSLATED[canonical].get(lang, canonical)
    return unit_name

def get_translated_unit_singular(unit_name, lang='en'):
    if not unit_name:
        return ""
    u_clean = str(unit_name).strip().lower()
    canonical = UNIT_TRANSLATIONS.get(u_clean, u_clean)
    if canonical in UNIT_NAMES_SINGULAR:
        return UNIT_NAMES_SINGULAR[canonical].get(lang, canonical)
    return get_translated_unit_name(unit_name, lang)

TE_PHONETIC_MAP = {
    'మీరు': 'Meeru', 'బియ్యం': 'biyyam', 'కిలోలు': 'kilolu', 'కిలో': 'kilo',
    'లేదా': 'leda', 'బస్తాలు': 'bastalu', 'బస్తా': 'basta', 'అని': 'ani',
    'ఉద్దేశించారా': 'uddesinchara', 'చక్కెర': 'chakkera', 'పాలు': 'paalu',
    'నూనె': 'noone', 'పప్పు': 'pappu', 'ఉప్పు': 'uppu', 'సబ్బు': 'sabbu',
    'బిస్కెట్లు': 'biscuits', 'గోధుమ పిండి': 'godhuma pindi', 'టీ పొడి': 'tea podi',
    'నిల్వ': 'nilva', 'నిల్వల': 'nilvala', 'పరిస్థితి': 'paristhithi', 'చాలా ఎక్కువ': 'chala ekkuva', 'సరిపోతుంది': 'saripotundi',
    'చాలా తక్కువ': 'chala thakkuva', 'ఉంది': 'undi', 'ఉన్నాయి': 'unnayi', 'సుమారు': 'sumaru',
    'రోజులు': 'rojulu', 'రోజుల్లో': 'rojullo', 'వస్తుంది': 'vasthundi', 'కలపబడ్డాయి': 'kalapabaddayi',
    'మొత్తం': 'motham', 'ఇప్పుడు': 'ippudu', 'తీసివేయబడ్డాయి': 'theesiveyabaddayi',
    'మిగిలిన': 'migilina', 'ఒక్కో': 'okko', 'ధర': 'dhara', 'సరుకులకు': 'sarukulaku', 'సరుకులు': 'sarukulu', 'సరుకూ': 'saruku',
    'రీఆర్డర్': 'reorder', 'జాబితా': 'jabitha', 'తయారైంది': 'thayaraindi',
    'అత్యధిక': 'athyadhika', 'లాభం': 'labham', 'ఇచ్చే': 'icche', 'సరుకు': 'saruku',
    'ప్రతి': 'prathi', 'పై': 'pai', 'మార్జిన్': 'margin', 'సరఫరా చేస్తారు': 'sarafara chestharu',
    'ఫోన్': 'phone', 'ఆర్డర్ సమయం': 'order samayam', 'కనుగొనబడలేదు': 'kanugonabadaledu',
    'ఏ సరుకును మార్చాలో దయచేసి పేరు చెప్పండి': 'Ye sarukunu marchalo dayachesi peru cheppandi',
    'ఉదా: బియ్యం, చక్కెర': 'uda biyyam chakkera',
    'క్షమించండి, నాకు అర్థం కాలేదు': 'Kshaminchandi, naaku artham kaledu',
    'చేర్చబడింది': 'cherchabadindi', 'ధృవీకరణ అవసరం': 'Dhruveekarana avasaram',
    'మీ వద్ద': 'Mee vaddha', 'ప్రస్తుత': 'prasthutha', 'తక్కువ స్టాక్ హెచ్చరిక': 'Thakkuva stock heccharika',
    'అన్ని నిల్వలు బాగున్నాయి! ఏ సరుకూ తక్కువగా లేదు.': 'Anni nilvalu bagunnayi! Ye saruku thakkuvaga ledu.',
    'ముందుగా పూర్తి అవుతుంది': 'mundhuga poorthi avuthundi', 'పూర్తి అవుతుంది': 'poorthi avuthundi',
    'మీ షాప్‌లో ప్రస్తుతం అన్ని నిల్వలు నిండుగా ఉన్నాయి.': 'Mee shop lo prasthutham anni nilvalu ninduga unnayi.',
    'నాకు తెలుసు! మీ షాప్‌లో నేర్చుకున్న కొలతలు': 'Naaku thelusu! Mee shop lo nerchukunna kolathalu',
    'ముఖ్యమైన నిల్వలు': 'mukhyamaina nilvalu', 'శుభోదయం! మీ షాప్‌లో': 'Shubhodhayam! Mee shop lo',
    'సరుకులు తక్కువగా ఉన్నాయి': 'sarukulu thakkuvaga unnayi', 'వెంటనే దృష్టి పెట్టాల్సినవి': 'ventane drushti pettalsinavi',
    'మొత్తం నిల్వ విలువ': 'motham nilva viluva', 'కొనుగోలు విలువ': 'konugolu viluva',
    'అమ్మకం మార్కెట్ విలువ': 'ammakam market viluva', 'అంచనా లాభం': 'anchana labham',
    '🟢': '', '🟡': '', '🔴': '', '⚠️': ''
}

HI_PHONETIC_MAP = {
    'क्या आपका मतलब': 'Kya aapka matlab', 'चावल': 'chawal', 'चीनी': 'cheeni', 'दूध': 'doodh',
    'तेल': 'tel', 'नमक': 'namak', 'दाल': 'daal', 'आटा': 'atta', 'साबुन': 'sabun', 'बिस्कुट': 'biscuits',
    'चाय': 'chai', 'किलो': 'kilo', 'बैग': 'bag', 'पैकेट': 'packet', 'लीटर': 'litre', 'या': 'ya',
    'है': 'hai', 'का स्टॉक': 'ka stock', 'बहुत अधिक': 'bahut adhik', 'पर्याप्त': 'paryapt',
    'कम स्टॉक': 'kam stock', 'जोड़े गए': 'jode gaye', 'हटाए गए': 'hatae gaye', 'कुल स्टॉक': 'kul stock',
    'शेष स्टॉक': 'shes stock', 'प्रति': 'prati', '🟢': '', '🟡': '', '🔴': '', '⚠️': ''
}

KN_PHONETIC_MAP = {
    'ನೀವು': 'Neevu', 'ಅಕ್ಕಿ': 'akki', 'ಸಕ್ಕರೆ': 'sakkare', 'ಹಾಲು': 'haalu', 'ಎಣ್ಣೆ': 'enne',
    'ಉಪ್ಪು': 'uppu', 'ಬೇಳೆ': 'bele', 'ಸಾಬೂನು': 'saboonu', 'ಬಿಸ್ಕತ್ತು': 'biscuit', 'ಚಹಾ': 'chaha',
    'ಕೆಜಿ': 'kg', 'ಚೀಲಗಳು': 'cheelagalu', 'ಚೀಲ': 'cheela', 'ಪ್ಯಾಕೆಟ್‌ಗಳು': 'packetgalu',
    'ಅಥವಾ': 'athava', 'ಎಂದು': 'endu', 'ಉದ್ದೇಶಿಸಿದ್ದೀರಾ': 'uddesissiddira', 'ದಾಸ್ತಾನು': 'dastanu',
    'ಹೆಚ್ಚು': 'hecchu', 'ಸರಿಯಾಗಿದೆ': 'sariyagide', 'ಕಡಿಮೆ': 'kadime', 'ಇದೆ': 'ide',
    'ಸೇರಿಸಲಾಗಿದೆ': 'serisalagide', 'ತೆಗೆದುಹಾಕಲಾಗಿದೆ': 'thegeduhakalagide', '🟢': '', '🟡': '', '🔴': '', '⚠️': ''
}

def get_phonetic_speech_text(text, lang='en'):
    if not text:
        return ""
    
    mapping = None
    if lang == 'te': mapping = TE_PHONETIC_MAP
    elif lang == 'hi': mapping = HI_PHONETIC_MAP
    elif lang == 'kn': mapping = KN_PHONETIC_MAP
    
    if not mapping:
        return text
        
    result = text
    for k, v in mapping.items():
        result = result.replace(k, v)
    return result

def get_translated_product_name(product_name, lang='en'):
    if product_name in PRODUCT_NAMES_TRANSLATED:
        return PRODUCT_NAMES_TRANSLATED[product_name].get(lang, product_name)
    return product_name

def build_localized_msg(msg_type, params, lang='en'):
    pname = params.get('product', '')
    qty_text = params.get('display_qty', '')
    total_text = params.get('total_qty', '')
    price_info = params.get('price_info', '')
    term = params.get('term', '')
    unit = params.get('unit', '')
    eq_qty = params.get('eq_qty', '')
    days = params.get('days', '')

    if msg_type == 'ADD_STOCK':
        if lang == 'te': return f"{pname} {qty_text}{price_info} కలపబడ్డాయి. మొత్తం నిల్వ ఇప్పుడు {total_text}."
        if lang == 'hi': return f"{pname} के {qty_text}{price_info} जोड़े गए। कुल स्टॉक अब {total_text} है।"
        if lang == 'kn': return f"{pname} {qty_text}{price_info} ಸೇರಿಸಲಾಗಿದೆ. ಒಟ್ಟು ದಾಸ್ತಾನು ಈಗ {total_text}."
        if lang == 'ta': return f"{pname} {qty_text}{price_info} சேர்க்கப்பட்டது. மொத்த இருப்பு இப்போது {total_text}."
        if lang == 'or': return f"{pname} ର {qty_text}{price_info} ଯୋଡାଗଲା। ମୋଟ ଷ୍ଟକ୍ ଏବେ {total_text}।"
        if lang == 'bn': return f"{pname} এর {qty_text}{price_info} যোগ করা হয়েছে। মোট স্টক এখন {total_text}।"
        if lang == 'mr': return f"{pname} चे {qty_text}{price_info} जोडले गेले. एकूण स्टॉक आता {total_text} आहे."
        if lang == 'ml': return f"{pname} {qty_text}{price_info} ചേർത്തു. ആകെ സ്റ്റോക്ക് ഇപ്പോൾ {total_text}."
        if lang == 'ja': return f"{pname}を{qty_text}{price_info}追加しました。現在の総在庫は{total_text}です。"
        if lang == 'es': return f"Se añadieron {qty_text} de {pname}{price_info}. El stock total ahora es {total_text}."
        return f"Added {qty_text} of {pname}{price_info}. Total stock is now {total_text}."

    elif msg_type == 'REMOVE_STOCK':
        if lang == 'te': return f"{pname} {qty_text} తీసివేయబడ్డాయి. మిగిలిన నిల్వ {total_text}."
        if lang == 'hi': return f"{pname} के {qty_text} हटाए गए। शेष स्टॉक {total_text} है।"
        if lang == 'kn': return f"{pname} {qty_text} ತೆಗೆದುಹಾಕಲಾಗಿದೆ. ಬಾಕಿ ದಾಸ್ತಾನು {total_text}."
        if lang == 'ta': return f"{pname} {qty_text} அகற்றப்பட்டது. மீதமுள்ள இருப்பு {total_text}."
        if lang == 'or': return f"{pname} ର {qty_text} କାଢ଼ିଦିଆଗଲା। ବାକି ଷ୍ଟକ୍ {total_text}।"
        if lang == 'bn': return f"{pname} এর {qty_text} সরানো হয়েছে। অবশিষ্ট স্টক {total_text}।"
        if lang == 'mr': return f"{pname} चे {qty_text} कमी केले. उर्वरित साठा {total_text} आहे."
        if lang == 'ml': return f"{pname} {qty_text} നീക്കംചെയ്തു. ബാക്കി സ്റ്റോക്ക് {total_text}."
        if lang == 'ja': return f"{pname}を{qty_text}減らしました。残りの在庫は{total_text}です。"
        if lang == 'es': return f"Se retiraron {qty_text} de {pname}. El stock restante es {total_text}."
        return f"Removed {qty_text} of {pname}. Remaining stock is {total_text}."

    elif msg_type == 'GET_STOCK_SINGLE':
        if lang == 'te': return f"మీ వద్ద {pname} {total_text} ఉంది."
        if lang == 'hi': return f"आपके पास {total_text} {pname} है।"
        if lang == 'kn': return f"ನಿಮ್ಮ ಬಳಿ {total_text} {pname} ಇದೆ."
        if lang == 'ta': return f"உங்களிடம் {total_text} {pname} உள்ளது."
        if lang == 'or': return f"ଆପଣଙ୍କ ପାଖରେ {total_text} {pname} ଅଛି।"
        if lang == 'bn': return f"আপনার কাছে {total_text} {pname} আছে।"
        if lang == 'mr': return f"तुमच्याकडे {total_text} {pname} आहे."
        if lang == 'ml': return f"നിങ്ങളുടെ കൈവശം {total_text} {pname} ഉണ്ട്."
        if lang == 'ja': return f"{pname}の在庫は{total_text}です。"
        if lang == 'es': return f"Tienes {total_text} de {pname}."
        return f"You have {total_text} of {pname}."

    elif msg_type == 'LEARN_VOCAB':
        if lang == 'te': return f"నేర్చుకున్నాను! 1 {term} = {eq_qty} {unit}."
        if lang == 'hi': return f"सीख लिया! 1 {term} = {eq_qty} {unit}।"
        if lang == 'kn': return f"ಕಲಿತಿದ್ದೇನೆ! 1 {term} = {eq_qty} {unit}."
        if lang == 'ta': return f"கற்றுக்கொண்டேன்! 1 {term} = {eq_qty} {unit}."
        if lang == 'or': return f"ଶିଖିଗଲି! 1 {term} = {eq_qty} {unit}।"
        if lang == 'bn': return f"শিখে নিয়েছি! 1 {term} = {eq_qty} {unit}।"
        if lang == 'mr': return f"शिकलो! 1 {term} = {eq_qty} {unit}."
        if lang == 'ml': return f"പഠിച്ചു! 1 {term} = {eq_qty} {unit}."
        if lang == 'ja': return f"学習しました！ 1 {term} = {eq_qty} {unit}。"
        if lang == 'es': return f"¡Aprendido! 1 {term} = {eq_qty} {unit}."
        return f"Learned! 1 {term} = {eq_qty} {unit}."

    elif msg_type == 'PREDICT_STOCKOUT':
        if lang == 'te': return f"{pname} సుమారు {days} రోజుల్లో ముందుగా పూర్తి అవుతుంది."
        if lang == 'hi': return f"{pname} लगभग {days} दिनों में सबसे पहले समाप्त हो जाएगा।"
        if lang == 'kn': return f"{pname} ಸುಮಾರು {days} ದಿನಗಳಲ್ಲಿ ಮೊದಲು ಮುಗಿಯುತ್ತದೆ."
        if lang == 'ta': return f"{pname} சுமார் {days} நாட்களில் முதலில் தீர்ந்துவிடும்."
        if lang == 'or': return f"{pname} ପ୍ରାୟ {days} ଦିନରେ ସରିଯିବ।"
        if lang == 'bn': return f"{pname} প্রায় {days} দিনের মধ্যে প্রথম শেষ হবে।"
        if lang == 'mr': return f"{pname} सुमारे {days} दिवसांत संपेल."
        if lang == 'ml': return f"{pname} ഏകദേശം {days} ദിവസത്തിനുള്ളിൽ തീരും."
        if lang == 'ja': return f"{pname}は約{days}日で最初に在庫切れになります。"
        if lang == 'es': return f"{pname} se agotará primero en aproximadamente {days} días."
        return f"{pname} will finish first in approximately {days} days."

    elif msg_type == 'NEED_VOCAB':
        if lang == 'te': return f"మీ షాప్‌లో 1 {term} అంటే ఏమిటి?"
        if lang == 'hi': return f"आपकी दुकान में 1 {term} का क्या मतलब है?"
        if lang == 'kn': return f"ನಿಮ್ಮ ಅಂಗಡಿಯಲ್ಲಿ 1 {term} ಎಂದರೆ ಏನು?"
        if lang == 'ta': return f"உங்கள் கடையில் 1 {term} என்றால் என்ன?"
        if lang == 'or': return f"ଆପଣଙ୍କ ଦୋକାନରେ 1 {term} ର ଅର୍ଥ କ’ଣ?"
        if lang == 'bn': return f"আপনার দোকানে 1 {term} মানে কি?"
        if lang == 'mr': return f"तुमच्या दुकानात 1 {term} म्हणजे काय?"
        if lang == 'ml': return f"നിങ്ങളുടെ കടയിൽ 1 {term} എന്നാൽ എന്താണ്?"
        if lang == 'ja': return f"あなたのお店で 1 {term} とはどういう意味ですか？"
        if lang == 'es': return f"¿Qué significa 1 {term} en tu tienda?"
        return f"What does 1 {term} mean in your shop?"

    return ""

def create_jwt_token(user_id, shop_id, email):
    payload = {
        "user_id": user_id,
        "shop_id": shop_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(days=30)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def decode_jwt_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except Exception as e:
        return None

def register_user(name, email, password, shop_name):
    email_clean = email.strip().lower()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE LOWER(email) = ?", (email_clean,))
    if cursor.fetchone():
        conn.close()
        return {"success": False, "message": "User with this email already exists."}

    password_hash = generate_password_hash(password)
    cursor.execute("""
        INSERT INTO users (name, email, password_hash, shop_name)
        VALUES (?, ?, ?, ?)
    """, (name, email_clean, password_hash, shop_name))
    user_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO shops (user_id, name)
        VALUES (?, ?)
    """, (user_id, shop_name))
    shop_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO conversations (shop_id, title)
        VALUES (?, 'Today''s Inventory')
    """, (shop_id,))
    conv_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO messages (conversation_id, sender, message, intent, language)
        VALUES (?, 'copilot', 'Welcome to Shop Copilot! Set up your inventory using CSV upload, voice input, or the product checklist.', 'WELCOME', 'en')
    """, (conv_id,))

    conn.commit()
    conn.close()

    token = create_jwt_token(user_id, shop_id, email_clean)
    return {
        "success": True,
        "token": token,
        "user": {"id": user_id, "name": name, "email": email_clean, "shop_name": shop_name},
        "shop": {"id": shop_id, "name": shop_name},
        "conversation_id": conv_id,
        "message": "Account registered successfully!"
    }

def seed_demo_inventory(shop_id=DEFAULT_SHOP_ID):
    conn = get_db_connection()
    cursor = conn.cursor()
    seed_products = [
        ('Rice', 'Grains', 50.0, 'bags', 1450.0, 1232.5, 10.0, 3.0, 2, shop_id),
        ('Sugar', 'Groceries', 25.0, 'kg', 42.0, 35.7, 10.0, 2.0, 1, shop_id),
        ('Biscuits', 'Snacks', 100.0, 'packets', 10.0, 8.5, 20.0, 5.0, 2, shop_id),
        ('Oil', 'Essentials', 40.0, 'litres', 160.0, 136.0, 10.0, 2.5, 1, shop_id),
        ('Milk', 'Dairy', 30.0, 'packets', 28.0, 23.8, 10.0, 5.0, 1, shop_id),
        ('Salt', 'Groceries', 50.0, 'packets', 20.0, 17.0, 10.0, 4.0, 1, shop_id),
        ('Wheat Flour', 'Grains', 20.0, 'bags', 340.0, 289.0, 5.0, 2.0, 2, shop_id),
        ('Dal', 'Groceries', 30.0, 'kg', 120.0, 102.0, 10.0, 3.0, 2, shop_id),
        ('Tea Powder', 'Beverages', 40.0, 'packets', 65.0, 55.25, 8.0, 3.0, 1, shop_id),
        ('Soap', 'Personal Care', 60.0, 'pieces', 35.0, 29.75, 15.0, 5.0, 2, shop_id)
    ]
    cursor.executemany("""
        INSERT INTO products (name, category, quantity, unit, price, purchase_price, reorder_level, avg_daily_usage, supplier_lead_days, shop_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(shop_id, name) DO UPDATE SET
            quantity = excluded.quantity,
            unit = excluded.unit,
            price = excluded.price,
            purchase_price = excluded.purchase_price;
    """, seed_products)
    conn.commit()
    conn.close()
    return {"success": True, "message": "Demo retail inventory loaded (10 items)."}

def bulk_add_products(products_list, shop_id=DEFAULT_SHOP_ID):
    if not products_list or not isinstance(products_list, list):
        return {"success": False, "message": "Invalid products list."}

    conn = get_db_connection()
    cursor = conn.cursor()
    added_count = 0

    for item in products_list:
        name = str(item.get("name") or item.get("product") or "").strip()
        if not name:
            continue

        cat = str(item.get("category") or "General").strip()
        qty = float(item.get("quantity") or item.get("qty") or 0.0)
        unit = str(item.get("unit") or "pieces").strip().lower()
        price = float(item.get("price") or item.get("selling_price") or 0.0)
        cost = float(item.get("purchase_price") or item.get("cost_price") or item.get("cost") or (price * 0.85))
        reorder_lvl = float(item.get("reorder_level") or max(5.0, qty * 0.2))
        usage = float(item.get("avg_daily_usage") or 1.0)
        lead = int(item.get("supplier_lead_days") or 2)

        cursor.execute("""
            INSERT INTO products (name, category, quantity, unit, price, purchase_price, reorder_level, avg_daily_usage, supplier_lead_days, shop_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(shop_id, name) DO UPDATE SET
                category = excluded.category,
                quantity = products.quantity + excluded.quantity,
                unit = excluded.unit,
                price = excluded.price,
                purchase_price = excluded.purchase_price,
                updated_at = CURRENT_TIMESTAMP
        """, (name, cat, qty, unit, price, cost, reorder_lvl, usage, lead, shop_id))

        cursor.execute("""
            INSERT INTO transactions (shop_id, product_id, product_name, action, quantity, unit, price, raw_text, source)
            VALUES (?, NULL, ?, 'ADD', ?, ?, ?, ?, 'import')
        """, (shop_id, name, qty, unit, price, f"Imported {qty} {unit} of {name}"))

        added_count += 1

    conn.commit()
    conn.close()

    return {
        "success": True,
        "added_count": added_count,
        "message": f"Successfully imported {added_count} products into inventory."
    }

def import_inventory_csv(csv_content, shop_id=DEFAULT_SHOP_ID):
    if not csv_content:
        return {"success": False, "message": "CSV content is empty."}

    try:
        f = io.StringIO(csv_content)
        reader = csv.DictReader(f)
        items_to_add = []

        for row in reader:
            # Map column names case-insensitively
            normalized_row = {str(k).strip().lower(): str(v).strip() for k, v in row.items() if k}
            
            p_name = (
                normalized_row.get("product") or 
                normalized_row.get("product name") or 
                normalized_row.get("name") or 
                normalized_row.get("item")
            )
            if not p_name:
                continue

            qty_str = (
                normalized_row.get("quantity") or 
                normalized_row.get("qty") or 
                normalized_row.get("stock") or "0"
            )
            unit_str = (
                normalized_row.get("unit") or 
                normalized_row.get("units") or "pieces"
            )
            price_str = (
                normalized_row.get("price") or 
                normalized_row.get("selling price") or 
                normalized_row.get("mrp") or "0"
            )
            cost_str = (
                normalized_row.get("purchase price") or 
                normalized_row.get("cost price") or 
                normalized_row.get("cost") or "0"
            )
            cat_str = (
                normalized_row.get("category") or 
                normalized_row.get("cat") or "General"
            )

            try:
                qty_val = float(qty_str.replace(",", ""))
            except ValueError:
                qty_val = 0.0

            try:
                price_val = float(price_str.replace(",", "").replace("₹", ""))
            except ValueError:
                price_val = 0.0

            try:
                cost_val = float(cost_str.replace(",", "").replace("₹", ""))
            except ValueError:
                cost_val = price_val * 0.85 if price_val > 0 else 0.0

            items_to_add.append({
                "name": p_name,
                "category": cat_str,
                "quantity": qty_val,
                "unit": unit_str,
                "price": price_val,
                "purchase_price": cost_val
            })

        if not items_to_add:
            return {"success": False, "message": "No valid product rows found in CSV. Please ensure column headers match 'Product, Quantity, Unit, Price, Cost, Category'."}

        return bulk_add_products(items_to_add, shop_id=shop_id)

    except Exception as e:
        return {"success": False, "message": f"CSV parse error: {str(e)}"}

def login_user(email, password):
    email_clean = email.strip().lower()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE LOWER(email) = ?", (email_clean,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return {"success": False, "message": "Invalid email or password."}

    user_dict = dict(user)
    if not check_password_hash(user_dict['password_hash'], password):
        conn.close()
        return {"success": False, "message": "Invalid email or password."}

    cursor.execute("SELECT * FROM shops WHERE user_id = ?", (user_dict['id'],))
    shop = cursor.fetchone()
    shop_dict = dict(shop) if shop else {"id": 1, "name": user_dict['shop_name']}

    cursor.execute("SELECT id FROM conversations WHERE shop_id = ? ORDER BY updated_at DESC LIMIT 1", (shop_dict['id'],))
    conv = cursor.fetchone()
    conv_id = conv['id'] if conv else None

    conn.close()

    token = create_jwt_token(user_dict['id'], shop_dict['id'], email_clean)
    return {
        "success": True,
        "token": token,
        "user": {"id": user_dict['id'], "name": user_dict['name'], "email": user_dict['email'], "shop_name": user_dict['shop_name']},
        "shop": shop_dict,
        "conversation_id": conv_id,
        "message": "Logged in successfully!"
    }

def get_conversations(shop_id=DEFAULT_SHOP_ID):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, shop_id, title, created_at, updated_at
        FROM conversations
        WHERE shop_id = ?
        ORDER BY updated_at DESC
    """, (shop_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_conversation(shop_id=DEFAULT_SHOP_ID, title="New Conversation"):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO conversations (shop_id, title)
        VALUES (?, ?)
    """, (shop_id, title))
    conv_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO messages (conversation_id, sender, message, intent, language)
        VALUES (?, 'copilot', 'New conversation started. How can Shop Copilot assist you?', 'WELCOME', 'en')
    """, (conv_id,))

    conn.commit()
    conn.close()
    return {"id": conv_id, "shop_id": shop_id, "title": title}

def get_conversation_messages(conversation_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, conversation_id, sender, message, intent, language, timestamp
        FROM messages
        WHERE conversation_id = ?
        ORDER BY timestamp ASC
    """, (conversation_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_chat_message(conversation_id, sender, message, intent=None, language='en'):
    if not conversation_id:
        return
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO messages (conversation_id, sender, message, intent, language)
        VALUES (?, ?, ?, ?, ?)
    """, (conversation_id, sender, message, intent, language))

    cursor.execute("""
        UPDATE conversations
        SET updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (conversation_id,))

    conn.commit()
    conn.close()

def resolve_context_aware_command(conversation_id, nlp_res):
    if not conversation_id:
        return nlp_res

    intent = nlp_res.get("intent")
    product = nlp_res.get("product")
    qty = nlp_res.get("quantity")
    unit = nlp_res.get("unit")

    if intent in ["ADD_STOCK", "REMOVE_STOCK"] and qty is not None and (product is None or unit is None):
        messages = get_conversation_messages(conversation_id)
        for msg in reversed(messages):
            msg_text = msg['message'].lower()
            if not product:
                for syn, canonical in PRODUCT_SYNONYMS.items():
                    if syn in msg_text:
                        product = canonical
                        break
            if not unit:
                for u in ['bags', 'kg', 'packets', 'litres', 'cartons', 'boxes', 'pieces', 'dozens']:
                    if u in msg_text:
                        unit = u
                        break
            if product:
                break

        if product:
            nlp_res["product"] = product
        if unit:
            nlp_res["unit"] = unit

    return nlp_res

def save_shop_memory(shop_id, memory_type, key, value, confidence=1.0):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO memories (shop_id, memory_type, key, value, confidence)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(shop_id, memory_type, key) DO UPDATE SET
            value = excluded.value,
            confidence = excluded.confidence,
            updated_at = CURRENT_TIMESTAMP
    """, (shop_id, memory_type, key, value, confidence))
    conn.commit()
    conn.close()

def get_shop_memories(shop_id=DEFAULT_SHOP_ID):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT memory_type, key, value, updated_at
        FROM memories
        WHERE shop_id = ?
        ORDER BY updated_at DESC
    """, (shop_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_products(shop_id=DEFAULT_SHOP_ID):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, category, quantity, unit, price, purchase_price, reorder_level, avg_daily_usage, supplier_lead_days, updated_at
        FROM products
        WHERE shop_id = ?
        ORDER BY name ASC
    """, (shop_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_product_by_name(product_name, shop_id=DEFAULT_SHOP_ID):
    if not product_name:
        return None
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM products
        WHERE shop_id = ? AND LOWER(name) = LOWER(?)
    """, (shop_id, product_name))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_vocabulary_map(shop_id=DEFAULT_SHOP_ID):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT term, equivalent_qty, equivalent_unit FROM vocabulary WHERE shop_id = ?", (shop_id,))
    rows = cursor.fetchall()
    conn.close()
    return {r['term'].lower(): {'qty': r['equivalent_qty'], 'unit': r['equivalent_unit'].lower()} for r in rows}

def learn_vocabulary(term, equivalent_qty, equivalent_unit, lang='en', shop_id=DEFAULT_SHOP_ID):
    term_clean = term.strip().lower()
    unit_clean = equivalent_unit.strip().lower()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO vocabulary (shop_id, term, equivalent_qty, equivalent_unit)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(shop_id, term) DO UPDATE SET
            equivalent_qty = excluded.equivalent_qty,
            equivalent_unit = excluded.equivalent_unit
    """, (shop_id, term_clean, float(equivalent_qty), unit_clean))
    conn.commit()
    conn.close()

    save_shop_memory(shop_id, "vocabulary", term_clean, f"{equivalent_qty} {unit_clean}")

    msg = build_localized_msg('LEARN_VOCAB', {'term': term_clean, 'eq_qty': equivalent_qty, 'unit': unit_clean}, lang=lang)
    return {
        "success": True,
        "term": term_clean,
        "equivalent_qty": float(equivalent_qty),
        "equivalent_unit": unit_clean,
        "language": lang,
        "message": msg
    }

def convert_unit_quantity(product, input_qty, input_unit, shop_id=DEFAULT_SHOP_ID):
    if not input_unit:
        return input_qty, product['unit'], None, None

    input_unit_clean = input_unit.lower().strip()
    if input_unit_clean in UNIT_TRANSLATIONS:
        input_unit_clean = UNIT_TRANSLATIONS[input_unit_clean]

    product_unit_clean = product['unit'].lower().strip()
    if input_unit_clean == product_unit_clean or input_unit_clean.rstrip('s') == product_unit_clean.rstrip('s'):
        return input_qty, product['unit'], None, None

    vocab = get_vocabulary_map(shop_id)
    if input_unit_clean in vocab:
        v = vocab[input_unit_clean]
        converted_qty = input_qty * v['qty']
        explanation = f"{input_qty} {input_unit} ({int(converted_qty) if converted_qty.is_integer() else converted_qty} {v['unit']})"
        return converted_qty, v['unit'], explanation, None

    return None, None, None, input_unit_clean

def add_stock(product_name, qty, unit=None, price=None, raw_text="", source="voice", lang="en", shop_id=DEFAULT_SHOP_ID):
    product = get_product_by_name(product_name, shop_id)
    if not product:
        msg = f"Could not find product '{product_name}' in inventory."
        return {"success": False, "status": "PRODUCT_NOT_FOUND", "language": lang, "message": msg}

    converted_qty, target_unit, explanation, missing_term = convert_unit_quantity(product, qty, unit, shop_id)

    if missing_term:
        msg = build_localized_msg('NEED_VOCAB', {'term': missing_term}, lang=lang)
        return {
            "success": False,
            "status": "NEED_VOCABULARY_LEARNING",
            "term": missing_term,
            "product": product['name'],
            "pending_action": "ADD_STOCK",
            "quantity": qty,
            "unit": unit,
            "price": price,
            "language": lang,
            "message": msg
        }

    new_qty = product['quantity'] + converted_qty
    actual_price = price if (price and price > 0) else product.get('price', 0.0)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE products
        SET quantity = ?, price = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND shop_id = ?
    """, (new_qty, actual_price, product['id'], shop_id))

    cursor.execute("""
        INSERT INTO transactions (shop_id, product_id, product_name, action, quantity, unit, price, raw_text, source)
        VALUES (?, ?, ?, 'ADD', ?, ?, ?, ?, ?)
    """, (shop_id, product['id'], product['name'], converted_qty, target_unit, actual_price, raw_text, source))
    conn.commit()
    conn.close()

    pname_lang = get_translated_product_name(product['name'], lang)
    unit_lang = get_translated_unit_name(target_unit, lang)
    total_unit_lang = get_translated_unit_name(product['unit'], lang)
    total_unit_sing = get_translated_unit_singular(product['unit'], lang)

    display_qty_text = explanation if explanation else f"{int(converted_qty) if converted_qty.is_integer() else converted_qty} {unit_lang}"
    total_qty_text = f"{int(new_qty) if new_qty.is_integer() else new_qty} {total_unit_lang}"
    
    if lang == 'te':
        price_info = f" (ఒక్కో {total_unit_sing} ధర ₹{actual_price:g})" if actual_price > 0 else ""
    elif lang == 'hi':
        price_info = f" (प्रति {total_unit_sing} ₹{actual_price:g})" if actual_price > 0 else ""
    elif lang == 'kn':
        price_info = f" (ಪ್ರತಿ {total_unit_sing} ₹{actual_price:g})" if actual_price > 0 else ""
    elif lang == 'ta':
        price_info = f" (ஒரு {total_unit_sing} ₹{actual_price:g})" if actual_price > 0 else ""
    else:
        price_info = f" (at ₹{actual_price:g}/{total_unit_sing})" if actual_price > 0 else ""

    msg = build_localized_msg('ADD_STOCK', {
        'product': pname_lang,
        'display_qty': display_qty_text,
        'total_qty': total_qty_text,
        'price_info': price_info
    }, lang=lang)

    return {
        "success": True,
        "status": "STOCK_UPDATED",
        "action": "ADD",
        "product": product['name'],
        "added_qty": converted_qty,
        "new_total": new_qty,
        "unit": product['unit'],
        "price": actual_price,
        "language": lang,
        "message": msg
    }

def remove_stock(product_name, qty, unit=None, price=None, raw_text="", source="voice", lang="en", shop_id=DEFAULT_SHOP_ID):
    product = get_product_by_name(product_name, shop_id)
    if not product:
        msg = f"Could not find product '{product_name}' in inventory."
        return {"success": False, "status": "PRODUCT_NOT_FOUND", "language": lang, "message": msg}

    converted_qty, target_unit, explanation, missing_term = convert_unit_quantity(product, qty, unit, shop_id)

    if missing_term:
        msg = build_localized_msg('NEED_VOCAB', {'term': missing_term}, lang=lang)
        return {
            "success": False,
            "status": "NEED_VOCABULARY_LEARNING",
            "term": missing_term,
            "product": product['name'],
            "pending_action": "REMOVE_STOCK",
            "quantity": qty,
            "unit": unit,
            "price": price,
            "language": lang,
            "message": msg
        }

    new_qty = max(0.0, product['quantity'] - converted_qty)
    actual_price = price if (price and price > 0) else product.get('price', 0.0)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE products
        SET quantity = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND shop_id = ?
    """, (new_qty, product['id'], shop_id))

    cursor.execute("""
        INSERT INTO transactions (shop_id, product_id, product_name, action, quantity, unit, price, raw_text, source)
        VALUES (?, ?, ?, 'REMOVE', ?, ?, ?, ?, ?)
    """, (shop_id, product['id'], product['name'], converted_qty, target_unit, actual_price, raw_text, source))
    conn.commit()
    conn.close()

    pname_lang = get_translated_product_name(product['name'], lang)
    unit_lang = get_translated_unit_name(target_unit, lang)
    total_unit_lang = get_translated_unit_name(product['unit'], lang)

    display_qty_text = explanation if explanation else f"{int(converted_qty) if converted_qty.is_integer() else converted_qty} {unit_lang}"
    total_qty_text = f"{int(new_qty) if new_qty.is_integer() else new_qty} {total_unit_lang}"

    msg = build_localized_msg('REMOVE_STOCK', {
        'product': pname_lang,
        'display_qty': display_qty_text,
        'total_qty': total_qty_text
    }, lang=lang)

    return {
        "success": True,
        "status": "STOCK_UPDATED",
        "action": "REMOVE",
        "product": product['name'],
        "removed_qty": converted_qty,
        "new_total": new_qty,
        "unit": product['unit'],
        "price": actual_price,
        "language": lang,
        "message": msg
    }

def get_translated_status_label(status, lang='en'):
    status_upper = str(status).upper()
    status_map = {
        'HIGH': {
            'te': 'చాలా ఎక్కువ 🟢', 'hi': 'बहुत अधिक 🟢', 'kn': 'ಹೆಚ್ಚು 🟢', 'ta': 'அதிகம் 🟢',
            'or': 'ଅଧିକ 🟢', 'bn': 'অনেক বেশি 🟢', 'mr': 'खूप जास्त 🟢', 'ml': 'കൂടുതൽ 🟢',
            'ja': '十分 🟢', 'es': 'ALTO 🟢', 'en': 'HIGH 🟢'
        },
        'OKAY': {
            'te': 'సరిపోతుంది 🟡', 'hi': 'पर्याप्त 🟡', 'kn': 'ಸರಿಯಾಗಿದೆ 🟡', 'ta': 'சரி 🟡',
            'or': 'ଠିକ୍ 🟡', 'bn': 'ঠিক আছে 🟡', 'mr': 'योग्य 🟡', 'ml': 'ശരി 🟡',
            'ja': '良好 🟡', 'es': 'CORRECTO 🟡', 'en': 'OKAY 🟡'
        },
        'LOW': {
            'te': 'చాలా తక్కువ 🔴', 'hi': 'कम स्टॉक 🔴', 'kn': 'ಕಡಿಮೆ 🔴', 'ta': 'குறைவு 🔴',
            'or': 'କମ୍ 🔴', 'bn': 'কম 🔴', 'mr': 'कमी साठा 🔴', 'ml': 'കുറവ് 🔴',
            'ja': '不足 🔴', 'es': 'BAJO ALERT 🔴', 'en': 'LOW ALERT 🔴'
        }
    }
    if status_upper in status_map:
        return status_map[status_upper].get(lang, status_map[status_upper]['en'])
    return status

def calculate_stock_health(product):
    qty = float(product.get('quantity') or 0.0)
    reorder_lvl = float(product.get('reorder_level') or 10.0)
    daily_usage = float(product.get('avg_daily_usage') or 1.0)
    days_left = math.ceil(qty / daily_usage) if daily_usage > 0 else 99

    if qty <= reorder_lvl:
        status = 'LOW'
    elif qty >= reorder_lvl * 2.0:
        status = 'HIGH'
    else:
        status = 'OKAY'

    return {
        'status': status,
        'days_remaining': days_left
    }

def get_stock(product_name=None, lang="en", shop_id=DEFAULT_SHOP_ID):
    if product_name:
        product = get_product_by_name(product_name, shop_id)
        if not product:
            pname_lang = get_translated_product_name(product_name, lang)
            if lang == 'te': msg = f"నిల్వలో '{pname_lang}' సరుకు కనుగొనబడలేదు."
            elif lang == 'hi': msg = f"स्टॉक में '{pname_lang}' आइटम नहीं मिला।"
            elif lang == 'kn': msg = f"ದಾಸ್ತಾನಿನಲ್ಲಿ '{pname_lang}' ಉತ್ಪನ್ನ ಕಂಡುಬಂದಿಲ್ಲ."
            elif lang == 'ta': msg = f"இருப்பில் '{pname_lang}' பொருள் பெறப்படவில்லை."
            else: msg = f"Could not find '{product_name}' in inventory."
            return {"success": False, "message": msg}

        health = calculate_stock_health(product)
        product['stock_status'] = health['status']
        product['days_remaining'] = health['days_remaining']

        unit_lang = get_translated_unit_name(product['unit'], lang)
        qty_str = f"{int(product['quantity']) if product['quantity'].is_integer() else product['quantity']} {unit_lang}"
        pname_lang = get_translated_product_name(product['name'], lang)

        status_label = get_translated_status_label(health['status'], lang)
        days_rem = health['days_remaining']

        if lang == 'te':
            msg = f"{pname_lang} నిల్వ {status_label} ({qty_str} ఉంది, సుమారు {days_rem} రోజులు వస్తుంది)."
        elif lang == 'hi':
            msg = f"{pname_lang} का स्टॉक {status_label} है ({qty_str} बचा है, लगभग {days_rem} दिन चलेगा)।"
        elif lang == 'kn':
            msg = f"{pname_lang} ದಾಸ್ತಾನು {status_label} ಆಗಿದೆ ({qty_str} ಇದೆ, ಸುಮಾರು {days_rem} ದಿನಗಳು ಬರಲಿದೆ)."
        elif lang == 'ta':
            msg = f"{pname_lang} இருப்பு {status_label} ஆகும் ({qty_str} உள்ளது, சுமார் {days_rem} நாட்கள் வரும்)."
        elif lang == 'or':
            msg = f"{pname_lang} ଷ୍ଟକ୍ {status_label} ଅଛି ({qty_str} ଅଛି, ପ୍ରାୟ {days_rem} ଦିନ ଚାଲିବ)।"
        elif lang == 'bn':
            msg = f"{pname_lang} স্টক {status_label} আছে ({qty_str} আছে, প্রায় {days_rem} দিন চলবে)।"
        elif lang == 'mr':
            msg = f"{pname_lang} साठा {status_label} आहे ({qty_str} शिल्लक आहे, सुमारे {days_rem} दिवस पुरेल)."
        elif lang == 'ml':
            msg = f"{pname_lang} സ്റ്റോക്ക് {status_label} ആണ് ({qty_str} ഉണ്ട്, ഏകദേശം {days_rem} ദിവസം വരും)."
        elif lang == 'ja':
            msg = f"{pname_lang}の在庫は{status_label}です（残り{qty_str}、約{days_rem}日分）。"
        elif lang == 'es':
            msg = f"El stock de {pname_lang} está {status_label} (quedan {qty_str}, aprox. {days_rem} días)."
        else:
            msg = f"{pname_lang} stock is {status_label} ({qty_str} left, est. {days_rem} days remaining)."

        return {"success": True, "products": [product], "stock_status": health['status'], "language": lang, "message": msg}

    products = get_all_products(shop_id)
    for p in products:
        h = calculate_stock_health(p)
        p['stock_status'] = h['status']
        p['days_remaining'] = h['days_remaining']

    summary_parts = [f"{get_translated_product_name(p['name'], lang)}: {int(p['quantity']) if p['quantity'].is_integer() else p['quantity']} {get_translated_unit_name(p['unit'], lang)} ({get_translated_status_label(p['stock_status'], lang)})" for p in products]
    joined_summary = ', '.join(summary_parts)

    if lang == 'te': msg = f"ప్రస్తుత నిల్వల పరిస్థితి: {joined_summary}."
    elif lang == 'hi': msg = f"वर्तमान स्टॉक स्थिति: {joined_summary}।"
    elif lang == 'kn': msg = f"ಪ್ರಸ್ತುತ ದಾಸ್ತಾನು ಸ್ಥಿತಿ: {joined_summary}."
    elif lang == 'ta': msg = f"தற்போதைய இருப்பு நிலை: {joined_summary}."
    elif lang == 'or': msg = f"ବର୍ତ୍ତମାନର ଷ୍ଟକ୍ ସ୍ଥିତି: {joined_summary}।"
    elif lang == 'bn': msg = f"বর্তমান স্টক অবস্থা: {joined_summary}।"
    elif lang == 'mr': msg = f"सध्याची साठा स्थिती: {joined_summary}."
    elif lang == 'ml': msg = f"നിലവിലെ സ്റ്റോക്ക് നില: {joined_summary}."
    elif lang == 'ja': msg = f"現在の在庫状況: {joined_summary}。"
    elif lang == 'es': msg = f"Estado actual de stock: {joined_summary}."
    else: msg = f"Current stock health: {joined_summary}."

    return {"success": True, "products": products, "language": lang, "message": msg}

def get_stock_assistant_data(shop_id=DEFAULT_SHOP_ID, lang="en"):
    products = get_all_products(shop_id)
    for p in products:
        h = calculate_stock_health(p)
        p['stock_status'] = h['status']
        p['days_remaining'] = h['days_remaining']

    high_items = [p for p in products if p['stock_status'] == 'HIGH']
    okay_items = [p for p in products if p['stock_status'] == 'OKAY']
    low_items = [p for p in products if p['stock_status'] == 'LOW']

    reorder_res = generate_reorder(lang=lang, shop_id=shop_id)

    return {
        "success": True,
        "total_products": len(products),
        "high_count": len(high_items),
        "okay_count": len(okay_items),
        "low_count": len(low_items),
        "products": products,
        "reorder_alerts": reorder_res.get("items", []),
        "whatsapp_message": reorder_res.get("whatsapp_message", "")
    }

def get_low_stock(lang="en", shop_id=DEFAULT_SHOP_ID):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM products
        WHERE shop_id = ? AND quantity <= reorder_level
        ORDER BY (quantity / reorder_level) ASC
    """, (shop_id,))
    rows = cursor.fetchall()
    conn.close()
    items = [dict(r) for r in rows]

    if not items:
        msg = "All stock levels are healthy! No items are currently low."
        if lang == 'te': msg = "అన్ని నిల్వలు బాగున్నాయి! ఏ సరుకూ తక్కువగా లేదు."
        elif lang == 'hi': msg = "सभी स्टॉक स्तर ठीक हैं! कोई भी आइटम कम नहीं है।"
        elif lang == 'kn': msg = "ಎಲ್ಲಾ ದಾಸ್ತಾನು ಹಂತಗಳು ಆರೋಗ್ಯಕರವಾಗಿವೆ!"
        elif lang == 'ta': msg = "அனைத்து இருப்பு நிலைகளும் ஆரோக்கியமாக உள்ளன!"
        elif lang == 'or': msg = "ସମସ୍ତ ଷ୍ଟକ୍ ସ୍ଥିତି ଭଲ ଅଛି!"
        elif lang == 'bn': msg = "সব স্টক স্তর ভালো আছে!"
        elif lang == 'mr': msg = "सर्व साठा पातळी योग्य आहे!"
        elif lang == 'ml': msg = "എല്ലാ സ്റ്റോക്ക് നിലകളും തൃപ്തികരമാണ്!"
        elif lang == 'ja': msg = "すべての在庫が適切に保たれています！"
        elif lang == 'es': msg = "¡Todos los niveles de stock están saludables!"

        return {"success": True, "items": [], "language": lang, "message": msg}

    parts = [f"{get_translated_product_name(item['name'], lang)} ({int(item['quantity'])} {get_translated_unit_name(item['unit'], lang)})" for item in items]
    msg = f"Low stock alert for {len(items)} items: {', '.join(parts)}."
    if lang == 'te': msg = f"తక్కువ స్టాక్ హెచ్చరిక: {', '.join(parts)}."
    elif lang == 'hi': msg = f"कम स्टॉक चेतावनी: {', '.join(parts)}।"
    elif lang == 'kn': msg = f"ಕಡಿಮೆ ದಾಸ್ತಾನು ಎಚ್ಚರಿಕೆ: {', '.join(parts)}."
    elif lang == 'ta': msg = f"குறைந்த இருப்பு எச்சரிக்கை: {', '.join(parts)}."
    elif lang == 'or': msg = f"କମ୍ ଷ୍ଟକ୍ ସୂଚନା: {', '.join(parts)}।"
    elif lang == 'bn': msg = f"কম স্টক সতর্কতা: {', '.join(parts)}।"
    elif lang == 'mr': msg = f"कमी साठा इशारा: {', '.join(parts)}."
    elif lang == 'ml': msg = f"കുറഞ്ഞ സ്റ്റോക്ക് മുന്നറിയിപ്പ്: {', '.join(parts)}."
    elif lang == 'ja': msg = f"在庫不足アラート: {', '.join(parts)}。"
    elif lang == 'es': msg = f"Alerta de stock bajo para {', '.join(parts)}."

    return {"success": True, "items": items, "language": lang, "message": msg}

def predict_stockout(lang="en", shop_id=DEFAULT_SHOP_ID):
    products = get_all_products(shop_id)
    predictions = []

    for p in products:
        usage = p['avg_daily_usage'] if p['avg_daily_usage'] > 0 else 1.0
        days_remaining = math.ceil(p['quantity'] / usage) if p['quantity'] > 0 else 0
        lead_days = p['supplier_lead_days']
        reorder_urgent = days_remaining <= (lead_days + 1)

        predictions.append({
            "product": p['name'],
            "quantity": p['quantity'],
            "unit": p['unit'],
            "daily_usage": usage,
            "days_remaining": days_remaining,
            "supplier_lead_days": lead_days,
            "reorder_urgent": reorder_urgent
        })

    predictions.sort(key=lambda x: x['days_remaining'])
    top = predictions[0] if predictions else None

    if top:
        pname = get_translated_product_name(top['product'], lang)
        msg = build_localized_msg('PREDICT_STOCKOUT', {'product': pname, 'days': top['days_remaining']}, lang=lang)
    else:
        msg = "Stock levels are stable."

    return {"success": True, "predictions": predictions, "language": lang, "message": msg}

def generate_reorder(lang="en", shop_id=DEFAULT_SHOP_ID):
    products = get_all_products(shop_id)
    reorder_items = []

    for p in products:
        usage = p['avg_daily_usage'] if p['avg_daily_usage'] > 0 else 1.0
        days_remaining = math.ceil(p['quantity'] / usage) if p['quantity'] > 0 else 0

        if p['quantity'] <= p['reorder_level'] or days_remaining <= 4:
            suggested_order_qty = math.ceil((p['reorder_level'] * 2) - p['quantity'])
            if suggested_order_qty > 0:
                reorder_items.append({
                    "product": p['name'],
                    "current_qty": p['quantity'],
                    "suggested_qty": suggested_order_qty,
                    "unit": p['unit'],
                    "days_remaining": days_remaining
                })

    if not reorder_items:
        msg = "Your inventory is currently well-stocked."
        if lang == 'te': msg = "మీ షాప్‌లో ప్రస్తుతం అన్ని నిల్వలు నిండుగా ఉన్నాయి."
        elif lang == 'hi': msg = "आपकी दुकान का स्टॉक वर्तमान में भरा हुआ है।"
        elif lang == 'kn': msg = "ನಿಮ್ಮ ಅಂಗಡಿಯ ದಾಸ್ತಾನು ಉತ್ತಮವಾಗಿದೆ."
        elif lang == 'ta': msg = "உங்கள் சரக்கு தற்போது நன்றாக உள்ளது."
        return {"success": True, "items": [], "whatsapp_message": msg, "language": lang, "message": msg}

    wa_lines = ["*SHOP PURCHASE ORDER*", "------------------------"]
    for item in reorder_items:
        pname = get_translated_product_name(item['product'], lang)
        unit_name = get_translated_unit_name(item['unit'], lang)
        wa_lines.append(f"• {pname}: {item['suggested_qty']} {unit_name}")
    wa_lines.append("------------------------")
    wa_lines.append("Please confirm delivery timeline. Thank you!")
    whatsapp_msg = "\n".join(wa_lines)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO reorder_orders (shop_id, status, message)
        VALUES (?, 'PREPARED', ?)
    """, (shop_id, whatsapp_msg))
    conn.commit()
    conn.close()

    item_summary = ", ".join([f"{get_translated_product_name(i['product'], lang)} ({i['suggested_qty']} {get_translated_unit_name(i['unit'], lang)})" for i in reorder_items])
    
    if lang == 'te':
        msg = f"{len(reorder_items)} సరుకులకు రీఆర్డర్ జాబితా తయారైంది: {item_summary}."
    elif lang == 'hi':
        msg = f"{len(reorder_items)} आइटम के लिए रीऑर्डर सूची तैयार है: {item_summary}।"
    elif lang == 'kn':
        msg = f"{len(reorder_items)} ವಸ್ತುಗಳಿಗೆ ಮರುಆರ್ಡರ್ ಪಟ್ಟಿ ಸಿದ್ಧವಾಗಿದೆ: {item_summary}."
    elif lang == 'ta':
        msg = f"{len(reorder_items)} பொருட்களுக்கான ரீஆர்டர் பட்டியல் தயார்: {item_summary}."
    elif lang == 'or':
        msg = f"{len(reorder_items)} ସାମଗ୍ରୀ ପାଇଁ ରିଅର୍ଡର ତାଲିକା ପ୍ରସ୍ତୁତ: {item_summary}।"
    elif lang == 'bn':
        msg = f"{len(reorder_items)} পণ্যের জন্য রিঅর্ডার তালিকা প্রস্তুত: {item_summary}।"
    elif lang == 'mr':
        msg = f"{len(reorder_items)} वस्तूंसाठी रीऑर्डर यादी तयार आहे: {item_summary}."
    elif lang == 'ml':
        msg = f"{len(reorder_items)} ഇനങ്ങൾക്കുള്ള റീഓർഡർ ലിസ്റ്റ് തയ്യാറാണ്: {item_summary}."
    elif lang == 'ja':
        msg = f"{len(reorder_items)}件の再注文リストが作成されました: {item_summary}。"
    elif lang == 'es':
        msg = f"Lista de reorden preparada para {len(reorder_items)} artículos: {item_summary}."
    else:
        msg = f"Suggested Reorder prepared for {len(reorder_items)} items: {item_summary}."

    return {
        "success": True,
        "items": reorder_items,
        "whatsapp_message": whatsapp_msg,
        "language": lang,
        "message": msg
    }

def get_transactions(shop_id=DEFAULT_SHOP_ID, limit=50):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, product_name, action, quantity, unit, price, raw_text, source, timestamp
        FROM transactions
        WHERE shop_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (shop_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_insights(shop_id=DEFAULT_SHOP_ID):
    products = get_all_products(shop_id)
    low_stock = [p for p in products if p['quantity'] <= p['reorder_level']]
    stockouts = predict_stockout(lang='en', shop_id=shop_id)['predictions']

    attention_items = []
    for s in stockouts:
        if s['days_remaining'] <= 3:
            attention_items.append({
                "product": s['product'],
                "status": f"{s['days_remaining']} days remaining",
                "severity": "CRITICAL" if s['days_remaining'] <= 2 else "WARNING"
            })
        elif s['quantity'] <= 10:
            attention_items.append({
                "product": s['product'],
                "status": "Low stock",
                "severity": "WARNING"
            })

    return {
        "total_products": len(products),
        "low_stock_count": len(low_stock),
        "attention_items": attention_items[:3],
        "products": products
    }

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
    
    vocab_parts = [f"1 {term} = {v['qty']} {get_translated_unit_name(v['unit'], lang)}" for term, v in vocab.items()]
    vocab_str = ", ".join(vocab_parts) if vocab_parts else ("పేటీ (12 ప్యాకెట్లు)" if lang == 'te' else "peti (12 packets)")

    p_units = list(set([f"{get_translated_product_name(p['name'], lang)} ({get_translated_unit_name(p['unit'], lang)})" for p in products[:3]]))
    p_units_str = ", ".join(p_units)

    sup_parts = [f"{s['products_supplied']} ({s['name']})" for s in suppliers[:2]]
    sup_str = ", ".join(sup_parts)

    msg = f"I remember that your custom units are: {vocab_str}. Your usual product units are: {p_units_str}. Suppliers: {sup_str}."
    
    if lang == 'te':
        msg = f"నాకు తెలుసు! మీ షాప్‌లో నేర్చుకున్న కొలతలు: {vocab_str}. ముఖ్యమైన నిల్వలు: {p_units_str}."
    elif lang == 'hi':
        msg = f"मुझे याद है! आपकी दुकान की मापें: {vocab_str}। मुख्य सामान: {p_units_str}।"
    elif lang == 'kn':
        msg = f"ನನಗೆ ನೆನಪಿದೆ! ನಿಮ್ಮ ಅಂಗಡಿಯ ಘಟಕಗಳು: {vocab_str}. ದಾಸ್ತಾನು: {p_units_str}."
    elif lang == 'ta':
        msg = f"எனக்கு நினைவிருக்கிறது! உங்கள் கடை அளவுகள்: {vocab_str}. முக்கிய பொருட்கள்: {p_units_str}."
    elif lang == 'or':
        msg = f"ମୋର ମନେଅଛି! ଆପଣଙ୍କ ଦୋକାନର ମାପ: {vocab_str}।"
    elif lang == 'bn':
        msg = f"আমার মনে আছে! আপনার দোকানের পরিমাপ: {vocab_str}।"
    elif lang == 'mr':
        msg = f"मला आठवते! तुमच्या दुकानातील मोजमापे: {vocab_str}."
    elif lang == 'ml':
        msg = f"എനിക്ക് ഓർമ്മയുണ്ട്! നിങ്ങളുടെ കടയിലെ അളവുകൾ: {vocab_str}."
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

    msg = f"Good morning! You have {len(low_stock)} items low in stock. "
    if urgent_items:
        u_str = ", ".join([get_translated_product_name(item, lang) for item in urgent_items])
        msg += f"Urgent attention needed for: {u_str}. "
    msg += f"Total inventory valuation is ₹{total_val:,.0f}."

    if lang == 'te':
        msg = f"శుభోదయం! మీ షాప్‌లో {len(low_stock)} సరుకులు తక్కువగా ఉన్నాయి. "
        if urgent_items:
            u_str = ", ".join([get_translated_product_name(item, lang) for item in urgent_items])
            msg += f"వెంటనే దృష్టి పెట్టాల్సినవి: {u_str}. "
        msg += f"మొత్తం నిల్వ విలువ ₹{total_val:,.0f}."
    elif lang == 'hi':
        msg = f"सुप्रभात! आपकी दुकान में {len(low_stock)} आइटम कम हैं। "
        if urgent_items:
            u_str = ", ".join([get_translated_product_name(item, lang) for item in urgent_items])
            msg += f"तुरंत ध्यान देने की आवश्यकता है: {u_str}। "
        msg += f"कुल स्टॉक मूल्य ₹{total_val:,.0f} है।"
    elif lang == 'kn':
        msg = f"ಶುಭೋದಯ! ನಿಮ್ಮ ಅಂಗಡಿಯಲ್ಲಿ {len(low_stock)} ವಸ್ತುಗಳು ಕಡಿಮೆಯಾಗಿವೆ. ಒಟ್ಟು ದಾಸ್ತಾನು ಮೌಲ್ಯ ₹{total_val:,.0f}."
    elif lang == 'ta':
        msg = f"காலை வணக்கம்! உங்கள் கடையில் {len(low_stock)} பொருட்கள் குறைவாக உள்ளன. மொத்த இருப்பு மதிப்பு ₹{total_val:,.0f}."

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
    total_units = sum(p['quantity'] for p in products)
    potential_profit = max(0.0, total_market_value - total_purchase_cost)

    msg = f"Your current inventory is worth approximately ₹{total_purchase_cost:,.0f} at purchase cost, with a potential retail market value of ₹{total_market_value:,.0f} (Estimated profit: ₹{potential_profit:,.0f})."
    
    if lang == 'te':
        msg = f"మీ ప్రస్తుత నిల్వల కొనుగోలు విలువ సుమారు ₹{total_purchase_cost:,.0f}, అమ్మకం మార్కెట్ విలువ ₹{total_market_value:,.0f} (అంచనా లాభం: ₹{potential_profit:,.0f})."
    elif lang == 'hi':
        msg = f"आपके वर्तमान स्टॉक का खरीद मूल्य लगभग ₹{total_purchase_cost:,.0f} है, और बिक्री मूल्य ₹{total_market_value:,.0f} है (अनुमानित लाभ: ₹{potential_profit:,.0f})।"
    elif lang == 'kn':
        msg = f"ನಿಮ್ಮ ದಾಸ್ತಾನಿನ ಖರೀದಿ ಮೌಲ್ಯ ಸುಮಾರು ₹{total_purchase_cost:,.0f}, ಮಾರಾಟ ಮೌಲ್ಯ ₹{total_market_value:,.0f}."
    elif lang == 'ta':
        msg = f"உங்கள் தற்போதைய இருப்பின் வாங்கிய மதிப்பு சுமார் ₹{total_purchase_cost:,.0f}, விற்பனை மதிப்பு ₹{total_market_value:,.0f}."

    return {
        "success": True,
        "language": lang,
        "total_purchase_cost": total_purchase_cost,
        "total_cost_valuation": total_purchase_cost,
        "total_market_value": total_market_value,
        "total_retail_valuation": total_market_value,
        "potential_profit": potential_profit,
        "potential_gross_profit": potential_profit,
        "total_items_in_stock": total_units,
        "message": msg
    }

def get_product_margins(shop_id=DEFAULT_SHOP_ID, lang='en'):
    products = get_all_products(shop_id)
    margin_items = []

    for p in products:
        sell_p = float(p.get('price') or 0.0)
        buy_p = float(p.get('purchase_price') or (sell_p * 0.85))
        margin = max(0.0, sell_p - buy_p)
        margin_pct = (margin / sell_p * 100) if sell_p > 0 else 0.0
        qty = float(p.get('quantity') or 0.0)
        stock_val = qty * buy_p

        margin_items.append({
            "product": p['name'],
            "category": p.get('category', 'General'),
            "quantity": qty,
            "unit": p['unit'],
            "purchase_price": round(buy_p, 2),
            "selling_price": round(sell_p, 2),
            "price": round(sell_p, 2),
            "margin": round(margin, 2),
            "margin_rs": round(margin, 2),
            "margin_pct": round(margin_pct, 1),
            "stock_valuation_cost": round(stock_val, 2)
        })

    margin_items.sort(key=lambda x: x['margin'], reverse=True)
    top_margin = margin_items[0] if margin_items else None

    if top_margin:
        pname_lang = get_translated_product_name(top_margin['product'], lang)
        unit_lang = get_translated_unit_singular(top_margin['unit'], lang)
        msg = f"The product with the highest profit margin is {pname_lang} with a margin of ₹{top_margin['margin']:g}/{unit_lang} ({top_margin['margin_pct']}% profit margin)."
    else:
        msg = "No product margins calculated."

    if lang == 'te' and top_margin:
        msg = f"అత్యధిక లాభం ఇచ్చే సరుకు: {pname_lang} (ప్రతి {unit_lang} పై ₹{top_margin['margin']:g} లాభం, {top_margin['margin_pct']}% మార్జిన్)."
    elif lang == 'hi' and top_margin:
        msg = f"सबसे ज्यादा मुनाफे वाला सामान: {pname_lang} (प्रति {unit_lang} ₹{top_margin['margin']:g} लाभ, {top_margin['margin_pct']}% मार्जिन)।"
    elif lang == 'kn' and top_margin:
        msg = f"ಹೆಚ್ಚಿನ ಲಾಭದ ಉತ್ಪನ್ನ: {pname_lang} (ಪ್ರತಿ {unit_lang} ಗೆ ₹{top_margin['margin']:g} ಲಾಭ)."
    elif lang == 'ta' and top_margin:
        msg = f"அதிக லாபம் தரும் பொருள்: {pname_lang} (ஒரு {unit_lang} க்கு ₹{top_margin['margin']:g} லாபம்)."

    return {
        "success": True,
        "language": lang,
        "margins": margin_items,
        "top_margin_product": top_margin,
        "message": msg
    }

