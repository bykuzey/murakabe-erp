import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Plus, Search, Package, AlertTriangle } from 'lucide-react';
import './Products.css';

interface ProductCategory {
  id: number;
  name: string;
  code: string;
}

interface Product {
  id: number;
  name: string;
  code: string;
  barcode?: string;
  category?: ProductCategory;
  product_type: 'storable' | 'consumable' | 'service';
  list_price: number;
  cost_price: number;
  qty_available: number;
  virtual_available: number;
  min_qty: number;
  reorder_point: number;
  uom: string;
  is_below_reorder_point: boolean;
}

interface DashboardStats {
  total_products: number;
  low_stock_count: number;
  total_value: number;
  moves_by_state: {
    draft: number;
    confirmed: number;
    done: number;
    cancelled: number;
  };
  low_stock_alerts: Array<{
    product_id: number;
    product_name: string;
    qty_available: number;
    reorder_point: number;
    shortage: number;
  }>;
}

const Products: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<ProductCategory[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [showLowStock, setShowLowStock] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [highlightedProductId, setHighlightedProductId] = useState<number | null>(null);

  useEffect(() => {
    const state = location.state as { productCreated?: boolean; createdProductId?: number } | null;
    if (state?.productCreated) {
      setSuccessMessage('Ürün başarıyla oluşturuldu.');
      if (state.createdProductId) {
        setHighlightedProductId(state.createdProductId);
      }
      navigate(location.pathname, { replace: true });
    }
  }, [location.state, location.pathname, navigate]);

  useEffect(() => {
    if (!successMessage) {
      return;
    }

    const timeoutId = window.setTimeout(() => setSuccessMessage(null), 5000);
    return () => window.clearTimeout(timeoutId);
  }, [successMessage]);

  useEffect(() => {
    if (highlightedProductId === null) {
      return;
    }

    const timeoutId = window.setTimeout(() => setHighlightedProductId(null), 6000);
    return () => window.clearTimeout(timeoutId);
  }, [highlightedProductId]);

  useEffect(() => {
    loadData();
  }, [selectedCategory, showLowStock]);

  const loadData = async () => {
    try {
      setLoading(true);

      // Stats
      const statsRes = await fetch('http://localhost:5252/api/inventory/stats/dashboard');
      const statsData = await statsRes.json();
      setStats(statsData);

      // Categories
      const catRes = await fetch('http://localhost:5252/api/inventory/categories');
      const catData = await catRes.json();
      setCategories(catData);

      // Products
      let url = 'http://localhost:5252/api/inventory/products?';
      if (searchTerm) url += `search=${searchTerm}&`;
      if (selectedCategory) url += `category_id=${selectedCategory}&`;
      if (showLowStock) url += `low_stock=true&`;

      const prodRes = await fetch(url);
      const prodData = await prodRes.json();
      setProducts(prodData);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadData();
  };

  const handleCreateNavigation = () => {
    navigate('/inventory/new');
  };

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      storable: 'Stoklanabilir',
      consumable: 'Sarf Malzemesi',
      service: 'Hizmet'
    };
    return labels[type] || type;
  };

  const getTypeClass = (type: string) => {
    const classes: Record<string, string> = {
      storable: 'type-storable',
      consumable: 'type-consumable',
      service: 'type-service'
    };
    return classes[type] || '';
  };

  if (loading) {
    return (
      <div className="products-page">
        <div className="loading">Yükleniyor...</div>
      </div>
    );
  }

  return (
    <div className="products-page">
      <div className="page-header">
        <div>
          <h1>
            <Package size={32} />
            Ürünler
          </h1>
          <p>Ürün stok yönetimi</p>
        </div>
        <button className="btn-primary" onClick={handleCreateNavigation}>
          <Plus size={20} />
          Yeni Ürün
        </button>
      </div>

      {successMessage && (
        <div className="success-message">
          {successMessage}
        </div>
      )}

      {/* Stats Cards */}
      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon blue">
              <Package size={24} />
            </div>
            <div className="stat-content">
              <div className="stat-label">Toplam Ürün</div>
              <div className="stat-value">{stats.total_products}</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon red">
              <AlertTriangle size={24} />
            </div>
            <div className="stat-content">
              <div className="stat-label">Düşük Stok</div>
              <div className="stat-value">{stats.low_stock_count}</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon green">
              <Package size={24} />
            </div>
            <div className="stat-content">
              <div className="stat-label">Toplam Değer</div>
              <div className="stat-value">
                {new Intl.NumberFormat('tr-TR', {
                  style: 'currency',
                  currency: 'TRY'
                }).format(stats.total_value)}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Low Stock Alerts */}
      {stats && stats.low_stock_alerts.length > 0 && (
        <div className="alert-section">
          <h3>
            <AlertTriangle size={20} />
            Düşük Stok Uyarıları
          </h3>
          <div className="alerts-grid">
            {stats.low_stock_alerts.map(alert => (
              <div key={alert.product_id} className="alert-card">
                <div className="alert-product">{alert.product_name}</div>
                <div className="alert-details">
                  <span>Mevcut: {alert.qty_available}</span>
                  <span>Min: {alert.reorder_point}</span>
                  <span className="shortage">Eksik: {Math.abs(alert.shortage)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="filters-section">
        <form onSubmit={handleSearch} className="search-form">
          <Search size={20} />
          <input
            type="text"
            placeholder="Ürün ara (isim, kod, barkod)..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <button type="submit">Ara</button>
        </form>

        <div className="filter-buttons">
          <button
            className={`filter-btn ${selectedCategory === null ? 'active' : ''}`}
            onClick={() => setSelectedCategory(null)}
          >
            Tüm Kategoriler
          </button>
          {categories.map(cat => (
            <button
              key={cat.id}
              className={`filter-btn ${selectedCategory === cat.id ? 'active' : ''}`}
              onClick={() => setSelectedCategory(cat.id)}
            >
              {cat.name}
            </button>
          ))}
          <button
            className={`filter-btn ${showLowStock ? 'active alert' : ''}`}
            onClick={() => setShowLowStock(!showLowStock)}
          >
            <AlertTriangle size={16} />
            Sadece Düşük Stok
          </button>
        </div>
      </div>

      {/* Products Grid */}
      <div className="products-grid">
        {products.map(product => (
          <div
            key={product.id}
            className={`product-card ${product.is_below_reorder_point ? 'low-stock' : ''} ${highlightedProductId === product.id ? 'highlighted' : ''}`}
          >
            {product.is_below_reorder_point && (
              <div className="low-stock-badge">
                <AlertTriangle size={16} />
                Düşük Stok
              </div>
            )}

            <div className="product-header">
              <div className="product-code">{product.code}</div>
              <div className={`product-type ${getTypeClass(product.product_type)}`}>
                {getTypeLabel(product.product_type)}
              </div>
            </div>

            <h3 className="product-name">{product.name}</h3>

            {product.category && (
              <div className="product-category">{product.category.name}</div>
            )}

            {product.barcode && (
              <div className="product-barcode">Barkod: {product.barcode}</div>
            )}

            <div className="product-prices">
              <div className="price-item">
                <span className="price-label">Alış</span>
                <span className="price-value">
                  {new Intl.NumberFormat('tr-TR', {
                    style: 'currency',
                    currency: 'TRY'
                  }).format(product.cost_price)}
                </span>
              </div>
              <div className="price-item">
                <span className="price-label">Satış</span>
                <span className="price-value">
                  {new Intl.NumberFormat('tr-TR', {
                    style: 'currency',
                    currency: 'TRY'
                  }).format(product.list_price)}
                </span>
              </div>
            </div>

            {product.product_type !== 'service' && (
              <div className="product-stock">
                <div className="stock-row">
                  <span>Fiziksel Stok:</span>
                  <strong className={product.qty_available < product.min_qty ? 'low' : ''}>
                    {product.qty_available} {product.uom}
                  </strong>
                </div>
                <div className="stock-row">
                  <span>Kullanılabilir:</span>
                  <strong>{product.virtual_available} {product.uom}</strong>
                </div>
                <div className="stock-row">
                  <span>Min. Stok:</span>
                  <strong>{product.min_qty} {product.uom}</strong>
                </div>
                <div className="stock-row">
                  <span>Sipariş Noktası:</span>
                  <strong>{product.reorder_point} {product.uom}</strong>
                </div>
              </div>
            )}

            <div className="product-actions">
              <button className="btn-secondary">Düzenle</button>
              <button className="btn-secondary">Stok Hareketi</button>
            </div>
          </div>
        ))}
      </div>

      {products.length === 0 && (
        <div className="empty-state">
          <Package size={64} />
          <h3>Ürün Bulunamadı</h3>
          <p>Seçili filtrelere uygun ürün bulunmamaktadır.</p>
        </div>
      )}

    </div>
  );
};

export default Products;
