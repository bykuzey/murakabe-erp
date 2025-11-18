import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  ShoppingCart,
  Package,
  Users,
  Settings,
  ChevronLeft,
  Bot,
  CreditCard
} from 'lucide-react';
import { useState } from 'react';
import styles from './Sidebar.module.css';

const menuItems = [
  { icon: LayoutDashboard, label: 'Genel Bakış', path: '/' },
  { icon: CreditCard, label: 'POS Satış', path: '/pos' },
  { icon: Package, label: 'Stok & Ürünler', path: '/inventory' },
  { icon: ShoppingCart, label: 'Satış Siparişleri', path: '/sales' },
  { icon: FileText, label: 'Finans & Muhasebe', path: '/accounting' },
  { icon: Users, label: 'Müşteriler', path: '/customers' },
  { icon: Bot, label: 'AI Raporları', path: '/ai-reports' },
  { icon: Settings, label: 'Ayarlar', path: '/settings' },
];

export default function Sidebar() {
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside className={`${styles.sidebar} ${collapsed ? styles.collapsed : ''}`}>
      {/* Logo */}
      <div className={styles['sidebar-logo']}>
        {!collapsed && (
          <div className={styles['logo-wrapper']}>
            <img
              src="/murakabe_logo_primary.svg"
              alt="Murakabe"
              className={styles['logo-image']}
            />
          </div>
        )}
        {collapsed && (
          <img
            src="/murakabe_icon_orbit.svg"
            alt="M"
            className={styles['logo-icon-small']}
          />
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className={styles['sidebar-toggle']}
        >
          <ChevronLeft />
        </button>
      </div>

      {/* Menu */}
      <nav className={styles['sidebar-menu']}>
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;

          return (
            <Link
              key={item.path}
              to={item.path}
              className={`${styles['sidebar-menu-item']} ${isActive ? styles.active : ''}`}
            >
              <Icon />
              {!collapsed && <span>{item.label}</span>}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
