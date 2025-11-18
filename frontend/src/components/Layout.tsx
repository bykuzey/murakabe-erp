import type { ReactNode } from 'react';
import Sidebar from './Sidebar';
import Navbar from './Navbar';
import styles from './Layout.module.css';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div className={styles.layout}>
      <Sidebar />
      <div className={styles['layout-main']}>
        <Navbar />
        <main className={styles['layout-content']}>
          {children}
        </main>
      </div>
    </div>
  );
}
