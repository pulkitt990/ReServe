import re

with open('/Users/pulkit/reserve/frontend/index.html', 'r') as f:
    content = f.read()

fonts = """    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400..900&family=Plus+Jakarta+Sans:wght@400..800&display=swap" rel="stylesheet">
"""

content = content.replace("</head>", fonts + "</head>")

with open('/Users/pulkit/reserve/frontend/index.html', 'w') as f:
    f.write(content)
