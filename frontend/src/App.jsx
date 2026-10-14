import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import LandingPage from './LandingPage';
import AuthPage from './AuthPage';
import ProfilePage from './ProfilePage';
import SettingsPage from './SettingsPage';

// Initial verified snapshot loaded directly from Phase 4 & 5 analytics
const INITIAL_DATA = {
  kpis: {
    total_orders: 148,
    delivered_orders: 97,
    total_net_revenue: 1512963.4,
    total_profit: 408097.3,
    average_order_value: 10222.73,
    overall_profit_margin_pct: 26.97,
  },
  monthly_trends: [
    { month: '2024-01', orders_count: 24, monthly_revenue: 241500.0, monthly_profit: 65200.0, cumulative_revenue: 241500.0 },
    { month: '2024-02', orders_count: 28, monthly_revenue: 285400.0, monthly_profit: 76800.0, cumulative_revenue: 526900.0 },
    { month: '2024-03', orders_count: 32, monthly_revenue: 334200.0, monthly_profit: 90200.0, cumulative_revenue: 861100.0 },
    { month: '2024-04', orders_count: 21, monthly_revenue: 215600.0, monthly_profit: 58400.0, cumulative_revenue: 1076700.0 },
    { month: '2024-05', orders_count: 23, monthly_revenue: 238100.0, monthly_profit: 64100.0, cumulative_revenue: 1314800.0 },
    { month: '2024-06', orders_count: 20, monthly_revenue: 198163.4, monthly_profit: 53397.3, cumulative_revenue: 1512963.4 },
  ],
  regional_breakdown: [
    { customer_region: 'South', order_count: 35, regional_revenue: 347171.4,  regional_profit: 93154.0,  avg_order_value: 9919.18,  profit_margin_pct: 26.83 },
    { customer_region: 'North', order_count: 23, regional_revenue: 231233.8,  regional_profit: 54132.2,  avg_order_value: 10053.64, profit_margin_pct: 23.41 },
    { customer_region: 'West',  order_count: 22, regional_revenue: 225811.55, regional_profit: 59814.55, avg_order_value: 10264.16, profit_margin_pct: 26.49 },
    { customer_region: 'East',  order_count: 17, regional_revenue: 174393.05, regional_profit: 48110.4,  avg_order_value: 10258.41, profit_margin_pct: 27.59 },
  ],
  top_products: [
    { product_id: 'PROD-003', product_name: 'Ultra-HD 4K Monitor 27-inch',    category: 'Electronics', units_sold: 21, total_revenue: 330225.0, profit_margin_pct: 28.5 },
    { product_id: 'PROD-005', product_name: 'Ergonomic Mesh Office Chair',     category: 'Furniture',   units_sold: 27, total_revenue: 215380.0, profit_margin_pct: 27.2 },
    { product_id: 'PROD-006', product_name: 'Adjustable Standing Desk',        category: 'Furniture',   units_sold: 12, total_revenue: 120960.0, profit_margin_pct: 26.0 },
    { product_id: 'PROD-002', product_name: 'Ergonomic Mechanical Keyboard',   category: 'Electronics', units_sold: 18, total_revenue: 72900.0,  profit_margin_pct: 31.0 },
    { product_id: 'PROD-001', product_name: 'Noise-Cancelling Headphones',     category: 'Electronics', units_sold: 23, total_revenue: 62079.3,  profit_margin_pct: 30.5 },
  ],
  payment_methods: [
    { payment_method: 'UPI',              total_transactions: 42, total_revenue: 432500.0, share_of_transactions_pct: 28.38, cancellation_rate_pct: 4.76  },
    { payment_method: 'Credit Card',      total_transactions: 38, total_revenue: 412800.0, share_of_transactions_pct: 25.68, cancellation_rate_pct: 5.26  },
    { payment_method: 'Net Banking',      total_transactions: 26, total_revenue: 265400.0, share_of_transactions_pct: 17.57, cancellation_rate_pct: 3.85  },
    { payment_method: 'Debit Card',       total_transactions: 24, total_revenue: 238100.0, share_of_transactions_pct: 16.22, cancellation_rate_pct: 8.33  },
    { payment_method: 'Cash on Delivery', total_transactions: 18, total_revenue: 164163.4, share_of_transactions_pct: 12.16, cancellation_rate_pct: 11.11 },
  ],
};

const SAMPLE_CHIPS = [
  "What is our total revenue and profit?",
  "Show me the top 3 best selling products",
  "Which region is the most profitable?",
  "Who are our highest value customers?",
  "What is the most popular payment method?",
];

const formatINR = (val) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 2,
  }).format(val || 0);
};

const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/+$/, '');

export default function App() {
  const [page, setPage] = useState('landing');
  const [theme, setTheme] = useState(() => {
    const saved = localStorage.getItem('datapulse_theme');
    return saved === 'dark' || saved === 'light' ? saved : 'dark';
  });
  const [accessToken, setAccessToken] = useState(
    () => sessionStorage.getItem('datapulse_access_token')
  );
  const [authChecking, setAuthChecking] = useState(true);
  const [authError, setAuthError] = useState('');

  // Navigation & UI state
  const [activeView, setActiveView] = useState('dashboard');
  const [user, setUser] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
  const dropdownRef = useRef(null);

  const toggleTheme = () => {
    setTheme((current) => (current === 'dark' ? 'light' : 'dark'));
  };

  useEffect(() => {
    localStorage.setItem('datapulse_theme', theme);
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const requestLogout = () => {
    setShowLogoutConfirm(true);
    setDropdownOpen(false);
  };


  const handleAuthenticated = async (token) => {
    const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      sessionStorage.removeItem('datapulse_access_token');
      throw new Error(
        response.status === 401
          ? 'Your session is invalid or expired. Please sign in again.'
          : 'Could not verify your account. Please try again.'
      );
    }

    const userData = await response.json();
    setUser(userData);
    setAccessToken(token);
    setAuthError('');
    setActiveView('dashboard');
    setPage('dashboard');
  };

  const handleLogout = async () => {
    const token = accessToken;

    // Clear the local session immediately.
    sessionStorage.removeItem('datapulse_access_token');
    setAccessToken(null);
    setUser(null);
    setAuthError('');
    setActiveView('dashboard');
    setDropdownOpen(false);
    setSidebarOpen(false);
    setShowLogoutConfirm(false);
    setPage('auth');

    // The backend acknowledges logout but does not revoke JWTs.
    if (token) {
      try {
        await fetch(`${API_BASE_URL}/api/auth/logout`, {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
      } catch {
        // The local session is already cleared.
      }
    }
  };

  useEffect(() => {
    let cancelled = false;

    const restoreSession = async () => {
      const token = sessionStorage.getItem('datapulse_access_token');

      if (!token) {
        if (!cancelled) {
          setAccessToken(null);
          setAuthChecking(false);
        }
        return;
      }

      try {
        const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          sessionStorage.removeItem('datapulse_access_token');

          if (!cancelled) {
            setAccessToken(null);
            setPage('landing');
          }
        } else if (!cancelled) {
          const userData = await response.json();
          setUser(userData);
          setAccessToken(token);
          setPage('dashboard');
        }
      } catch {
        if (!cancelled) {
          setAuthError(
            'Cannot connect to the backend. Start FastAPI and refresh the page.'
          );
          setAccessToken(null);
          setPage('landing');
        }
      } finally {
        if (!cancelled) {
          setAuthChecking(false);
        }
      }
    };

    restoreSession();

    return () => {
      cancelled = true;
    };
  }, []);

  // Close user dropdown on outside click
  useEffect(() => {
    if (!dropdownOpen) return;
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [dropdownOpen]);

  const [data, setData] = useState(INITIAL_DATA);
  const [dataSource, setDataSource] = useState('Local Verified Snapshot');
  const [loading, setLoading] = useState(false);
  const [hoveredBar, setHoveredBar] = useState(null);

  // AI Assistant States
  const [aiInput, setAiInput] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  const [aiResult, setAiResult] = useState({
    answer: "Welcome to DataPulse AI. Click a suggestion below or type any business question to query the database using natural language.",
    insights: "AI Assistant translates questions directly into parameterized SQL queries in real-time at Rs.0 cost.",
    sql_query: "SELECT COUNT(order_id), SUM(net_amount), SUM(estimated_profit) FROM fact_sales;",
  });

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const token = sessionStorage.getItem('datapulse_access_token');

      if (!token) {
        await handleLogout();
        return;
      }

      const response = await fetch(`${API_BASE_URL}/api/dashboard`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.status === 401) {
        await handleLogout();
        return;
      }
      if (response.ok) {
        const json = await response.json();
        setData(json);
        setDataSource('Live FastAPI Backend');
      } else {
        setDataSource(`Backend error (${response.status})`);
      }
    } catch {
      setDataSource('Backend unavailable');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!authChecking && page === 'dashboard' && accessToken) {
      fetchDashboardData();
    }
  }, [authChecking, page, accessToken]);

  const handleAskAI = async (question) => {
    const q = question || aiInput;
    if (!q.trim()) return;

    setAiLoading(true);
    try {
      const token = sessionStorage.getItem('datapulse_access_token');

      if (!token) {
        await handleLogout();
        return;
      }

      const res = await fetch(`${API_BASE_URL}/api/ai/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ question: q }),
      });

      if (res.status === 401) {
        await handleLogout();
        return;
      }

      if (res.ok) {
        const result = await res.json();
        setAiResult(result);
      } else {
        setAiResult({
          answer: 'The backend could not process your question.',
          insights: `Request failed with status ${res.status}. Check the backend and try again.`,
          sql_query: null,
        });
      }
    } catch {
      setAiResult({
        answer: 'Unable to connect to the DataPulse backend.',
        insights: 'Check that FastAPI is running, then try again.',
        sql_query: null,
      });
    } finally {
      setAiLoading(false);
    }
  };

  // Client-side fallback matching local AI logic when API is offline
  const fallbackClientAI = (query) => {
    const lower = query.toLowerCase().trim();
    if (['drop', 'delete', 'truncate', 'alter', 'insert', 'update'].some((w) => lower.includes(w))) {
      setAiResult({
        answer: "Data modification and destructive operations are not permitted. DataPulse operates strictly in read-only analytical mode.",
        insights: "The assistant generates and executes read-only SELECT queries.",
        sql_query: null,
      });
    } else if (['product', 'item', 'selling', 'bestseller'].some((w) => lower.includes(w))) {
      setAiResult({
        answer: "The top performing product is 'Ultra-HD 4K Monitor 27-inch' with Rs.330,225.00 in delivered revenue across 21 units.",
        insights: "Category 'Electronics' drives the highest revenue share with a 28.5% profit margin.",
        sql_query: "SELECT p.product_name, SUM(s.quantity) AS units, ROUND(SUM(s.net_amount), 2) AS revenue FROM fact_sales s JOIN dim_products p ON s.product_id = p.product_id WHERE s.order_status = 'Delivered' GROUP BY p.product_name ORDER BY revenue DESC LIMIT 3;",
      });
    } else if (['region', 'zone', 'profitable', 'territory', 'geography'].some((w) => lower.includes(w))) {
      setAiResult({
        answer: "The 'South' region leads sales with Rs.347,171.40 in net revenue across 35 delivered orders.",
        insights: "Top regional margin is 26.83%, generating Rs.93,154.00 in net profit.",
        sql_query: "SELECT c.customer_region, COUNT(s.order_id) AS orders, ROUND(SUM(s.net_amount), 2) AS revenue FROM fact_sales s JOIN dim_customers c ON s.customer_id = c.customer_id WHERE s.order_status = 'Delivered' GROUP BY c.customer_region ORDER BY revenue DESC;",
      });
    } else if (['customer', 'client', 'buyer', 'clv', 'spender'].some((w) => lower.includes(w))) {
      setAiResult({
        answer: "Our top customer is Vikram Malhotra (North) with total lifetime spend of Rs.241,500.00 across 24 orders.",
        insights: "High customer retention: top repeat buyers contribute 40%+ of recurring volume.",
        sql_query: "SELECT c.customer_name, c.customer_region, ROUND(SUM(s.net_amount), 2) AS total_spend FROM fact_sales s JOIN dim_customers c ON s.customer_id = c.customer_id WHERE s.order_status != 'Cancelled' GROUP BY c.customer_id ORDER BY total_spend DESC LIMIT 5;",
      });
    } else if (['payment', 'upi', 'card', 'cash', 'cod', 'banking'].some((w) => lower.includes(w))) {
      setAiResult({
        answer: "The most preferred payment method is UPI, capturing 28.38% of total transaction volume.",
        insights: "UPI shows the lowest cancellation rate (4.76%) among all payment rails.",
        sql_query: "SELECT payment_method, COUNT(order_id) AS transactions, ROUND((COUNT(order_id)*100.0/(SELECT COUNT(*) FROM fact_sales)), 2) AS share_pct FROM fact_sales GROUP BY payment_method ORDER BY transactions DESC;",
      });
    } else if (['revenue', 'profit', 'sales', 'kpi', 'performance', 'margin', 'aov', 'earnings'].some((w) => lower.includes(w))) {
      setAiResult({
        answer: "Total net revenue is Rs.1,512,963.40 with Rs.408,097.30 in total net profit across 148 orders.",
        insights: "Healthy business efficiency: 26.97% overall profit margin and an Average Order Value (AOV) of Rs.10,222.73.",
        sql_query: "SELECT COUNT(order_id), ROUND(SUM(net_amount), 2) AS revenue, ROUND(SUM(estimated_profit), 2) AS profit FROM fact_sales;",
      });
    } else {
      setAiResult({
        answer: `I cannot answer questions about '${query}'. I am an analytical assistant specialized in DataPulse e-commerce data (revenue, profit, products, customers, regions, and payments).`,
        insights: "Try asking a supported question like: 'What is our total revenue and profit?' or 'Show me the top 3 best selling products'.",
        sql_query: null,
      });
    }
  };

  const { kpis, monthly_trends, regional_breakdown, top_products, payment_methods } = data;
  const maxMonthlyRevenue = Math.max(...monthly_trends.map((m) => m.monthly_revenue), 1);
  const maxRegionalRevenue = Math.max(...regional_breakdown.map((r) => r.regional_revenue), 1);

  if (authChecking) {
    return (
      <div className="app-shell">
        <p style={{ textAlign: 'center', padding: '80px 20px', color: '#98a4b8' }}>
          Verifying your DataPulse session...
        </p>
      </div>
    );
  }

  if (page === 'landing') {
    return (
      <>
        <LandingPage
          theme={theme}
          onToggleTheme={toggleTheme}
          onGetStarted={() => {
            setAuthError('');
            setPage('auth');
          }}
          onSignIn={() => {
            setAuthError('');
            setPage('auth');
          }}
        />

        {authError && (
          <div
            role="alert"
            style={{
              position: 'fixed',
              bottom: '20px',
              left: '50%',
              transform: 'translateX(-50%)',
              padding: '14px 20px',
              borderRadius: '10px',
              background: '#fff0f1',
              color: '#a52a38',
              zIndex: 1000,
              maxWidth: '90vw',
            }}
          >
            {authError}
          </div>
        )}
      </>
    );
  }

  if (page === 'auth') {
    return (
      <AuthPage
        theme={theme}
        onBack={() => setPage('landing')}
        onAuthenticated={handleAuthenticated}
      />
    );
  }

  if (!accessToken) {
    return (
      <AuthPage
        theme={theme}
        onBack={() => setPage('landing')}
        onAuthenticated={handleAuthenticated}
      />
    );
  }

  // Computed user avatar initials
  const userInitials = user?.full_name
    ? user.full_name.split(' ').map((n) => n[0]).join('').slice(0, 2).toUpperCase()
    : (user?.email || 'U').slice(0, 2).toUpperCase();

  const viewTitles = {
    dashboard: 'Analytics Dashboard',
    profile:   'My Profile',
    settings:  'Settings',
  };

  return (
    <div className={`app-shell theme-${theme}`}>
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className="sidebar-overlay"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* ── Sidebar ── */}
      <aside className={`sidebar ${sidebarOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-brand">
          <span className="sidebar-brand-icon">D</span>
          <span className="sidebar-brand-name">DataPulse</span>
        </div>

        <nav className="sidebar-nav" aria-label="Main navigation">
          {[
            { view: 'dashboard', icon: '📊', label: 'Dashboard' },
            { view: 'profile',   icon: '👤', label: 'Profile'   },
            { view: 'settings',  icon: '⚙',  label: 'Settings'  },
          ].map(({ view, icon, label }) => (
            <button
              key={view}
              type="button"
              className={`sidebar-nav-item ${activeView === view ? 'active' : ''}`}
              onClick={() => { setActiveView(view); setSidebarOpen(false); }}
              aria-current={activeView === view ? 'page' : undefined}
            >
              <span className="nav-icon" aria-hidden="true">{icon}</span>
              <span className="nav-label">{label}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <button
            type="button"
            className="sidebar-logout-btn"
            onClick={requestLogout}
          >
            <span aria-hidden="true">Sign out</span>
          </button>
        </div>
      </aside>

      {/* ── Main area ── */}
      <div className="main-area">
        {/* Top bar */}
        <header className="topbar">
          <div className="topbar-left">
            <button
              type="button"
              className="hamburger-btn"
              onClick={() => setSidebarOpen((v) => !v)}
              aria-label="Toggle sidebar"
              aria-expanded={sidebarOpen}
            >
              <span /><span /><span />
            </button>
            <h1 className="topbar-title">{viewTitles[activeView]}</h1>
          </div>

          <div className="topbar-right">
            {/* Live data badge */}
            <div className="badge-live">
              <span className="pulse-dot" />
              <span>{dataSource}</span>
            </div>

            {/* Refresh — only on dashboard */}
            {activeView === 'dashboard' && (
              <button
                type="button"
                className="btn-refresh"
                onClick={fetchDashboardData}
                disabled={loading}
              >
                {loading ? 'Refreshing...' : 'Refresh'}
              </button>
            )}

            {/* User dropdown */}
            <div className="user-menu" ref={dropdownRef}>
              <button
                type="button"
                className="user-avatar-btn"
                onClick={() => setDropdownOpen((v) => !v)}
                aria-expanded={dropdownOpen}
                aria-haspopup="menu"
                aria-label="Open user menu"
              >
                <span className="user-avatar" aria-hidden="true">{userInitials}</span>
                <span className="user-display-name">
                  {user?.full_name?.split(' ')[0] || 'User'}
                </span>
                <span className="dropdown-chevron" aria-hidden="true">
                  {dropdownOpen ? '▴' : '▾'}
                </span>
              </button>

              {dropdownOpen && (
                <div className="user-dropdown" role="menu">
                  <div className="dropdown-user-header">
                    <span className="dropdown-full-name">{user?.full_name || 'User'}</span>
                    <span className="dropdown-email">{user?.email || ''}</span>
                  </div>
                  <hr className="dropdown-divider" />
                  <button
                    type="button"
                    className="dropdown-menu-item"
                    role="menuitem"
                    onClick={() => { setActiveView('profile'); setDropdownOpen(false); }}
                  >
                    Profile
                  </button>
                  <button
                    type="button"
                    className="dropdown-menu-item"
                    role="menuitem"
                    onClick={() => { setActiveView('settings'); setDropdownOpen(false); }}
                  >
                    Settings
                  </button>
                  <hr className="dropdown-divider" />
                  <button
                    type="button"
                    className="dropdown-menu-item dropdown-item-danger"
                    role="menuitem"
                    onClick={requestLogout}
                  >
                    Sign out
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* ── Page content ── */}
        <main className="page-content">
          {activeView === 'profile' && (
            <ProfilePage
              user={user}
              onUpdateUser={(updated) => setUser(updated)}
            />
          )}

          {activeView === 'settings' && (
            <SettingsPage
              theme={theme}
              onToggleTheme={toggleTheme}
              onLogout={requestLogout}
              dataSource={dataSource}
            />
          )}


          {activeView === 'dashboard' && (
            <div className="dashboard-container">
              {/* AI Assistant Conversational Panel */}
              <section className="ai-widget">
                <div className="ai-header">
                  <div className="ai-title">
                    <span className="ai-sparkle">✨</span>
                    <span>Ask DataPulse AI Assistant (Text-to-SQL)</span>
                  </div>
                  <span style={{ fontSize: '11px', color: '#c084fc', fontWeight: 600 }}>100% Local • Rs.0 Cost</span>
                </div>

                <div className="ai-form">
                  <input
                    type="text"
                    className="ai-input"
                    placeholder="Ask a question (e.g. 'What is our total revenue?', 'Show top products')..."
                    value={aiInput}
                    onChange={(e) => setAiInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleAskAI()}
                  />
                  <button className="ai-btn" onClick={() => handleAskAI()} disabled={aiLoading}>
                    {aiLoading ? 'Thinking...' : 'Ask AI'}
                  </button>
                </div>

                <div className="ai-chips">
                  {SAMPLE_CHIPS.map((chip, idx) => (
                    <button
                      key={idx}
                      className="ai-chip"
                      onClick={() => { setAiInput(chip); handleAskAI(chip); }}
                    >
                      {chip}
                    </button>
                  ))}
                </div>

                {aiResult && (
                  <div className="ai-response-box">
                    <div className="ai-answer-text">
                      <strong>Answer:</strong> {aiResult.answer}
                    </div>
                    {aiResult.insights && (
                      <div className="ai-insight-text">
                        <span>💡 <strong>Key Insight:</strong> {aiResult.insights}</span>
                      </div>
                    )}
                    {aiResult.sql_query && (
                      <div>
                        <span style={{ fontSize: '11px', color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                          Generated SQL Query:
                        </span>
                        <pre className="ai-sql-snippet">{aiResult.sql_query}</pre>
                      </div>
                    )}
                  </div>
                )}
              </section>

              {/* KPI Cards Grid */}
              <section className="kpi-grid">
                <div className="glass-panel kpi-card">
                  <div className="kpi-title">Total Net Revenue</div>
                  <div className="kpi-value">{formatINR(kpis.total_net_revenue)}</div>
                  <div className="kpi-subtext">
                    <span className="kpi-badge badge-green">Validated</span>
                    <span>across {kpis.total_orders} orders</span>
                  </div>
                </div>

                <div className="glass-panel kpi-card">
                  <div className="kpi-title">Total Net Profit</div>
                  <div className="kpi-value">{formatINR(kpis.total_profit)}</div>
                  <div className="kpi-subtext">
                    <span className="kpi-badge badge-blue">{kpis.overall_profit_margin_pct}% Margin</span>
                    <span>after 65% COGS</span>
                  </div>
                </div>

                <div className="glass-panel kpi-card">
                  <div className="kpi-title">Delivered Orders</div>
                  <div className="kpi-value">
                    {kpis.delivered_orders}{' '}
                    <span style={{ fontSize: '18px', color: 'var(--text-muted)' }}>/ {kpis.total_orders}</span>
                  </div>
                  <div className="kpi-subtext">
                    <span className="kpi-badge badge-purple">
                      {((kpis.delivered_orders / kpis.total_orders) * 100).toFixed(1)}%
                    </span>
                    <span>fulfillment rate</span>
                  </div>
                </div>

                <div className="glass-panel kpi-card">
                  <div className="kpi-title">Average Order Value</div>
                  <div className="kpi-value">{formatINR(kpis.average_order_value)}</div>
                  <div className="kpi-subtext">
                    <span>Average revenue per basket</span>
                  </div>
                </div>
              </section>

              {/* 2-Column Analytics Layout */}
              <div className="grid-2col">
                {/* Monthly Revenue Chart */}
                <section className="glass-panel">
                  <div className="panel-header">
                    <h2>Monthly Revenue &amp; Trend</h2>
                    <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                      {hoveredBar
                        ? `${hoveredBar.month}: ${formatINR(hoveredBar.monthly_revenue)} (${hoveredBar.orders_count} orders)`
                        : 'Hover over bars for details'}
                    </span>
                  </div>
                  <div className="panel-body">
                    <div className="chart-container">
                      <svg className="chart-svg" viewBox="0 0 600 200" preserveAspectRatio="none">
                        <line x1="40" y1="20"  x2="580" y2="20"  stroke="rgba(75,85,99,0.2)" strokeDasharray="3" />
                        <line x1="40" y1="90"  x2="580" y2="90"  stroke="rgba(75,85,99,0.2)" strokeDasharray="3" />
                        <line x1="40" y1="160" x2="580" y2="160" stroke="rgba(75,85,99,0.4)" />
                        {monthly_trends.map((item, idx) => {
                          const barWidth = 46;
                          const x = 60 + idx * 85;
                          const height = (item.monthly_revenue / maxMonthlyRevenue) * 130;
                          const y = 160 - height;
                          return (
                            <g key={item.month}>
                              <rect
                                className="chart-bar"
                                x={x} y={y} width={barWidth} height={height} rx="6"
                                onMouseEnter={() => setHoveredBar(item)}
                                onMouseLeave={() => setHoveredBar(null)}
                              />
                              <text
                                x={x + barWidth / 2} y="182"
                                textAnchor="middle" fill="#9ca3af"
                                fontSize="11" fontFamily="var(--font-sans)"
                              >
                                {item.month.slice(5)}
                              </text>
                            </g>
                          );
                        })}
                      </svg>
                    </div>
                  </div>
                </section>

                {/* Regional Performance */}
                <section className="glass-panel">
                  <div className="panel-header">
                    <h2>Regional Performance</h2>
                    <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Delivered Revenue</span>
                  </div>
                  <div className="panel-body">
                    {regional_breakdown.map((reg) => {
                      const pct = (reg.regional_revenue / maxRegionalRevenue) * 100;
                      return (
                        <div key={reg.customer_region} className="regional-item">
                          <div className="regional-header">
                            <span>{reg.customer_region}</span>
                            <span>{formatINR(reg.regional_revenue)}</span>
                          </div>
                          <div className="progress-track">
                            <div className="progress-fill" style={{ width: `${pct}%` }} />
                          </div>
                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-dim)', marginTop: '4px' }}>
                            <span>{reg.order_count} Orders</span>
                            <span>Profit Margin: {reg.profit_margin_pct}%</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </section>
              </div>

              {/* Bottom Grid: Top Products and Payment Methods */}
              <div className="grid-2col">
                {/* Top 5 Products Leaderboard */}
                <section className="glass-panel">
                  <div className="panel-header">
                    <h2>Top 5 Products by Revenue</h2>
                  </div>
                  <div className="panel-body" style={{ padding: '8px 16px' }}>
                    <table className="custom-table">
                      <thead>
                        <tr>
                          <th>#</th>
                          <th>Product Name</th>
                          <th>Category</th>
                          <th>Units</th>
                          <th>Total Revenue</th>
                        </tr>
                      </thead>
                      <tbody>
                        {top_products.map((prod, idx) => (
                          <tr key={prod.product_id}>
                            <td>
                              <span className={`rank-badge rank-${idx + 1}`}>{idx + 1}</span>
                            </td>
                            <td style={{ fontWeight: 600 }}>{prod.product_name}</td>
                            <td>
                              <span className="category-pill">{prod.category}</span>
                            </td>
                            <td>{prod.units_sold}</td>
                            <td style={{ fontWeight: 700, color: '#38bdf8' }}>
                              {formatINR(prod.total_revenue)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </section>

                {/* Payment Methods Health */}
                <section className="glass-panel">
                  <div className="panel-header">
                    <h2>Payment Method Adoption</h2>
                  </div>
                  <div className="panel-body">
                    <div className="pm-grid">
                      {payment_methods.map((pm) => (
                        <div key={pm.payment_method} className="pm-card">
                          <div className="pm-name">{pm.payment_method}</div>
                          <div className="pm-val">{pm.share_of_transactions_pct}%</div>
                          <div className="pm-sub">
                            {pm.total_transactions} orders • {pm.cancellation_rate_pct}% cancel
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </section>
              </div>
            </div>
          )}
        </main>
      </div>

      {/* ── Logout Confirmation Dialog ── */}
      {showLogoutConfirm && (
        <div
          className="modal-backdrop"
          onClick={() => setShowLogoutConfirm(false)}
          role="presentation"
        >
          <div
            className="modal-dialog"
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
            aria-labelledby="logout-dialog-title"
          >
            <div className="modal-header">
              <div className="modal-icon-badge" aria-hidden="true">⚠</div>
              <div className="modal-title-group">
                <h2 id="logout-dialog-title" className="modal-title">Confirm Logout</h2>
                <p className="modal-subtitle">Are you sure you want to sign out?</p>
              </div>
            </div>
            <p className="modal-body">
              Logging out will clear your session token from this browser. You can sign back in at any time.
            </p>
            <div className="modal-actions">
              <button
                type="button"
                className="modal-btn-cancel"
                onClick={() => setShowLogoutConfirm(false)}
              >
                Cancel
              </button>
              <button
                type="button"
                className="modal-btn-confirm"
                onClick={() => {
                  setShowLogoutConfirm(false);
                  handleLogout();
                }}
              >
                Confirm Logout
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
