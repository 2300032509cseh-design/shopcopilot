import React, { useState } from 'react';
import { Search, Plus, Package, Edit, AlertTriangle, CheckCircle, Zap } from 'lucide-react';
import './InventoryTable.css';

const COMMON_UNITS = [
  'pieces',
  'kg',
  'bags',
  'cartons',
  'boxes',
  'dozens',
  'litres',
  'packets'
];

export default function InventoryTable({ products, onAddStock, onRemoveStock, onAddProduct, onOpenWizard }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterMode, setFilterMode] = useState('all'); // 'all', 'low_stock', 'grains'
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);

  // Add / Edit Product Form State
  const [name, setName] = useState('');
  const [category, setCategory] = useState('Groceries');
  const [quantity, setQuantity] = useState(10);
  const [unit, setUnit] = useState('kg');
  const [price, setPrice] = useState(50);
  const [reorderLevel, setReorderLevel] = useState(10);
  const [avgDailyUsage, setAvgDailyUsage] = useState(2.0);
  const [leadDays, setLeadDays] = useState(2);

  const floatValue = (val) => parseFloat(val) || 0;

  const openAddModal = () => {
    setName('');
    setCategory('Groceries');
    setQuantity(10);
    setUnit('kg');
    setPrice(50);
    setReorderLevel(10);
    setAvgDailyUsage(2.0);
    setLeadDays(2);
    setEditingProduct(null);
    setShowAddModal(true);
  };

  const openEditModal = (prod) => {
    setEditingProduct(prod);
    setName(prod.name);
    setCategory(prod.category || 'General');
    setQuantity(prod.quantity);
    setUnit(prod.unit);
    setPrice(prod.price || 0);
    setReorderLevel(prod.reorder_level);
    setAvgDailyUsage(prod.avg_daily_usage || 2.0);
    setLeadDays(prod.supplier_lead_days || 2);
    setShowAddModal(true);
  };

  const handleSave = (e) => {
    e.preventDefault();
    if (!name.trim()) return;
    onAddProduct({
      name,
      category,
      quantity: floatValue(quantity),
      unit,
      price: floatValue(price),
      reorder_level: floatValue(reorderLevel),
      avg_daily_usage: floatValue(avgDailyUsage),
      supplier_lead_days: parseInt(leadDays, 10) || 2
    });
    setShowAddModal(false);
    setEditingProduct(null);
  };

  const filtered = products.filter(p => {
    const matchesSearch = p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          (p.category && p.category.toLowerCase().includes(searchTerm.toLowerCase()));
    if (!matchesSearch) return false;

    if (filterMode === 'low_stock') {
      return p.quantity <= p.reorder_level;
    }
    if (filterMode === 'grains') {
      return (p.category && p.category.toLowerCase().includes('grain')) || p.unit === 'bags';
    }
    return true;
  });

  return (
    <div className="inventory-card glass-card">
      <div className="inventory-header">
        <div className="inventory-title-group">
          <Package size={22} className="title-icon" />
          <div>
            <h3 className="inventory-title">Product & Stock Management</h3>
            <span className="inventory-subtitle">{products.length} active products tracked</span>
          </div>
        </div>

        <div className="inventory-controls">
          <div className="filter-pills-row">
            <button
              type="button"
              className={`filter-pill ${filterMode === 'all' ? 'active' : ''}`}
              onClick={() => setFilterMode('all')}
            >
              All ({products.length})
            </button>
            <button
              type="button"
              className={`filter-pill ${filterMode === 'low_stock' ? 'active' : ''}`}
              onClick={() => setFilterMode('low_stock')}
            >
              ⚠️ Low Stock ({products.filter(p => p.quantity <= p.reorder_level).length})
            </button>
          </div>

          <div className="search-box">
            <Search size={16} className="search-icon" />
            <input
              type="text"
              className="search-input"
              placeholder="Search product..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <button 
            type="button" 
            className="import-stock-btn" 
            onClick={() => onOpenWizard && onOpenWizard()}
            style={{
              background: '#059669',
              color: '#ffffff',
              border: 'none',
              padding: '0.45rem 0.85rem',
              borderRadius: '8px',
              fontWeight: 700,
              fontSize: '0.82rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem'
            }}
          >
            <span>📥 Import / Setup Stock</span>
          </button>

          <button type="button" className="add-product-btn" onClick={openAddModal}>
            <Plus size={16} />
            <span>Add Product</span>
          </button>
        </div>
      </div>

      <div className="table-responsive">
        <table className="inventory-table">
          <thead>
            <tr>
              <th>Product Name</th>
              <th>Category</th>
              <th>Available Stock</th>
              <th>Unit Price (₹)</th>
              <th>Stock Value (₹)</th>
              <th>Reorder Alert Level</th>
              <th>Status</th>
              <th style={{ textAlign: 'right' }}>Actions & Stock Updates</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={8} className="empty-row">
                  No products match your current search/filter.
                </td>
              </tr>
            ) : (
              filtered.map((prod) => {
                const isLow = prod.quantity <= prod.reorder_level;
                const totalValue = (prod.quantity * (prod.price || 0)).toFixed(2);
                return (
                  <tr key={prod.id} className={isLow ? 'low-stock-row' : ''}>
                    <td className="product-name-cell">
                      <span className="product-name">{prod.name}</span>
                    </td>
                    <td>
                      <span className="category-pill">{prod.category || 'General'}</span>
                    </td>
                    <td className={`qty-cell ${isLow ? 'low-stock-text' : 'healthy-text'}`}>
                      <strong>{prod.quantity}</strong> {prod.unit}
                    </td>
                    <td className="price-cell">
                      ₹{prod.price ? prod.price.toLocaleString() : '0'}
                    </td>
                    <td className="value-cell">
                      ₹{parseFloat(totalValue).toLocaleString()}
                    </td>
                    <td>{prod.reorder_level} {prod.unit}</td>
                    <td>
                      {isLow ? (
                        <span className="stock-badge badge-critical">
                          <AlertTriangle size={12} /> Low Stock Alert
                        </span>
                      ) : (
                        <span className="stock-badge badge-healthy">
                          <CheckCircle size={12} /> Healthy
                        </span>
                      )}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <div className="action-buttons">
                        <button
                          type="button"
                          className="edit-product-btn"
                          onClick={() => openEditModal(prod)}
                          title="Manually edit product details"
                        >
                          <Edit size={14} />
                          <span>Edit</span>
                        </button>

                        <button
                          type="button"
                          className="quick-stock-btn add-btn"
                          onClick={() => onAddStock(prod.name, 5, prod.unit)}
                          title={`Add 5 ${prod.unit}`}
                        >
                          +5 {prod.unit}
                        </button>
                        <button
                          type="button"
                          className="quick-stock-btn remove-btn"
                          onClick={() => onRemoveStock(prod.name, 2, prod.unit)}
                          title={`Remove 2 ${prod.unit}`}
                        >
                          -2 {prod.unit}
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Add / Edit Product Modal */}
      {showAddModal && (
        <div className="modal-overlay">
          <div className="modal-card glass-card">
            <div className="modal-header">
              <div className="modal-icon">{editingProduct ? <Edit size={20} /> : <Plus size={20} />}</div>
              <h3>{editingProduct ? `Edit Product: ${editingProduct.name}` : 'Add New Product'}</h3>
            </div>
            <form onSubmit={handleSave} className="modal-form">
              <div className="form-group">
                <label>Product Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Basmati Rice, Sunflower Oil, Salt"
                  value={name}
                  onChange={e => setName(e.target.value)}
                />
              </div>

              <div className="form-group">
                <label>Category</label>
                <input
                  type="text"
                  placeholder="e.g. Grains, Groceries, Snacks, Dairy, Beverages"
                  value={category}
                  onChange={e => setCategory(e.target.value)}
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Current Stock Quantity</label>
                  <input
                    type="number"
                    step="any"
                    required
                    value={quantity}
                    onChange={e => setQuantity(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>Tracking Unit</label>
                  <select value={unit} onChange={e => setUnit(e.target.value)}>
                    {COMMON_UNITS.map(u => (
                      <option key={u} value={u}>{u}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Price per Unit (₹)</label>
                  <input
                    type="number"
                    step="any"
                    placeholder="0.00"
                    value={price}
                    onChange={e => setPrice(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>Reorder Alert Level</label>
                  <input
                    type="number"
                    step="any"
                    value={reorderLevel}
                    onChange={e => setReorderLevel(e.target.value)}
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Average Daily Usage</label>
                  <input
                    type="number"
                    step="any"
                    placeholder="2.0"
                    value={avgDailyUsage}
                    onChange={e => setAvgDailyUsage(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>Supplier Lead Time (Days)</label>
                  <input
                    type="number"
                    step="1"
                    placeholder="2"
                    value={leadDays}
                    onChange={e => setLeadDays(e.target.value)}
                  />
                </div>
              </div>

              <div className="modal-actions">
                <button type="button" className="cancel-btn" onClick={() => setShowAddModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="save-btn">
                  {editingProduct ? 'Update Product' : 'Save Product'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
