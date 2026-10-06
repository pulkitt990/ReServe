import React, { useState } from 'react';
import { HeartHandshake, CheckCircle, Package, Clock, Building, MapPin, Settings } from 'lucide-react';

export default function NGODashboard({ 
  listings, loading, formatCountdown, handleAutoAllocate, handleUpdateStatus 
}) {
  const [capacity, setCapacity] = useState(100);

  // Filter listings to OPEN or ALLOCATED to this NGO (for now let's just show open/allocated)
  const displayListings = listings.filter(l => l.status === 'open' || l.status === 'allocated');

  return (
    <div className="space-y-6">
      {/* Capacity Settings */}
      <div className="bg-white rounded-2xl border border-stone-200 p-6 shadow-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Settings className="w-5 h-5 text-reserve-primary" />
            <h3 className="font-display text-xl font-bold text-reserve-dark">Shelter Capacity Settings</h3>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm font-bold text-stone-600">Max Meals:</span>
            <input 
              type="number" 
              value={capacity} 
              onChange={e => setCapacity(e.target.value)}
              className="w-20 px-2 py-1 border border-stone-300 rounded text-sm text-center"
            />
          </div>
        </div>
        <p className="text-xs text-stone-500 mt-2">Adjust your daily capacity to influence auto-allocation algorithms.</p>
      </div>

      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-display text-xl font-bold text-reserve-dark flex items-center gap-2">
            <HeartHandshake className="w-5 h-5 text-reserve-urgency" /> Available Open Listings
          </h3>
          <span className="text-xs text-stone-500">Sorted by proximity & expiry</span>
        </div>

        {loading ? (
          <div className="p-12 text-center bg-white rounded-xl border border-stone-200 text-stone-500 text-sm">
            Loading feed...
          </div>
        ) : displayListings.length === 0 ? (
          <div className="p-12 text-center bg-white rounded-xl border border-dashed border-stone-300 space-y-3">
            <Package className="w-10 h-10 text-stone-400 mx-auto" />
            <p className="text-stone-600 font-semibold text-sm">No open food listings currently available.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {displayListings.map((item) => {
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

                  <div className="px-5 py-3.5 bg-stone-50 border-t border-stone-100 rounded-b-xl flex items-center justify-between gap-2">
                    {item.status === 'open' ? (
                      <button
                        onClick={() => handleAutoAllocate(item.id)}
                        className="w-full py-2 px-3 rounded-lg bg-reserve-primary hover:bg-reserve-dark text-white text-xs font-bold transition-all flex items-center justify-center gap-1.5 shadow-sm"
                      >
                        <HeartHandshake className="w-4 h-4 text-reserve-urgency" /> Auto-allocate
                      </button>
                    ) : item.status === 'allocated' ? (
                      <button
                        onClick={() => handleUpdateStatus(item.id, 'picked_up')}
                        className="w-full py-2 px-3 rounded-lg bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-bold transition-all flex items-center justify-center gap-1.5"
                      >
                        <CheckCircle className="w-4 h-4" /> Confirm Picked Up
                      </button>
                    ) : (
                      <span className="text-xs text-stone-500 italic mx-auto">Claim completed</span>
                    )}
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
