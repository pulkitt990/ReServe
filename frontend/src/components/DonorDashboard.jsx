import React from 'react';
import { Sparkles, Utensils, Package, Clock, Building, MapPin } from 'lucide-react';

export default function DonorDashboard({ 
  forecasts, fetchForecasts, setNotification, listings, loading, setShowCreateModal, formatCountdown 
}) {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-2xl border border-emerald-200 p-6 shadow-sm relative overflow-hidden">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-reserve-urgency" />
            <h3 className="font-display text-xl font-bold text-reserve-dark">Predictive Surplus Forecasting</h3>
          </div>
          <button 
            onClick={async () => {
              setNotification("Training model and generating forecast...");
              await fetch((import.meta.env.VITE_API_URL || '') + '/api/v1/forecasting/predict/1?days=7', { method: 'POST' });
              fetchForecasts();
            }}
            className="px-4 py-1.5 bg-emerald-100 hover:bg-emerald-200 text-emerald-800 text-xs font-bold rounded-lg transition-colors border border-emerald-300"
          >
            Generate 7-Day Forecast
          </button>
        </div>
        {forecasts.length === 0 ? (
          <p className="text-sm text-stone-500 italic">No forecast data available. Click generate to train the ML model and predict upcoming surplus.</p>
        ) : (
          <div className="flex overflow-x-auto gap-4 pb-2">
            {forecasts.map(f => {
              const dateObj = new Date(f.forecast_for_date);
              const dayName = dateObj.toLocaleDateString('en-US', { weekday: 'short' });
              const dateNum = dateObj.getDate();
              return (
                <div key={f.id} className="min-w-[120px] bg-stone-50 border border-stone-200 rounded-xl p-3 text-center shadow-sm">
                  <div className="text-xs font-bold text-stone-500 uppercase">{dayName}</div>
                  <div className="text-sm font-semibold text-stone-800 mb-1">{dateNum}</div>
                  <div className="text-2xl font-display font-bold text-reserve-primary">
                    {Math.round(f.predicted_quantity_meals)}
                  </div>
                  <div className="text-[10px] text-stone-400 mt-1">Meals</div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-display text-xl font-bold text-reserve-dark flex items-center gap-2">
            <Utensils className="w-5 h-5 text-reserve-urgency" /> Active Food Listings & History
          </h3>
          <div className="flex items-center gap-4"><span className="text-xs text-stone-500 hidden sm:inline">Sorted by earliest expiry first</span><button onClick={() => setShowCreateModal(true)} className="px-3 py-1.5 bg-reserve-primary hover:bg-reserve-primary/90 text-white text-xs font-bold rounded-lg transition-colors shadow-sm">Create Listing</button></div>
        </div>

        {loading ? (
          <div className="p-12 text-center bg-white rounded-xl border border-stone-200 text-stone-500 text-sm">
            Loading perishability feed...
          </div>
        ) : listings.length === 0 ? (
          <div className="p-12 text-center bg-white rounded-xl border border-dashed border-stone-300 space-y-3">
            <Package className="w-10 h-10 text-stone-400 mx-auto" />
            <p className="text-stone-600 font-semibold text-sm">No food listings currently in database.</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 rounded-lg bg-reserve-primary text-white text-xs font-bold"
            >
              Create First Listing
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {listings.map((item) => {
              const countdown = formatCountdown(item.minutes_to_expiry);
              const isUrgent = countdown.urgent && item.status === 'open';

              return (
                <div 
                  key={item.id}
                  className={`bg-white rounded-xl border transition-all duration-200 flex flex-col justify-between shadow-sm hover:shadow-md ${
                    isUrgent ? 'border-amber-400 ring-2 ring-amber-100' : 'border-stone-200'
                  }`}
                >
                  <div className="p-5 space-y-3">
                    <div className="flex items-center justify-between gap-2">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-bold uppercase tracking-wider ${
                        item.status === 'open' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                        : item.status === 'allocated' ? 'bg-amber-50 text-amber-800 border border-amber-200'
                        : item.status === 'picked_up' ? 'bg-blue-50 text-blue-800 border border-blue-200'
                        : 'bg-stone-100 text-stone-500 border border-stone-200'
                      }`}>
                        {item.status.replace('_', ' ')}
                      </span>
                      <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-bold ${
                        isUrgent ? 'bg-reserve-urgency/20 text-amber-900 border border-reserve-urgency/40 animate-pulse' : 'bg-stone-100 text-stone-700'
                      }`}>
                        <Clock className="w-3.5 h-3.5" />
                        {countdown.text}
                      </span>
                    </div>
                    <div>
                      <h4 className="font-display font-bold text-lg text-reserve-dark leading-snug">{item.title}</h4>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="font-display font-extrabold text-reserve-primary text-base">{item.quantity_meals} meals</span>
                        <span className="text-stone-300">•</span>
                        <span className="text-xs uppercase tracking-wider font-semibold text-stone-500">{item.food_type.replace('_', ' ')}</span>
                      </div>
                    </div>
                    {item.description && (
                      <p className="text-xs text-stone-600 line-clamp-2 leading-relaxed">{item.description}</p>
                    )}
                    <div className="pt-2 border-t border-stone-100 text-xs text-stone-500 space-y-1">
                      <div className="flex items-center gap-1.5 font-medium text-stone-700">
                        <Building className="w-3.5 h-3.5 text-stone-400 shrink-0" />
                        <span className="truncate">{item.donor_name || 'Verified Kitchen'}</span>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <MapPin className="w-3.5 h-3.5 text-stone-400 shrink-0" />
                        <span className="truncate">{item.pickup_address}</span>
                      </div>
                    </div>
                  </div>
                  <div className="px-5 py-3.5 bg-stone-50 border-t border-stone-100 rounded-b-xl flex items-center justify-between text-xs text-stone-600">
                    <span className="font-medium">Lifecycle State:</span>
                    <span className="font-bold uppercase tracking-wider text-reserve-primary">{item.status}</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}
