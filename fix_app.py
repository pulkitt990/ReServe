import re

with open('/Users/pulkit/reserve/frontend/src/App.jsx', 'r') as f:
    content = f.read()

# Remove the broken imports
content = content.replace("import DonorDashboard from './components/DonorDashboard';\n", "")
content = content.replace("import NGODashboard from './components/NGODashboard';\n", "")
content = content.replace("import AdminDashboard from './components/AdminDashboard';\n", "")

# Add them after lucide-react
target = "} from 'lucide-react';\n"
imports = """
import DonorDashboard from './components/DonorDashboard';
import NGODashboard from './components/NGODashboard';
import AdminDashboard from './components/AdminDashboard';
"""

content = content.replace(target, target + imports)

with open('/Users/pulkit/reserve/frontend/src/App.jsx', 'w') as f:
    f.write(content)
