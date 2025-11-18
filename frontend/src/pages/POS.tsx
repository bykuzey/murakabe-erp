import { useState, useRef, useEffect } from 'react';
import { ShoppingCart, Search, Scan, Users, CreditCard, X, Plus, Minus, Loader2 } from 'lucide-react';
import { posAPI } from '../lib/api';
import Receipt from '../components/Receipt';
import './POS.css';

// Türkçe sayıya formatla
const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY'
  }).format(amount);
};

// Interfaces
interface Product {
  id: number;
  name: string;
  barcode: string | null;
  list_price: number;
  tax_rate: number;
  category_id: number | null;
  image_url: string | null;
  color: string;
  qty_available: number;
}

interface Category {
  id: number;
  name: string;
  color: string;
}

interface CartItem {
  product: Product;
  qty: number;
  discount: number;
}

export default function POS() {
  // State
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [cart, setCart] = useState<CartItem[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [showCustomerModal, setShowCustomerModal] = useState(false);
  const [showReceipt, setShowReceipt] = useState(false);
  const [lastOrder, setLastOrder] = useState<any>(null);
  const [customer, setCustomer] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [currentSession, setCurrentSession] = useState<any>(null);
  const [processing, setProcessing] = useState(false);
  const barcodeInputRef = useRef<HTMLInputElement>(null);

  // Load data on mount
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      setLoading(true);

      // Load products and categories
      const [productsRes, categoriesRes] = await Promise.all([
        posAPI.getProducts(),
        posAPI.getCategories()
      ]);

      setProducts(productsRes.data);
      setCategories(categoriesRes.data);

      // Check for open session or create new one
      const sessionsRes = await posAPI.getSessions({ state: 'opened' });
      if (sessionsRes.data.length > 0) {
        setCurrentSession(sessionsRes.data[0]);
      } else {
        // Create new session
        const newSession = await posAPI.createSession({
          user_id: 1,
          user_name: 'Admin Kullanıcı',
          opening_cash: 0,
          notes: 'Otomatik açılan seans'
        });
        setCurrentSession(newSession.data);
      }
    } catch (error) {
      console.error('Veri yüklenirken hata:', error);
      alert('Veriler yüklenirken bir hata oluştu!');
    } finally {
      setLoading(false);
    }
  };

  // Filtered products
  const filteredProducts = products.filter(product => {
    const matchesSearch = product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         product.barcode?.includes(searchQuery);
    const matchesCategory = selectedCategory === null || product.category_id === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  // Sepet hesaplamaları
  const cartSubtotal = cart.reduce((sum, item) => {
    const itemTotal = item.product.list_price * item.qty * (1 - item.discount / 100);
    return sum + itemTotal;
  }, 0);

  const cartTax = cart.reduce((sum, item) => {
    const itemSubtotal = item.product.list_price * item.qty * (1 - item.discount / 100);
    const itemTax = itemSubtotal * (item.product.tax_rate / 100);
    return sum + itemTax;
  }, 0);

  const cartTotal = cartSubtotal + cartTax;

  // Ürün ekle
  const addToCart = (product: Product) => {
    const existingItem = cart.find(item => item.product.id === product.id);

    if (existingItem) {
      setCart(cart.map(item =>
        item.product.id === product.id
          ? { ...item, qty: item.qty + 1 }
          : item
      ));
    } else {
      setCart([...cart, { product, qty: 1, discount: 0 }]);
    }

    // Arama kutusunu temizle
    setSearchQuery('');
    barcodeInputRef.current?.focus();
  };

  // Barkod ile ürün ara ve ekle
  const handleBarcodeSearch = async (barcode: string) => {
    try {
      const response = await posAPI.getProductByBarcode(barcode);
      addToCart(response.data);
    } catch (error) {
      console.error('Ürün bulunamadı:', error);
      alert('Ürün bulunamadı!');
    }
    setSearchQuery('');
  };

  // Enter tuşu ile barkod okuma
  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && searchQuery.length > 5) {
      handleBarcodeSearch(searchQuery);
    }
  };

  // Miktar güncelle
  const updateQty = (productId: number, newQty: number) => {
    if (newQty <= 0) {
      setCart(cart.filter(item => item.product.id !== productId));
    } else {
      setCart(cart.map(item =>
        item.product.id === productId
          ? { ...item, qty: newQty }
          : item
      ));
    }
  };

  // İndirim güncelle
  const updateDiscount = (productId: number, discount: number) => {
    setCart(cart.map(item =>
      item.product.id === productId
        ? { ...item, discount: Math.min(100, Math.max(0, discount)) }
        : item
    ));
  };

  // Sepeti temizle
  const clearCart = () => {
    if (confirm('Sepeti temizlemek istediğinize emin misiniz?')) {
      setCart([]);
      setCustomer(null);
    }
  };

  // Ödeme tamamla
  const completePayment = async (paymentData: any) => {
    if (!currentSession) {
      alert('Aktif bir seans bulunamadı!');
      return;
    }

    try {
      setProcessing(true);

      // Sipariş verilerini hazırla
      const orderData = {
        session_id: currentSession.id,
        customer_id: customer?.id,
        customer_name: customer?.name,
        customer_phone: customer?.phone,
        customer_tax_id: customer?.tax_id,
        lines: cart.map(item => ({
          product_id: item.product.id,
          product_name: item.product.name,
          product_barcode: item.product.barcode || undefined,
          qty: item.qty,
          price_unit: item.product.list_price,
          discount: item.discount,
          tax_rate: item.product.tax_rate
        })),
        payments: paymentData.payments,
        note: paymentData.note
      };

      // Siparişi oluştur
      const createdOrder = await posAPI.createOrder(orderData);

      // Başarılı - sepeti temizle
      setCart([]);
      setCustomer(null);
      setShowPaymentModal(false);

      // Fişi göster
      setLastOrder(createdOrder);
      setShowReceipt(true);

    } catch (error) {
      console.error('Ödeme hatası:', error);
      alert('Ödeme işlemi sırasında bir hata oluştu!');
    } finally {
      setProcessing(false);
    }
  };

  if (loading) {
    return (
      <div className="pos-loading">
        <Loader2 className="animate-spin" size={48} />
        <p>Yükleniyor...</p>
      </div>
    );
  }

  return (
    <div className="pos-container">
      {/* Sol Panel - Ürünler */}
      <div className="pos-products-panel">
        {/* Arama ve Barkod */}
        <div className="pos-search-bar">
          <div className="pos-search-input-wrapper">
            <Search className="pos-search-icon" size={20} />
            <input
              ref={barcodeInputRef}
              type="text"
              placeholder="Barkod okutun veya ürün arayın..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              className="pos-search-input"
              autoFocus
            />
            <Scan className="pos-barcode-icon" size={20} />
          </div>
        </div>

        {/* Kategoriler */}
        <div className="pos-categories">
          <button
            className={`pos-category-btn ${selectedCategory === null ? 'active' : ''}`}
            onClick={() => setSelectedCategory(null)}
          >
            Tümü
          </button>
          {categories.map(category => (
            <button
              key={category.id}
              className={`pos-category-btn ${selectedCategory === category.id ? 'active' : ''}`}
              onClick={() => setSelectedCategory(category.id)}
            >
              {category.name}
            </button>
          ))}
        </div>

        {/* Ürün Grid */}
        <div className="pos-products-grid">
          {filteredProducts.map(product => (
            <button
              key={product.id}
              className="pos-product-card"
              onClick={() => addToCart(product)}
              style={{ borderColor: product.color }}
            >
              <div className="pos-product-image" style={{ backgroundColor: product.color + '20' }}>
                {product.image_url ? (
                  <img src={product.image_url} alt={product.name} />
                ) : (
                  <div className="pos-product-placeholder">
                    <ShoppingCart size={24} style={{ color: product.color }} />
                  </div>
                )}
              </div>
              <div className="pos-product-info">
                <div className="pos-product-name">{product.name}</div>
                <div className="pos-product-price" style={{ color: product.color }}>
                  {formatCurrency(product.list_price)}
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Sağ Panel - Sepet */}
      <div className="pos-cart-panel">
        {/* Başlık */}
        <div className="pos-cart-header">
          <div className="pos-cart-title">
            <ShoppingCart size={24} />
            <span>Sepet ({cart.length})</span>
          </div>
          {cart.length > 0 && (
            <button className="pos-clear-cart-btn" onClick={clearCart}>
              <X size={20} />
              Temizle
            </button>
          )}
        </div>

        {/* Müşteri Bilgisi */}
        <div className="pos-customer-section">
          <button
            className="pos-customer-btn"
            onClick={() => setShowCustomerModal(true)}
          >
            <Users size={20} />
            <span>
              {customer ? customer.name : 'Müşteri Seç (Opsiyonel)'}
            </span>
          </button>
        </div>

        {/* Sepet İçeriği */}
        <div className="pos-cart-items">
          {cart.length === 0 ? (
            <div className="pos-empty-cart">
              <ShoppingCart size={48} />
              <p>Sepet boş</p>
              <span>Ürün eklemek için tıklayın</span>
            </div>
          ) : (
            cart.map((item) => (
              <div key={item.product.id} className="pos-cart-item">
                <div className="pos-cart-item-header">
                  <div className="pos-cart-item-name">{item.product.name}</div>
                  <button
                    className="pos-cart-item-remove"
                    onClick={() => updateQty(item.product.id, 0)}
                  >
                    <X size={16} />
                  </button>
                </div>

                <div className="pos-cart-item-details">
                  <div className="pos-cart-item-qty">
                    <button
                      className="pos-qty-btn"
                      onClick={() => updateQty(item.product.id, item.qty - 1)}
                    >
                      <Minus size={16} />
                    </button>
                    <input
                      type="number"
                      value={item.qty}
                      onChange={(e) => updateQty(item.product.id, parseFloat(e.target.value) || 0)}
                      className="pos-qty-input"
                      min="0"
                      step="0.01"
                    />
                    <button
                      className="pos-qty-btn"
                      onClick={() => updateQty(item.product.id, item.qty + 1)}
                    >
                      <Plus size={16} />
                    </button>
                  </div>

                  <div className="pos-cart-item-price">
                    {formatCurrency(item.product.list_price)}
                  </div>
                </div>

                {/* İndirim */}
                <div className="pos-cart-item-discount">
                  <label>İndirim %</label>
                  <input
                    type="number"
                    value={item.discount}
                    onChange={(e) => updateDiscount(item.product.id, parseFloat(e.target.value) || 0)}
                    className="pos-discount-input"
                    min="0"
                    max="100"
                  />
                </div>

                <div className="pos-cart-item-total">
                  Ara Toplam: {formatCurrency(item.product.list_price * item.qty * (1 - item.discount / 100))}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Toplam */}
        <div className="pos-cart-summary">
          <div className="pos-summary-row">
            <span>Ara Toplam</span>
            <span>{formatCurrency(cartSubtotal)}</span>
          </div>
          <div className="pos-summary-row">
            <span>KDV</span>
            <span>{formatCurrency(cartTax)}</span>
          </div>
          <div className="pos-summary-row pos-summary-total">
            <span>TOPLAM</span>
            <span>{formatCurrency(cartTotal)}</span>
          </div>
        </div>

        {/* Ödeme Butonu */}
        <button
          className="pos-payment-btn"
          disabled={cart.length === 0 || processing}
          onClick={() => setShowPaymentModal(true)}
        >
          {processing ? (
            <>
              <Loader2 className="animate-spin" size={24} />
              <span>İşleniyor...</span>
            </>
          ) : (
            <>
              <CreditCard size={24} />
              <span>Ödeme Al ({formatCurrency(cartTotal)})</span>
            </>
          )}
        </button>
      </div>

      {/* Ödeme Modal */}
      {showPaymentModal && (
        <PaymentModal
          total={cartTotal}
          onClose={() => setShowPaymentModal(false)}
          onComplete={completePayment}
        />
      )}

      {/* Receipt Modal */}
      {showReceipt && lastOrder && (
        <Receipt
          order={lastOrder}
          config={{
            company_name: 'MURAKABE MARKET',
            company_address: 'Örnek Mahallesi, Ticaret Cad. No:123, İstanbul',
            company_phone: '0212 555 0123',
            company_vat: '1234567890',
            receipt_header: 'Her Zaman Yanınızda',
            receipt_footer: 'Tekrar Bekleriz\nwww.murakabe.com'
          }}
          onClose={() => setShowReceipt(false)}
        />
      )}

      {/* Müşteri Modal */}
      {showCustomerModal && (
        <div className="pos-modal-overlay" onClick={() => setShowCustomerModal(false)}>
          <div className="pos-modal" onClick={(e) => e.stopPropagation()}>
            <div className="pos-modal-header">
              <h2>Müşteri Seç</h2>
              <button onClick={() => setShowCustomerModal(false)}>
                <X size={24} />
              </button>
            </div>
            <div className="pos-modal-body">
              <p>Müşteri seçim ekranı geliştiriliyor...</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Payment Modal Component
function PaymentModal({ total, onClose, onComplete }: any) {
  const [paymentMethod, setPaymentMethod] = useState('cash');
  const [cashAmount, setCashAmount] = useState(total);
  const [note, setNote] = useState('');

  const change = Math.max(0, cashAmount - total);

  const handleSubmit = () => {
    const paymentData = {
      payments: [
        {
          payment_method: paymentMethod,
          payment_method_name: paymentMethod === 'cash' ? 'Nakit' : 'Kredi Kartı',
          amount: cashAmount
        }
      ],
      note
    };

    onComplete(paymentData);
  };

  return (
    <div className="pos-modal-overlay" onClick={onClose}>
      <div className="pos-modal pos-payment-modal" onClick={(e) => e.stopPropagation()}>
        <div className="pos-modal-header">
          <h2>Ödeme</h2>
          <button onClick={onClose}>
            <X size={24} />
          </button>
        </div>
        <div className="pos-modal-body">
          <div className="payment-total">
            <span>Ödenecek Tutar</span>
            <strong>{formatCurrency(total)}</strong>
          </div>

          <div className="payment-methods">
            <button
              className={`payment-method-btn ${paymentMethod === 'cash' ? 'active' : ''}`}
              onClick={() => setPaymentMethod('cash')}
            >
              💵 Nakit
            </button>
            <button
              className={`payment-method-btn ${paymentMethod === 'card' ? 'active' : ''}`}
              onClick={() => setPaymentMethod('card')}
            >
              💳 Kart
            </button>
          </div>

          {paymentMethod === 'cash' && (
            <div className="cash-input-section">
              <label>Alınan Tutar</label>
              <input
                type="number"
                value={cashAmount}
                onChange={(e) => setCashAmount(parseFloat(e.target.value) || 0)}
                className="cash-input"
                min={total}
                step="0.01"
                autoFocus
              />
              <div className="change-amount">
                <span>Para Üstü:</span>
                <strong>{formatCurrency(change)}</strong>
              </div>
            </div>
          )}

          <div className="payment-note">
            <label>Not (Opsiyonel)</label>
            <textarea
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder="Sipariş notu..."
              rows={3}
            />
          </div>

          <button
            className="payment-complete-btn"
            onClick={handleSubmit}
            disabled={cashAmount < total}
          >
            ✓ Ödemeyi Tamamla
          </button>
        </div>
      </div>
    </div>
  );
}

