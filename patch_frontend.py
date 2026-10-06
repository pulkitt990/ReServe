import re

with open("frontend/src/App.jsx", "r") as f:
    content = f.read()

# Add state for allocation explanation
state_match = re.search(r'const \[showCreateModal, setShowCreateModal\] = useState\(false\);', content)
if state_match:
    content = content[:state_match.end()] + "\n  const [allocationExplanation, setAllocationExplanation] = useState(null);" + content[state_match.end():]

# Add handleAutoAllocate
handle_allocate = """
  const handleAutoAllocate = async (id) => {
    try {
      const res = await fetch(`/api/v1/allocation/allocate/${id}`, { method: 'POST' });
      if (!res.ok) throw new Error('Failed to auto allocate');
      const data = await res.json();
      
      if (data.status === 'success') {
        setAllocationExplanation(data.allocation);
      } else {
        alert("No eligible NGO found");
      }
      fetchListings();
    } catch (err) {
      console.error(err);
      alert('Error allocating');
    }
  };
"""
# insert before handleUpdateStatus
idx = content.find("const handleUpdateStatus")
content = content[:idx] + handle_allocate + content[idx:]

# Update button
button_old = """onClick={() => handleUpdateStatus(item.id, 'allocated')}
                              className="w-full py-2 px-3 rounded-lg bg-reserve-primary hover:bg-reserve-dark text-white text-xs font-bold transition-all flex items-center justify-center gap-1.5 shadow-sm"
                            >
                              <HeartHandshake className="w-4 h-4 text-reserve-urgency" /> Request Pickup Allocation"""
button_new = """onClick={() => handleAutoAllocate(item.id)}
                              className="w-full py-2 px-3 rounded-lg bg-reserve-primary hover:bg-reserve-dark text-white text-xs font-bold transition-all flex items-center justify-center gap-1.5 shadow-sm"
                            >
                              <HeartHandshake className="w-4 h-4 text-reserve-urgency" /> Auto-allocate"""

content = content.replace(button_old, button_new)

# Add Modal
modal_code = """
      {/* Allocation Explanation Modal */}
      {allocationExplanation && (
        <div className="fixed inset-0 bg-stone-950/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-white rounded-2xl max-w-2xl w-full p-6 shadow-2xl border border-stone-200 space-y-4">
            <div className="flex items-center justify-between border-b border-stone-100 pb-3">
              <h3 className="font-display text-xl font-bold text-reserve-dark">Allocation Decision</h3>
              <button onClick={() => setAllocationExplanation(null)} className="text-stone-400 font-bold">✕</button>
            </div>
            <div className="text-sm space-y-4">
              <p className="font-bold text-reserve-primary">{allocationExplanation.explanation_text}</p>
              <div>
                <h4 className="font-bold border-b pb-1 mb-2">Candidates</h4>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {allocationExplanation.evidence_json?.candidates?.map(c => (
                    <div key={c.ngo_id} className="p-2 border rounded">
                      <div className="font-bold">{c.ngo_id} {c.is_eligible ? '' : `(Rejected: ${c.rejection_reason})`}</div>
                      {c.is_eligible && (
                        <div className="text-xs flex gap-4 text-stone-600">
                          <span>Total: {c.total_score}</span>
                          <span>Urg: {c.weighted_contributions.urgency}</span>
                          <span>Prx: {c.weighted_contributions.proximity}</span>
                          <span>Cap: {c.weighted_contributions.capacity}</span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
"""

# insert before {/* Post Surplus Food Modal */}
idx = content.find("{/* Post Surplus Food Modal */}")
content = content[:idx] + modal_code + content[idx:]

with open("frontend/src/App.jsx", "w") as f:
    f.write(content)

