
with open('c:/Users/kai/OneDrive/桌面/毕业/analytics_module.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
text = re.sub(r'conn\.execute\(', 'conn.cursor().execute(', text)

with open('c:/Users/kai/OneDrive/桌面/毕业/analytics_module.py', 'w', encoding='utf-8') as f:
    f.write(text)
