import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Save } from 'lucide-react';
import './ProductCreate.css';

interface ProductCategory {
  id: number;
  name: string;
  code: string;
}

type ProductType = 'storable' | 'consumable' | 'service';

interface ProductFormData {
  name: string;
  barcode: string;
  description: string;
  category_id: number | '';
  product_type: ProductType;
  list_price: number;
  cost_price: number;
  min_qty: number;
  reorder_point: number;
  uom: string;
  can_be_sold: boolean;
  can_be_purchased: boolean;
  tax_rate: number;
}

const defaultFormData: ProductFormData = {
  name: '',
  barcode: '',
  description: '',
  category_id: '',
  product_type: 'storable',
  list_price: 0,
  cost_price: 0,
  min_qty: 0,
  reorder_point: 0,
  uom: 'Adet',
  can_be_sold: true,
  can_be_purchased: true,
  tax_rate: 20,
};

const ProductCreate: React.FC = () => {
  const navigate = useNavigate();
  const [categories, setCategories] = useState<ProductCategory[]>([]);
  const [formData, setFormData] = useState<ProductFormData>(defaultFormData);
  const [loadingCategories, setLoadingCategories] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await fetch('http://localhost:5252/api/inventory/categories');
        if (!response.ok) {
          throw new Error('Kategoriler alınamadı.');
        }
        const data: ProductCategory[] = await response.json();
        setCategories(data);
      } catch (fetchError) {
        console.error('Kategori listesi yüklenirken hata oluştu:', fetchError);
        setError('Kategori listesi yüklenirken bir hata oluştu.');
      } finally {
        setLoadingCategories(false);
      }
    };

    fetchCategories();
  }, []);

  useEffect(() => {
    if (categories.length === 0) {
      return;
    }

    setFormData((prev) => ({
      ...prev,
      category_id: prev.category_id === '' ? categories[0].id : prev.category_id,
    }));
  }, [categories]);

  const handleInputChange = (field: keyof ProductFormData) => (
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const value = event.target.value;
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleNumberChange = (field: keyof ProductFormData) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const parsedValue = parseFloat(event.target.value);
    setFormData((prev) => ({
      ...prev,
      [field]: Number.isNaN(parsedValue) ? 0 : parsedValue,
    }));
  };

  const handleProductTypeChange = (value: ProductType) => {
    setFormData((prev) => ({
      ...prev,
      product_type: value,
      min_qty: value === 'service' ? 0 : prev.min_qty,
      reorder_point: value === 'service' ? 0 : prev.reorder_point,
    }));
  };

  const handleCategoryChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selected = event.target.value;
    setFormData((prev) => ({
      ...prev,
      category_id: selected ? Number(selected) : '',
    }));
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!formData.name.trim()) {
      setError('Ürün adı zorunludur.');
      return;
    }

    try {
      setSaving(true);
      setError(null);

      const payload: Record<string, any> = {
        name: formData.name.trim(),
        product_type: formData.product_type,
        list_price: Number(formData.list_price) || 0,
        cost_price: Number(formData.cost_price) || 0,
        min_qty: Number(formData.min_qty) || 0,
        reorder_point: Number(formData.reorder_point) || 0,
        uom: formData.uom || 'Adet',
        can_be_sold: formData.can_be_sold,
        can_be_purchased: formData.can_be_purchased,
        tax_rate: Number(formData.tax_rate) || 0,
        is_active: true,
      };

      if (formData.category_id) {
        payload.category_id = formData.category_id;
      }

      if (formData.barcode.trim()) {
        payload.barcode = formData.barcode.trim();
      }

      if (formData.description.trim()) {
        payload.description = formData.description.trim();
      }

      const response = await fetch('http://localhost:5252/api/inventory/products', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        const message = errorData?.detail || 'Ürün oluşturulurken hata oluştu.';
        throw new Error(message);
      }

      let createdProductId: number | undefined;
      try {
        const data = await response.json();
        createdProductId = data?.id;
      } catch (parseError) {
        console.warn('Yanıt verisi okunamadı:', parseError);
      }

      navigate('/inventory', {
        state: {
          productCreated: true,
          createdProductId,
        },
      });
    } catch (submitError: any) {
      console.error('Error creating product:', submitError);
      setError(submitError.message || 'Ürün oluşturulamadı.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="create-product-page">
      <div className="create-product-header">
        <button
          type="button"
          className="back-button"
          onClick={() => navigate(-1)}
          aria-label="Önceki sayfaya dön"
        >
          <ArrowLeft size={18} />
          Geri Dön
        </button>
        <h1>Yeni Ürün</h1>
      </div>

      <div className="create-product-card">
        <form onSubmit={handleSubmit} className="create-product-form">
          {error && <div className="error-message">{error}</div>}

          <section className="form-section">
            <h2>Genel Bilgiler</h2>
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="product-name">Ürün Adı *</label>
                <input
                  id="product-name"
                  type="text"
                  value={formData.name}
                  onChange={handleInputChange('name')}
                  placeholder="Örn. Kablosuz Mouse"
                  autoFocus
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="product-category">Kategori</label>
                <select
                  id="product-category"
                  value={formData.category_id === '' ? '' : formData.category_id}
                  onChange={handleCategoryChange}
                  disabled={loadingCategories}
                >
                  <option value="">Kategori seçin...</option>
                  {categories.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="product-type">Ürün Tipi</label>
                <select
                  id="product-type"
                  value={formData.product_type}
                  onChange={(event) => handleProductTypeChange(event.target.value as ProductType)}
                >
                  <option value="storable">Stoklanabilir</option>
                  <option value="consumable">Sarf Malzemesi</option>
                  <option value="service">Hizmet</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="product-barcode">Barkod</label>
                <input
                  id="product-barcode"
                  type="text"
                  value={formData.barcode}
                  onChange={handleInputChange('barcode')}
                  placeholder="Opsiyonel"
                />
              </div>

              <div className="form-group">
                <label htmlFor="product-uom">Birim</label>
                <input
                  id="product-uom"
                  type="text"
                  value={formData.uom}
                  onChange={handleInputChange('uom')}
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="product-description">Açıklama</label>
              <textarea
                id="product-description"
                value={formData.description}
                onChange={handleInputChange('description')}
                rows={3}
                placeholder="Ürünle ilgili kısa açıklama"
              />
            </div>
          </section>

          <section className="form-section">
            <h2>Fiyatlandırma</h2>
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="list-price">Satış Fiyatı (TRY)</label>
                <input
                  id="list-price"
                  type="number"
                  min="0"
                  step="0.01"
                  value={formData.list_price}
                  onChange={handleNumberChange('list_price')}
                />
              </div>

              <div className="form-group">
                <label htmlFor="cost-price">Maliyet Fiyatı (TRY)</label>
                <input
                  id="cost-price"
                  type="number"
                  min="0"
                  step="0.01"
                  value={formData.cost_price}
                  onChange={handleNumberChange('cost_price')}
                />
              </div>
            </div>
          </section>

          {formData.product_type !== 'service' && (
            <section className="form-section">
              <h2>Stok Bilgileri</h2>
              <div className="form-grid">
                <div className="form-group">
                  <label htmlFor="min-qty">Min. Stok</label>
                  <input
                    id="min-qty"
                    type="number"
                    min="0"
                    step="0.01"
                    value={formData.min_qty}
                    onChange={handleNumberChange('min_qty')}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="reorder-point">Sipariş Noktası</label>
                  <input
                    id="reorder-point"
                    type="number"
                    min="0"
                    step="0.01"
                    value={formData.reorder_point}
                    onChange={handleNumberChange('reorder_point')}
                  />
                </div>
              </div>
            </section>
          )}

          <section className="form-section">
            <h2>Vergi ve Durum</h2>
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="tax-rate">KDV Oranı (%)</label>
                <input
                  id="tax-rate"
                  type="number"
                  min="0"
                  step="0.1"
                  value={formData.tax_rate}
                  onChange={handleNumberChange('tax_rate')}
                />
              </div>
              <div className="form-group checkbox-group">
                <label>Satış Durumları</label>
                <div className="checkbox-row">
                  <label>
                    <input
                      type="checkbox"
                      checked={formData.can_be_sold}
                      onChange={(event) =>
                        setFormData((prev) => ({ ...prev, can_be_sold: event.target.checked }))
                      }
                    />
                    Satılabilir
                  </label>
                  <label>
                    <input
                      type="checkbox"
                      checked={formData.can_be_purchased}
                      onChange={(event) =>
                        setFormData((prev) => ({ ...prev, can_be_purchased: event.target.checked }))
                      }
                    />
                    Satın Alınabilir
                  </label>
                </div>
              </div>
            </div>
          </section>

          <div className="info-box">
            İlk stok girişini yapmak için ürün oluşturduktan sonra
            <strong> Stok Hareketleri </strong>
            sayfasından giriş hareketi oluşturabilirsiniz.
          </div>

          <div className="form-actions">
            <button
              type="button"
              className="btn-secondary"
              onClick={() => navigate('/inventory')}
              disabled={saving}
            >
              İptal
            </button>
            <button type="submit" className="btn-primary" disabled={saving}>
              <Save size={18} />
              {saving ? 'Kaydediliyor...' : 'Ürünü Kaydet'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ProductCreate;
