/**
 * Murakabe — Single Page Landing (React + Tailwind)
 * Note: Requires tailwind base; replace icons if lucide-react not available.
 */
import React from "react";

export default function MurakabeLanding() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-800">
      <header className="sticky top-0 z-50 bg-white/70 backdrop-blur border-b border-slate-200">
        <div className="mx-auto max-w-6xl px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-[#0B1533] relative">
              <svg viewBox="0 0 64 64" className="absolute inset-0"><ellipse cx="32" cy="34" rx="18" ry="10" stroke="#2E7FF6" strokeWidth="3" fill="none"/><path d="M14 38a18 10 0 0 0 36 0" stroke="#2E7FF6" strokeWidth="3" fill="none"/><circle cx="45.5" cy="24.5" r="3.5" fill="#2E7FF6"/></svg>
            </div>
            <span className="font-bold">murakabe</span>
          </div>
          <a href="#demo" className="rounded-xl bg-blue-600 px-4 py-2 text-white">Demo al</a>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-16">
        <h1 className="text-4xl font-extrabold text-slate-900">İşletmenizin <span className="text-blue-600">akıllı denetimi</span> ve akışı</h1>
        <p className="mt-3 text-lg text-slate-600">Murakabe veriyi tek eksende birleştirir; siparişten tahsilata tüm süreçleri hızlandırır ve kararları netleştirir.</p>
      </main>
    </div>
  );
}
