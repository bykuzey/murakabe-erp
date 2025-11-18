import { useState, useEffect } from 'react';
import { Users, Plus, Search, Edit, Trash2, Building2, User, Mail, Phone } from 'lucide-react';
import { salesAPI } from '../lib/api';
import './Customers.css';

interface Customer {
  id: number;
  name: string;
  code: string;
  customer_type: 'individual' | 'corporate';
  email: string | null;
  phone: string | null;
  mobile: string | null;
  city: string | null;
  tax_office: string | null;
  tax_number: string | null;
  payment_term: string;
  credit_limit: number;
  is_active: boolean;
  created_at: string;
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY'
  }).format(amount);
};

const paymentTermLabels: { [key: string]: string } = {
  immediate: 'Peşin',
  net15: '15 Gün',
  net30: '30 Gün',
  net60: '60 Gün',
  net90: '90 Gün'
};

export default function Customers() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    loadCustomers();
  }, []);

  const loadCustomers = async () => {
    try {
      setLoading(true);
      const response = await salesAPI.getCustomers();
      setCustomers(response.data);
    } catch (error) {
      console.error('Müşteriler yüklenirken hata:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredCustomers = customers.filter(customer =>
    customer.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    customer.code.toLowerCase().includes(searchQuery.toLowerCase()) ||
    customer.email?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    customer.tax_number?.includes(searchQuery)
  );

  if (loading) {
    return (
      <div className="page-loading">
        <div className="spinner"></div>
        <p>Yükleniyor...</p>
      </div>
    );
  }

  return (
    <div className="customers-page">
      <div className="page-header">
        <div className="header-title">
          <Users size={32} />
          <div>
            <h1>Müşteriler</h1>
            <p>{customers.length} müşteri kayıtlı</p>
          </div>
        </div>
        <button className="btn-primary" onClick={() => setShowForm(true)}>
          <Plus size={20} />
          Yeni Müşteri
        </button>
      </div>

      <div className="page-content">
        {/* Arama */}
        <div className="search-bar">
          <Search size={20} />
          <input
            type="text"
            placeholder="Müşteri adı, kod, email veya vergi no ile ara..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        {/* Müşteri Listesi */}
        <div className="customers-grid">
          {filteredCustomers.map(customer => (
            <div key={customer.id} className="customer-card">
              <div className="customer-header">
                <div className="customer-icon">
                  {customer.customer_type === 'corporate' ? (
                    <Building2 size={24} />
                  ) : (
                    <User size={24} />
                  )}
                </div>
                <div className="customer-info">
                  <h3>{customer.name}</h3>
                  <span className="customer-code">{customer.code}</span>
                </div>
                <div className="customer-actions">
                  <button className="btn-icon" title="Düzenle">
                    <Edit size={18} />
                  </button>
                  <button className="btn-icon btn-danger" title="Sil">
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>

              <div className="customer-details">
                {customer.email && (
                  <div className="detail-row">
                    <Mail size={16} />
                    <span>{customer.email}</span>
                  </div>
                )}
                {(customer.phone || customer.mobile) && (
                  <div className="detail-row">
                    <Phone size={16} />
                    <span>{customer.mobile || customer.phone}</span>
                  </div>
                )}
                {customer.city && (
                  <div className="detail-row">
                    <span className="detail-label">Şehir:</span>
                    <span>{customer.city}</span>
                  </div>
                )}
                {customer.tax_office && (
                  <div className="detail-row">
                    <span className="detail-label">Vergi D.:</span>
                    <span>{customer.tax_office}</span>
                  </div>
                )}
              </div>

              <div className="customer-footer">
                <div className="footer-item">
                  <span className="label">Vade:</span>
                  <span className="value">{paymentTermLabels[customer.payment_term]}</span>
                </div>
                <div className="footer-item">
                  <span className="label">Limit:</span>
                  <span className="value">{formatCurrency(customer.credit_limit)}</span>
                </div>
                <div className="footer-item">
                  <span className={`badge ${customer.is_active ? 'badge-success' : 'badge-danger'}`}>
                    {customer.is_active ? 'Aktif' : 'Pasif'}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredCustomers.length === 0 && (
          <div className="empty-state">
            <Users size={64} />
            <h3>Müşteri Bulunamadı</h3>
            <p>Arama kriterlerinize uygun müşteri bulunamadı.</p>
          </div>
        )}
      </div>

      {/* Form Modal - Gelecekte eklenecek */}
      {showForm && (
        <div className="modal-overlay" onClick={() => setShowForm(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Yeni Müşteri</h2>
              <button onClick={() => setShowForm(false)}>×</button>
            </div>
            <div className="modal-body">
              <p>Form yakında eklenecek...</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
