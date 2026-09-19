import React, { useState, useEffect } from 'react';
import './BusinessAnalyticsTab.css';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5050/api';

export default function BusinessAnalyticsTab() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('shop_copilot_token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};

      const res = await fetch(`${API_BASE}/analytics`, { headers });
      if (!res.ok) {
        throw new Error(`Server returned status ${res.status}`);
      }
      const data = await res.json();
      if (data.success) {
        setAnalytics(data);
      } else {
        setError(data.message || 'Failed to fetch analytics');
      }
    } catch (err) {
      console.error('Failed to load business analytics:', err);
      setError('Could not connect to backend analytics service.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  if (loading) {
    return <div className="analytics-loading">⏳ Loading Business & Profit Analytics...</div>;
  }

  if (error) {
    return (
      <div className="analytics-container">
        <div className="analytics-error">
          <h3>⚠️ Unable to load insights</h3>
          <p>{error}</p>
          <button onClick={fetchAnalytics} className="refresh-btn">🔄 Retry</button>
        </div>
      </div>
    );
  }

  const val = analytics?.valuation || {};
  const costValuation = val.total_cost_valuation ?? val.total_purchase_cost ?? 0;
  const retailValuation = val.total_retail_valuation ?? val.total_market_value ?? 0;
  const potentialProfit = val.potential_gross_profit ?? val.potential_profit ?? 0;
  const totalUnits = val.total_items_in_stock ?? 0;

  const marginsData = analytics?.margins;
  const marginsList = Array.isArray(marginsData)
    ? marginsData
    : (Array.isArray(marginsData?.margins) ? marginsData.margins : []);

  const revenue = analytics?.revenue ?? 0;
  const itemsSold = analytics?.items_sold ?? 0;

  return (
    <div className="analytics-container">
      <div className="analytics-header">
        <div>
          <h2>📊 Business Insights & Margins</h2>
          <p className="subtitle">Real-time valuation, profit margins, and daily sales metrics</p>
        </div>
        <button onClick={fetchAnalytics} className="refresh-btn">🔄 Refresh Data</button>
      </div>

      {/* KPI Cards */}
      <div className="analytics-kpi-grid">
        <div className="kpi-card">
          <div className="kpi-icon">💰</div>
          <div className="kpi-content">
            <span className="kpi-label">Total Inventory Valuation</span>
            <span className="kpi-value">₹{Math.round(costValuation).toLocaleString()}</span>
            <span className="kpi-sub">Cost basis ({totalUnits} total units)</span>
          </div>
        </div>

        <div className="kpi-card accent">
          <div className="kpi-icon">🏷️</div>
          <div className="kpi-content">
            <span className="kpi-label">Estimated Retail Value</span>
            <span className="kpi-value">₹{Math.round(retailValuation).toLocaleString()}</span>
            <span className="kpi-sub">Expected sales value</span>
          </div>
        </div>

        <div className="kpi-card success">
          <div className="kpi-icon">📈</div>
          <div className="kpi-content">
            <span className="kpi-label">Potential Gross Profit</span>
            <span className="kpi-value">₹{Math.round(potentialProfit).toLocaleString()}</span>
            <span className="kpi-sub">Retail vs Cost gap</span>
          </div>
        </div>

        <div className="kpi-card info">
          <div className="kpi-icon">🛒</div>
          <div className="kpi-content">
            <span className="kpi-label">Total Recorded Sales</span>
            <span className="kpi-value">₹{Math.round(revenue).toLocaleString()}</span>
            <span className="kpi-sub">{itemsSold} units sold in period</span>
          </div>
        </div>
      </div>

      {/* Product Profit Margin Table */}
      <div className="analytics-section">
        <h3>🏆 Product Profit Margins Breakdown</h3>
        <p className="section-desc">Inspect per-unit profits and total inventory value per item.</p>

        <div className="table-responsive">
          <table className="margins-table">
            <thead>
              <tr>
                <th>Product Name</th>
                <th>Category</th>
                <th>Current Stock</th>
                <th>Selling Price</th>
                <th>Purchase Cost</th>
                <th>Margin / Unit (₹)</th>
                <th>Margin (%)</th>
                <th>Stock Valuation (Cost)</th>
              </tr>
            </thead>
            <tbody>
              {marginsList.length === 0 ? (
                <tr>
                  <td colSpan="8" className="empty-row">No product margin data available.</td>
                </tr>
              ) : (
                marginsList.map((item, idx) => {
                  const pName = item.product || item.name || 'Unknown';
                  const cat = item.category || 'General';
                  const qty = item.quantity ?? 0;
                  const unit = item.unit || 'units';
                  const sellP = item.selling_price ?? item.price ?? 0;
                  const buyP = item.purchase_price ?? (sellP * 0.85);
                  const marginRs = item.margin_rs ?? item.margin ?? (sellP - buyP);
                  const marginPct = item.margin_pct ?? (sellP > 0 ? (marginRs / sellP * 100) : 0);
                  const stockVal = item.stock_valuation_cost ?? (qty * buyP);

                  return (
                    <tr key={idx} className={marginPct >= 25 ? 'high-margin' : ''}>
                      <td className="product-name">{pName}</td>
                      <td><span className="cat-badge">{cat}</span></td>
                      <td>{qty} {unit}</td>
                      <td className="price-cell">₹{sellP}</td>
                      <td className="price-cell cost">₹{buyP}</td>
                      <td className="profit-cell">₹{marginRs}</td>
                      <td>
                        <span className={`margin-badge ${marginPct >= 20 ? 'good' : 'normal'}`}>
                          {marginPct}%
                        </span>
                      </td>
                      <td className="val-cell">₹{Math.round(stockVal)}</td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
