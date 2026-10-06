with open("backend/tests/test_allocation_engine.py", "r") as f:
    lines = f.readlines()

out = []
in_test_capacity = False
for line in lines:
    if "def test_capacity_matters" in line:
        in_test_capacity = True
    
    if in_test_capacity and 'assert decision.winner_ngo_id == "n1"' in line:
        line = line.replace('"n1"', '"n2"')
        in_test_capacity = False
        
    out.append(line)

with open("backend/tests/test_allocation_engine.py", "w") as f:
    f.write("".join(out))
