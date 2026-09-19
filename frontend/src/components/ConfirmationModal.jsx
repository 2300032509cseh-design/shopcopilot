import React from 'react';
import './ConfirmationModal.css';

export default function ConfirmationModal({ data, onConfirm, onCancel }) {
  if (!data) return null;

  const { product, quantity, unit, message } = data;

  return (
    <div className="confirmation-overlay">
      <div className="confirmation-modal">
        <div className="warning-banner">
          <span className="warning-icon">⚠️</span>
          <h3>Safety Confirmation Required</h3>
        </div>

        <div className="modal-body">
          <p className="confirmation-msg">
            {message || `You are about to remove a large quantity (${quantity} ${unit}) of '${product}'.`}
          </p>

          <div className="reduction-details">
            <div className="detail-item">
              <span className="lbl">Product:</span>
              <span className="val highlight">{product}</span>
            </div>
            <div className="detail-item">
              <span className="lbl">Removal Quantity:</span>
              <span className="val warning">{quantity} {unit}</span>
            </div>
          </div>

          <p className="sub-hint">Are you sure you want to proceed with this inventory reduction?</p>
        </div>

        <div className="modal-actions">
          <button className="cancel-btn" onClick={onCancel}>
            ❌ Cancel
          </button>
          <button className="confirm-btn" onClick={onConfirm}>
            ✅ Yes, Proceed Stock Change
          </button>
        </div>
      </div>
    </div>
  );
}
