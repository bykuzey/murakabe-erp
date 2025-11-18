import { useRef } from 'react';
import { X, Printer } from 'lucide-react';
import './Receipt.css';

interface ReceiptProps {
  order: any;
  config: any;
  onClose: () => void;
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY'
  }).format(amount);
};

const formatDateTime = (date: string) => {
  return new Date(date).toLocaleString('tr-TR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

export default function Receipt({ order, config, onClose }: ReceiptProps) {
  const receiptRef = useRef<HTMLDivElement>(null);

  const handlePrint = () => {
    const printContent = receiptRef.current;
    if (!printContent) return;

    const printWindow = window.open('', '', 'height=600,width=400');
    if (!printWindow) return;

    printWindow.document.write(`
      <html>
        <head>
          <title>Fiş #${order.name}</title>
          <style>
            * {
              margin: 0;
              padding: 0;
              box-sizing: border-box;
            }
            body {
              font-family: 'Courier New', monospace;
              font-size: 12px;
              line-height: 1.4;
              padding: 10px;
              background: white;
            }
            .receipt {
              max-width: 300px;
              margin: 0 auto;
            }
            .header {
              text-align: center;
              border-bottom: 2px dashed #000;
              padding-bottom: 10px;
              margin-bottom: 10px;
            }
            .company-name {
              font-size: 16px;
              font-weight: bold;
              margin-bottom: 5px;
            }
            .company-info {
              font-size: 10px;
              margin: 2px 0;
            }
            .receipt-header {
              font-size: 10px;
              margin: 5px 0;
            }
            .items {
              border-bottom: 2px dashed #000;
              padding: 10px 0;
            }
            .item {
              margin: 5px 0;
            }
            .item-name {
              font-weight: bold;
            }
            .item-details {
              display: flex;
              justify-content: space-between;
              font-size: 10px;
            }
            .totals {
              padding: 10px 0;
              border-bottom: 2px dashed #000;
            }
            .total-row {
              display: flex;
              justify-content: space-between;
              margin: 3px 0;
            }
            .total-row.grand {
              font-size: 14px;
              font-weight: bold;
              margin-top: 5px;
              padding-top: 5px;
              border-top: 1px solid #000;
            }
            .payment {
              padding: 10px 0;
              font-size: 10px;
            }
            .footer {
              text-align: center;
              padding-top: 10px;
              font-size: 10px;
              white-space: pre-line;
            }
            @media print {
              body { padding: 0; }
              .no-print { display: none; }
            }
          </style>
        </head>
        <body>
          ${printContent.innerHTML}
        </body>
      </html>
    `);

    printWindow.document.close();
    printWindow.focus();

    setTimeout(() => {
      printWindow.print();
      printWindow.close();
    }, 250);
  };

  return (
    <div className="receipt-modal-overlay" onClick={onClose}>
      <div className="receipt-modal" onClick={(e) => e.stopPropagation()}>
        <div className="receipt-modal-header">
          <h2>Satış Fişi</h2>
          <div className="receipt-modal-actions">
            <button className="receipt-print-btn" onClick={handlePrint}>
              <Printer size={20} />
              Yazdır
            </button>
            <button className="receipt-close-btn" onClick={onClose}>
              <X size={20} />
            </button>
          </div>
        </div>

        <div className="receipt-container">
          <div ref={receiptRef} className="receipt">
            {/* Header */}
            <div className="header">
              <div className="company-name">{config?.company_name || 'MURAKABE MARKET'}</div>
              {config?.company_address && (
                <div className="company-info">{config.company_address}</div>
              )}
              {config?.company_phone && (
                <div className="company-info">Tel: {config.company_phone}</div>
              )}
              {config?.company_vat && (
                <div className="company-info">VKN: {config.company_vat}</div>
              )}
              {config?.receipt_header && (
                <div className="company-info" style={{ marginTop: '5px' }}>
                  {config.receipt_header}
                </div>
              )}
            </div>

            {/* Receipt Info */}
            <div className="receipt-header">
              <div>Fiş No: {order.name}</div>
              <div>Tarih: {formatDateTime(order.date_order)}</div>
              {order.customer_name && (
                <div>Müşteri: {order.customer_name}</div>
              )}
            </div>

            {/* Items */}
            <div className="items">
              {order.lines?.map((line: any, index: number) => (
                <div key={index} className="item">
                  <div className="item-name">{line.product_name}</div>
                  <div className="item-details">
                    <span>
                      {line.qty} x {formatCurrency(line.price_unit)}
                      {line.discount > 0 && ` (-%${line.discount})`}
                    </span>
                    <span>{formatCurrency(line.price_subtotal_incl)}</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Totals */}
            <div className="totals">
              <div className="total-row">
                <span>Ara Toplam:</span>
                <span>{formatCurrency(order.amount_total - order.amount_tax)}</span>
              </div>
              <div className="total-row">
                <span>KDV:</span>
                <span>{formatCurrency(order.amount_tax)}</span>
              </div>
              <div className="total-row grand">
                <span>TOPLAM:</span>
                <span>{formatCurrency(order.amount_total)}</span>
              </div>
            </div>

            {/* Payment */}
            {order.payments && order.payments.length > 0 && (
              <div className="payment">
                {order.payments.map((payment: any, index: number) => (
                  <div key={index} className="total-row">
                    <span>{payment.payment_method_name}:</span>
                    <span>{formatCurrency(payment.amount)}</span>
                  </div>
                ))}
                {order.amount_return > 0 && (
                  <div className="total-row">
                    <span>Para Üstü:</span>
                    <span>{formatCurrency(order.amount_return)}</span>
                  </div>
                )}
              </div>
            )}

            {/* Footer */}
            <div className="footer">
              {config?.receipt_footer || 'Tekrar Bekleriz\nwww.murakabe.com'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
