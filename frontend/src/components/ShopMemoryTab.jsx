import React, { useState, useEffect } from 'react';
import './ShopMemoryTab.css';

export default function ShopMemoryTab({ shop, onTriggerVoicePrompt }) {
  const [memories, setMemories] = useState([]);
  const [vocab, setVocab] = useState([]);
  const [memorySummary, setMemorySummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [newKey, setNewKey] = useState('');
  const [newValue, setNewValue] = useState('');

  const fetchShopMemory = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('shop_copilot_token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};

      const [memRes, vocabRes, analyticsRes] = await Promise.all([
        fetch('http://127.0.0.1:5050/api/memory', { headers }),
        fetch('http://127.0.0.1:5050/api/vocabulary', { headers }),
        fetch('http://127.0.0.1:5050/api/analytics', { headers }),
      ]);

      const memData = await memRes.json();
      const vocabData = await vocabRes.json();
      const analyticsData = await analyticsRes.json();

      if (memData.memories) setMemories(memData.memories);
      if (vocabData.vocabulary) setVocab(vocabData.vocabulary);
      if (analyticsData.briefing) setMemorySummary(analyticsData.briefing);
    } catch (err) {
      console.error('Failed to load shop memory:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchShopMemory();
  }, []);

  const handleAddMemory = async (e) => {
    e.preventDefault();
    if (!newKey || !newValue) return;
    try {
      const token = localStorage.getItem('shop_copilot_token');
      const headers = {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      };

      const res = await fetch('http://127.0.0.1:5050/api/memory', {
        method: 'POST',
        headers,
        body: JSON.stringify({ key: newKey, value: newValue, memory_type: 'preference' }),
      });
      const data = await res.json();
      if (data.success) {
        setNewKey('');
        setNewValue('');
        fetchShopMemory();
      }
    } catch (err) {
      console.error('Error adding memory:', err);
    }
  };

  return (
    <div className="shop-memory-container">
      <div className="shop-memory-header">
        <div className="header-title-box">
          <span className="brain-icon">🧠</span>
          <div>
            <h2>Shop Memory & Intelligence</h2>
            <p className="subtitle">
              Copilot remembers key facts, custom terminology, unit mappings, and vendor relations isolated to <strong>{shop?.shop_name || 'Your Shop'}</strong>.
            </p>
          </div>
        </div>
        <button 
          className="voice-query-btn"
          onClick={() => onTriggerVoicePrompt && onTriggerVoicePrompt("What do you remember about my shop?")}
        >
          🎙️ Ask: "What do you remember?"
        </button>
      </div>

      {loading ? (
        <div className="memory-loading">Loading Shop Memory state...</div>
      ) : (
        <div className="memory-grid">
          {/* Card 1: Daily Briefing & Health */}
          <div className="memory-card highlight">
            <h3>☀️ Copilot Daily Briefing Snapshot</h3>
            <p className="briefing-greeting">{memorySummary?.greeting || 'Shop memory active.'}</p>
            <div className="briefing-stats">
              <div className="stat-badge">
                <span className="label">Total Products:</span>
                <span className="value">{memorySummary?.total_products || 0}</span>
              </div>
              <div className="stat-badge alert">
                <span className="label">Low Stock Items:</span>
                <span className="value">{memorySummary?.stockouts_count || 0}</span>
              </div>
            </div>
            {memorySummary?.recommendations?.length > 0 && (
              <div className="briefing-recs">
                <strong>Current Focus:</strong>
                <ul>
                  {memorySummary.recommendations.map((rec, idx) => (
                    <li key={idx}>{rec}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Card 2: Learned Custom Vocabulary */}
          <div className="memory-card">
            <h3>📚 Custom Shop Vocabulary & Units</h3>
            <p className="card-desc">Local words Copilot understands for your inventory:</p>
            <div className="vocab-chips">
              {vocab.map((v, i) => (
                <div key={i} className="vocab-chip">
                  <span className="term">{v.term}</span>
                  <span className="arrow">➔</span>
                  <span className="eq">{v.equivalent_qty} {v.equivalent_unit}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Card 3: Explicit Custom Memories */}
          <div className="memory-card">
            <h3>📝 Saved Shop Notes & Preferences</h3>
            <p className="card-desc">Persistent rules remembered by Copilot:</p>
            <div className="custom-memories-list">
              {memories.length === 0 ? (
                <div className="empty-memories">No explicit notes saved yet. Add one below!</div>
              ) : (
                memories.map((m, idx) => (
                  <div key={idx} className="memory-item">
                    <span className="key">{m.key}:</span>
                    <span className="val">{m.value}</span>
                  </div>
                ))
              )}
            </div>

            <form onSubmit={handleAddMemory} className="add-memory-form">
              <input
                type="text"
                placeholder="Topic (e.g. Peak Hours)"
                value={newKey}
                onChange={(e) => setNewKey(e.target.value)}
                required
              />
              <input
                type="text"
                placeholder="Details (e.g. 5 PM to 9 PM daily)"
                value={newValue}
                onChange={(e) => setNewValue(e.target.value)}
                required
              />
              <button type="submit" className="save-mem-btn">+ Save</button>
            </form>
          </div>

          {/* Card 4: Voice Questions Copilot Can Answer */}
          <div className="memory-card voice-prompts-card">
            <h3>💬 Voice Memory Questions</h3>
            <p className="card-desc">Try saying any of these to your Copilot:</p>
            <div className="prompt-buttons">
              <button onClick={() => onTriggerVoicePrompt && onTriggerVoicePrompt("What do you remember about my shop?")}>
                🗣️ "What do you remember about my shop?"
              </button>
              <button onClick={() => onTriggerVoicePrompt && onTriggerVoicePrompt(" Give me daily briefing")}>
                ☀️ "Give me daily briefing"
              </button>
              <button onClick={() => onTriggerVoicePrompt && onTriggerVoicePrompt("What is my total inventory value?")}>
                💰 "What is my total inventory value?"
              </button>
              <button onClick={() => onTriggerVoicePrompt && onTriggerVoicePrompt("Which product gives the highest margin?")}>
                📈 "Which product gives the highest margin?"
              </button>
              <button onClick={() => onTriggerVoicePrompt && onTriggerVoicePrompt("Who supplies Rice?")}>
                👥 "Who supplies Rice?"
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
