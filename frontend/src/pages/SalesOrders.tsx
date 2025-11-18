import { useState, useEffect } from 'react';
import { ShoppingBag, Plus, Search, FileText, CheckCircle, XCircle, Clock, Package } from 'lucide-react';
import { salesAPI } from '../lib/api';
import './SalesOrders.css';

interface SalesOrder {
  id: number;
  name: string;
  state: 'draft' | 'quotation' | 'confirmed' | 'delivered' | 'cancelled';
  customer_id: number;
  customer_name: string;
  order_date: string;
  amount_total: number;
  created_at: string;
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY'
  }).format(amount);
};

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('tr-TR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric'
  });
};

const stateLabels: { [key: string]: string } = {
  draft: 'Taslak',
  quotation: 'Teklif',
  confirmed: 'Onaylandı',
  delivered: 'Teslim Edildi',
  cancelled: 'İptal'
};

const stateIcons: { [key: string]: any } = {
  draft: FileText,
  quotation: Clock,
  confirmed: CheckCircle,
  delivered: Package,
  cancelled: XCircle
};

const stateColors: { [key: string]: string } = {
  draft: 'state-draft',
  quotation: 'state-quotation',
  confirmed: 'state-confirmed',
  delivered: 'state-delivered',
  cancelled: 'state-cancelled'
};

export default function SalesOrders() {
  const [orders, setOrders] = useState<SalesOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterState, setFilterState] = useState<string>('all');

  useEffect(() => {
    loadOrders();
  }, []);

  const loadOrders = async () => {
    try {
      setLoading(true);
      const response = await salesAPI.getOrders();
      setOrders(response.data);
    } catch (error) {
      console.error('Siparişler yüklenirken hata:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredOrders = orders.filter(order => {
    const matchesSearch =
      order.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      order.customer_name.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesState = filterState === 'all' || order.state === filterState;

    return matchesSearch && matchesState;
  });

  // Statistics
  const stats = {
    total: orders.length,
    draft: orders.filter(o => o.state === 'draft').length,
    quotation: orders.filter(o => o.state === 'quotation').length,
    confirmed: orders.filter(o => o.state === 'confirmed').length,
    totalAmount: orders.reduce((sum, o) => sum + o.amount_total, 0)
  };

  if (loading) {
    return (
      <div className="page-loading">
        <div className="spinner"></div>
        <p>Yükleniyor...</p>
      </div>
    );
  }

  return (
    <div className="sales-orders-page">
      <div className="page-header">
        <div className="header-title">
          <ShoppingBag size={32} />
          <div>
            <h1>Satış Siparişleri</h1>
            <p>{stats.total} sipariş • {formatCurrency(stats.totalAmount)} toplam</p>
          </div>
        </div>
        <button className="btn-primary">
          <Plus size={20} />
          Yeni Sipariş
        </button>
      </div>

      <div className="page-content">
        {/* Stats Cards */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon state-draft">
              <FileText size={24} />
            </div>
            <div className="stat-content">
              <span className="stat-label">Taslak</span>
              <span className="stat-value">{stats.draft}</span>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon state-quotation">
              <Clock size={24} />
            </div>
            <div className="stat-content">
              <span className="stat-label">Teklif</span>
              <span className="stat-value">{stats.quotation}</span>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon state-confirmed">
              <CheckCircle size={24} />
            </div>
            <div className="stat-content">
              <span className="stat-label">Onaylı</span>
              <span className="stat-value">{stats.confirmed}</span>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="filters-bar">
          <div className="search-bar">
            <Search size={20} />
            <input
              type="text"
              placeholder="Sipariş no veya müşteri adı ile ara..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <div className="filter-buttons">
            <button
              className={`filter-btn ${filterState === 'all' ? 'active' : ''}`}
              onClick={() => setFilterState('all')}
            >
              Tümü
            </button>
            <button
              className={`filter-btn ${filterState === 'draft' ? 'active' : ''}`}
              onClick={() => setFilterState('draft')}
            >
              Taslak
            </button>
            <button
              className={`filter-btn ${filterState === 'quotation' ? 'active' : ''}`}
              onClick={() => setFilterState('quotation')}
            >
              Teklif
            </button>
            <button
              className={`filter-btn ${filterState === 'confirmed' ? 'active' : ''}`}
              onClick={() => setFilterState('confirmed')}
            >
              Onaylı
            </button>
          </div>
        </div>

        {/* Orders List */}
        <div className="orders-list">
          {filteredOrders.map(order => {
            const StateIcon = stateIcons[order.state];
            return (
              <div key={order.id} className="order-card">
                <div className="order-header">
                  <div className="order-number">
                    <ShoppingBag size={20} />
                    <span>{order.name}</span>
                  </div>
                  <div className={`order-state ${stateColors[order.state]}`}>
                    <StateIcon size={16} />
                    <span>{stateLabels[order.state]}</span>
                  </div>
                </div>

                <div className="order-body">
                  <div className="order-info">
                    <div className="info-item">
                      <span className="info-label">Müşteri</span>
                      <span className="info-value">{order.customer_name}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">Tarih</span>
                      <span className="info-value">{formatDate(order.order_date)}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">Tutar</span>
                      <span className="info-value amount">{formatCurrency(order.amount_total)}</span>
                    </div>
                  </div>
                </div>

                <div className="order-actions">
                  <button className="btn-secondary">Görüntüle</button>
                  {order.state === 'draft' || order.state === 'quotation' ? (
                    <button className="btn-success">Onayla</button>
                  ) : null}
                </div>
              </div>
            );
          })}
        </div>

        {filteredOrders.length === 0 && (
          <div className="empty-state">
            <ShoppingBag size={64} />
            <h3>Sipariş Bulunamadı</h3>
            <p>Arama kriterlerinize uygun sipariş bulunamadı.</p>
          </div>
        )}
      </div>
    </div>
  );
}
