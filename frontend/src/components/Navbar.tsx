import { Bell, Search, User } from 'lucide-react';
import styles from './Navbar.module.css';

export default function Navbar() {
  return (
    <header className={styles.navbar}>
      {/* Search */}
      <div className={styles['navbar-search']}>
        <div className={styles['search-wrapper']}>
          <Search />
          <input
            type="text"
            placeholder="Ara... (Ctrl+K)"
          />
        </div>
      </div>

      {/* Right section */}
      <div className={styles['navbar-right']}>
        {/* Notifications */}
        <button className={styles['navbar-notification']}>
          <Bell />
          <span className={styles['notification-badge']}></span>
        </button>

        {/* User menu */}
        <div className={styles['navbar-user']}>
          <div className={styles['navbar-user-info']}>
            <p>Admin Kullanıcı</p>
            <span>admin@minimalerp.com</span>
          </div>
          <button className={styles['navbar-user-avatar']}>
            <User />
          </button>
        </div>
      </div>
    </header>
  );
}
