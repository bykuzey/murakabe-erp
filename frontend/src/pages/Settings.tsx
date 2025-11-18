import { useEffect, useState } from 'react';
import { systemAPI } from '../lib/api';
import './Settings.css';

interface HealthResponse {
  status: string;
  version: string;
  environment: string;
}

export default function Settings() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    loadHealth();
  }, []);

  const loadHealth = async () => {
    try {
      const res = await systemAPI.getHealth();
      setHealth(res.data);
    } catch (error) {
      console.error('Health yüklenirken hata:', error);
    }
  };

  const handleAccountingSetup = async () => {
    try {
      setBusy(true);
      setMessage(null);
      const [companyRes, chartRes] = await Promise.all([
        systemAPI.ensureDefaultCompany(),
        systemAPI.seedChartOfAccounts(),
      ]);
      setMessage(
        `Şirket: ${companyRes.data.name} (ID: ${companyRes.data.id}) · Yeni hesap sayısı: ${chartRes.data.created}`
      );
    } catch (error) {
      console.error('Muhasebe kurulumu sırasında hata:', error);
      setMessage('Muhasebe kurulumu başarısız oldu.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="settings-page">
      <div className="settings-header">
        <div>
          <h1>Ayarlar</h1>
          <p>Sistem bilgileri ve muhasebe kurulumu</p>
        </div>
      </div>

      {health && (
        <div className="settings-card">
          <h2>Sistem Durumu</h2>
          <div className="settings-row">
            <span>Durum:</span>
            <strong>{health.status}</strong>
          </div>
          <div className="settings-row">
            <span>Versiyon:</span>
            <strong>{health.version}</strong>
          </div>
          <div className="settings-row">
            <span>Ortam:</span>
            <strong>{health.environment}</strong>
          </div>
        </div>
      )}

      <div className="settings-card">
        <h2>Muhasebe Hızlı Kurulum</h2>
        <p className="settings-description">
          Tek tıkla varsayılan şirketi oluşturur ve Türk Tekdüzen Hesap Planı için temel
          hesapları ekler. Fatura ekranının dolu çalışması için önerilir.
        </p>
        <button
          className="btn-primary"
          onClick={handleAccountingSetup}
          disabled={busy}
        >
          {busy ? 'Kurulum yapılıyor...' : 'Muhasebe Kurulumu Yap'}
        </button>
        {message && <p className="settings-message">{message}</p>}
      </div>
    </div>
  );
}
