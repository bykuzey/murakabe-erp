import { useEffect, useState } from 'react';
import { AlertTriangle, Activity, RefreshCw } from 'lucide-react';
import { accountingAPI } from '../lib/api';
import './AIReports.css';

interface CashFlowForecast {
  forecast_date: string;
  predicted_inflow: number;
  predicted_outflow: number;
  predicted_balance: number;
  confidence_score?: number | null;
}

interface Anomaly {
  id: number;
  detection_date: string;
  anomaly_type: string;
  severity: string;
  anomaly_score: number;
  description: string;
  is_resolved: boolean;
}

const formatCurrency = (amount: number) =>
  new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
  }).format(amount);

export default function AIReports() {
  const [forecast, setForecast] = useState<CashFlowForecast | null>(null);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [loading, setLoading] = useState(true);
  const [detecting, setDetecting] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [forecastRes, anomaliesRes] = await Promise.all([
        accountingAPI.getCashFlowForecast({ days_ahead: 30 }),
        accountingAPI.getAnomalies({ is_resolved: false }),
      ]);
      setForecast(forecastRes.data);
      setAnomalies(anomaliesRes.data);
    } catch (error) {
      console.error('AI raporları yüklenirken hata:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDetectAnomalies = async () => {
    try {
      setDetecting(true);
      await accountingAPI.detectAnomalies();
      await loadData();
    } catch (error) {
      console.error('Anomali tespiti çalışırken hata:', error);
    } finally {
      setDetecting(false);
    }
  };

  if (loading) {
    return (
      <div className="ai-page">
        <div className="ai-loading">AI raporları yükleniyor...</div>
      </div>
    );
  }

  return (
    <div className="ai-page">
      <div className="ai-header">
        <div>
          <h1>AI Raporları</h1>
          <p>Nakit akışı tahmini ve anomali tespitleri</p>
        </div>
        <button
          className="btn-primary"
          onClick={handleDetectAnomalies}
          disabled={detecting}
        >
          <RefreshCw size={18} />
          {detecting ? 'Analiz yapılıyor...' : 'Anomali Analizi Çalıştır'}
        </button>
      </div>

      <div className="ai-grid">
        {forecast && (
          <div className="ai-card">
            <div className="ai-card-header">
              <Activity size={20} />
              <h2>30 Günlük Nakit Akışı Tahmini</h2>
            </div>
            <div className="ai-card-body">
              <div className="ai-metric">
                <span>Toplam Giriş</span>
                <strong>{formatCurrency(forecast.predicted_inflow)}</strong>
              </div>
              <div className="ai-metric">
                <span>Toplam Çıkış</span>
                <strong>{formatCurrency(forecast.predicted_outflow)}</strong>
              </div>
              <div className="ai-metric">
                <span>Beklenen Net Bakiye</span>
                <strong>{formatCurrency(forecast.predicted_balance)}</strong>
              </div>
            </div>
          </div>
        )}

        <div className="ai-card">
          <div className="ai-card-header">
            <AlertTriangle size={20} />
            <h2>Aktif Anomaliler</h2>
          </div>
          <div className="ai-card-body">
            {anomalies.length === 0 && (
              <p className="ai-empty">Aktif anomali bulunmuyor.</p>
            )}
            {anomalies.length > 0 && (
              <ul className="ai-anomaly-list">
                {anomalies.map((a) => (
                  <li key={a.id} className={`ai-anomaly ai-anomaly-${a.severity.toLowerCase()}`}>
                    <div>
                      <strong>{a.anomaly_type}</strong>
                      <p>{a.description}</p>
                    </div>
                    <span className="ai-score">
                      Skor: {a.anomaly_score.toFixed(2)}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

