import React, { useState, useEffect } from 'react';
import './SuppliersTab.css';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5050/api';

export default function SuppliersTab({ onTriggerVoicePrompt }) {
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [name, setName] = useState('');
  const [productsSupplied, setProductsSupplied] = useState('');
  const [contactPhone, setContactPhone] = useState('');
  const [leadDays, setLeadDays] = useState(2);
  const [showAddForm, setShowAddForm] = useState(false);

  const fetchSuppliers = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('shop_copilot_token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};

      const res = await fetch(`${API_BASE}/suppliers`, { headers });
      const data = await res.json();
      if (data.success) {
        setSuppliers(data.suppliers || []);
      }
    } catch (err) {
      console.error('Failed to load suppliers:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSuppliers();
  }, []);

  const handleSaveSupplier = async (e) => {
    e.preventDefault();
    if (!name) return;

    try {
      const token = localStorage.getItem('shop_copilot_token');
      const headers = {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      };

      const res = await fetch(`${API_BASE}/suppliers`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          name,
          products_supplied: productsSupplied,
          contact_phone: contactPhone,
          typical_lead_days: leadDays
        })
      });

      const data = await res.json();
      if (data.success) {
        setName('');
        setProductsSupplied('');
        setContactPhone('');
        setLeadDays(2);
        setShowAddForm(false);
        fetchSuppliers();
      }
    } catch (err) {
      console.error('Error saving supplier:', err);
    }
  };

  return (
    <div className="suppliers-container">
      <div className="suppliers-header">
        <div>
          <h2>👥 Supplier Management</h2>
          <p className="subtitle">Track vendors, products supplied, lead delivery times, and direct contacts</p>
        </div>
        <button 
          className="add-supplier-btn"
          onClick={() => setShowAddForm(!showAddForm)}
        >
          {showAddForm ? 'Close Form' : '+ Add New Supplier'}
        </button>
      </div>

      {showAddForm && (
        <form onSubmit={handleSaveSupplier} className="supplier-form-card">
          <h3>Add / Edit Supplier</h3>
          <div className="form-grid">
            <div className="form-group">
              <label>Supplier Name *</label>
              <input 
                type="text" 
                placeholder="e.g. Annapurna Rice Mill" 
                value={name} 
                onChange={(e) => setName(e.target.value)} 
                required 
              />
            </div>
            <div className="form-group">
              <label>Products Supplied</label>
              <input 
                type="text" 
                placeholder="e.g. Rice, Sona Masoori" 
                value={productsSupplied} 
                onChange={(e) => setProductsSupplied(e.target.value)} 
              />
            </div>
            <div className="form-group">
              <label>Contact Phone</label>
              <input 
                type="text" 
                placeholder="e.g. +91 9876543210" 
                value={contactPhone} 
                onChange={(e) => setContactPhone(e.target.value)} 
              />
            </div>
            <div className="form-group">
              <label>Lead Days (Delivery Time)</label>
              <input 
                type="number" 
                value={leadDays} 
                onChange={(e) => setLeadDays(parseInt(e.target.value) || 1)} 
                min="1" 
              />
            </div>
          </div>
          <button type="submit" className="save-btn">Save Supplier</button>
        </form>
      )}

      {loading ? (
        <div className="suppliers-loading">Loading suppliers data...</div>
      ) : (
        <div className="suppliers-grid">
          {suppliers.map((sup, idx) => (
            <div key={idx} className="supplier-card">
              <div className="supplier-card-header">
                <span className="vendor-icon">🏭</span>
                <div>
                  <h4>{sup.name}</h4>
                  <span className="lead-badge">⚡ Delivery: {sup.typical_lead_days} days</span>
                </div>
              </div>

              <div className="supplier-details">
                <div className="detail-row">
                  <span className="label">Products:</span>
                  <span className="value products">{sup.products_supplied || 'General Goods'}</span>
                </div>
                <div className="detail-row">
                  <span className="label">Phone:</span>
                  <span className="value phone">{sup.contact_phone || 'N/A'}</span>
                </div>
              </div>

              <div className="supplier-actions">
                <button 
                  className="voice-ask-btn"
                  onClick={() => onTriggerVoicePrompt && onTriggerVoicePrompt(`Who supplies ${sup.products_supplied.split(',')[0]}?`)}
                >
                  🎙️ Ask Copilot
                </button>
                {sup.contact_phone && (
                  <a 
                    href={`https://wa.me/${sup.contact_phone.replace(/[^0-9]/g, '')}`} 
                    target="_blank" 
                    rel="noreferrer"
                    className="whatsapp-btn"
                  >
                    💬 WhatsApp
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
