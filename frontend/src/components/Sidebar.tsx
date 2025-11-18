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
  CreditCard,
  Menu,
  X,
  ChevronDown,
  TrendingUp,
  Warehouse,
  DollarSign,
  Receipt,
  BarChart3
} from 'lucide-react';
import { useState, useEffect } from 'react';
import styles from './Sidebar.module.css';

interface MenuItem {
  icon: any;
  label: string;
  path: string;
  badge?: string;
}

interface MenuCategory {
  id: string;
  label: string;
  icon: any;
  items: MenuItem[];
}

const menuCategories: MenuCategory[] = [
  {
    id: 'overview',
    label: 'Genel Bakış',
    icon: LayoutDashboard,
    items: [
      { icon: LayoutDashboard, label: 'Dashboard', path: '/' },
      { icon: Bot, label: 'AI Raporları', path: '/ai-reports' },
    ],
  },
  {
    id: 'sales',
    label: 'Satış & Müşteri',
    icon: ShoppingCart,
    items: [
      { icon: CreditCard, label: 'POS Satış', path: '/pos' },
      { icon: ShoppingCart, label: 'Satış Siparişleri', path: '/sales' },
      { icon: Users, label: 'Müşteriler', path: '/customers' },
    ],
  },
  {
    id: 'inventory',
    label: 'Stok & Envanter',
    icon: Package,
    items: [
      { icon: Package, label: 'Ürünler', path: '/inventory' },
      { icon: Warehouse, label: 'Stok Hareketleri', path: '/inventory/moves' },
    ],
  },
  {
    id: 'accounting',
    label: 'Finans & Muhasebe',
    icon: DollarSign,
    items: [
      { icon: FileText, label: 'Muhasebe', path: '/accounting' },
      { icon: Receipt, label: 'Faturalar', path: '/accounting/invoices' },
      { icon: BarChart3, label: 'Raporlar', path: '/accounting/reports' },
    ],
  },
  {
    id: 'system',
    label: 'Sistem',
    icon: Settings,
    items: [
      { icon: Settings, label: 'Ayarlar', path: '/settings' },
    ],
  },
];

export default function Sidebar() {
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(
    new Set(['overview'])
  );

  // Check if path matches any item in category
  const isCategoryActive = (category: MenuCategory) => {
    return category.items.some(item => {
      if (item.path === '/') {
        return location.pathname === '/';
      }
      return location.pathname.startsWith(item.path);
    });
  };

  // Check if item is active
  const isItemActive = (item: MenuItem) => {
    if (item.path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(item.path);
  };

  const toggleCategory = (categoryId: string) => {
    setExpandedCategories(prev => {
      const newSet = new Set(prev);
      if (newSet.has(categoryId)) {
        newSet.delete(categoryId);
      } else {
        newSet.add(categoryId);
      }
      return newSet;
    });
  };

  // Close mobile menu when route changes
  useEffect(() => {
    setMobileOpen(false);
  }, [location.pathname]);

  // Auto-expand category if it contains active item
  useEffect(() => {
    menuCategories.forEach(category => {
      if (isCategoryActive(category)) {
        setExpandedCategories(prev => new Set(prev).add(category.id));
      }
    });
  }, [location.pathname]);

  return (
    <>
      {/* Mobile Menu Button */}
      <button
        className={styles['mobile-menu-button']}
        onClick={() => setMobileOpen(!mobileOpen)}
        aria-label="Toggle menu"
      >
        {mobileOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Mobile Overlay */}
      {mobileOpen && (
        <div
          className={styles['mobile-overlay']}
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`${styles.sidebar} ${collapsed ? styles.collapsed : ''} ${mobileOpen ? styles.mobileOpen : ''}`}
      >
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
            aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            <ChevronLeft />
          </button>
        </div>

        {/* Menu */}
        <nav className={styles['sidebar-menu']}>
          {menuCategories.map((category) => {
            const CategoryIcon = category.icon;
            const isExpanded = expandedCategories.has(category.id);
            const isActive = isCategoryActive(category);

            return (
              <div key={category.id} className={styles['menu-category']}>
                {/* Category Header */}
                {!collapsed ? (
                  <button
                    className={`${styles['category-header']} ${isActive ? styles.active : ''}`}
                    onClick={() => toggleCategory(category.id)}
                  >
                    <CategoryIcon />
                    <span className={styles['category-label']}>{category.label}</span>
                    <ChevronDown
                      className={`${styles['category-chevron']} ${isExpanded ? styles.expanded : ''}`}
                    />
                  </button>
                ) : (
                  <div className={styles['category-header-collapsed']}>
                    <CategoryIcon />
                  </div>
                )}

                {/* Category Items */}
                {(!collapsed && isExpanded) && (
                  <div className={styles['category-items']}>
                    {category.items.map((item) => {
                      const ItemIcon = item.icon;
                      const itemActive = isItemActive(item);

                      return (
                        <Link
                          key={item.path}
                          to={item.path}
                          className={`${styles['sidebar-menu-item']} ${styles['sub-item']} ${itemActive ? styles.active : ''}`}
                        >
                          <ItemIcon />
                          <span>{item.label}</span>
                          {item.badge && (
                            <span className={styles['menu-badge']}>{item.badge}</span>
                          )}
                        </Link>
                      );
                    })}
                  </div>
                )}

                {/* Collapsed Tooltip Items */}
                {collapsed && (
                  <div className={styles['collapsed-items']}>
                    {category.items.map((item) => {
                      const ItemIcon = item.icon;
                      const itemActive = isItemActive(item);

                      return (
                        <Link
                          key={item.path}
                          to={item.path}
                          className={`${styles['sidebar-menu-item']} ${itemActive ? styles.active : ''}`}
                          title={item.label}
                        >
                          <ItemIcon />
                        </Link>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </nav>
      </aside>
    </>
  );
}
