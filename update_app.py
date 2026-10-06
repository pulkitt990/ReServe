import re

with open('/Users/pulkit/reserve/frontend/src/App.jsx', 'r') as f:
    content = f.read()

imports_to_add = """
import DonorDashboard from './components/DonorDashboard';
import NGODashboard from './components/NGODashboard';
import AdminDashboard from './components/AdminDashboard';
"""
# Insert after last import
last_import_idx = content.rfind("import ")
next_newline = content.find("\n", last_import_idx)
content = content[:next_newline+1] + imports_to_add + content[next_newline+1:]

main_regex = re.compile(r'<main className="flex-1 max-w-7xl mx-auto w-full p-6 space-y-6">.*?</main>', re.DOTALL)

replacement_main = """<main className="flex-1 max-w-7xl mx-auto w-full p-6 space-y-6">
        {/* System Bar */}
        <div className="bg-white rounded-xl border border-stone-200 p-4 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className={`w-3 h-3 rounded-full ${
              health.status === 'ok' ? 'bg-emerald-500 ring-4 ring-emerald-100' : 'bg-reserve-urgency ring-4 ring-amber-100'
            }`} />
            <div>
              <div className="text-xs font-bold uppercase tracking-wider text-stone-600">
                Cluster Health: <span className="text-reserve-primary">{health.status}</span>
              </div>
              <div className="text-xs text-stone-500">
                PostgreSQL: <span className="font-semibold text-stone-700">{health.database}</span> • Redis: <span className="font-semibold text-stone-700">{health.redis}</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={fetchListings}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-stone-200 hover:bg-stone-50 text-xs font-semibold text-stone-700 transition-colors"
            >
              <RefreshCw className="w-3.5 h-3.5" /> Refresh
            </button>
            {activePersona === 'donor' && (
              <button
                onClick={() => setShowCreateModal(true)}
                className="inline-flex items-center gap-2 px-4 py-1.5 rounded-lg bg-reserve-primary hover:bg-reserve-dark text-white text-xs font-bold shadow-sm transition-all"
              >
                <PlusCircle className="w-4 h-4 text-reserve-urgency" /> Post Surplus Food
              </button>
            )}
          </div>
        </div>

        {/* Dashboards */}
        {activePersona === 'donor' && (
          <DonorDashboard 
            forecasts={forecasts} fetchForecasts={fetchForecasts} setNotification={setNotification} 
            listings={listings.filter(l => l.donor_id === '1')} loading={loading} setShowCreateModal={setShowCreateModal} formatCountdown={formatCountdown} 
          />
        )}
        {activePersona === 'ngo' && (
          <NGODashboard 
            listings={listings} loading={loading} formatCountdown={formatCountdown} 
            handleAutoAllocate={handleAutoAllocate} handleUpdateStatus={handleUpdateStatus} 
          />
        )}
        {activePersona === 'admin' && (
          <AdminDashboard listings={listings} loading={loading} />
        )}
      </main>"""

content = main_regex.sub(replacement_main, content)

with open('/Users/pulkit/reserve/frontend/src/App.jsx', 'w') as f:
    f.write(content)
