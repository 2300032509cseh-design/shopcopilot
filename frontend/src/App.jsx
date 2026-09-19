import React, { useState, useEffect } from 'react';

import VoiceCopilotBar from './components/VoiceCopilotBar';
import ConversationFeed from './components/ConversationFeed';
import DashboardInsights from './components/DashboardInsights';
import InventoryTable from './components/InventoryTable';
import ShopVocabularyManager from './components/ShopVocabularyManager';
import TransactionAuditLog from './components/TransactionAuditLog';
import ReorderModal from './components/ReorderModal';
import LoginModal from './components/LoginModal';
import ConversationSidebar from './components/ConversationSidebar';
import ShopMemoryTab from './components/ShopMemoryTab';
import BusinessAnalyticsTab from './components/BusinessAnalyticsTab';
import SuppliersTab from './components/SuppliersTab';
import ConfirmationModal from './components/ConfirmationModal';
import OnboardingWizard from './components/OnboardingWizard';
import StockQuestionsTab from './components/StockQuestionsTab';

import {
  Mic,
  Package,
  BookOpen,
  History,
  LogOut,
  User,
  Store,
  Brain,
  TrendingUp,
  Users,
  HelpCircle
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5050/api';

export default function App() {
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem('shop_copilot_user');
    return savedUser ? JSON.parse(savedUser) : null;
  });

  const [token, setToken] = useState(() => {
    return localStorage.getItem('shop_copilot_token') || null;
  });

  const [activeTab, setActiveTab] = useState('copilot');
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);

  const [messages, setMessages] = useState([]);
  const [products, setProducts] = useState([]);
  const [vocabulary, setVocabulary] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [insights, setInsights] = useState(null);
  const [reorderData, setReorderData] = useState(null);
  const [showReorderModal, setShowReorderModal] = useState(false);
  const [confirmationData, setConfirmationData] = useState(null);
  const [pendingConfirmationCommand, setPendingConfirmationCommand] = useState(null);
  const [showOnboardingWizard, setShowOnboardingWizard] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [voices, setVoices] = useState([]);

  const getAuthHeaders = () => {
    const headers = { 'Content-Type': 'application/json' };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  };

  /* -------------------------------------------------------
     INITIAL DATA & AUTH VERIFICATION
  ------------------------------------------------------- */

  useEffect(() => {
    if (token) {
      verifyUser();
      fetchConversations();
      fetchProducts();
      fetchVocabulary();
      fetchTransactions();
      fetchInsights();
    }
  }, [token]);

  useEffect(() => {
    if ('speechSynthesis' in window) {
      const loadVoices = () => {
        const available = window.speechSynthesis.getVoices();
        setVoices(available);
      };

      loadVoices();
      window.speechSynthesis.onvoiceschanged = loadVoices;

      return () => {
        window.speechSynthesis.onvoiceschanged = null;
      };
    }
  }, []);

  const verifyUser = async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API_BASE}/auth/me`, {
        headers: getAuthHeaders()
      });
      if (!res.ok) {
        handleLogout();
        return;
      }
      const data = await res.json();
      if (data.user) {
        setUser(data.user);
        localStorage.setItem('shop_copilot_user', JSON.stringify(data.user));
      }
    } catch (err) {
      console.warn('Error verifying auth:', err);
    }
  };

  /* -------------------------------------------------------
     CONVERSATION MANAGEMENT
  ------------------------------------------------------- */

  const fetchConversations = async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API_BASE}/conversations`, {
        headers: getAuthHeaders()
      });
      const data = await res.json();
      if (data.conversations) {
        setConversations(data.conversations);
        if (data.conversations.length > 0 && !currentConversationId) {
          const firstId = data.conversations[0].id;
          setCurrentConversationId(firstId);
          fetchMessagesForConversation(firstId);
        } else if (data.conversations.length === 0) {
          handleCreateNewConversation();
        }
      }
    } catch (err) {
      console.warn('Error fetching conversations:', err);
    }
  };

  const fetchMessagesForConversation = async (convId) => {
    if (!token || !convId) return;
    try {
      const res = await fetch(`${API_BASE}/conversations/${convId}/messages`, {
        headers: getAuthHeaders()
      });
      const data = await res.json();
      if (data.messages) {
        setMessages(
          data.messages.map((m) => ({
            sender: m.sender,
            text: m.message,
            intent: m.intent,
            language: m.language,
            timestamp: m.timestamp
          }))
        );
      }
    } catch (err) {
      console.warn('Error fetching messages:', err);
    }
  };

  const handleSelectConversation = (convId) => {
    setCurrentConversationId(convId);
    fetchMessagesForConversation(convId);
  };

  const handleCreateNewConversation = async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API_BASE}/conversations`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ title: 'New Conversation' })
      });
      const data = await res.json();
      if (data.conversation) {
        setConversations((prev) => [data.conversation, ...prev]);
        setCurrentConversationId(data.conversation.id);
        setMessages([]);
      }
    } catch (err) {
      console.warn('Error creating conversation:', err);
    }
  };

  /* -------------------------------------------------------
     API FETCHERS
  ------------------------------------------------------- */

  const fetchProducts = async () => {
    try {
      const res = await fetch(`${API_BASE}/products`, {
        headers: getAuthHeaders()
      });
      const data = await res.json();
      if (data.products) {
        setProducts(data.products);
        if (data.products.length === 0) {
          setShowOnboardingWizard(true);
        }
      }
    } catch (err) {
      console.warn('Error fetching products:', err);
    }
  };

  const fetchVocabulary = async () => {
    try {
      const res = await fetch(`${API_BASE}/vocabulary`, {
        headers: getAuthHeaders()
      });
      const data = await res.json();
      if (data.vocabulary) {
        setVocabulary(data.vocabulary);
      }
    } catch (err) {
      console.warn('Error fetching vocabulary:', err);
    }
  };

  const fetchTransactions = async () => {
    try {
      const res = await fetch(`${API_BASE}/transactions`, {
        headers: getAuthHeaders()
      });
      const data = await res.json();
      if (data.transactions) {
        setTransactions(data.transactions);
      }
    } catch (err) {
      console.warn('Error fetching transactions:', err);
    }
  };

  const fetchInsights = async () => {
    try {
      const res = await fetch(`${API_BASE}/insights`, {
        headers: getAuthHeaders()
      });
      const data = await res.json();
      if (data.insights) {
        setInsights(data.insights);
      }
    } catch (err) {
      console.warn('Error fetching insights:', err);
    }
  };

  /* -------------------------------------------------------
     AUTH HANDLERS
  ------------------------------------------------------- */

  const handleLoginSuccess = (userData, userToken) => {
    setUser(userData);
    setToken(userToken);
  };

  const handleLogout = () => {
    localStorage.removeItem('shop_copilot_token');
    localStorage.removeItem('shop_copilot_user');
    setUser(null);
    setToken(null);
    setConversations([]);
    setMessages([]);
    setCurrentConversationId(null);
  };

  /* -------------------------------------------------------
     TEXT TO SPEECH
  ------------------------------------------------------- */

  const speakText = (text, lang = 'en', speechText = null) => {
    if (!('speechSynthesis' in window) || !text) {
      return;
    }

    window.speechSynthesis.cancel();

    const availableVoices =
      voices.length > 0 ? voices : window.speechSynthesis.getVoices();

    const langCodeMap = {
      'te': 'te-IN', 'hi': 'hi-IN', 'kn': 'kn-IN', 'ta': 'ta-IN', 'or': 'or-IN',
      'bn': 'bn-IN', 'mr': 'mr-IN', 'ml': 'ml-IN', 'ja': 'ja-JP', 'es': 'es-ES', 'en': 'en-IN'
    };

    const targetLang = langCodeMap[lang] || 'en-IN';

    const hasNativeLangVoice = availableVoices.some((v) =>
      v.lang.toLowerCase().startsWith(lang.toLowerCase())
    );

    const matchedVoice =
      availableVoices.find((v) => v.lang.toLowerCase() === targetLang.toLowerCase()) ||
      availableVoices.find((v) => v.lang.toLowerCase().startsWith(lang.toLowerCase())) ||
      availableVoices.find((v) => v.lang.includes('IN')) ||
      availableVoices.find((v) => v.lang.startsWith('en'));

    // Use native script if browser voice exists; otherwise use phonetic transliteration so English voice speaks full sentence!
    const finalContentToSpeak = (hasNativeLangVoice ? text : (speechText || text)) || text;

    const utterance = new SpeechSynthesisUtterance(finalContentToSpeak);
    utterance.lang = targetLang;

    if (matchedVoice) {
      utterance.voice = matchedVoice;
    }

    utterance.rate = 0.95;
    utterance.pitch = 1;

    window.speechSynthesis.speak(utterance);
  };

  /* -------------------------------------------------------
     MAIN COPILOT COMMAND & CONFIRMATION HANDLING
  ------------------------------------------------------- */

  const handleProcessVoice = async (textPrompt, langTag = null, confirmed = false) => {
    if (!textPrompt?.trim()) {
      return;
    }

    if (!confirmed) {
      const userMsg = {
        sender: 'user',
        text: textPrompt,
        timestamp: new Date().toISOString()
      };
      setMessages((prev) => [...prev, userMsg]);
    }

    setIsProcessing(true);

    try {
      const res = await fetch(`${API_BASE}/process-voice`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          text: textPrompt,
          language: langTag,
          conversation_id: currentConversationId,
          confirmed: confirmed
        })
      });

      if (!res.ok) {
        throw new Error(`Backend returned ${res.status}`);
      }

      const data = await res.json();

      // Check for safety confirmation requirement
      if (data.status === 'NEED_CONFIRMATION') {
        setConfirmationData(data);
        setPendingConfirmationCommand({ textPrompt, langTag });
        setIsProcessing(false);
        return;
      }

      setConfirmationData(null);
      setPendingConfirmationCommand(null);

      const copilotMsg = {
        sender: 'copilot',
        text: data.message || 'Understood.',
        speech_text: data.speech_text || data.message,
        intent: data.intent,
        status: data.status,
        language: data.language || langTag || 'en',
        learned_vocab: data.learned_vocab,
        timestamp: new Date().toISOString()
      };

      setMessages((prev) => [...prev, copilotMsg]);

      if (data.message) {
        speakText(data.message, data.language || langTag || 'en', data.speech_text);
      }

      if (data.intent === 'REORDER' && data.whatsapp_message) {
        setReorderData(data);
        setShowReorderModal(true);
      }

      await fetchConversations();
      await Promise.all([
        fetchProducts(),
        fetchVocabulary(),
        fetchTransactions(),
        fetchInsights()
      ]);
    } catch (err) {
      console.error('Error processing voice command:', err);
      setMessages((prev) => [
        ...prev,
        {
          sender: 'copilot',
          text: 'Backend server error. Please verify backend/app.py is running.',
          timestamp: new Date().toISOString()
        }
      ]);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleConfirmSafetyAction = () => {
    if (pendingConfirmationCommand) {
      const { textPrompt, langTag } = pendingConfirmationCommand;
      handleProcessVoice(textPrompt, langTag, true);
    }
  };

  const handleCancelSafetyAction = () => {
    setConfirmationData(null);
    setPendingConfirmationCommand(null);
  };

  /* -------------------------------------------------------
     MANUAL INVENTORY & PRODUCT ACTIONS
  ------------------------------------------------------- */

  const handleAddStockManual = (productName, qty, unit) => {
    handleProcessVoice(`Add ${qty} ${unit} ${productName}`);
  };

  const handleRemoveStockManual = (productName, qty, unit) => {
    handleProcessVoice(`Remove ${qty} ${unit} ${productName}`);
  };

  const handleAddProductManual = async (productData) => {
    try {
      await fetch(`${API_BASE}/products`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(productData)
      });
      await fetchProducts();
      await fetchInsights();
    } catch (err) {
      console.error('Error adding product:', err);
    }
  };

  const handleAddVocabularyManual = async (vocabData) => {
    try {
      await fetch(`${API_BASE}/vocabulary`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(vocabData)
      });
      await fetchVocabulary();
      handleProcessVoice(
        `${vocabData.term} means ${vocabData.equivalent_qty} ${vocabData.equivalent_unit}`
      );
    } catch (err) {
      console.error('Error adding vocabulary:', err);
    }
  };

  const handleTriggerReorder = async () => {
    try {
      const res = await fetch(`${API_BASE}/reorder`, {
        method: 'POST',
        headers: getAuthHeaders()
      });
      const data = await res.json();
      setReorderData(data);
      setShowReorderModal(true);
    } catch (err) {
      console.error('Error generating reorder:', err);
    }
  };

  if (!token || !user) {
    return (
      <LoginModal
        apiBase={API_BASE}
        onLoginSuccess={handleLoginSuccess}
      />
    );
  }

  return (
    <div className="app-container">
      {/* HEADER */}
      <header className="app-header glass-card">
        <div className="brand-logo">
          <div className="brand-icon">🛒</div>
          <div className="brand-copy">
            <div className="brand-title">SHOP COPILOT</div>
            <div className="brand-subtitle">
              Voice-first inventory & intelligence for small shops
            </div>
          </div>
        </div>

        <div className="header-user-info">
          <div className="shop-badge">
            <Store size={14} />
            <span>{user.shop_name || 'My Shop'}</span>
          </div>
          <div className="user-badge">
            <User size={14} />
            <span>{user.name}</span>
          </div>
          <button
            type="button"
            className="logout-btn"
            onClick={handleLogout}
            title="Log Out"
          >
            <LogOut size={16} />
          </button>
        </div>

        {/* NAVIGATION TABS */}
        <nav className="nav-tabs">
          <button
            type="button"
            className={`nav-btn ${activeTab === 'copilot' ? 'active' : ''}`}
            onClick={() => setActiveTab('copilot')}
          >
            <Mic size={16} />
            <span>Copilot</span>
          </button>

          <button
            type="button"
            className={`nav-btn ${activeTab === 'stock-assistant' ? 'active' : ''}`}
            onClick={() => setActiveTab('stock-assistant')}
          >
            <HelpCircle size={16} />
            <span>Stock Assistant</span>
          </button>

          <button
            type="button"
            className={`nav-btn ${activeTab === 'inventory' ? 'active' : ''}`}
            onClick={() => setActiveTab('inventory')}
          >
            <Package size={16} />
            <span>
              Inventory <b>{products.length}</b>
            </span>
          </button>

          <button
            type="button"
            className={`nav-btn ${activeTab === 'analytics' ? 'active' : ''}`}
            onClick={() => setActiveTab('analytics')}
          >
            <TrendingUp size={16} />
            <span>Insights & Margins</span>
          </button>

          <button
            type="button"
            className={`nav-btn ${activeTab === 'memory' ? 'active' : ''}`}
            onClick={() => setActiveTab('memory')}
          >
            <Brain size={16} />
            <span>Shop Memory</span>
          </button>

          <button
            type="button"
            className={`nav-btn ${activeTab === 'suppliers' ? 'active' : ''}`}
            onClick={() => setActiveTab('suppliers')}
          >
            <Users size={16} />
            <span>Suppliers</span>
          </button>

          <button
            type="button"
            className={`nav-btn ${activeTab === 'vocabulary' ? 'active' : ''}`}
            onClick={() => setActiveTab('vocabulary')}
          >
            <BookOpen size={16} />
            <span>
              Vocabulary <b>{vocabulary.length}</b>
            </span>
          </button>

          <button
            type="button"
            className={`nav-btn ${activeTab === 'transactions' ? 'active' : ''}`}
            onClick={() => setActiveTab('transactions')}
          >
            <History size={16} />
            <span>
              Audit Log <b>{transactions.length}</b>
            </span>
          </button>
        </nav>
      </header>

      {/* TAB CONTENTS */}
      {activeTab === 'copilot' && (
        <main className="main-grid">
          <section className="main-column">
            <VoiceCopilotBar
              onSendMessage={(prompt, lang) => handleProcessVoice(prompt, lang, false)}
              isProcessing={isProcessing}
              attentionItems={insights ? insights.attention_items : []}
            />

            <ConversationFeed
              messages={messages}
              onSelectOption={(prompt) => handleProcessVoice(prompt)}
              onSpeakText={(txt, lang, speechTxt) => speakText(txt, lang, speechTxt)}
            />
          </section>

          <aside className="insights-column" style={{ gap: '18px' }}>
            <ConversationSidebar
              conversations={conversations}
              activeConversationId={currentConversationId}
              onSelectConversation={handleSelectConversation}
              onNewConversation={handleCreateNewConversation}
            />

            <DashboardInsights
              insights={insights}
              onOpenReorder={handleTriggerReorder}
            />
          </aside>
        </main>
      )}

      {activeTab === 'stock-assistant' && (
        <main className="single-page">
          <StockQuestionsTab
            onAskVoiceQuestion={(prompt) => {
              // Voice processing handled inside component or forwarded
            }}
            onOpenReorderModal={() => handleTriggerReorder()}
          />
        </main>
      )}

      {activeTab === 'inventory' && (
        <main className="single-page">
          <InventoryTable
            products={products}
            onAddStock={handleAddStockManual}
            onRemoveStock={handleRemoveStockManual}
            onAddProduct={handleAddProductManual}
            onOpenWizard={() => setShowOnboardingWizard(true)}
          />
        </main>
      )}

      {activeTab === 'analytics' && (
        <main className="single-page">
          <BusinessAnalyticsTab />
        </main>
      )}

      {activeTab === 'memory' && (
        <main className="single-page">
          <ShopMemoryTab
            shop={user}
            onTriggerVoicePrompt={(prompt) => {
              setActiveTab('copilot');
              handleProcessVoice(prompt);
            }}
          />
        </main>
      )}

      {activeTab === 'suppliers' && (
        <main className="single-page">
          <SuppliersTab
            onTriggerVoicePrompt={(prompt) => {
              setActiveTab('copilot');
              handleProcessVoice(prompt);
            }}
          />
        </main>
      )}

      {activeTab === 'vocabulary' && (
        <main className="single-page">
          <ShopVocabularyManager
            vocabulary={vocabulary}
            onAddVocabulary={handleAddVocabularyManual}
          />
        </main>
      )}

      {activeTab === 'transactions' && (
        <main className="single-page">
          <TransactionAuditLog transactions={transactions} />
        </main>
      )}

      {/* MODALS */}
      {showReorderModal && (
        <ReorderModal
          reorderData={reorderData}
          onClose={() => setShowReorderModal(false)}
        />
      )}

      {confirmationData && (
        <ConfirmationModal
          data={confirmationData}
          onConfirm={handleConfirmSafetyAction}
          onCancel={handleCancelSafetyAction}
        />
      )}

      {showOnboardingWizard && (
        <OnboardingWizard
          onClose={() => setShowOnboardingWizard(false)}
          onImportSuccess={async () => {
            await fetchProducts();
            await fetchTransactions();
            await fetchInsights();
          }}
          onVoiceImport={(voicePrompt) => {
            setShowOnboardingWizard(false);
            setActiveTab('copilot');
            handleProcessVoice(voicePrompt);
          }}
        />
      )}
    </div>
  );
}