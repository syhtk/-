with open('review_response_system.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('json\\n', '`json\\n').replace('}\\n', '}\\n`')

with open('review_response_system.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("json fix done")
