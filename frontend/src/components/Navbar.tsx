import { Bell, Search, User, Home, ChevronRight } from 'lucide-react';
import { useLocation, Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import styles from './Navbar.module.css';

// Route to label mapping
const routeLabels: Record<string, string> = {
  '/': 'Dashboard',
  '/pos': 'POS Satış',
  '/pos/history': 'POS Geçmişi',
  '/sales': 'Satış Siparişleri',
  '/inventory': 'Ürünler',
  '/inventory/new': 'Yeni Ürün',
  '/inventory/moves': 'Stok Hareketleri',
  '/customers': 'Müşteriler',
  '/accounting': 'Muhasebe',
  '/accounting/invoices': 'Faturalar',
  '/accounting/reports': 'Raporlar',
  '/ai-reports': 'AI Raporları',
  '/settings': 'Ayarlar',
};

const getBreadcrumbs = (pathname: string): Array<{ path: string; label: string }> => {
  const paths = pathname.split('/').filter(Boolean);
  const breadcrumbs: Array<{ path: string; label: string }> = [{ path: '/', label: 'Ana Sayfa' }];

  let currentPath = '';
  paths.forEach((segment) => {
    currentPath += `/${segment}`;
    const label = routeLabels[currentPath] || segment.charAt(0).toUpperCase() + segment.slice(1);
    breadcrumbs.push({ path: currentPath, label });
  });

  return breadcrumbs;
};

export default function Navbar() {
  const location = useLocation();
  const [searchFocused, setSearchFocused] = useState(false);
  const breadcrumbs = getBreadcrumbs(location.pathname);

  // Keyboard shortcut for search (Ctrl+K / Cmd+K)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[type="text"]') as HTMLInputElement;
        searchInput?.focus();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <header className={styles.navbar}>
      {/* Breadcrumb Navigation */}
      <nav className={styles['navbar-breadcrumb']} aria-label="Breadcrumb">
        <ol className={styles['breadcrumb-list']}>
          {breadcrumbs.map((crumb, index) => (
            <li key={crumb.path} className={styles['breadcrumb-item']}>
              {index < breadcrumbs.length - 1 ? (
                <Link to={crumb.path} className={styles['breadcrumb-link']}>
                  {index === 0 && <Home size={16} />}
                  <span>{crumb.label}</span>
                </Link>
              ) : (
                <span className={styles['breadcrumb-current']}>{crumb.label}</span>
              )}
              {index < breadcrumbs.length - 1 && (
                <ChevronRight size={16} className={styles['breadcrumb-separator']} />
              )}
            </li>
          ))}
        </ol>
      </nav>

      {/* Search */}
      <div className={styles['navbar-search']}>
        <div className={`${styles['search-wrapper']} ${searchFocused ? styles.focused : ''}`}>
          <Search size={18} />
          <input
            type="text"
            placeholder="Ara... (Ctrl+K)"
            onFocus={() => setSearchFocused(true)}
            onBlur={() => setSearchFocused(false)}
          />
        </div>
      </div>

      {/* Right section */}
      <div className={styles['navbar-right']}>
        {/* Notifications */}
        <button className={styles['navbar-notification']} aria-label="Bildirimler">
          <Bell size={20} />
          <span className={styles['notification-badge']}></span>
        </button>

        {/* User menu */}
        <div className={styles['navbar-user']}>
          <div className={styles['navbar-user-info']}>
            <p>Admin Kullanıcı</p>
            <span>admin@minimalerp.com</span>
          </div>
          <button className={styles['navbar-user-avatar']} aria-label="Kullanıcı menüsü">
            <User size={20} />
          </button>
        </div>
      </div>
    </header>
  );
}
