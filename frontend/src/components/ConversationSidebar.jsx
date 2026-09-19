import React from 'react';
import { MessageSquarePlus, MessageSquare, Clock, ChevronRight } from 'lucide-react';
import './ConversationSidebar.css';

export default function ConversationSidebar({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewConversation
}) {
  const formatDate = (isoString) => {
    if (!isoString) return 'Just now';
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays === 1) return 'Yesterday';
    return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
  };

  return (
    <aside className="conversation-sidebar glass-card">
      <div className="sidebar-header">
        <div className="sidebar-title-group">
          <MessageSquare size={18} className="sidebar-icon" />
          <h3 className="sidebar-title">Conversations</h3>
        </div>
        <button
          type="button"
          onClick={onNewConversation}
          className="new-conv-btn"
          title="Start new conversation"
        >
          <MessageSquarePlus size={16} />
          <span>New Chat</span>
        </button>
      </div>

      <div className="conversations-list">
        {conversations.length === 0 ? (
          <div className="empty-conversations">
            <p>No past conversations yet.</p>
            <button
              type="button"
              onClick={onNewConversation}
              className="start-first-btn"
            >
              Start First Conversation
            </button>
          </div>
        ) : (
          conversations.map((conv) => {
            const isActive = conv.id === activeConversationId;
            return (
              <div
                key={conv.id}
                className={`conversation-item ${isActive ? 'active' : ''}`}
                onClick={() => onSelectConversation(conv.id)}
              >
                <div className="conv-item-content">
                  <div className="conv-item-title">{conv.title || 'New Conversation'}</div>
                  <div className="conv-item-meta">
                    <Clock size={12} />
                    <span>{formatDate(conv.updated_at || conv.created_at)}</span>
                  </div>
                </div>
                {isActive && <ChevronRight size={16} className="conv-active-arrow" />}
              </div>
            );
          })
        )}
      </div>
    </aside>
  );
}
