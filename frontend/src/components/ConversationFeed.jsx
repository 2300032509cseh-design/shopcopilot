import React from 'react';
import { Bot, User, Volume2 } from 'lucide-react';
import './ConversationFeed.css';

export default function ConversationFeed({ messages, onSelectOption, onSpeakText }) {
  return (
    <div className="glass-card conversation-card">
      <div className="conversation-header">
        <h3 className="feed-title">
          <Bot size={18} className="feed-title-icon" />
          <span>Live Conversation Feed</span>
        </h3>
        <span className="feed-count">
          {messages.length} messages
        </span>
      </div>

      <div className="conversation-box">
        {messages.length === 0 ? (
          <div className="empty-feed">
            <Bot size={36} className="empty-feed-icon" />
            <p>No voice commands yet. Speak or click a storyline prompt above!</p>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div
              key={idx}
              className={`message-bubble ${
                msg.sender === 'user'
                  ? 'user'
                  : msg.status === 'NEED_UNIT_CLARIFICATION' ||
                    msg.status === 'NEED_VOCABULARY_LEARNING' ||
                    msg.status === 'NEED_PRODUCT_CLARIFICATION'
                  ? 'copilot-clarify'
                  : 'copilot'
              }`}
            >
              <div className="message-header">
                <span className="sender-tag">
                  {msg.sender === 'user' ? <User size={13} /> : <Bot size={13} />}
                  {msg.sender === 'user' ? 'SHOPKEEPER' : 'SHOP COPILOT'}
                </span>
                {msg.intent && (
                  <span className="intent-badge">
                    {msg.intent}
                  </span>
                )}
              </div>

              <div className="message-text">
                {msg.text}
              </div>

              {/* Memory updated tag */}
              {msg.learned_vocab && (
                <div className="memory-updated-tag">
                  🧠 <strong>Memory Updated:</strong> {msg.learned_vocab}
                </div>
              )}

              {/* Interactive Clarification Quick Options */}
              {msg.status === 'NEED_UNIT_CLARIFICATION' && (
                <div className="quick-options-row">
                  <button
                    type="button"
                    className="option-btn"
                    onClick={() => onSelectOption('kg')}
                  >
                    👉 Say "kg"
                  </button>
                  <button
                    type="button"
                    className="option-btn"
                    onClick={() => onSelectOption('bags')}
                  >
                    👉 Say "bags"
                  </button>
                </div>
              )}

              {/* Interactive Product Clarification Quick Options */}
              {msg.status === 'NEED_PRODUCT_CLARIFICATION' && (
                <div className="quick-options-row">
                  <button
                    type="button"
                    className="option-btn"
                    onClick={() => onSelectOption('Rice')}
                  >
                    👉 Say "Rice"
                  </button>
                  <button
                    type="button"
                    className="option-btn"
                    onClick={() => onSelectOption('Sugar')}
                  >
                    👉 Say "Sugar"
                  </button>
                  <button
                    type="button"
                    className="option-btn"
                    onClick={() => onSelectOption('Biscuits')}
                  >
                    👉 Say "Biscuits"
                  </button>
                </div>
              )}

              {/* TTS Audio Replay Button */}
              {msg.sender === 'copilot' && (
                <div className="audio-replay-row">
                  <button
                    type="button"
                    onClick={() => onSpeakText(msg.text, msg.language, msg.speech_text)}
                    className="replay-audio-btn"
                    title="Replay Voice Audio"
                  >
                    <Volume2 size={13} /> Play Audio
                  </button>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
