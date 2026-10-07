import React, { useState } from 'react';

export default function CreateListingModal({ isOpen, onClose, fetchListings, setNotification }) {
  if (!isOpen) return null;
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const form = new FormData(e.target);
      // Rough approximation of prep/expiry based on hours provided
      const now = new Date();
      const prepTime = new Date(now.getTime() - parseInt(form.get('prep_hrs')) * 3600000);
      const expiryTime = new Date(now.getTime() + parseInt(form.get('expiry_hrs')) * 3600000);
      
      const payload = {
        donor_id: "1", // Hardcoded to first donor for demo
        title: form.get('title'),
        food_type: form.get('food_type'),
        quantity_meals: parseInt(form.get('qty')),
        description: form.get('desc'),
        pickup_address: "42 Market Street, Sector 18",
        latitude: 28.5700,
        longitude: 77.3200,
        prep_time: prepTime.toISOString(),
        expiry_time: expiryTime.toISOString(),
        dietary_flags: []
      };

      await fetch((import.meta.env.VITE_API_URL || '') + '/api/v1/listings/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      setNotification("New surplus listing created successfully!");
      fetchListings();
      onClose();
    } catch (err) {
      console.error(err);
      setNotification("Failed to create listing.");
    }
    setLoading(false);
  };

  return (
    <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl p-6 w-full max-w-md shadow-2xl relative">
        <h2 className="text-xl font-bold text-reserve-dark mb-4">Log Surplus Food</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div><label className="block text-xs font-bold text-stone-600 mb-1">Food Title</label><input required name="title" className="w-full border rounded-lg p-2 text-sm" placeholder="e.g. 50 portions Dal & Rice" /></div>
          <div className="grid grid-cols-2 gap-4">
            <div><label className="block text-xs font-bold text-stone-600 mb-1">Quantity (Meals)</label><input required name="qty" type="number" className="w-full border rounded-lg p-2 text-sm" placeholder="50" /></div>
            <div><label className="block text-xs font-bold text-stone-600 mb-1">Food Type</label><select name="food_type" className="w-full border rounded-lg p-2 text-sm"><option value="cooked_meals">Cooked Meals</option><option value="produce">Produce</option><option value="bakery">Bakery</option></select></div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div><label className="block text-xs font-bold text-stone-600 mb-1">Prep Time (Hrs Ago)</label><input required name="prep_hrs" type="number" step="0.5" className="w-full border rounded-lg p-2 text-sm" placeholder="2" defaultValue="1" /></div>
            <div><label className="block text-xs font-bold text-stone-600 mb-1">Expires In (Hrs)</label><input required name="expiry_hrs" type="number" step="0.5" className="w-full border rounded-lg p-2 text-sm" placeholder="4" defaultValue="4" /></div>
          </div>
          <div><label className="block text-xs font-bold text-stone-600 mb-1">Description</label><textarea name="desc" className="w-full border rounded-lg p-2 text-sm" placeholder="Brief details about packaging etc." /></div>
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose} className="px-4 py-2 text-sm font-bold text-stone-500">Cancel</button>
            <button type="submit" disabled={loading} className="px-4 py-2 bg-reserve-primary text-white text-sm font-bold rounded-lg">{loading ? 'Saving...' : 'Create Listing'}</button>
          </div>
        </form>
      </div>
    </div>
  );
}
