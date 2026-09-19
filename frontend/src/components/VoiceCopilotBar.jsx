import React, { useState, useEffect } from 'react';
import {
  Mic,
  MicOff,
  Send,
  AlertTriangle,
  Globe
} from 'lucide-react';

import './VoiceCopilotBar.css';

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

const MULTILINGUAL_STORYLINE = [
  { id: 1, label: '🧠 What do you remember?', prompt: 'What do you remember about my shop?', lang: 'en' },
  { id: 2, label: '☀️ Daily Briefing', prompt: 'Give me daily briefing', lang: 'en' },
  { id: 3, label: '💰 Total Inventory Value', prompt: 'What is my total inventory value?', lang: 'en' },
  { id: 4, label: '📈 Highest Profit Margin', prompt: 'Which product gives the highest margin?', lang: 'en' },
  { id: 5, label: '👥 Who supplies Rice?', prompt: 'Who supplies Rice?', lang: 'en' },
  { id: 6, label: '🌾 Rice 5 bags aaye', prompt: 'Rice ke 5 bags aaye hain', lang: 'en' },
  { id: 7, label: '🇮🇳 బియ్యం 5 బస్తాలు వచ్చాయి', prompt: 'బియ్యం 5 బస్తాలు వచ్చాయి', lang: 'te' },
  { id: 8, label: '🇮🇳 నా దగ్గర ఎంత బియ్యం ఉంది?', prompt: 'నా దగ్గర ఎంత బియ్యం ఉంది?', lang: 'te' },
  { id: 9, label: '🇮🇳 चावल 5 बैग आये', prompt: 'चावल के 5 बैग आये हैं', lang: 'hi' },
  { id: 10, label: '🇮🇳 ಅಕ್ಕಿ 5 ಚೀಲಗಳು ಸೇರಿಸು', prompt: 'ಅಕ್ಕಿ 5 ಚೀಲಗಳು ಸೇರಿಸು', lang: 'kn' },
  { id: 11, label: '🇮🇳 அரிசி 5 மூட்டைகள் சேர்', prompt: 'அரிசி 5 மூட்டைகள் சேர்', lang: 'ta' },
  { id: 12, label: '🇯🇵 お米を 5 バッグ 追加', prompt: 'お米を 5 バッグ 追加', lang: 'ja' },
  { id: 13, label: '🇪🇸 Añadir 5 bolsas de arroz', prompt: 'Añadir 5 bolsas de arroz', lang: 'es' },
  { id: 14, label: '⚠️ Remove 25 bags Rice (Safety Check)', prompt: 'Rice 25 bags remove', lang: 'en' }
];

export default function VoiceCopilotBar({
  onSendMessage,
  isProcessing,
  attentionItems
}) {
  const [selectedLang, setSelectedLang] = useState('en-IN');
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [textInput, setTextInput] = useState('');
  const [recognition, setRecognition] = useState(null);

  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      return;
    }

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
        // Recognition may already be stopped.
      }
    };
  }, [selectedLang]);

  const handleLangChange = (langCode) => {
    if (isListening && recognition) {
      try {
        recognition.stop();
      } catch {
        // Already stopped.
      }
    }
    setSelectedLang(langCode);
  };

  const toggleListening = () => {
    if (!recognition) {
      alert(
        'Browser speech recognition is not supported. You can type or click the demo prompts below!'
      );
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
    } catch (error) {
      console.warn('Could not start speech recognition:', error);
    }
  };

  const handleSend = (textToSend, forcedLang = null) => {
    const text = textToSend || textInput || transcript;
    if (!text.trim()) {
      return;
    }

    let langTag = forcedLang;
    if (!langTag) {
      const match = SUPPORTED_LANGUAGES.find((l) => l.code === selectedLang);
      langTag = match ? match.tag : 'en';
    }

    onSendMessage(text, langTag);

    setTextInput('');
    setTranscript('');

    if (isListening && recognition) {
      try {
        recognition.stop();
      } catch {
        // Already stopped.
      }
    }
  };

  return (
    <div className="glass-card copilot-hero-card">
      {/* ATTENTION BANNER */}
      {attentionItems && attentionItems.length > 0 && (
        <div
          style={{
            background: 'var(--accent-ochre-light)',
            border: '1px solid rgba(214, 163, 94, 0.4)',
            borderRadius: '12px',
            padding: '0.55rem 0.9rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.65rem',
            fontSize: '0.82rem',
            color: 'var(--accent-ochre-dark)'
          }}
        >
          <AlertTriangle size={16} color="#C69248" />
          <div
            style={{
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap'
            }}
          >
            <strong>Attention: </strong>
            {attentionItems.map((item, idx) => (
              <span key={idx} style={{ marginRight: '0.75rem' }}>
                ⚠️ <strong>{item.product}</strong> ({item.status})
              </span>
            ))}
          </div>
        </div>
      )}

      {/* LANGUAGE SELECTION BAR */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          paddingBottom: '0.55rem',
          borderBottom: '1px solid var(--border-sand)',
          flexWrap: 'wrap',
          gap: '0.5rem'
        }}
      >
        <div
          style={{
            fontSize: '0.8rem',
            fontWeight: 700,
            color: 'var(--accent-denim-dark)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.35rem'
          }}
        >
          <Globe size={15} />
          Spoken Speech Mode
        </div>

        <div className="lang-pills-row">
          {SUPPORTED_LANGUAGES.map((langObj) => (
            <button
              key={langObj.code}
              type="button"
              className={`lang-pill ${
                selectedLang === langObj.code ? 'active' : ''
              }`}
              onClick={() => handleLangChange(langObj.code)}
            >
              {langObj.label}
            </button>
          ))}
        </div>
      </div>

      {/* MICROPHONE */}
      <div className="mic-wrapper">
        <button
          className={`mic-button ${isListening ? 'listening' : ''}`}
          onClick={toggleListening}
          title={
            isListening ? 'Listening... Click to stop' : 'Tap to speak'
          }
        >
          {isListening ? <MicOff size={34} /> : <Mic size={34} />}
        </button>

        <div style={{ marginTop: '0.45rem', textAlign: 'center' }}>
          <div
            style={{
              fontSize: '0.95rem',
              fontWeight: 800,
              color: isListening ? '#C96F73' : 'var(--accent-denim-dark)'
            }}
          >
            {isListening
              ? `🎙️ Listening (${selectedLang.toUpperCase()})...`
              : isProcessing
              ? '🧠 Thinking & updating database...'
              : '🎙️ TAP TO SPEAK'}
          </div>
        </div>

        {/* Wave */}
        <div className="sound-wave">
          {[1, 2, 3, 4, 5].map((i) => (
            <div
              key={i}
              className={`wave-bar ${isListening ? 'active' : ''}`}
            />
          ))}
        </div>

        {/* Transcript */}
        {transcript && (
          <div
            style={{
              marginTop: '0.4rem',
              padding: '0.45rem 0.8rem',
              background: 'var(--accent-denim-light)',
              border: '1px solid var(--accent-faded-denim)',
              borderRadius: '10px',
              fontSize: '0.82rem',
              color: 'var(--accent-denim-dark)',
              fontStyle: 'italic',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              maxWidth: '90%'
            }}
          >
            <span>"{transcript}"</span>
            <button
              onClick={() => handleSend(transcript)}
              className="btn-primary"
              style={{ padding: '0.25rem 0.55rem', fontSize: '0.75rem' }}
            >
              Send
            </button>
          </div>
        )}
      </div>

      {/* TEXT INPUT */}
      <div className="text-input-bar">
        <input
          type="text"
          className="app-input"
          placeholder='Type a command in any language... e.g. "Rice 5 bags", "అక్కి 5 ಚೀಲಗಳು", "お米を5バッグ"'
          value={textInput}
          onChange={(e) => setTextInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              handleSend();
            }
          }}
        />

        <button
          className="btn-primary"
          onClick={() => handleSend()}
          disabled={isProcessing}
        >
          <Send size={15} />
          Send
        </button>
      </div>

      {/* DEMO STORYLINE */}
      <div>
        <div
          style={{
            fontSize: '10px',
            fontWeight: 700,
            color: 'var(--text-muted)',
            marginBottom: '5px',
            textTransform: 'uppercase',
            letterSpacing: '0.08em'
          }}
        >
          Try a demo command
        </div>

        <div className="storyline-chips-container">
          {MULTILINGUAL_STORYLINE.map((step) => (
            <button
              key={step.id}
              className="story-chip"
              onClick={() => handleSend(step.prompt, step.lang)}
              disabled={isProcessing}
            >
              <span>{step.label}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}