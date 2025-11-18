import { useEffect, useState } from 'react';
import { Plus, Search, Filter } from 'lucide-react';
import { accountingAPI } from '../lib/api';
import styles from './Accounting.module.css';

interface Invoice {
  id: number;
  invoice_number: string;
  invoice_date: string;
  invoice_type: string;
  company_id: number;
  partner_id: number;
  subtotal: number;
  vat_amount: number;
  total_amount: number;
  status: string;
  created_at: string;
}

const statusLabels: Record<string, string> = {
  TASLAK: 'Taslak',
  BEKLEMEDE: 'Beklemede',
  GONDERILDI: 'Gönderildi',
  ONAYLANDI: 'Onaylandı',
  REDDEDILDI: 'Reddedildi',
  IPTAL: 'İptal',
};

export default function Accounting() {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);

  const today = new Date().toISOString().slice(0, 10);
  const [form, setForm] = useState({
    invoice_number: `INV-${today.replace(/-/g, '')}-0001`,
    invoice_date: today,
    invoice_type: 'SATIS',
    partner_id: '',
    description: '',
    quantity: 1,
    unit_price: 0,
    vat_rate: 20,
  });

  useEffect(() => {
    loadInvoices();
  }, []);

  const loadInvoices = async () => {
    try {
      setLoading(true);
      const res = await accountingAPI.getInvoices();
      setInvoices(res.data);
    } catch (error) {
      console.error('Faturalar yüklenirken hata:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredInvoices = invoices.filter(invoice => {
    const matchesSearch =
      invoice.invoice_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      invoice.partner_id.toString().includes(searchTerm);
    const matchesFilter = filterStatus === 'all' || invoice.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  const totalAmount = filteredInvoices.reduce((sum, inv) => sum + inv.total_amount, 0);

  const handleFormChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]:
        name === 'quantity' || name === 'unit_price' || name === 'vat_rate'
          ? Number(value)
          : value,
    }));
  };

  const handleCreateInvoice = async () => {
    if (!form.partner_id) {
      alert('Cari ID (partner_id) zorunludur.');
      return;
    }
    try {
      setSaving(true);
      const payload = {
        invoice_number: form.invoice_number,
        invoice_date: form.invoice_date,
        invoice_type: form.invoice_type,
        company_id: 1,
        partner_id: Number(form.partner_id),
        lines: [
          {
            description: form.description || 'Satış',
            quantity: form.quantity,
            unit_price: form.unit_price,
            vat_rate: form.vat_rate,
            withholding_rate: 0,
          },
        ],
      };
      await accountingAPI.createInvoice(payload);
      setShowForm(false);
      await loadInvoices();
    } catch (error) {
      console.error('Fatura oluşturulurken hata:', error);
      alert('Fatura oluşturulamadı. Lütfen alanları kontrol edin.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className={styles.accounting}>
        <div className={styles['loading']}>Faturalar yükleniyor...</div>
      </div>
    );
  }

  return (
    <div className={styles.accounting}>
      {/* Header */}
      <div className={styles['accounting-header']}>
        <div>
          <h1>Muhasebe</h1>
          <p>Faturalar ve mali işlemler</p>
        </div>
        <div className={styles['header-actions']}>
          <button
            className={styles['btn-primary']}
            onClick={() => setShowForm(true)}
          >
            <Plus />
            <span>Yeni Fatura</span>
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className={styles['stats-row']}>
        <div className={styles['stat-card']}>
          <span className={styles['stat-label']}>Toplam Fatura</span>
          <span className={styles['stat-value']}>{filteredInvoices.length}</span>
        </div>
        <div className={styles['stat-card']}>
          <span className={styles['stat-label']}>Toplam Tutar</span>
          <span className={styles['stat-value']}>₺{totalAmount.toLocaleString('tr-TR')}</span>
        </div>
        <div className={styles['stat-card']}>
          <span className={styles['stat-label']}>Ödenen</span>
          <span className={styles['stat-value']} style={{color: '#10b981'}}>
            {filteredInvoices.filter(i => i.status === 'ONAYLANDI' || i.status === 'GONDERILDI').length}
          </span>
        </div>
        <div className={styles['stat-card']}>
          <span className={styles['stat-label']}>Bekleyen</span>
          <span className={styles['stat-value']} style={{color: '#f59e0b'}}>
            {filteredInvoices.filter(i => i.status === 'TASLAK' || i.status === 'BEKLEMEDE').length}
          </span>
        </div>
      </div>

      {/* Filters and Search */}
      <div className={styles['table-controls']}>
        <div className={styles['search-box']}>
          <Search />
          <input
            type="text"
            placeholder="Fatura no veya cari ID ara..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className={styles['filter-group']}>
          <button className={styles['filter-btn']}>
            <Filter />
            <span>Filtrele</span>
          </button>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className={styles['filter-select']}
          >
            <option value="all">Tüm Durumlar</option>
            <option value="TASLAK">Taslak</option>
            <option value="BEKLEMEDE">Beklemede</option>
            <option value="GONDERILDI">Gönderildi</option>
            <option value="ONAYLANDI">Onaylandı</option>
            <option value="REDDEDILDI">Reddedildi</option>
            <option value="IPTAL">İptal</option>
          </select>
        </div>
      </div>

      {/* Invoices Table */}
      <div className={styles['table-container']}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Fatura No</th>
              <th>Cari ID</th>
              <th>Tarih</th>
              <th>Tutar</th>
              <th>Durum</th>
              <th>İşlemler</th>
            </tr>
          </thead>
          <tbody>
            {filteredInvoices.map((invoice) => (
              <tr key={invoice.id}>
                <td>
                  <span className={styles['invoice-id']}>{invoice.invoice_number}</span>
                </td>
                <td>{invoice.partner_id}</td>
                <td>{new Date(invoice.invoice_date).toLocaleDateString('tr-TR')}</td>
                <td className={styles['amount']}>₺{invoice.total_amount.toLocaleString('tr-TR')}</td>
                <td>
                  <span className={`${styles.badge} ${styles[invoice.status.toLowerCase()] || ''}`}>
                    {statusLabels[invoice.status] || invoice.status}
                  </span>
                </td>
                <td>
                  <div className={styles['action-buttons']}>
                    <button className={styles['action-btn']}>Görüntüle</button>
                    <button className={styles['action-btn']} disabled>
                      Düzenle
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showForm && (
        <div className={styles['modal-backdrop']} onClick={() => !saving && setShowForm(false)}>
          <div className={styles['modal']} onClick={(e) => e.stopPropagation()}>
            <div className={styles['modal-header']}>
              <h2 className={styles['modal-title']}>Yeni Fatura</h2>
              <button
                className={styles['modal-close']}
                onClick={() => !saving && setShowForm(false)}
              >
                ×
              </button>
            </div>
            <div className={styles['modal-body']}>
              <div className={styles['form-row']}>
                <label>Fatura No</label>
                <input
                  name="invoice_number"
                  value={form.invoice_number}
                  onChange={handleFormChange}
                />
              </div>
              <div className={styles['form-row']}>
                <label>Tarih</label>
                <input
                  type="date"
                  name="invoice_date"
                  value={form.invoice_date}
                  onChange={handleFormChange}
                />
              </div>
              <div className={styles['form-row']}>
                <label>Tür</label>
                <select
                  name="invoice_type"
                  value={form.invoice_type}
                  onChange={handleFormChange}
                >
                  <option value="SATIS">Satış</option>
                  <option value="ALIS">Alış</option>
                </select>
              </div>
              <div className={styles['form-row']}>
                <label>Cari ID (partner_id)</label>
                <input
                  name="partner_id"
                  value={form.partner_id}
                  onChange={handleFormChange}
                  placeholder="Örn: 1"
                />
              </div>
              <div className={styles['form-row']}>
                <label>Açıklama</label>
                <input
                  name="description"
                  value={form.description}
                  onChange={handleFormChange}
                  placeholder="Ürün / hizmet açıklaması"
                />
              </div>
              <div className={styles['form-row']}>
                <label>Miktar</label>
                <input
                  type="number"
                  name="quantity"
                  value={form.quantity}
                  onChange={handleFormChange}
                  min={0}
                  step={0.01}
                />
              </div>
              <div className={styles['form-row']}>
                <label>Birim Fiyat</label>
                <input
                  type="number"
                  name="unit_price"
                  value={form.unit_price}
                  onChange={handleFormChange}
                  min={0}
                  step={0.01}
                />
              </div>
              <div className={styles['form-row']}>
                <label>KDV Oranı (%)</label>
                <input
                  type="number"
                  name="vat_rate"
                  value={form.vat_rate}
                  onChange={handleFormChange}
                  min={0}
                  step={1}
                />
              </div>
            </div>
            <div className={styles['modal-footer']}>
              <button
                className={styles['btn-secondary']}
                onClick={() => !saving && setShowForm(false)}
              >
                Vazgeç
              </button>
              <button
                className={styles['btn-primary']}
                onClick={handleCreateInvoice}
                disabled={saving}
              >
                {saving ? 'Kaydediliyor...' : 'Kaydet'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
