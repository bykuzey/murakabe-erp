import styles from './Loading.module.css';

interface LoadingProps {
  size?: 'small' | 'medium' | 'large';
  fullScreen?: boolean;
  message?: string;
}

export default function Loading({ size = 'medium', fullScreen = false, message }: LoadingProps) {
  const sizeClass = styles[size];
  
  if (fullScreen) {
    return (
      <div className={styles['loading-fullscreen']}>
        <div className={`${styles.spinner} ${sizeClass}`}></div>
        {message && <p className={styles['loading-message']}>{message}</p>}
      </div>
    );
  }

  return (
    <div className={styles['loading-inline']}>
      <div className={`${styles.spinner} ${sizeClass}`}></div>
      {message && <p className={styles['loading-message']}>{message}</p>}
    </div>
  );
}

