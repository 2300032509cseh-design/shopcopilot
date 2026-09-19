import React, { useState } from 'react';
import { BookOpen, Plus, Lightbulb } from 'lucide-react';
import './ShopVocabularyManager.css';

export default function ShopVocabularyManager({ vocabulary, onAddVocabulary }) {
  const [term, setTerm] = useState('');
  const [qty, setQty] = useState(12);
  const [unit, setUnit] = useState('packets');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!term.trim()) return;
    onAddVocabulary({
      term: term.trim().toLowerCase(),
      equivalent_qty: parseFloat(qty) || 1,
      equivalent_unit: unit.trim().toLowerCase()
    });
    setTerm('');
  };

  return (
    <div className="vocab-card glass-card">
      <div className="vocab-header">
        <div className="vocab-title-group">
          <BookOpen size={22} className="vocab-icon" />
          <div>
            <h3 className="vocab-title">Shop-Specific Vocabulary Memory</h3>
            <span className="vocab-subtitle">{vocabulary.length} custom terms learned</span>
          </div>
        </div>
      </div>

      <div className="vocab-info-banner">
        <Lightbulb size={18} className="info-icon" />
        <div>
          <strong>How it works:</strong> Every shop keeper uses local terms. Speak or define terms like <em>"1 peti is 12 packets"</em> and Shop Copilot remembers them for all future voice commands!
        </div>
      </div>

      {/* Existing Learned Terms Grid */}
      <div className="vocab-grid">
        {vocabulary.length === 0 ? (
          <div className="empty-vocab">No custom vocabulary learned yet. Add your first shop term below!</div>
        ) : (
          vocabulary.map((item, idx) => (
            <div key={idx} className="vocab-item-card">
              <div className="vocab-term-name">"{item.term}"</div>
              <div className="vocab-term-equals">
                = <strong>{item.equivalent_qty}</strong> {item.equivalent_unit}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Form to teach a new term */}
      <form onSubmit={handleSubmit} className="vocab-form">
        <div className="form-group flex-1">
          <label>Shop Term (e.g. peti, bora)</label>
          <input
            type="text"
            required
            placeholder="e.g. peti"
            value={term}
            onChange={(e) => setTerm(e.target.value)}
          />
        </div>

        <div className="form-group width-100">
          <label>Equals Qty</label>
          <input
            type="number"
            required
            value={qty}
            onChange={(e) => setQty(e.target.value)}
          />
        </div>

        <div className="form-group flex-1">
          <label>Standard Unit</label>
          <input
            type="text"
            required
            placeholder="e.g. packets"
            value={unit}
            onChange={(e) => setUnit(e.target.value)}
          />
        </div>

        <button type="submit" className="teach-btn">
          <Plus size={16} />
          <span>Teach Copilot</span>
        </button>
      </form>
    </div>
  );
}
