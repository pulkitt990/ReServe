with open("README.md", "r") as f:
    content = f.read()

# Replace old implementation notes with new ones, or update existing ones
notes = """
---

### Implementation Notes for Milestone 2
- **Urgency (0.45)**: Implemented as arrival safety margin `min(1.0, (expiry - (travel_time + 20)) / 120.0)`. High score = safe margin.
- **Proximity (0.30)**: Linear decay `max(0, 1.0 - distance_km / 15.0)`.
- **Capacity (0.25)**: `min(1.0, (available_capacity - quantity) / quantity)`. More remaining capacity = higher score.
"""

if "### Implementation Notes for Milestone 2" in content:
    idx = content.find("### Implementation Notes for Milestone 2")
    content = content[:idx] + notes.strip()
else:
    content += "\n" + notes

with open("README.md", "w") as f:
    f.write(content)
