import React from 'react';
import { Package, AlertTriangle, ShoppingBag, Clock, Zap, CheckCircle2 } from 'lucide-react';
import './DashboardInsights.css';

export default function DashboardInsights({ insights, onOpenReorder }) {
  if (!insights) return null;

  const lowStockCount = insights.low_stock_count || 0;
  const totalProducts = insights.total_products || 0;
  const products = insights.products || [];

  return (
    <div className="insights-container">
      {/* Metric Cards Grid */}
      <div className="metrics-grid">
        <div className="glass-card metric-card">
          <div className="metric-header">
            <span className="metric-label">Total Stock Items</span>
            <Package size={20} className="metric-icon blue-icon" />
          </div>
          <div className="metric-value">
            {totalProducts}
          </div>
          <div className="metric-subtext">Active inventory products</div>
        </div>

        <div className="glass-card metric-card">
          <div className="metric-header">
            <span className="metric-label">Low Stock Alert</span>
            <AlertTriangle size={20} className="metric-icon yellow-icon" />
          </div>
          <div className={`metric-value ${lowStockCount > 0 ? 'warning-text' : 'healthy-text'}`}>
            {lowStockCount}
          </div>
          <div className="metric-subtext">
            {lowStockCount > 0 ? 'Items below reorder limit' : 'All stock levels healthy'}
          </div>
        </div>
      </div>

      {/* Stockout Risk Attention List */}
      <div className="glass-card predictions-card">
        <div className="predictions-header">
          <h4 className="predictions-title">
            <Clock size={16} className="title-icon" />
            <span>Smart Stockout Predictions</span>
          </h4>
          <span className="predictions-badge">AI Powered</span>
        </div>

        <div className="predictions-list">
          {products.map((prod, idx) => {
            const usage = prod.avg_daily_usage > 0 ? prod.avg_daily_usage : 1;
            const daysLeft = Math.ceil(prod.quantity / usage);
            const isLow = prod.quantity <= prod.reorder_level;
            const isCritical = daysLeft <= 3 || isLow;

            return (
              <div key={idx} className={`prediction-item ${isCritical ? 'critical-bg' : ''}`}>
                <div className="prod-meta">
                  <div className="prod-name-row">
                    <span className="prod-name">{prod.name}</span>
                    {isCritical ? (
                      <span className="days-badge critical">
                        <AlertTriangle size={10} /> {daysLeft}d left
                      </span>
                    ) : (
                      <span className="days-badge healthy">
                        <CheckCircle2 size={10} /> {daysLeft}d safe
                      </span>
                    )}
                  </div>
                  <div className="prod-details">
                    Current: <strong>{prod.quantity} {prod.unit}</strong> • Usage: {usage} {prod.unit}/day
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* High-Contrast Prepare Purchase Order Button */}
        <button
          type="button"
          className="reorder-trigger-btn"
          onClick={onOpenReorder}
        >
          <ShoppingBag size={18} />
          <span>Prepare Purchase Order</span>
          <Zap size={15} style={{ marginLeft: 'auto', opacity: 0.8 }} />
        </button>
      </div>
    </div>
  );
}
