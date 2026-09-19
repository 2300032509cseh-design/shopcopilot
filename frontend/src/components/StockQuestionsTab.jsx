import React, { useState, useEffect } from 'react';
import './StockQuestionsTab.css';

const SUPPORTED_LANGUAGES = [
  { code: 'en-IN', label: '🌐 Auto / Hinglish', tag: 'en' },
  { code: 'te-IN', label: '🇮🇳 Telugu', tag: 'te' },
  { code: 'hi-IN', label: '🇮🇳 Hindi', tag: 'hi' },
  { code: 'kn-IN', label: '🇮🇳 Kannada', tag: 'kn' },
  { code: 'ta-IN', label: '🇮🇳 Tamil', tag: 'ta' },
  { code: 'or-IN', label: '🇮🇳 Odia', tag: 'or' },
  { code: 'bn-IN', label: '🇮🇳 Bengali', tag: 'bn' },
  { code: 'mr-IN', label: '🇮🇳 Marathi', tag: 'mr' },
  { code: 'ml-IN', label: '🇮🇳 Malayalam', tag: 'ml' },
  { code: 'ja-JP', label: '🇯🇵 Japanese', tag: 'ja' },
  { code: 'es-ES', label: '🇪🇸 Spanish', tag: 'es' }
];

const VOICE_QUESTION_CHIPS = [
  { id: 1, label: '🌾 How much Rice left?', prompt: 'How much Rice do I have left?', lang: 'en' },
  { id: 2, label: '🇮🇳 నా దగ్గర ఎంత బియ్యం ఉంది?', prompt: 'నా దగ్గర ఎంత బియ్యం ఉంది?', lang: 'te' },
  { id: 3, label: '⚠️ Which items are low?', prompt: 'Which items are low in stock?', lang: 'en' },
  { id: 4, label: '🇮🇳 ఏ సరుకులు తక్కువగా ఉన్నాయి?', prompt: 'ఏ సరుకులు తక్కువగా ఉన్నాయి?', lang: 'te' },
  { id: 5, label: '📉 What will finish first?', prompt: 'What will finish first?', lang: 'en' },
  { id: 6, label: '🛒 Do I need to reorder today?', prompt: 'Do I need to reorder anything today?', lang: 'en' },
  { id: 7, label: '🥛 Is Milk stock okay or low?', prompt: 'Is Milk stock okay or low?', lang: 'en' },
  { id: 8, label: '🇮🇳 పప్పు నిల్వ ఎంత ఉంది?', prompt: 'పప్పు నిల్వ ఎంత ఉంది?', lang: 'te' },
  { id: 9, label: '🇮🇳 चावल कितना बचा है?', prompt: 'चावल कितना बचा है?', lang: 'hi' }
];

export default function StockQuestionsTab({ onAskVoiceQuestion, onOpenReorderModal }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filterMode, setFilterMode] = useState('all');
  const [queryText, setQueryText] = useState('');
  const [activeAnswer, setActiveAnswer] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  // Speech Recognition States
  const [selectedLang, setSelectedLang] = useState('en-IN');
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [recognition, setRecognition] = useState(null);

  useEffect(() => {
    fetchStockAssistantData();
  }, []);

  // Web Speech Recognition Setup
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return;

    const rec = new SpeechRecognition();
    rec.continuous = false;
    rec.interimResults = true;
    rec.lang = selectedLang;

    rec.onstart = () => {
      setIsListening(true);
    };

    rec.onresult = (event) => {
      let fullTranscript = '';
      for (let i = 0; i < event.results.length; i++) {
        fullTranscript += event.results[i][0].transcript;
      }
      setTranscript(fullTranscript);
      setQueryText(fullTranscript);
    };

    rec.onerror = (event) => {
      console.warn('Speech recognition error:', event.error);
      setIsListening(false);
    };

    rec.onend = () => {
      setIsListening(false);
    };

    setRecognition(rec);

    return () => {
      try {
        rec.stop();
      } catch {
        // Recognition already stopped
      }
    };
  }, [selectedLang]);

  const toggleListening = () => {
    if (!recognition) {
      alert('Browser speech recognition is not supported in this browser. You can type or click the demo question chips below!');
      return;
    }

    if (isListening) {
      recognition.stop();
      return;
    }

    setTranscript('');
    try {
      recognition.lang = selectedLang;
      recognition.start();
    } catch (err) {
      console.warn('Could not start speech recognition:', err);
    }
  };

  const speakText = (text, lang = 'en', speechText = null) => {
    const textToSpeak = speechText || text;
    if (!('speechSynthesis' in window) || !textToSpeak) return;
    window.speechSynthesis.cancel();
    const voices = window.speechSynthesis.getVoices();

    const langCodeMap = {
      'te': 'te-IN', 'hi': 'hi-IN', 'kn': 'kn-IN', 'ta': 'ta-IN', 'or': 'or-IN',
      'bn': 'bn-IN', 'mr': 'mr-IN', 'ml': 'ml-IN', 'ja': 'ja-JP', 'es': 'es-ES', 'en': 'en-IN'
    };

    const targetLang = langCodeMap[lang] || selectedLang || 'en-IN';

    const hasNativeLangVoice = voices.some((v) =>
      v.lang.toLowerCase().startsWith(lang.toLowerCase())
    );

    const matchedVoice =
      voices.find((v) => v.lang.toLowerCase() === targetLang.toLowerCase()) ||
      voices.find((v) => v.lang.toLowerCase().startsWith(lang.toLowerCase())) ||
      voices.find((v) => v.lang.includes('IN')) ||
      voices.find((v) => v.lang.startsWith('en'));

    const finalContentToSpeak = (hasNativeLangVoice ? text : textToSpeak) || text;
    const utterance = new SpeechSynthesisUtterance(finalContentToSpeak);
    utterance.lang = targetLang;

    if (matchedVoice) utterance.voice = matchedVoice;
    utterance.rate = 0.95;
    window.speechSynthesis.speak(utterance);
  };

  const fetchStockAssistantData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('shop_copilot_token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};

      const res = await fetch('http://127.0.0.1:5050/api/stock-assistant', { headers });
      const resData = await res.json();
      if (resData.success) {
        setData(resData);
      }
    } catch (err) {
      console.error('Failed to load stock assistant data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAskQuestion = async (promptText) => {
    const text = promptText || queryText || transcript;
    if (!text.trim()) return;

    if (isListening && recognition) {
      try { recognition.stop(); } catch {}
    }

    setIsProcessing(true);
    setActiveAnswer(null);

    try {
      const token = localStorage.getItem('shop_copilot_token');
      const headers = {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      };

      const matchLang = SUPPORTED_LANGUAGES.find(l => l.code === selectedLang);
      const langTag = matchLang ? matchLang.tag : 'en';

      const res = await fetch('http://127.0.0.1:5050/api/process-voice', {
        method: 'POST',
        headers,
        body: JSON.stringify({ text, language: langTag })
      });
      const resData = await res.json();
      
      setActiveAnswer(resData);
      setQueryText('');
      setTranscript('');
      fetchStockAssistantData();

      if (resData.message) {
        speakText(resData.message, resData.language || langTag, resData.speech_text);
      }

      if (onAskVoiceQuestion) {
        onAskVoiceQuestion(text);
      }
    } catch (err) {
      console.error('Error processing question:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const getStatusBadge = (status) => {
    if (status === 'HIGH') return <span className="status-badge high">🟢 HIGH STOCK</span>;
    if (status === 'OKAY') return <span className="status-badge okay">🟡 OKAY</span>;
    return <span className="status-badge low">🔴 LOW ALERT</span>;
  };

  const productsList = data?.products || [];
  const filteredProducts = productsList.filter(p => {
    if (filterMode === 'all') return true;
    return p.stock_status === filterMode;
  });

  return (
    <div className="stock-assistant-container">
      {/* HEADER & VOICE ASSISTANT BAR */}
      <div className="stock-assistant-header">
        <div className="header-title">
          <span className="icon">🎙️</span>
          <div>
            <h2>Voice Stock Assistant & Reorder Alerts</h2>
            <p className="subtitle">Ask any stock question by voice — get instant HIGH, OKAY, or LOW status ratings out loud</p>
          </div>
        </div>

        {/* Language Selection Row */}
        <div className="assistant-lang-row">
          <span className="lang-label">🌐 Voice Language:</span>
          <div className="lang-pills-scroll">
            {SUPPORTED_LANGUAGES.map((l) => (
              <button
                key={l.code}
                className={`lang-pill-btn ${selectedLang === l.code ? 'active' : ''}`}
                onClick={() => setSelectedLang(l.code)}
              >
                {l.label}
              </button>
            ))}
          </div>
        </div>

        {/* Voice Input & Mic Control Card */}
        <div className="voice-input-card">
          <div className="mic-control-row">
            <button
              type="button"
              className={`big-mic-btn ${isListening ? 'listening' : ''}`}
              onClick={toggleListening}
              title={isListening ? 'Listening... Tap to stop' : 'Tap to speak question'}
            >
              {isListening ? '🛑 Stop' : '🎙️ TAP TO SPEAK'}
            </button>

            <div className="mic-status-info">
              {isListening ? (
                <span className="recording-text">🎙️ Listening in {selectedLang.toUpperCase()}... Speak now!</span>
              ) : isProcessing ? (
                <span className="thinking-text">🧠 Analyzing stock & answering...</span>
              ) : (
                <span className="idle-text">Click the mic or type your question below:</span>
              )}
            </div>
          </div>

          <div className="input-group">
            <input
              type="text"
              placeholder='Type or speak a stock question... e.g. "How much Rice left?", "Is Sugar low?", "నా దగ్గర ఎంత బియ్యం ఉంది?"'
              value={queryText}
              onChange={(e) => setQueryText(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAskQuestion()}
            />
            <button 
              className="ask-btn"
              onClick={() => handleAskQuestion()}
              disabled={isProcessing}
            >
              {isProcessing ? 'Thinking...' : '⚡ Ask Copilot'}
            </button>
          </div>

          <div className="question-chips">
            <span className="chips-label">Try asking:</span>
            {VOICE_QUESTION_CHIPS.map(chip => (
              <button 
                key={chip.id} 
                className="chip-btn"
                onClick={() => handleAskQuestion(chip.prompt)}
                disabled={isProcessing}
              >
                {chip.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* VOICE RESPONSE DISPLAY CARD */}
      {activeAnswer && (
        <div className={`answer-card ${activeAnswer.status === 'NEED_CONFIRMATION' ? 'alert' : ''}`}>
          <div className="answer-header">
            <span className="copilot-badge">🧠 Copilot Spoken Answer</span>
            <button 
              className="replay-btn"
              onClick={() => speakText(activeAnswer.message, activeAnswer.language || 'en', activeAnswer.speech_text)}
            >
              🔊 Replay Voice
            </button>
            {activeAnswer.stock_status && getStatusBadge(activeAnswer.stock_status)}
          </div>
          <p className="answer-text">"{activeAnswer.message}"</p>
        </div>
      )}

      {loading ? (
        <div className="stock-loading">Loading stock health and reorder alerts...</div>
      ) : (
        <>
          {/* HEALTH SUMMARY KPI CARDS */}
          <div className="stock-kpi-grid">
            <div className="kpi-box">
              <span className="kpi-num">{data?.total_products || 0}</span>
              <span className="kpi-label">Total Products Tracked</span>
            </div>

            <div className="kpi-box high" onClick={() => setFilterMode('HIGH')}>
              <span className="kpi-num">🟢 {data?.high_count || 0}</span>
              <span className="kpi-label">Healthy & High Stock</span>
            </div>

            <div className="kpi-box okay" onClick={() => setFilterMode('OKAY')}>
              <span className="kpi-num">🟡 {data?.okay_count || 0}</span>
              <span className="kpi-label">Okay / Sufficient Stock</span>
            </div>

            <div className="kpi-box low" onClick={() => setFilterMode('LOW')}>
              <span className="kpi-num">🔴 {data?.low_count || 0}</span>
              <span className="kpi-label">Low Stock Alerts</span>
            </div>
          </div>

          {/* ACTIVE REORDER ALERTS PANEL */}
          {data?.reorder_alerts?.length > 0 && (
            <div className="reorder-alerts-panel">
              <div className="panel-header">
                <h3>⚠️ Active Reorder Alerts ({data.reorder_alerts.length} Items Below Threshold)</h3>
                <button 
                  className="whatsapp-order-all-btn"
                  onClick={() => onOpenReorderModal && onOpenReorderModal()}
                >
                  💬 Prepare WhatsApp Order
                </button>
              </div>

              <div className="alerts-grid">
                {data.reorder_alerts.map((alert, idx) => (
                  <div key={idx} className="alert-card">
                    <div className="alert-card-header">
                      <span className="alert-pname">{alert.product}</span>
                      <span className="alert-days">Est. {alert.days_remaining} days left</span>
                    </div>

                    <div className="alert-details">
                      <div>Current Stock: <strong>{alert.current_qty} {alert.unit}</strong></div>
                      <div>Suggested Reorder: <strong className="suggested">{alert.suggested_qty} {alert.unit}</strong></div>
                    </div>

                    <button 
                      className="card-wa-btn"
                      onClick={() => onOpenReorderModal && onOpenReorderModal()}
                    >
                      💬 Order {alert.product}
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* SHOP STOCK HEALTH GRID */}
          <div className="stock-grid-section">
            <div className="section-header">
              <h3>📦 Shop Stock Health Overview</h3>
              <div className="filter-buttons">
                <button className={filterMode === 'all' ? 'active' : ''} onClick={() => setFilterMode('all')}>All ({data?.total_products || 0})</button>
                <button className={filterMode === 'HIGH' ? 'active' : ''} onClick={() => setFilterMode('HIGH')}>🟢 High ({data?.high_count || 0})</button>
                <button className={filterMode === 'OKAY' ? 'active' : ''} onClick={() => setFilterMode('OKAY')}>🟡 Okay ({data?.okay_count || 0})</button>
                <button className={filterMode === 'LOW' ? 'active' : ''} onClick={() => setFilterMode('LOW')}>🔴 Low Alerts ({data?.low_count || 0})</button>
              </div>
            </div>

            <div className="table-responsive">
              <table className="stock-health-table">
                <thead>
                  <tr>
                    <th>Product Name</th>
                    <th>Category</th>
                    <th>Available Stock</th>
                    <th>Reorder Threshold</th>
                    <th>Stock Health Status</th>
                    <th>Est. Days Left</th>
                    <th>Ask Status</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredProducts.length === 0 ? (
                    <tr>
                      <td colSpan="7" className="empty-row">No products match the selected status filter.</td>
                    </tr>
                  ) : (
                    filteredProducts.map((p, idx) => (
                      <tr key={idx} className={p.stock_status === 'LOW' ? 'row-low' : ''}>
                        <td className="p-name">{p.name}</td>
                        <td><span className="cat-chip">{p.category}</span></td>
                        <td className="qty-cell">{p.quantity} {p.unit}</td>
                        <td>{p.reorder_level} {p.unit}</td>
                        <td>{getStatusBadge(p.stock_status)}</td>
                        <td><strong>~{p.days_remaining} days</strong></td>
                        <td>
                          <button 
                            className="ask-item-btn"
                            onClick={() => handleAskQuestion(`How much ${p.name} do I have left?`)}
                          >
                            🎙️ Ask Status
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
