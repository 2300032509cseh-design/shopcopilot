import React, { useState } from 'react';
import './OnboardingWizard.css';

const SAMPLE_CSV = `Product,Quantity,Unit,Price,Cost,Category
Rice,50,bags,1450,1232,Grains
Sugar,25,kg,42,35.7,Groceries
Cooking Oil,40,litres,160,136,Essentials
Biscuits,100,packets,10,8.5,Snacks
Milk,30,packets,28,23.8,Dairy
Salt,50,packets,20,17,Groceries
Wheat Flour,20,bags,340,289,Grains
Toor Dal,30,kg,120,102,Groceries
Tea Powder,40,packets,65,55,Beverages
Bath Soap,60,pieces,35,29.7,Personal Care`;

const QUICK_PICK_PRODUCTS = [
  { id: 1, name: 'Rice', category: 'Grains', qty: 50, unit: 'bags', price: 1450, cost: 1232, selected: true },
  { id: 2, name: 'Sugar', category: 'Groceries', qty: 25, unit: 'kg', price: 42, cost: 35, selected: true },
  { id: 3, name: 'Cooking Oil', category: 'Essentials', qty: 40, unit: 'litres', price: 160, cost: 136, selected: true },
  { id: 4, name: 'Biscuits', category: 'Snacks', qty: 100, unit: 'packets', price: 10, cost: 8.5, selected: true },
  { id: 5, name: 'Milk', category: 'Dairy', qty: 30, unit: 'packets', price: 28, cost: 23, selected: true },
  { id: 6, name: 'Salt', category: 'Groceries', qty: 50, unit: 'packets', price: 20, cost: 17, selected: true },
  { id: 7, name: 'Wheat Flour', category: 'Grains', qty: 20, unit: 'bags', price: 340, cost: 289, selected: false },
  { id: 8, name: 'Toor Dal', category: 'Groceries', qty: 30, unit: 'kg', price: 120, cost: 102, selected: false },
  { id: 9, name: 'Tea Powder', category: 'Beverages', qty: 40, unit: 'packets', price: 65, cost: 55, selected: false },
  { id: 10, name: 'Bath Soap', category: 'Personal Care', qty: 60, unit: 'pieces', price: 35, cost: 29.7, selected: false },
  { id: 11, name: 'Detergent Powder', category: 'Home Care', qty: 25, unit: 'packets', price: 110, cost: 90, selected: false },
  { id: 12, name: 'Shampoo', category: 'Personal Care', qty: 50, unit: 'bottles', price: 180, cost: 150, selected: false }
];

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5050/api';

export default function OnboardingWizard({ onClose, onImportSuccess, onVoiceImport }) {
  const [activeTab, setActiveTab] = useState('csv'); // 'csv' | 'voice' | 'pick'
  const [csvText, setCsvText] = useState('');
  const [voiceText, setVoiceText] = useState('');
  const [pickList, setPickList] = useState(QUICK_PICK_PRODUCTS);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const getHeaders = () => {
    const token = localStorage.getItem('shop_copilot_token');
    return {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    };
  };

  // CSV Upload Handler
  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (evt) => {
      setCsvText(evt.target.result);
    };
    reader.readAsText(file);
  };

  const handleImportCsv = async () => {
    if (!csvText.trim()) {
      setMessage({ type: 'error', text: 'Please select a CSV file or paste CSV text.' });
      return;
    }
    setLoading(true);
    setMessage(null);

    try {
      const res = await fetch(`${API_BASE}/inventory/import-csv`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ csv_text: csvText })
      });
      const data = await res.json();
      if (data.success) {
        setMessage({ type: 'success', text: data.message });
        setTimeout(() => {
          onImportSuccess && onImportSuccess();
          onClose && onClose();
        }, 1200);
      } else {
        setMessage({ type: 'error', text: data.message });
      }
    } catch (err) {
      console.error('CSV import error:', err);
      setMessage({ type: 'error', text: 'Import failed. Please check backend connection.' });
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadSample = () => {
    const blob = new Blob([SAMPLE_CSV], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'shop_copilot_inventory_template.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  // Voice Import Handler
  const handleVoiceImportSubmit = () => {
    if (!voiceText.trim()) return;
    if (onVoiceImport) {
      onVoiceImport(voiceText);
      onClose && onClose();
    }
  };

  // Pick & Add Handler
  const handleTogglePick = (id) => {
    setPickList(prev => prev.map(item => item.id === id ? { ...item, selected: !item.selected } : item));
  };

  const handleUpdatePickField = (id, field, value) => {
    setPickList(prev => prev.map(item => item.id === id ? { ...item, [field]: value } : item));
  };

  const handleSavePickedItems = async () => {
    const selectedItems = pickList.filter(i => i.selected);
    if (selectedItems.length === 0) {
      setMessage({ type: 'error', text: 'Please select at least one product.' });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const res = await fetch(`${API_BASE}/inventory/bulk-add`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({
          products: selectedItems.map(i => ({
            name: i.name,
            category: i.category,
            quantity: parseFloat(i.qty),
            unit: i.unit,
            price: parseFloat(i.price),
            purchase_price: parseFloat(i.cost)
          }))
        })
      });
      const data = await res.json();
      if (data.success) {
        setMessage({ type: 'success', text: data.message });
        setTimeout(() => {
          onImportSuccess && onImportSuccess();
          onClose && onClose();
        }, 1200);
      } else {
        setMessage({ type: 'error', text: data.message });
      }
    } catch (err) {
      console.error('Pick import error:', err);
      setMessage({ type: 'error', text: 'Failed to save products.' });
    } finally {
      setLoading(false);
    }
  };

  // Load Seed Demo Shortcut
  const handleLoadDemo = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/inventory/seed-demo`, {
        method: 'POST',
        headers: getHeaders()
      });
      const data = await res.json();
      if (data.success) {
        setMessage({ type: 'success', text: 'Loaded 10 sample retail store products!' });
        setTimeout(() => {
          onImportSuccess && onImportSuccess();
          onClose && onClose();
        }, 1000);
      }
    } catch (err) {
      console.error('Demo load error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="onboarding-overlay">
      <div className="onboarding-modal">
        <div className="wizard-header">
          <div className="wizard-title">
            <span className="store-icon">🛒</span>
            <div>
              <h2>Set Up Your Shop Inventory</h2>
              <p className="subtitle">Choose how you want to add your existing products & stock</p>
            </div>
          </div>
          {onClose && <button className="close-btn" onClick={onClose}>✕</button>}
        </div>

        {/* METHOD TABS */}
        <div className="wizard-tabs">
          <button 
            className={`tab-btn ${activeTab === 'csv' ? 'active' : ''}`}
            onClick={() => setActiveTab('csv')}
          >
            📄 Upload CSV Sheet
          </button>
          <button 
            className={`tab-btn ${activeTab === 'voice' ? 'active' : ''}`}
            onClick={() => setActiveTab('voice')}
          >
            🎙️ Voice Entry ("Just Say")
          </button>
          <button 
            className={`tab-btn ${activeTab === 'pick' ? 'active' : ''}`}
            onClick={() => setActiveTab('pick')}
          >
            🛒 Pick & Add Form
          </button>
        </div>

        {message && (
          <div className={`status-banner ${message.type}`}>
            {message.text}
          </div>
        )}

        <div className="wizard-body">
          {/* TAB 1: CSV UPLOAD */}
          {activeTab === 'csv' && (
            <div className="tab-content">
              <div className="csv-upload-box">
                <div className="file-dropzone">
                  <span className="upload-icon">📁</span>
                  <p>Choose a <strong>.CSV file</strong> from your computer</p>
                  <input type="file" accept=".csv, .txt" onChange={handleFileUpload} />
                </div>

                <div className="template-row">
                  <span>Don't have a format?</span>
                  <button type="button" className="sample-link" onClick={handleDownloadSample}>
                    📥 Download Sample CSV Template
                  </button>
                </div>

                <div className="csv-text-area">
                  <label>Or paste CSV content directly:</label>
                  <textarea
                    rows={6}
                    placeholder="Product,Quantity,Unit,Price,Cost,Category&#10;Rice,50,bags,1450,1232,Grains&#10;Sugar,25,kg,42,35.7,Groceries"
                    value={csvText}
                    onChange={(e) => setCsvText(e.target.value)}
                  />
                </div>

                <div className="action-row">
                  <button 
                    className="demo-btn" 
                    onClick={() => setCsvText(SAMPLE_CSV)}
                  >
                    Load Sample CSV Text
                  </button>
                  <button 
                    className="import-btn" 
                    onClick={handleImportCsv}
                    disabled={loading || !csvText.trim()}
                  >
                    {loading ? 'Importing...' : '✅ Import CSV Stock'}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: VOICE ENTRY */}
          {activeTab === 'voice' && (
            <div className="tab-content">
              <div className="voice-entry-box">
                <p className="voice-hint">
                  Speak or type all your products together in any language. Copilot will extract and populate your inventory automatically!
                </p>

                <div className="voice-examples">
                  <strong>Example statements:</strong>
                  <ul>
                    <li>🗣️ <em>"I have 50 bags Rice at 1450 per bag, 25 kg Sugar at 42 per kg, and 40 litres Oil"</em></li>
                    <li>🗣️ <em>"నా దగ్గర 10 బస్తాల బియ్యం 1400 రూపాయిలు, 20 లీటర్ల నూనె 150 రూపాయిలు ఉన్నాయి"</em></li>
                    <li>🗣️ <em>"मेरे पास 20 बैग चावल 1400 रुपये और 10 किलो चीनी 42 रुपये है"</em></li>
                  </ul>
                </div>

                <textarea
                  rows={4}
                  placeholder="Enter multi-product command... e.g. 'Rice 50 bags, Sugar 25 kg, Cooking Oil 40 litres'"
                  value={voiceText}
                  onChange={(e) => setVoiceText(e.target.value)}
                />

                <div className="action-row">
                  <button 
                    className="import-btn"
                    onClick={handleVoiceImportSubmit}
                    disabled={!voiceText.trim()}
                  >
                    🎙️ Submit Voice Stock
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: PICK & ADD FORM */}
          {activeTab === 'pick' && (
            <div className="tab-content">
              <p className="pick-hint">Select the items you sell and customize your starting stock & prices:</p>
              
              <div className="pick-grid">
                {pickList.map(item => (
                  <div key={item.id} className={`pick-card ${item.selected ? 'selected' : ''}`}>
                    <div className="pick-header">
                      <input 
                        type="checkbox" 
                        checked={item.selected} 
                        onChange={() => handleTogglePick(item.id)}
                      />
                      <span className="p-name">{item.name}</span>
                      <span className="p-cat">{item.category}</span>
                    </div>

                    {item.selected && (
                      <div className="pick-inputs">
                        <div className="input-field">
                          <label>Stock Qty:</label>
                          <input 
                            type="number" 
                            value={item.qty} 
                            onChange={(e) => handleUpdatePickField(item.id, 'qty', e.target.value)}
                          />
                        </div>
                        <div className="input-field">
                          <label>Unit:</label>
                          <input 
                            type="text" 
                            value={item.unit} 
                            onChange={(e) => handleUpdatePickField(item.id, 'unit', e.target.value)}
                          />
                        </div>
                        <div className="input-field">
                          <label>Selling Price (₹):</label>
                          <input 
                            type="number" 
                            value={item.price} 
                            onChange={(e) => handleUpdatePickField(item.id, 'price', e.target.value)}
                          />
                        </div>
                        <div className="input-field">
                          <label>Cost Price (₹):</label>
                          <input 
                            type="number" 
                            value={item.cost} 
                            onChange={(e) => handleUpdatePickField(item.id, 'cost', e.target.value)}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>

              <div className="action-row">
                <button 
                  className="import-btn"
                  onClick={handleSavePickedItems}
                  disabled={loading}
                >
                  {loading ? 'Saving...' : `✅ Save Selected Inventory (${pickList.filter(i => i.selected).length})`}
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="wizard-footer">
          <div className="demo-shortcut">
            <span>Just testing?</span>
            <button onClick={handleLoadDemo} className="load-demo-link" disabled={loading}>
              ⚡ Load Sample Retail Store Demo (10 Items)
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
