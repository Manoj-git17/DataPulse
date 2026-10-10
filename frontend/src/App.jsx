import React, { useState, useEffect } from 'react';
import './App.css';

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
    { customer_region: 'South', order_count: 35, regional_revenue: 347171.4, regional_profit: 93154.0, avg_order_value: 9919.18, profit_margin_pct: 26.83 },
    { customer_region: 'North', order_count: 23, regional_revenue: 231233.8, regional_profit: 54132.2, avg_order_value: 10053.64, profit_margin_pct: 23.41 },
    { customer_region: 'West',  order_count: 22, regional_revenue: 225811.55, regional_profit: 59814.55, avg_order_value: 10264.16, profit_margin_pct: 26.49 },
    { customer_region: 'East',  order_count: 17, regional_revenue: 174393.05, regional_profit: 48110.4, avg_order_value: 10258.41, profit_margin_pct: 27.59 },
  ],
  top_products: [
    { product_id: 'PROD-003', product_name: 'Ultra-HD 4K Monitor 27-inch', category: 'Electronics', units_sold: 21, total_revenue: 330225.0, profit_margin_pct: 28.5 },
    { product_id: 'PROD-005', product_name: 'Ergonomic Mesh Office Chair', category: 'Furniture', units_sold: 27, total_revenue: 215380.0, profit_margin_pct: 27.2 },
    { product_id: 'PROD-006', product_name: 'Adjustable Standing Desk', category: 'Furniture', units_sold: 12, total_revenue: 120960.0, profit_margin_pct: 26.0 },
    { product_id: 'PROD-002', product_name: 'Ergonomic Mechanical Keyboard', category: 'Electronics', units_sold: 18, total_revenue: 72900.0, profit_margin_pct: 31.0 },
    { product_id: 'PROD-001', product_name: 'Noise-Cancelling Headphones', category: 'Electronics', units_sold: 23, total_revenue: 62079.3, profit_margin_pct: 30.5 },
  ],
  payment_methods: [
    { payment_method: 'UPI', total_transactions: 42, total_revenue: 432500.0, share_of_transactions_pct: 28.38, cancellation_rate_pct: 4.76 },
    { payment_method: 'Credit Card', total_transactions: 38, total_revenue: 412800.0, share_of_transactions_pct: 25.68, cancellation_rate_pct: 5.26 },
    { payment_method: 'Net Banking', total_transactions: 26, total_revenue: 265400.0, share_of_transactions_pct: 17.57, cancellation_rate_pct: 3.85 },
    { payment_method: 'Debit Card', total_transactions: 24, total_revenue: 238100.0, share_of_transactions_pct: 16.22, cancellation_rate_pct: 8.33 },
    { payment_method: 'Cash on Delivery', total_transactions: 18, total_revenue: 164163.4, share_of_transactions_pct: 12.16, cancellation_rate_pct: 11.11 },
  ],
};

const formatINR = (val) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 2,
  }).format(val || 0);
};

export default function App() {
  const [data, setData] = useState(INITIAL_DATA);
  const [dataSource, setDataSource] = useState('Local Verified Snapshot');
  const [loading, setLoading] = useState(false);
  const [hoveredBar, setHoveredBar] = useState(null);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/dashboard');
      if (response.ok) {
        const json = await response.json();
        setData(json);
        setDataSource('Live FastAPI Backend');
      } else {
        setDataSource('Local Snapshot (FastAPI Offline)');
      }
    } catch {
      setDataSource('Local Snapshot (FastAPI Offline)');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const { kpis, monthly_trends, regional_breakdown, top_products, payment_methods } = data;
  const maxMonthlyRevenue = Math.max(...monthly_trends.map((m) => m.monthly_revenue), 1);
  const maxRegionalRevenue = Math.max(...regional_breakdown.map((r) => r.regional_revenue), 1);

  return (
    <div className="dashboard-container">
      {/* Header Bar */}
      <header className="header-bar">
        <div className="brand-wrapper">
          <h1>DataPulse Analytics</h1>
          <p>Intelligent Data Engineering & Analytics Platform • Python • SQL • FastAPI • React</p>
        </div>
        <div className="header-actions">
          <div className="badge-live">
            <span className="pulse-dot"></span>
            <span>{dataSource}</span>
          </div>
          <button className="btn-refresh" onClick={fetchDashboardData} disabled={loading}>
            {loading ? 'Refreshing...' : '↻ Refresh'}
          </button>
        </div>
      </header>

      {/* KPI Cards Grid */}
      <section className="kpi-grid">
        <div className="glass-panel kpi-card">
          <div className="kpi-title">Total Net Revenue</div>
          <div className="kpi-value">{formatINR(kpis.total_net_revenue)}</div>
          <div className="kpi-subtext">
            <span className="kpi-badge badge-green">+18.4%</span>
            <span>across 148 orders</span>
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
          <div className="kpi-value">{kpis.delivered_orders} <span style={{ fontSize: '18px', color: 'var(--text-muted)' }}>/ {kpis.total_orders}</span></div>
          <div className="kpi-subtext">
            <span className="kpi-badge badge-purple">{((kpis.delivered_orders / kpis.total_orders) * 100).toFixed(1)}%</span>
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
            <h2>Monthly Revenue & Trend</h2>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              {hoveredBar ? `${hoveredBar.month}: ${formatINR(hoveredBar.monthly_revenue)} (${hoveredBar.orders_count} orders)` : 'Hover over bars for details'}
            </span>
          </div>
          <div className="panel-body">
            <div className="chart-container">
              <svg className="chart-svg" viewBox="0 0 600 200" preserveAspectRatio="none">
                {/* Horizontal grid lines */}
                <line x1="40" y1="20" x2="580" y2="20" stroke="rgba(75, 85, 99, 0.2)" strokeDasharray="3" />
                <line x1="40" y1="90" x2="580" y2="90" stroke="rgba(75, 85, 99, 0.2)" strokeDasharray="3" />
                <line x1="40" y1="160" x2="580" y2="160" stroke="rgba(75, 85, 99, 0.4)" />

                {/* Bars */}
                {monthly_trends.map((item, idx) => {
                  const barWidth = 46;
                  const x = 60 + idx * 85;
                  const height = (item.monthly_revenue / maxMonthlyRevenue) * 130;
                  const y = 160 - height;
                  return (
                    <g key={item.month}>
                      <rect
                        className="chart-bar"
                        x={x}
                        y={y}
                        width={barWidth}
                        height={height}
                        rx="6"
                        onMouseEnter={() => setHoveredBar(item)}
                        onMouseLeave={() => setHoveredBar(null)}
                      />
                      <text
                        x={x + barWidth / 2}
                        y="182"
                        textAnchor="middle"
                        fill="#9ca3af"
                        fontSize="11"
                        fontFamily="var(--font-sans)"
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
                    <div className="progress-fill" style={{ width: `${pct}%` }}></div>
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
                    <td style={{ fontWeight: 700, color: '#38bdf8' }}>{formatINR(prod.total_revenue)}</td>
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
  );
}
