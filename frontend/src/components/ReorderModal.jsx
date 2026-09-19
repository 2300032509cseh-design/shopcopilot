import React, { useState, useEffect } from 'react';
import { ShoppingBag, Copy, Share2, Check, X, Edit3, PlusCircle } from 'lucide-react';
import './ReorderModal.css';

export default function ReorderModal({ reorderData, onClose }) {
  const [editableMessage, setEditableMessage] = useState('');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (reorderData && reorderData.whatsapp_message) {
      setEditableMessage(reorderData.whatsapp_message);
    }
  }, [reorderData]);

  if (!reorderData) return null;

  const handleCopy = () => {
    if (editableMessage) {
      navigator.clipboard.writeText(editableMessage);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleWhatsAppShare = () => {
    if (editableMessage) {
      const url = `https://api.whatsapp.com/send?text=${encodeURIComponent(editableMessage)}`;
      window.open(url, '_blank');
    }
  };

  const appendSnippet = (snippetText) => {
    setEditableMessage((prev) => `${prev}\n${snippetText}`);
  };

  return (
    <div className="reorder-modal-backdrop">
      <div className="glass-card reorder-modal-card">
        {/* Header */}
        <div className="reorder-modal-header">
          <div className="reorder-title">
            <ShoppingBag size={22} className="reorder-icon" />
            <span>Suggested Purchase Order</span>
          </div>
          <button type="button" className="close-btn" onClick={onClose} title="Close">
            <X size={20} />
          </button>
        </div>

        <p className="reorder-subtitle">
          Auto-generated purchase order based on current stock levels and supplier lead times:
        </p>

        {/* Item Summary Cards */}
        <div className="reorder-items-list">
          {reorderData.items && reorderData.items.map((item, idx) => (
            <div key={idx} className="reorder-item-card">
              <div>
                <strong className="item-name">{item.product}</strong>
                <div className="item-meta">
                  Current stock: {item.current_qty} {item.unit} • Est. stockout: {item.days_remaining}d
                </div>
              </div>
              <span className="suggested-qty-badge">
                + {item.suggested_qty} {item.unit}
              </span>
            </div>
          ))}
        </div>

        {/* Editable WhatsApp Text Box */}
        <div className="whatsapp-box-container">
          <div className="whatsapp-box-header">
            <label className="whatsapp-label">
              <Edit3 size={14} /> WhatsApp Purchase Order Message (Editable)
            </label>
            <span className="edit-hint">Shopkeeper can customize below</span>
          </div>

          <textarea
            className="app-input whatsapp-textarea"
            value={editableMessage}
            onChange={(e) => setEditableMessage(e.target.value)}
            rows={6}
            placeholder="Edit purchase order message..."
          />

          {/* Quick Snippet Chips */}
          <div className="snippet-chips-row">
            <button
              type="button"
              className="snippet-chip"
              onClick={() => appendSnippet('• Supplier Name: Main Wholesaler')}
            >
              <PlusCircle size={12} /> Supplier Name
            </button>
            <button
              type="button"
              className="snippet-chip"
              onClick={() => appendSnippet('⚠️ Urgent delivery required by tomorrow morning!')}
            >
              <PlusCircle size={12} /> Urgent Note
            </button>
            <button
              type="button"
              className="snippet-chip"
              onClick={() => appendSnippet('• Payment: Cash on delivery / UPI upon arrival.')}
            >
              <PlusCircle size={12} /> Payment Info
            </button>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="reorder-modal-actions">
          <button type="button" className="btn-secondary copy-btn" onClick={handleCopy}>
            {copied ? <Check size={16} color="#10B981" /> : <Copy size={16} />}
            <span>{copied ? 'Copied to Clipboard!' : 'Copy Text'}</span>
          </button>

          <button type="button" className="whatsapp-send-btn" onClick={handleWhatsAppShare}>
            <Share2 size={16} />
            <span>Send via WhatsApp</span>
          </button>
        </div>
      </div>
    </div>
  );
}
