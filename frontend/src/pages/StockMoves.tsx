import React, { useState, useEffect } from 'react';
import { Plus, TrendingUp, TrendingDown, ArrowRightLeft, Calendar } from 'lucide-react';
import './StockMoves.css';

interface Product {
  id: number;
  name: string;
  code: string;
}

interface Location {
  id: number;
  name: string;
  code: string;
}

interface StockMove {
  id: number;
  name: string;
  product: Product;
  move_type: 'in' | 'out' | 'internal';
  state: 'draft' | 'confirmed' | 'done' | 'cancelled';
  location_from: Location;
  location_to: Location;
  quantity: number;
  unit_price: number;
  total_amount: number;
  reference?: string;
  scheduled_date: string;
  done_date?: string;
  created_at: string;
}

interface NewMove {
  product_id: number;
  move_type: 'in' | 'out' | 'internal';
  location_from_id: number;
  location_to_id: number;
  quantity: number;
  unit_price: number;
  reference?: string;
  scheduled_date: string;
}

const StockMoves: React.FC = () => {
  const [moves, setMoves] = useState<StockMove[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState<string>('all');
  const [filterState, setFilterState] = useState<string>('all');
  const [showModal, setShowModal] = useState(false);
  const [newMove, setNewMove] = useState<NewMove>({
    product_id: 0,
    move_type: 'in',
    location_from_id: 0,
    location_to_id: 0,
    quantity: 1,
    unit_price: 0,
    scheduled_date: new Date().toISOString().split('T')[0]
  });

  useEffect(() => {
    loadData();
  }, [filterType, filterState]);

  const loadData = async () => {
    try {
      setLoading(true);

      // Products
      const prodRes = await fetch('http://localhost:5252/api/inventory/products');
      const prodData = await prodRes.json();
      setProducts(prodData);

      // Locations
      const locRes = await fetch('http://localhost:5252/api/inventory/locations');
      const locData = await locRes.json();
      setLocations(locData);

      // Moves
      let url = 'http://localhost:5252/api/inventory/moves?';
      if (filterType !== 'all') url += `move_type=${filterType}&`;
      if (filterState !== 'all') url += `state=${filterState}&`;

      const movesRes = await fetch(url);
      const movesData = await movesRes.json();
      setMoves(movesData);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateMove = async () => {
    if (!newMove.product_id || !newMove.location_from_id || !newMove.location_to_id) {
      alert('Lütfen tüm zorunlu alanları doldurun');
      return;
    }

    try {
      const response = await fetch('http://localhost:5252/api/inventory/moves', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newMove)
      });

      if (response.ok) {
        setShowModal(false);
        loadData();
        // Reset form
        setNewMove({
          product_id: 0,
          move_type: 'in',
          location_from_id: 0,
          location_to_id: 0,
          quantity: 1,
          unit_price: 0,
          scheduled_date: new Date().toISOString().split('T')[0]
        });
      }
    } catch (error) {
      console.error('Error creating move:', error);
      alert('Hareket oluşturulurken hata oluştu');
    }
  };

  const handleConfirmMove = async (moveId: number) => {
    try {
      const response = await fetch(`http://localhost:5252/api/inventory/moves/${moveId}/confirm`, {
        method: 'POST'
      });

      if (response.ok) {
        loadData();
      }
    } catch (error) {
      console.error('Error confirming move:', error);
      alert('Hareket onaylanırken hata oluştu');
    }
  };

  const handleExecuteMove = async (moveId: number) => {
    try {
      const response = await fetch(`http://localhost:5252/api/inventory/moves/${moveId}/execute`, {
        method: 'POST'
      });

      if (response.ok) {
        loadData();
      }
    } catch (error) {
      console.error('Error executing move:', error);
      alert('Hareket gerçekleştirilirken hata oluştu');
    }
  };

  const getMoveTypeIcon = (type: string) => {
    switch (type) {
      case 'in': return <TrendingUp size={20} />;
      case 'out': return <TrendingDown size={20} />;
      case 'internal': return <ArrowRightLeft size={20} />;
      default: return null;
    }
  };

  const getMoveTypeClass = (type: string) => {
    const classes: Record<string, string> = {
      in: 'type-in',
      out: 'type-out',
      internal: 'type-internal'
    };
    return classes[type] || '';
  };

  const getStateLabel = (state: string) => {
    const labels: Record<string, string> = {
      draft: 'Taslak',
      confirmed: 'Onaylandı',
      done: 'Tamamlandı',
      cancelled: 'İptal Edildi'
    };
    return labels[state] || state;
  };

  const getStateClass = (state: string) => {
    const classes: Record<string, string> = {
      draft: 'state-draft',
      confirmed: 'state-confirmed',
      done: 'state-done',
      cancelled: 'state-cancelled'
    };
    return classes[state] || '';
  };

  if (loading) {
    return (
      <div className="stock-moves-page">
        <div className="loading">Yükleniyor...</div>
      </div>
    );
  }

  return (
    <div className="stock-moves-page">
      <div className="page-header">
        <div>
          <h1>
            <ArrowRightLeft size={32} />
            Stok Hareketleri
          </h1>
          <p>Stok giriş, çıkış ve transfer işlemleri</p>
        </div>
        <button className="btn-primary" onClick={() => setShowModal(true)}>
          <Plus size={20} />
          Yeni Hareket
        </button>
      </div>

      {/* Filters */}
      <div className="filters-section">
        <div className="filter-group">
          <label>Hareket Tipi</label>
          <div className="filter-buttons">
            <button
              className={`filter-btn ${filterType === 'all' ? 'active' : ''}`}
              onClick={() => setFilterType('all')}
            >
              Tümü
            </button>
            <button
              className={`filter-btn ${filterType === 'in' ? 'active' : ''}`}
              onClick={() => setFilterType('in')}
            >
              <TrendingUp size={16} />
              Giriş
            </button>
            <button
              className={`filter-btn ${filterType === 'out' ? 'active' : ''}`}
              onClick={() => setFilterType('out')}
            >
              <TrendingDown size={16} />
              Çıkış
            </button>
            <button
              className={`filter-btn ${filterType === 'internal' ? 'active' : ''}`}
              onClick={() => setFilterType('internal')}
            >
              <ArrowRightLeft size={16} />
              Transfer
            </button>
          </div>
        </div>

        <div className="filter-group">
          <label>Durum</label>
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
              className={`filter-btn ${filterState === 'confirmed' ? 'active' : ''}`}
              onClick={() => setFilterState('confirmed')}
            >
              Onaylandı
            </button>
            <button
              className={`filter-btn ${filterState === 'done' ? 'active' : ''}`}
              onClick={() => setFilterState('done')}
            >
              Tamamlandı
            </button>
          </div>
        </div>
      </div>

      {/* Moves List */}
      <div className="moves-grid">
        {moves.map(move => (
          <div key={move.id} className={`move-card ${getMoveTypeClass(move.move_type)}`}>
            <div className="move-header">
              <div className="move-name">
                <span className={`move-type-icon ${getMoveTypeClass(move.move_type)}`}>
                  {getMoveTypeIcon(move.move_type)}
                </span>
                {move.name}
              </div>
              <div className={`move-state ${getStateClass(move.state)}`}>
                {getStateLabel(move.state)}
              </div>
            </div>

            <div className="move-product">
              <strong>{move.product.name}</strong>
              <span className="product-code">{move.product.code}</span>
            </div>

            <div className="move-locations">
              <div className="location-box from">
                <span className="location-label">Kaynak</span>
                <span className="location-name">{move.location_from.name}</span>
              </div>
              <div className="location-arrow">→</div>
              <div className="location-box to">
                <span className="location-label">Hedef</span>
                <span className="location-name">{move.location_to.name}</span>
              </div>
            </div>

            <div className="move-details">
              <div className="detail-row">
                <span>Miktar:</span>
                <strong>{move.quantity} Adet</strong>
              </div>
              <div className="detail-row">
                <span>Birim Fiyat:</span>
                <strong>
                  {new Intl.NumberFormat('tr-TR', {
                    style: 'currency',
                    currency: 'TRY'
                  }).format(move.unit_price)}
                </strong>
              </div>
              <div className="detail-row">
                <span>Toplam:</span>
                <strong className="total">
                  {new Intl.NumberFormat('tr-TR', {
                    style: 'currency',
                    currency: 'TRY'
                  }).format(move.total_amount)}
                </strong>
              </div>
            </div>

            {move.reference && (
              <div className="move-reference">
                Referans: {move.reference}
              </div>
            )}

            <div className="move-dates">
              <div>
                <Calendar size={14} />
                Planlandı: {new Date(move.scheduled_date).toLocaleDateString('tr-TR')}
              </div>
              {move.done_date && (
                <div>
                  <Calendar size={14} />
                  Tamamlandı: {new Date(move.done_date).toLocaleDateString('tr-TR')}
                </div>
              )}
            </div>

            {move.state === 'draft' && (
              <div className="move-actions">
                <button
                  className="btn-confirm"
                  onClick={() => handleConfirmMove(move.id)}
                >
                  Onayla
                </button>
              </div>
            )}

            {move.state === 'confirmed' && (
              <div className="move-actions">
                <button
                  className="btn-execute"
                  onClick={() => handleExecuteMove(move.id)}
                >
                  Gerçekleştir
                </button>
              </div>
            )}
          </div>
        ))}
      </div>

      {moves.length === 0 && (
        <div className="empty-state">
          <ArrowRightLeft size={64} />
          <h3>Stok Hareketi Bulunamadı</h3>
          <p>Seçili filtrelere uygun hareket bulunmamaktadır.</p>
        </div>
      )}

      {/* Create Move Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Yeni Stok Hareketi</h2>
              <button className="modal-close" onClick={() => setShowModal(false)}>×</button>
            </div>

            <div className="modal-body">
              <div className="form-group">
                <label>Ürün *</label>
                <select
                  value={newMove.product_id}
                  onChange={(e) => {
                    const productId = parseInt(e.target.value);
                    const product = products.find(p => p.id === productId);
                    setNewMove({
                      ...newMove,
                      product_id: productId,
                      unit_price: product ? (product as any).cost_price || 0 : 0
                    });
                  }}
                >
                  <option value={0}>Ürün seçin...</option>
                  {products.map(p => (
                    <option key={p.id} value={p.id}>
                      {p.code} - {p.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Hareket Tipi *</label>
                <select
                  value={newMove.move_type}
                  onChange={(e) => setNewMove({ ...newMove, move_type: e.target.value as any })}
                >
                  <option value="in">Giriş (Tedarikçi → Depo)</option>
                  <option value="out">Çıkış (Depo → Müşteri)</option>
                  <option value="internal">İç Transfer (Depo → Depo)</option>
                </select>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Kaynak Lokasyon *</label>
                  <select
                    value={newMove.location_from_id}
                    onChange={(e) => setNewMove({ ...newMove, location_from_id: parseInt(e.target.value) })}
                  >
                    <option value={0}>Lokasyon seçin...</option>
                    {locations.map(loc => (
                      <option key={loc.id} value={loc.id}>
                        {loc.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>Hedef Lokasyon *</label>
                  <select
                    value={newMove.location_to_id}
                    onChange={(e) => setNewMove({ ...newMove, location_to_id: parseInt(e.target.value) })}
                  >
                    <option value={0}>Lokasyon seçin...</option>
                    {locations.map(loc => (
                      <option key={loc.id} value={loc.id}>
                        {loc.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Miktar *</label>
                  <input
                    type="number"
                    min="0.01"
                    step="0.01"
                    value={newMove.quantity}
                    onChange={(e) => setNewMove({ ...newMove, quantity: parseFloat(e.target.value) })}
                  />
                </div>

                <div className="form-group">
                  <label>Birim Fiyat *</label>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    value={newMove.unit_price}
                    onChange={(e) => setNewMove({ ...newMove, unit_price: parseFloat(e.target.value) })}
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Planlanan Tarih *</label>
                <input
                  type="date"
                  value={newMove.scheduled_date}
                  onChange={(e) => setNewMove({ ...newMove, scheduled_date: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label>Referans (Opsiyonel)</label>
                <input
                  type="text"
                  placeholder="Sipariş no, fatura no vb."
                  value={newMove.reference || ''}
                  onChange={(e) => setNewMove({ ...newMove, reference: e.target.value })}
                />
              </div>

              <div className="total-preview">
                <span>Toplam Tutar:</span>
                <strong>
                  {new Intl.NumberFormat('tr-TR', {
                    style: 'currency',
                    currency: 'TRY'
                  }).format(newMove.quantity * newMove.unit_price)}
                </strong>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn-secondary" onClick={() => setShowModal(false)}>
                İptal
              </button>
              <button className="btn-primary" onClick={handleCreateMove}>
                Oluştur
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StockMoves;
