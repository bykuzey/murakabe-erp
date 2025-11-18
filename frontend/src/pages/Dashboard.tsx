import { TrendingUp, TrendingDown, DollarSign, FileText, Users, Package } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import styles from './Dashboard.module.css';

// Mock data
const cashFlowData = [
  { month: 'Oca', gelir: 45000, gider: 32000 },
  { month: 'Şub', gelir: 52000, gider: 35000 },
  { month: 'Mar', gelir: 48000, gider: 38000 },
  { month: 'Nis', gelir: 61000, gider: 42000 },
  { month: 'May', gelir: 55000, gider: 39000 },
  { month: 'Haz', gelir: 67000, gider: 44000 },
];

const invoiceStatusData = [
  { name: 'Ödendi', value: 45, color: '#10b981' },
  { name: 'Beklemede', value: 30, color: '#f59e0b' },
  { name: 'Gecikmiş', value: 15, color: '#ef4444' },
  { name: 'Taslak', value: 10, color: '#6b7280' },
];

const stats = [
  {
    title: 'Toplam Gelir',
    value: '₺328,000',
    change: '+12.5%',
    trend: 'up',
    icon: DollarSign,
    color: 'bg-green-500',
  },
  {
    title: 'Açık Faturalar',
    value: '₺48,500',
    change: '-8.2%',
    trend: 'down',
    icon: FileText,
    color: 'bg-blue-500',
  },
  {
    title: 'Aktif Müşteriler',
    value: '152',
    change: '+24',
    trend: 'up',
    icon: Users,
    color: 'bg-purple-500',
  },
  {
    title: 'Stok Değeri',
    value: '₺186,200',
    change: '+5.4%',
    trend: 'up',
    icon: Package,
    color: 'bg-orange-500',
  },
];

export default function Dashboard() {
  return (
    <div className={styles.dashboard}>
      {/* Header */}
      <div className={styles['dashboard-header']}>
        <h1>Dashboard</h1>
        <p>İşletmenizin genel durumu</p>
      </div>

      {/* Stats Grid */}
      <div className={styles['stats-grid']}>
        {stats.map((stat) => {
          const Icon = stat.icon;
          const isPositive = stat.trend === 'up';

          return (
            <div key={stat.title} className={styles['stat-card']}>
              <div className={styles['stat-card-content']}>
                <div className={styles['stat-card-info']}>
                  <p className={styles['stat-card-title']}>{stat.title}</p>
                  <p className={styles['stat-card-value']}>{stat.value}</p>
                  <div className={`${styles['stat-card-change']} ${isPositive ? styles.positive : styles.negative}`}>
                    {isPositive ? (
                      <TrendingUp />
                    ) : (
                      <TrendingDown />
                    )}
                    <span>
                      {stat.change}
                    </span>
                  </div>
                </div>
                <div className={`${styles['stat-card-icon']} ${styles[stat.color.replace('bg-', '').replace('-500', '')]}`}>
                  <Icon />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Charts Grid */}
      <div className={styles['charts-grid']}>
        {/* Cash Flow Chart */}
        <div className={styles['chart-card']}>
          <h3>Nakit Akışı (Son 6 Ay)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={cashFlowData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip formatter={(value) => `₺${Number(value).toLocaleString('tr-TR')}`} />
              <Line
                type="monotone"
                dataKey="gelir"
                stroke="#10b981"
                strokeWidth={2}
                name="Gelir"
              />
              <Line
                type="monotone"
                dataKey="gider"
                stroke="#ef4444"
                strokeWidth={2}
                name="Gider"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Invoice Status Pie */}
        <div className={styles['chart-card']}>
          <h3>Fatura Durumu</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={invoiceStatusData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${percent ? (percent * 100).toFixed(0) : 0}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {invoiceStatusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Activity */}
      <div className={styles['activity-card']}>
        <h3>Son Aktiviteler</h3>
        <div className={styles['activity-list']}>
          {[
            { type: 'invoice', desc: 'Yeni fatura oluşturuldu: #INV-2024-001', time: '5 dk önce', status: 'success' },
            { type: 'anomaly', desc: 'AI tarafından anomali tespit edildi', time: '23 dk önce', status: 'warning' },
            { type: 'payment', desc: 'Ödeme alındı: ₺12,500', time: '1 saat önce', status: 'success' },
            { type: 'stock', desc: 'Stok seviyesi düşük: Ürün #P-123', time: '2 saat önce', status: 'error' },
          ].map((activity, i) => (
            <div key={i} className={styles['activity-item']}>
              <div className={`${styles['activity-dot']} ${styles[activity.status]}`} />
              <div className={styles['activity-content']}>
                <p className={styles['activity-desc']}>{activity.desc}</p>
                <p className={styles['activity-time']}>{activity.time}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
