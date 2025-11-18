import React, { useState, useEffect } from 'react';
import { Calendar, DollarSign, ShoppingCart, Clock, CheckCircle, XCircle } from 'lucide-react';
import './POSHistory.css';

interface POSSession {
  id: number;
  name: string;
  state: 'opening' | 'in_progress' | 'closing' | 'closed';
  start_date: string;
  end_date?: string;
  opening_balance: number;
  closing_balance?: number;
  cash_register_difference?: number;
  total_sales: number;
  order_count: number;
  created_at: string;
}

interface SessionStats {
  total_sessions: number;
  active_session: POSSession | null;
  today_sales: number;
  today_orders: number;
  cash_in_register: number;
}

const POSHistory: React.FC = () => {
  const [sessions, setSessions] = useState<POSSession[]>([]);
  const [stats, setStats] = useState<SessionStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [filterState, setFilterState] = useState<string>('all');
  const [showCloseModal, setShowCloseModal] = useState(false);
  const [selectedSession, setSelectedSession] = useState<POSSession | null>(null);
  const [closingBalance, setClosingBalance] = useState<number>(0);

  useEffect(() => {
    loadData();
  }, [filterState]);

  const loadData = async () => {
    try {
      setLoading(true);

      // Stats
      const statsRes = await fetch('http://localhost:5252/api/pos/sessions/stats');
      const statsData = await statsRes.json();
      setStats(statsData);

      // Sessions
      let url = 'http://localhost:5252/api/pos/sessions?';
      if (filterState !== 'all') url += `state=${filterState}`;

      const sessionsRes = await fetch(url);
      const sessionsData = await sessionsRes.json();
      setSessions(sessionsData);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenSession = async () => {
    const openingBalance = prompt('Açılış kasası tutarını girin (TRY):');
    if (!openingBalance) return;

    try {
      const response = await fetch('http://localhost:5252/api/pos/sessions/open', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ opening_balance: parseFloat(openingBalance) })
      });

      if (response.ok) {
        loadData();
      }
    } catch (error) {
      console.error('Error opening session:', error);
      alert('Session açılırken hata oluştu');
    }
  };

  const handleCloseSession = async () => {
    if (!selectedSession) return;

    try {
      const response = await fetch(`http://localhost:5252/api/pos/sessions/${selectedSession.id}/close`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ closing_balance: closingBalance })
      });

      if (response.ok) {
        setShowCloseModal(false);
        setSelectedSession(null);
        setClosingBalance(0);
        loadData();
      }
    } catch (error) {
      console.error('Error closing session:', error);
      alert('Session kapatılırken hata oluştu');
    }
  };

  const openCloseModal = (session: POSSession) => {
    setSelectedSession(session);
    setClosingBalance(session.opening_balance + session.total_sales);
    setShowCloseModal(true);
  };

  const getStateLabel = (state: string) => {
    const labels: Record<string, string> = {
      opening: 'Açılıyor',
      in_progress: 'Devam Ediyor',
      closing: 'Kapanıyor',
      closed: 'Kapalı'
    };
    return labels[state] || state;
  };

  const getStateClass = (state: string) => {
    const classes: Record<string, string> = {
      opening: 'state-opening',
      in_progress: 'state-active',
      closing: 'state-closing',
      closed: 'state-closed'
    };
    return classes[state] || '';
  };

  if (loading) {
    return (
      <div className="pos-history-page">
        <div className="loading">Yükleniyor...</div>
      </div>
    );
  }

  return (
    <div className="pos-history-page">
      <div className="page-header">
        <div>
          <h1>
            <ShoppingCart size={32} />
            POS Session Yönetimi
          </h1>
          <p>Kasa oturumları ve günlük satış raporları</p>
        </div>
        {!stats?.active_session && (
          <button className="btn-primary" onClick={handleOpenSession}>
            <CheckCircle size={20} />
            Yeni Session Aç
          </button>
        )}
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon blue">
              <Calendar size={24} />
            </div>
            <div className="stat-content">
              <div className="stat-label">Toplam Session</div>
              <div className="stat-value">{stats.total_sessions}</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon green">
              <DollarSign size={24} />
            </div>
            <div className="stat-content">
              <div className="stat-label">Bugünkü Satışlar</div>
              <div className="stat-value">
                {new Intl.NumberFormat('tr-TR', {
                  style: 'currency',
                  currency: 'TRY'
                }).format(stats.today_sales)}
              </div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon orange">
              <ShoppingCart size={24} />
            </div>
            <div className="stat-content">
              <div className="stat-label">Bugünkü Siparişler</div>
              <div className="stat-value">{stats.today_orders}</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon purple">
              <DollarSign size={24} />
            </div>
            <div className="stat-content">
              <div className="stat-label">Kasadaki Para</div>
              <div className="stat-value">
                {new Intl.NumberFormat('tr-TR', {
                  style: 'currency',
                  currency: 'TRY'
                }).format(stats.cash_in_register)}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Active Session Alert */}
      {stats?.active_session && (
        <div className="active-session-alert">
          <div className="alert-content">
            <div className="alert-header">
              <Clock size={24} />
              <h3>Aktif Session: {stats.active_session.name}</h3>
            </div>
            <div className="alert-details">
              <div className="detail-item">
                <span>Başlangıç:</span>
                <strong>{new Date(stats.active_session.start_date).toLocaleString('tr-TR')}</strong>
              </div>
              <div className="detail-item">
                <span>Açılış Kasası:</span>
                <strong>
                  {new Intl.NumberFormat('tr-TR', {
                    style: 'currency',
                    currency: 'TRY'
                  }).format(stats.active_session.opening_balance)}
                </strong>
              </div>
              <div className="detail-item">
                <span>Toplam Satış:</span>
                <strong>
                  {new Intl.NumberFormat('tr-TR', {
                    style: 'currency',
                    currency: 'TRY'
                  }).format(stats.active_session.total_sales)}
                </strong>
              </div>
              <div className="detail-item">
                <span>Sipariş Sayısı:</span>
                <strong>{stats.active_session.order_count}</strong>
              </div>
            </div>
          </div>
          <button
            className="btn-close-session"
            onClick={() => openCloseModal(stats.active_session!)}
          >
            <XCircle size={20} />
            Session'ı Kapat
          </button>
        </div>
      )}

      {/* Filters */}
      <div className="filters-section">
        <label>Session Durumu</label>
        <div className="filter-buttons">
          <button
            className={`filter-btn ${filterState === 'all' ? 'active' : ''}`}
            onClick={() => setFilterState('all')}
          >
            Tümü
          </button>
          <button
            className={`filter-btn ${filterState === 'in_progress' ? 'active' : ''}`}
            onClick={() => setFilterState('in_progress')}
          >
            Aktif
          </button>
          <button
            className={`filter-btn ${filterState === 'closed' ? 'active' : ''}`}
            onClick={() => setFilterState('closed')}
          >
            Kapalı
          </button>
        </div>
      </div>

      {/* Sessions List */}
      <div className="sessions-grid">
        {sessions.map(session => (
          <div key={session.id} className={`session-card ${getStateClass(session.state)}`}>
            <div className="session-header">
              <div className="session-name">{session.name}</div>
              <div className={`session-state ${getStateClass(session.state)}`}>
                {getStateLabel(session.state)}
              </div>
            </div>

            <div className="session-dates">
              <div className="date-row">
                <Calendar size={16} />
                <span>Başlangıç:</span>
                <strong>{new Date(session.start_date).toLocaleString('tr-TR')}</strong>
              </div>
              {session.end_date && (
                <div className="date-row">
                  <Calendar size={16} />
                  <span>Bitiş:</span>
                  <strong>{new Date(session.end_date).toLocaleString('tr-TR')}</strong>
                </div>
              )}
            </div>

            <div className="session-financials">
              <div className="financial-row">
                <span>Açılış Kasası:</span>
                <strong>
                  {new Intl.NumberFormat('tr-TR', {
                    style: 'currency',
                    currency: 'TRY'
                  }).format(session.opening_balance)}
                </strong>
              </div>
              <div className="financial-row">
                <span>Toplam Satış:</span>
                <strong className="sales">
                  {new Intl.NumberFormat('tr-TR', {
                    style: 'currency',
                    currency: 'TRY'
                  }).format(session.total_sales)}
                </strong>
              </div>
              {session.closing_balance !== undefined && (
                <div className="financial-row">
                  <span>Kapanış Kasası:</span>
                  <strong>
                    {new Intl.NumberFormat('tr-TR', {
                      style: 'currency',
                      currency: 'TRY'
                    }).format(session.closing_balance)}
                  </strong>
                </div>
              )}
              {session.cash_register_difference !== undefined && session.cash_register_difference !== 0 && (
                <div className="financial-row">
                  <span>Kasa Farkı:</span>
                  <strong className={session.cash_register_difference > 0 ? 'positive' : 'negative'}>
                    {session.cash_register_difference > 0 ? '+' : ''}
                    {new Intl.NumberFormat('tr-TR', {
                      style: 'currency',
                      currency: 'TRY'
                    }).format(session.cash_register_difference)}
                  </strong>
                </div>
              )}
            </div>

            <div className="session-stats">
              <div className="stat-item">
                <ShoppingCart size={16} />
                <span>{session.order_count} Sipariş</span>
              </div>
              {session.order_count > 0 && (
                <div className="stat-item">
                  <DollarSign size={16} />
                  <span>
                    Ort: {new Intl.NumberFormat('tr-TR', {
                      style: 'currency',
                      currency: 'TRY'
                    }).format(session.total_sales / session.order_count)}
                  </span>
                </div>
              )}
            </div>

            {session.state === 'in_progress' && (
              <button
                className="btn-close-session-small"
                onClick={() => openCloseModal(session)}
              >
                Session'ı Kapat
              </button>
            )}
          </div>
        ))}
      </div>

      {sessions.length === 0 && (
        <div className="empty-state">
          <ShoppingCart size={64} />
          <h3>Session Bulunamadı</h3>
          <p>Henüz hiç POS session açılmamış.</p>
        </div>
      )}

      {/* Close Session Modal */}
      {showCloseModal && selectedSession && (
        <div className="modal-overlay" onClick={() => setShowCloseModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Session Kapat: {selectedSession.name}</h2>
              <button className="modal-close" onClick={() => setShowCloseModal(false)}>×</button>
            </div>

            <div className="modal-body">
              <div className="close-summary">
                <h3>Session Özeti</h3>
                <div className="summary-row">
                  <span>Açılış Kasası:</span>
                  <strong>
                    {new Intl.NumberFormat('tr-TR', {
                      style: 'currency',
                      currency: 'TRY'
                    }).format(selectedSession.opening_balance)}
                  </strong>
                </div>
                <div className="summary-row">
                  <span>Toplam Satış:</span>
                  <strong>
                    {new Intl.NumberFormat('tr-TR', {
                      style: 'currency',
                      currency: 'TRY'
                    }).format(selectedSession.total_sales)}
                  </strong>
                </div>
                <div className="summary-row">
                  <span>Sipariş Sayısı:</span>
                  <strong>{selectedSession.order_count}</strong>
                </div>
                <div className="summary-row expected">
                  <span>Beklenen Kasa:</span>
                  <strong>
                    {new Intl.NumberFormat('tr-TR', {
                      style: 'currency',
                      currency: 'TRY'
                    }).format(selectedSession.opening_balance + selectedSession.total_sales)}
                  </strong>
                </div>
              </div>

              <div className="form-group">
                <label>Kapanış Kasası Tutarı *</label>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={closingBalance}
                  onChange={(e) => setClosingBalance(parseFloat(e.target.value))}
                  placeholder="Kasadaki toplam parayı girin"
                  autoFocus
                />
              </div>

              <div className={`difference-alert ${
                closingBalance - (selectedSession.opening_balance + selectedSession.total_sales) === 0
                  ? 'balanced'
                  : closingBalance - (selectedSession.opening_balance + selectedSession.total_sales) > 0
                  ? 'surplus'
                  : 'deficit'
              }`}>
                <strong>Kasa Farkı:</strong>
                <span>
                  {closingBalance - (selectedSession.opening_balance + selectedSession.total_sales) > 0 ? '+' : ''}
                  {new Intl.NumberFormat('tr-TR', {
                    style: 'currency',
                    currency: 'TRY'
                  }).format(closingBalance - (selectedSession.opening_balance + selectedSession.total_sales))}
                </span>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn-secondary" onClick={() => setShowCloseModal(false)}>
                İptal
              </button>
              <button className="btn-primary" onClick={handleCloseSession}>
                Session'ı Kapat
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default POSHistory;
