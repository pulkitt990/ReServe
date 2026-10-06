import React, { useState, useEffect } from 'react';
import { ShieldCheck, Database, Activity, RefreshCw } from 'lucide-react';

export default function AdminDashboard({ listings, loading }) {
  const [stats, setStats] = useState({ total_food_rescued: 0, active_listings: 0, system_health: 'checking' });
  const [statsLoading, setStatsLoading] = useState(true);

  const fetchStats = () => {
    setStatsLoading(true);
    fetch('/api/v1/admin/stats')
      .then(res => res.json())
      .then(data => {
        setStats(data);
        setStatsLoading(false);
      })
      .catch(err => {
        console.error(err);
        setStatsLoading(false);
      });
  };

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6">
      {/* Platform Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-2xl border border-stone-200 p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-emerald-100 rounded-lg"><Activity className="w-5 h-5 text-reserve-primary" /></div>
            <h4 className="font-bold text-stone-600">Total Food Rescued</h4>
          </div>
          <div className="text-3xl font-display font-bold text-reserve-dark">
            {statsLoading ? '...' : stats.total_food_rescued} <span className="text-sm font-sans text-stone-400">meals</span>
          </div>
        </div>
        
        <div className="bg-white rounded-2xl border border-stone-200 p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-amber-100 rounded-lg"><Database className="w-5 h-5 text-amber-600" /></div>
            <h4 className="font-bold text-stone-600">Active Listings</h4>
          </div>
          <div className="text-3xl font-display font-bold text-reserve-dark">
            {statsLoading ? '...' : stats.active_listings}
          </div>
        </div>

        <div className="bg-white rounded-2xl border border-stone-200 p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-blue-100 rounded-lg"><ShieldCheck className="w-5 h-5 text-blue-600" /></div>
            <h4 className="font-bold text-stone-600">System Health</h4>
          </div>
          <div className="text-xl font-bold uppercase tracking-wider text-emerald-600 mt-2">
            {statsLoading ? '...' : stats.system_health}
          </div>
        </div>
      </div>

      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-display text-xl font-bold text-reserve-dark">All Platform Listings</h3>
          <button onClick={fetchStats} className="text-xs flex items-center gap-1 text-stone-500 hover:text-stone-800">
            <RefreshCw className="w-3.5 h-3.5" /> Refresh Stats
          </button>
        </div>

        {loading ? (
          <div className="p-12 text-center bg-white rounded-xl border border-stone-200 text-stone-500 text-sm">
            Loading system data...
          </div>
        ) : (
          <div className="bg-white rounded-xl border border-stone-200 overflow-hidden shadow-sm">
            <table className="w-full text-left text-sm">
              <thead className="bg-stone-50 border-b border-stone-200 text-stone-600">
                <tr>
                  <th className="p-3 font-semibold">ID</th>
                  <th className="p-3 font-semibold">Title</th>
                  <th className="p-3 font-semibold">Meals</th>
                  <th className="p-3 font-semibold">Status</th>
                  <th className="p-3 font-semibold">Donor</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-100">
                {listings.map(l => (
                  <tr key={l.id} className="hover:bg-stone-50">
                    <td className="p-3 font-mono text-xs text-stone-500">{l.id.substring(0, 8)}</td>
                    <td className="p-3 font-bold text-stone-800">{l.title}</td>
                    <td className="p-3 text-reserve-primary font-bold">{l.quantity_meals}</td>
                    <td className="p-3">
                      <span className={`px-2 py-1 text-[10px] uppercase font-bold rounded ${
                        l.status === 'open' ? 'bg-emerald-50 text-emerald-700' : 'bg-stone-100 text-stone-600'
                      }`}>
                        {l.status}
                      </span>
                    </td>
                    <td className="p-3 text-xs text-stone-500 truncate max-w-[120px]">{l.donor_name || l.donor_id.substring(0, 8)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
