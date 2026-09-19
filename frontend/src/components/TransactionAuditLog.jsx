import React from 'react';
import { History, Mic, Edit3, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import './TransactionAuditLog.css';

export default function TransactionAuditLog({ transactions }) {
  return (
    <div className="audit-card glass-card">
      <div className="audit-header">
        <div className="audit-title-group">
          <History size={22} className="audit-icon" />
          <div>
            <h3 className="audit-title">Real-Time Audit Log</h3>
            <span className="audit-subtitle">{transactions.length} recorded stock events</span>
          </div>
        </div>
      </div>

      <div className="table-responsive">
        <table className="audit-table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Product</th>
              <th>Action</th>
              <th>Quantity</th>
              <th>Source</th>
              <th>Spoken Prompt / Raw Log</th>
            </tr>
          </thead>
          <tbody>
            {transactions.length === 0 ? (
              <tr>
                <td colSpan={6} className="empty-audit-row">
                  No transaction events recorded yet.
                </td>
              </tr>
            ) : (
              transactions.map((tx) => {
                const isAdd = tx.action === 'ADD';
                const formattedTime = tx.timestamp ? new Date(tx.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : 'Just now';
                return (
                  <tr key={tx.id}>
                    <td className="timestamp-cell">
                      {formattedTime}
                    </td>
                    <td className="product-cell">{tx.product_name}</td>
                    <td>
                      <span className={`action-badge ${isAdd ? 'add' : 'remove'}`}>
                        {isAdd ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
                        {tx.action}
                      </span>
                    </td>
                    <td className="quantity-cell">
                      {isAdd ? '+' : '-'}{tx.quantity} {tx.unit}
                    </td>
                    <td>
                      <span className="source-badge">
                        {tx.source === 'voice' ? <Mic size={14} className="source-icon voice" /> : <Edit3 size={14} className="source-icon manual" />}
                        {tx.source}
                      </span>
                    </td>
                    <td className="raw-text-cell">
                      "{tx.raw_text || '-'}"
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
