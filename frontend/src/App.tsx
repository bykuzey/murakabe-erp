import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import POS from './pages/POS';
import Customers from './pages/Customers';
import SalesOrders from './pages/SalesOrders';
import Products from './pages/Products';
import StockMoves from './pages/StockMoves';
import POSHistory from './pages/POSHistory';
import ProductCreate from './pages/ProductCreate';
import Accounting from './pages/Accounting';
import AIReports from './pages/AIReports';
import Settings from './pages/Settings';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/pos" element={<POS />} />
            <Route path="/pos/history" element={<POSHistory />} />
            <Route path="/accounting" element={<Accounting />} />
            <Route path="/sales" element={<SalesOrders />} />
            <Route path="/inventory" element={<Products />} />
            <Route path="/inventory/new" element={<ProductCreate />} />
            <Route path="/inventory/moves" element={<StockMoves />} />
            <Route path="/customers" element={<Customers />} />
            <Route path="/ai-reports" element={<AIReports />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
